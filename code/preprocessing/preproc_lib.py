import numpy as np
import scipy.io as sio
from scipy.signal import butter, sosfiltfilt, iirnotch, filtfilt, hilbert
import pandas as pd
import os
import json

# --- CONFIG ---
IMPEDANCE_THRESHOLD_KOHM = 3.0  # 3 kOhm
REF_CHANNELS = ["CH11", "CH27"]
FS_TARGET = 500.0
HFA_BAND = (70.0, 150.0)
FILTER_ORDER = 4

def load_cortec_data(mat_path):
    """Loads a Cortec .mat file and extracts signals/fs/ch_names."""
    if not os.path.exists(mat_path):
        raise FileNotFoundError(f"File not found: {mat_path}")
    
    try:
        mat = sio.loadmat(mat_path, struct_as_record=False, squeeze_me=True)
    except Exception as e:
        print(f"Error loading {mat_path}: {e}")
        return None, None, None

    if 'data_st' not in mat:
        raise ValueError("Invalid Cortec file format: 'data_st' missing.")
        
    st = mat['data_st']
    fs = float(getattr(st, 'sampling_rate'))
    signals = getattr(st, 'signals') # (n_samples, n_ch)
    ch_names = getattr(st, 'channel_names')
    
    # Ensure signals are (Time, Channels)
    if signals.shape[0] < signals.shape[1]: 
        print(f"Warning: Transposing signals from {signals.shape}")
        signals = signals.T
    
    # Ensure correct type
    signals = signals.astype(np.float32)

    # Clean channel names
    ch_clean = []
    # Handle both single string array and object array
    if isinstance(ch_names, np.ndarray):
        for c in ch_names:
            if isinstance(c, (str, np.str_)):
                ch_clean.append(str(c).strip())
            else:
                ch_clean.append(str(c).strip())
    else:
         ch_clean = [str(ch_names).strip()]
            
    return signals, fs, ch_clean

def check_impedance(imp_csv_path, ch_names_all):
    """
    Reads headerless impedance CSV.
    Assumes 32 lines corresponding to CH01-CH32.
    Returns list of bad channel names based on > 4k Ohm threshold.
    """
    if not os.path.exists(imp_csv_path):
        print(f"Warning: Impedance file not found: {imp_csv_path}")
        return []
        
    try:
        # Read headerless
        df = pd.read_csv(imp_csv_path, header=None)
        
        # Expecting at least 32 values
        if len(df) < 32:
            print(f"Warning: Impedance file has {len(df)} lines, expected >=32.")
            
        vals = pd.to_numeric(df[0], errors='coerce').values
        
        bad_imp = []
        
        # Map line i to CH{i+1}
        # Only check up to 32
        for i in range(min(32, len(vals))):
            z = vals[i]
            expected_name = f"CH{i+1:02d}"
            
            # If channel exists in the recording
            if expected_name in ch_names_all:
                # Logic: If > Threshold OR NaN/Inf
                # Check for NaN, Inf, or > Threshold
                if np.isnan(z) or np.isinf(z) or z > (IMPEDANCE_THRESHOLD_KOHM * 1000):
                    bad_imp.append(expected_name)
        
        return bad_imp
            
    except Exception as e:
        print(f"Error reading impedance checking: {e}")
        return []

def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    if high >= 1.0: high = 0.99
    sos = butter(order, [low, high], btype='band', output='sos')
    return sos

def apply_preprocessing_step(signals, fs, ch_names, bad_channels_pre=[], ref_exclude_names=[]):
    """
    Full preprocessing chain:
    1. Bandpass 0.5-250
    2. Notch
    3. Iterative Bad Channel (combined with bad_channels_pre)
    4. Selective CMR (Common Median Reference)
    5. HFA Extraction
    """
    
    # 1. Bandpass
    sos_bp = butter_bandpass(0.5, 240.0, fs, order=FILTER_ORDER)
    sig_bp = sosfiltfilt(sos_bp, signals, axis=0)
    
    # 2. Notch
    for f0 in [60, 120, 180]:
        if f0 < 0.5 * fs:
            b, a = iirnotch(w0=f0, Q=30.0, fs=fs)
            sig_bp = filtfilt(b, a, sig_bp, axis=0)
            
    # 3. Bad Channel Detection
    # Only analyze 'CH' channels
    ch_idx_map = {name: i for i, name in enumerate(ch_names)}
    ch_indices = [i for i, name in enumerate(ch_names) if name.startswith("CH")]
    
    # Initial bad set (Impedance + Ref) -> Convert to indices
    bad_indices_pre = []
    for name in bad_channels_pre:
        if name in ch_idx_map:
            bad_indices_pre.append(ch_idx_map[name])
            
    # Iterative MAD 
    # Logic: robust z-score of SD
    current_bads = set(bad_indices_pre)
    
    for _ in range(3):
        good = [i for i in ch_indices if i not in current_bads]
        if not good: break
        
        # Robust CMR for detection
        ref = np.median(sig_bp[:, good], axis=1, keepdims=True)
        sig_check = sig_bp - ref
        
        # SD
        sds = np.std(sig_check[:, ch_indices], axis=0)
        med_sd = np.median(sds)
        mad = np.median(np.abs(sds - med_sd)) * 1.4826
        z = np.abs(sds - med_sd) / (mad + 1e-6)
        
        # Map back to original indices
        new_bads = []
        for i, val in enumerate(z):
            if val > 3.5: # Threshold
                real_idx = ch_indices[i]
                if real_idx not in current_bads:
                    new_bads.append(real_idx)
                    
        if not new_bads: break
        current_bads.update(new_bads)
        
    final_bad_names = [ch_names[i] for i in sorted(list(current_bads))]
    
    # 4. Selective CMR (Common Median Reference)
    # Exclude both auto-detected bads AND requested exclusion list (e.g. Auditory ROI)
    exclude_indices = set(current_bads)
    for name in ref_exclude_names:
        if name in ch_idx_map:
            exclude_indices.add(ch_idx_map[name])
            
    good_final = [i for i in ch_indices if i not in exclude_indices]
    
    if good_final:
        cmr_signal = np.median(sig_bp[:, good_final], axis=1, keepdims=True)
        sig_cmr = sig_bp - cmr_signal
    else:
        sig_cmr = sig_bp
        
    # 5. HFA Extraction (70-150Hz)
    sos_gamma = butter_bandpass(HFA_BAND[0], HFA_BAND[1], fs, order=FILTER_ORDER)
    sig_gamma = sosfiltfilt(sos_gamma, sig_cmr, axis=0)
    sig_hfa = np.abs(hilbert(sig_gamma, axis=0))
    
    return {
        "signals_cmr": sig_cmr,
        "hfa": sig_hfa,
        "bad_channels_final": final_bad_names,
        "fs": fs
    }
