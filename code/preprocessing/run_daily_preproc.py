#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Phase 1: Preprocessing (Selective CMR & Artifact Masking)
-------------------------------------------------------
Referencing: Selective Common Median Reference (CMR)
    - Reference Pool: All Channels - (Impedance Bad (>3k) + Hard Refs (11,27) + Auditory ROI)
    - Apply: Subtract Median(Reference Pool) from ALL channels.

Bad Channels:
    - Impedance > 3k Ohm
    - Hard coded refs: CH11, CH27
    - (Optionally) Manual bad channels from functional_rois.json

Artifact Marking:
    - Time-resolved Peak-to-Peak (PtP) detection.
    - Used for bad epoch rejection in Phase 2.

Output:
    - derivatives/preproc/<Subject>/<Session>/<file>_preproc.npz
"""

import os
import sys
import json
import glob
import logging
import numpy as np
import scipy.io as sio
from scipy.signal import butter, sosfiltfilt, iirnotch, hilbert, resample
from pathlib import Path
from datetime import datetime

# --- CONFIGURATION ---
# Filters
LOWCUT = 0.5
HIGHCUT = 250.0
NOTCH_FREQS = [60, 120, 180]
HFA_BAND = (70.0, 150.0)
FILTER_ORDER = 4

# Impedance
IMPEDANCE_THRESHOLD = 3000.0  # Ohms (> 3k is bad)
HARD_EXCLUDE_CHS = [11, 27]   # 1-based index (CH11, CH27)

# Artifact Detection (PtP)
ART_WIN_SEC = 1.0
ART_STEP_SEC = 0.5
ART_THR_FACTOR = 5.0  # Threshold factor for PtP (std deviations or similar? Old pipeline used median * factor)
# We will use the logic from old pipeline: 
#   thr = factor * median(ptp_values) 

# Sampling
TARGET_FS = 500.0

# Paths
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
DATA_ROOT = PROJECT_ROOT / "data"
DERIVATIVES_ROOT = PROJECT_ROOT / "derivatives"
PREPROC_OUT_DIR = DERIVATIVES_ROOT / "preproc"
ROIS_JSON_PATH = DERIVATIVES_ROOT / "rois" / "functional_rois.json"

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths (second block — not duplicated above)
ELECTRODE_JSON_PATH = DATA_ROOT / "electrode_bipolar.json"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- HELPERS ---

def load_remapping(subject_name):
    """Load channel remapping for the subject from electrode_bipolar.json."""
    if not ELECTRODE_JSON_PATH.exists():
        logger.warning("electrode_bipolar.json not found.")
        return {}
    
    with open(ELECTRODE_JSON_PATH, 'r') as f:
        config = json.load(f)
    
    return config.get("channel_remapping", {}).get(subject_name, {})

def apply_remapping(signals, ch_names, imp_values, remap_dict):
    """
    Swap signals and impedance values based on remapping dict.
    remap_dict: {'CH09': 'CH01', ...} means Raw 'CH09' should be labeled 'CH01'.
    Wait, usually remapping is RawName -> RealName.
    JSON says: "CH09": "CH01", "CH01": "CH09".
    This implies indices need to be swapped.
    
    We need to map:
    - signals column for Raw CH01 -> becomes data for Real CH09
    - signals column for Raw CH09 -> becomes data for Real CH01
    
    - imp_values index for Raw CH01 -> becomes imp for Real CH09
    """
    if not remap_dict:
        return signals, ch_names, imp_values
        
    # Create mapping: current_name -> new_name
    # ch_names are 'CH01', 'CH02'... based on raw index.
    
    new_ch_names = list(ch_names)
    new_signals = signals.copy()
    new_imp = imp_values.copy()
    
    # We must be careful not to double swap if we iterate.
    # Map index to new index?
    # Or just rename properties?
    
    # Let's perform a swap.
    # Identify indices of channels involved
    name_to_idx = {n: i for i, n in enumerate(ch_names)}
    
    # Check consistency
    for source, target in remap_dict.items():
        if source not in name_to_idx:
            continue
            
    # Actually, simpler: Construct new arrays.
    # We want the result to be sorted CH01..CH32 usually?
    # Or just correctly labeled.
    # Let's rename the list `new_ch_names` first.
    
    # If JSON: "CH09": "CH01" implies the channel currently named CH09 is actually CH01.
    # So we change the NAME of the column. Data stays (it is the recording of that wire).
    
    # Example: Wire 9 (Raw CH09) is connected to Electrode 1 location.
    # So we should call it CH01.
    # Wire 1 (Raw CH01) is connected to Electrode 9 location.
    # So we should call it CH09.
    
    # So we just rename the `ch_names` entries?
    # AND verify impedance?
    # Impedance array at index 0 is Wire 1 (Raw CH01).
    # If we rename Raw CH01 to "CH09", then Impedance[0] belongs to "CH09".
    # So we don't need to swap data columns, just RENAME them?
    
    # BUT, downstream we prefer channels to be in order CH01, CH02...
    # So after renaming, we should re-sort everything (signals, impedance, names) by name.
    
    # 1. Rename
    temp_names = list(ch_names)
    for i, name in enumerate(ch_names):
        if name in remap_dict:
            temp_names[i] = remap_dict[name]
            
    # 2. Re-sort to standard order (CH01...CH32)
    # Combine into tuples and sort
    combined = []
    for i in range(len(temp_names)):
        combined.append({
            'name': temp_names[i],
            'sig': signals[:, i],
            'imp': imp_values[i]
        })
        
    combined.sort(key=lambda x: x['name'])
    
    # Unpack
    sorted_names = [x['name'] for x in combined]
    sorted_sig = np.stack([x['sig'] for x in combined], axis=1)
    sorted_imp = np.array([x['imp'] for x in combined])
    
    logger.info(f"Remapped channels: {remap_dict}")
    return sorted_sig, sorted_names, sorted_imp

def load_functional_rois_and_bad(subject_name):
    """Load Auditory ROI channels and Manual Bad channels from JSON."""
    if not ROIS_JSON_PATH.exists():
        logger.warning(f"Functional ROIs JSON not found at {ROIS_JSON_PATH}")
        return set(), set()
    
    with open(ROIS_JSON_PATH, 'r') as f:
        rois = json.load(f)
    
    subj_data = rois.get("subjects", {}).get(subject_name, {})
    if not subj_data:
        logger.warning(f"No entry for subject {subject_name} in ROIs JSON")
        return set(), set()

    # Flatten Auditory ROIs
    aud_channels = set()
    aud_groups = subj_data.get("Auditory", {})
    for group_name, ch_list in aud_groups.items():
        if isinstance(ch_list, list):
            aud_channels.update(ch_list)
    
    # Manual Bad Channels
    manual_bad = set(subj_data.get("Bad_Channels", []))
    
    return aud_channels, manual_bad

def load_impedance(subject_name, date_str):
    """Load impedance CSV for the given subject and date (YYYYMMDD)."""
    imp_dir = DATA_ROOT / "impedance" / subject_name
    # Pattern: YYYYMMDD*.csv
    pattern = str(imp_dir / f"{date_str}*.csv")
    files = sorted(glob.glob(pattern))
    
    if not files:
        logger.warning(f"No impedance file found for {subject_name} on {date_str}. Assuming all pass (except hard excludes).")
        return np.full(32, 0.0) # Dummy 0 impedance
    
    # Pick the first one
    imp_file = files[0]
    logger.info(f"Loading impedance from {imp_file}")
    
    try:
        # Read 32 lines, no header
        imp_values = np.loadtxt(imp_file)
        if len(imp_values) != 32:
            logger.error(f"Impedance file {imp_file} has {len(imp_values)} lines, expected 32.")
            return np.full(32, np.inf) # Fail safe
        return imp_values
    except Exception as e:
        logger.error(f"Error reading impedance file: {e}")
        return np.full(32, np.inf)

def get_bad_channels_impedance(imp_values, threshold=IMPEDANCE_THRESHOLD):
    """Return list of bad channel names (e.g. 'CH01') based on impedance."""
    bad_indices = np.where(imp_values > threshold)[0] # 0-based
    bad_names = [f"CH{i+1:02d}" for i in bad_indices]
    return set(bad_names)

def butter_bandpass_sos(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = butter(order, [low, high], btype='band', output='sos')
    return sos

def bandpass_filter(data, sos):
    """Apply SOS bandpass filter."""
    return sosfiltfilt(sos, data, axis=0)

def notch_filter(data, fs, freqs):
    """Apply IIR Notch filter for each freq."""
    data_out = data.copy()
    for f in freqs:
        b, a = iirnotch(f, Q=30, fs=fs)
        data_out = scipy.signal.filtfilt(b, a, data_out, axis=0) # zero-phase
    return data_out

import scipy.signal

def detect_artifacts_ptp(data, fs, win_sec=ART_WIN_SEC, step_sec=ART_STEP_SEC, thr_factor=ART_THR_FACTOR):
    """
    Detect artifacts using sliding window Peak-to-Peak amplitude.
    Returns a boolean mask (same shape as data).
    """
    n_samples, n_ch = data.shape
    win_samples = int(win_sec * fs)
    step_samples = int(step_sec * fs)
    
    mask = np.zeros_like(data, dtype=bool)
    
    # Calculate PtP for every window
    # To be robust, we can calculate PtP profile first?
    # Simple sliding window loop might be slow but straightforward.
    
    # Vectorized approach for efficiency?
    # Let's stick to simple loop for now, optimize if slow.
    
    # We need a threshold. Old pipeline: median * factor ??
    # Implementation Plan says: "Sliding window Peak-to-Peak (PtP) detection."
    # Let's define threshold as: Median PtP of the channel * Factor.
    
    # 1. Calculate PtP profile (rough)
    # Actually, let's just loop windows and mark them.
    # We accept that we need to first compute the threshold.
    
    # Compute global median PtP per channel to set threshold?
    # Or just use a fixed high value? usually relative is better.
    
    # Let's use a simplified approach:
    # Calculate envelope or rolling PtP?
    # Let's iterate windows to compute median PtP 
    
    start_indices = range(0, n_samples - win_samples, step_samples)
    ptp_values = []
    
    # First pass: collect PtPs to find median
    # (Actually, calculating median of ALL windows might be memory intensive if we store all)
    # Let's just pick a subset or calculate on the fly?
    # Optimization: Calculate PtP for all windows first.
    
    n_windows = len(start_indices)
    window_ptps = np.zeros((n_windows, n_ch))
    
    for i, start in enumerate(start_indices):
        end = start + win_samples
        chunk = data[start:end, :]
        ptp = np.ptp(chunk, axis=0)
        window_ptps[i, :] = ptp
        
    # Per-channel threshold
    median_ptps = np.median(window_ptps, axis=0)
    thresholds = median_ptps * thr_factor
    
    # Mark artifacts
    for i, start in enumerate(start_indices):
        end = start + win_samples
        # Check which channels exceed threshold
        bad_mask = window_ptps[i, :] > thresholds
        if np.any(bad_mask):
            # Mark the whole window for that channel as bad
            # (mask[start:end, ch] = True)
            # We want to identify TIME segments that are bad?
            # Or Channel-Time segments? Reference says "Output: A boolean mask artifact_mask (Time x Channels)".
            # So channel-specific masking is good.
            for ch_idx in np.where(bad_mask)[0]:
                mask[start:end, ch_idx] = True
                
    return mask

def process_file(mat_file, subject_name):
    # 1. Load Data
    logger.info(f"Processing {mat_file.name}...")
    try:
        mat_contents = sio.loadmat(mat_file, squeeze_me=True, struct_as_record=False)
        if 'data_st' not in mat_contents:
            logger.error(f"Missing 'data_st' in {mat_file.name}")
            return
        
        data_st = mat_contents['data_st']
        fs_raw = float(data_st.sampling_rate)
        
        # Helper to safely get channel names
        raw_ch_names = data_st.channel_names
        if isinstance(raw_ch_names, (np.ndarray, list)):
             raw_ch_names = [str(x).strip() for x in raw_ch_names]
        else:
             logger.error("Unknown channel_names format")
             return

        # Helper to safely get experiment_stimuli -> sequence_version
        try:
            seq_ver_raw = getattr(data_st, "experiment_stimuli", "")
            # Basic cleaning if it's char array
            if isinstance(seq_ver_raw, np.ndarray):
                sequence_version = "".join([chr(c) for c in seq_ver_raw.flatten()]) if seq_ver_raw.size > 0 else ""
            else:
                 sequence_version = str(seq_ver_raw)
        except:
            sequence_version = "unknown"

        # signals: (Samples, Channels) or (Channels, Samples)?
        # Usually (Samples, Channels) in Python from MATLAB 'signals' if it was Time x Ch.
        # Check shape.
        signals = data_st.signals
        if signals.shape[0] < signals.shape[1]: 
            # Likely Ch x Time, transpose
            signals = signals.T
        
        # Filter for CHxx channels only (exclude others if any)
        ch_indices = [i for i, name in enumerate(raw_ch_names) if name.startswith("CH") and len(name) <= 4]
        # Adjust check to be more robust, e.g. "CH01", "CH1". assuming standard naming
        
        # Actually, let's trust the indices 0-31 map to CH01-CH32 if there are 32 channels.
        # But let's be safe and pick by name.
        ch_names = [raw_ch_names[i] for i in ch_indices]
        signals = signals[:, ch_indices]
        
    except Exception as e:
        logger.error(f"Failed to load {mat_file.name}: {e}")
        return

    # 2. Impedance Check
    date_str = mat_file.stem[:8] # YYYYMMDD
    imp_values = load_impedance(subject_name, date_str)
    
    # --- REMAPPING START ---
    # Apply Channel Remapping (Raw -> Real)
    # This must happen before Bad Channel detection and ROI lookup.
    remap_dict = load_remapping(subject_name)
    if remap_dict:
        signals, ch_names, imp_values = apply_remapping(signals, ch_names, imp_values, remap_dict)
    # --- REMAPPING END ---
    
    # Identify Bad Channels
    # A. Impedance Bad
    bad_imp_names = get_bad_channels_impedance(imp_values)
    
    # B. Hard Excludes
    bad_hard_names = {f"CH{i:02d}" for i in HARD_EXCLUDE_CHS}
    
    # C. ROI Lookup (For Reference Exclusion ONLY)
    # User requested to IGNORE bad channels from JSON.
    aud_rois, _ = load_functional_rois_and_bad(subject_name)
    
    # Combine Bad Channels for Reference Exclusion
    # "Reference Pool Definition: Start with ALL, Exclude Imp Bad, Hard Excludes, and Auditory ROI"
    # Manual Bad from JSON is IGNORED based on user request.
    
    all_bad_names = bad_imp_names.union(bad_hard_names)
    
    # Identify indices
    ch_name_to_idx = {name: i for i, name in enumerate(ch_names)}
    
    bad_indices = [ch_name_to_idx[n] for n in all_bad_names if n in ch_name_to_idx]
    aud_indices = [ch_name_to_idx[n] for n in aud_rois if n in ch_name_to_idx]
    
    # Reference Exclusion Set (Indices)
    ref_exclude_indices = set(bad_indices).union(set(aud_indices))
    
    # Reference Pool Indices (Sorted List)
    all_indices = set(range(len(ch_names)))
    ref_pool_indices = sorted(list(all_indices - ref_exclude_indices))
    
    if len(ref_pool_indices) == 0:
        logger.error(f"No channels left for reference! (ImpBad: {len(bad_indices)}, AudROI: {len(aud_indices)})")
        # Fallback? Maybe using mean of all? Or just fail.
        # Let's fail.
        return

    # 3. Signal Conditioning
    # Bandpass
    sos = butter_bandpass_sos(LOWCUT, HIGHCUT, fs_raw, order=FILTER_ORDER)
    signals_bp = bandpass_filter(signals, sos)
    
    # Notch
    signals_notch = notch_filter(signals_bp, fs_raw, NOTCH_FREQS)
    
    # 4. Selective CMR
        # Calculate Median of Reference Pool
    ref_signal = np.median(signals_notch[:, ref_pool_indices], axis=1, keepdims=True)
    
    # Apply to ALL channels
    signals_cmr = signals_notch - ref_signal
    
    # 5. Feature Extraction
    
    # A. LFP (Downsample)
    # Resample to TARGET_FS
    # Calculate number of samples
    num_samples_target = int(len(signals_cmr) * TARGET_FS / fs_raw)
    signals_lfp = resample(signals_cmr, num_samples_target, axis=0) # This does FFT resampling
    
    # B. HFA
    # Filter 70-150 Hz (on CMR signal)
    sos_hfa = butter_bandpass_sos(HFA_BAND[0], HFA_BAND[1], fs_raw, order=FILTER_ORDER)
    hfa_amp = np.abs(hilbert(bandpass_filter(signals_cmr, sos_hfa), axis=0))
    # Downsample HFA envelope
    hfa_env = resample(hfa_amp, num_samples_target, axis=0)
    
    # 6. Artifact Masking (on LFP?)
    # Plan says: "Artifact Masking (Time-Resolved)... This mask is used in Phase 2"
    # Should use the Cleaned LFP signals (signals_lfp).
    # PtP detection
    artifact_mask = detect_artifacts_ptp(signals_lfp, TARGET_FS)
    
    # 7. Determine Output Directory based on Condition
    # Search for matching event file in bids_events
    events_candidates = list(sorted((DATA_ROOT / "bids_events").glob(f"*/{subject_name}/{mat_file.stem}_events.tsv")))
    
    if len(events_candidates) > 0:
        event_file = events_candidates[0]
        condition_name = event_file.parent.parent.name
        logger.info(f"Found condition: {condition_name}")
    else:
        condition_name = "Unknown"
        logger.warning(f"No event file found for {mat_file.stem}, using 'Unknown' condition.")
    
    # Prepare output directory
    subject_out_dir = PREPROC_OUT_DIR / condition_name / subject_name
    subject_out_dir.mkdir(parents=True, exist_ok=True)
    
    out_name = f"{mat_file.stem}_preproc.npz"
    out_path = subject_out_dir / out_name
    
    np.savez_compressed(
        out_path,
        signals_cmr=signals_lfp.astype(np.float32),
        hfa_cmr=hfa_env.astype(np.float32),
        artifact_mask=artifact_mask,
        fs=TARGET_FS,
        channel_names=ch_names,
        sequence_version=sequence_version,
        bad_channels=list(all_bad_names), # For record
        ref_pool_size=len(ref_pool_indices)
    )
    logger.info(f"Saved {out_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run daily preprocessing (Phase 1).")
    parser.add_argument("--subject", type=str, help="Process only this subject")
    parser.add_argument("--file", type=str, help="Process only this specific file (stem or full name)")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of files per subject (0 = no limit)")
    args = parser.parse_args()

    if not DATA_ROOT.exists():
        logger.error(f"Data root not found: {DATA_ROOT}")
        return

    # Iterate Subjects
    matfiles_root = DATA_ROOT / "matfiles"
    if not matfiles_root.exists():
         logger.error(f"Matfiles root not found: {matfiles_root}")
         return

    subjects = [d for d in matfiles_root.iterdir() if d.is_dir()]
    if args.subject:
        subjects = [d for d in subjects if d.name == args.subject]

    for subject_dir in subjects:
        subject_name = subject_dir.name
        
        # Load ROIs once to verify subject exists in JSON
        _, _ = load_functional_rois_and_bad(subject_name)
        
        logger.info(f"--- Subject: {subject_name} ---")
        
        # Iterate Files
        mat_files = sorted(subject_dir.glob("*.mat"))
        if args.file:
            mat_files = [f for f in mat_files if args.file in f.name]
            
        if args.limit > 0:
            mat_files = mat_files[:args.limit]
            
        for mat_file in mat_files:
            process_file(mat_file, subject_name)

if __name__ == "__main__":
    main()
