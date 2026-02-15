#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze Gating Latency, RSI & Morphology
========================================

Tests Efficiency and Precision hypotheses using:
1. Latency & RSI (Tone 1, Tone 2).
2. Morphological Metrics (Tone 0, Tone 1, Tone 2):
   - AUC (Area Under Curve): Energy
   - FWHM (Full Width Half Max): Precision/Sharpness
   - Rise Slope: Attack Speed

Outputs:
- latency_stats.csv, rsi_stats.csv, morphology_stats.csv
- Figures: Gating_DiffWave.png
"""

import os
import json
import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats, integrate

import argparse

# Config
# Default values, will be overridden by args
DEFAULT_GLM_DATA_FILE = "derivatives/glm_data/glm_dataset_erp_baselocal.h5"
ROI_JSON = "derivatives/rois/functional_rois.json"
OUT_DIR = "derivatives/analysis/gating"
# Visualization dir will be dynamic based on args

# Time Definitions
FS = None

def detect_fs_from_h5(h5_path):
    """Read FS from HDF5 attribute strictly."""
    import h5py
    with h5py.File(h5_path, 'r') as hf:
        if 'fs' in hf.attrs and hf.attrs['fs'] > 0:
            return float(hf.attrs['fs'])
    raise RuntimeError(f"Could not detect 'fs' attribute in {h5_path}")

def detect_fs_from_npz(npz_path):
    """Read FS from epoch .npz file strictly."""
    import numpy as np
    data = np.load(npz_path, allow_pickle=True)
    if 'fs' not in data:
        raise RuntimeError(f"Missing 'fs' in {npz_path}")
    return float(data['fs'])

T_START = -0.2

# Windows (Absolute Time)
# Tone 0: Previous Tone (-250ms to -50ms) -> [-0.25, -0.05]
# But T_START is -0.2. So we might miss the start of Tone 0 if epoch start is -0.2.
# Check epoch range: user said T_START = -0.2 in previous scripts.
# If Epoch starts at -0.2, we can only analyze -0.2 to -0.05.
# Let's assume we can only analyze available data.
WIN_T0 = (-0.20, -0.05) # Limited by T_START
WIN_T1 = (0.05, 0.20)   # Tone 1
WIN_T2 = (0.25, 0.45)   # Tone 2

WINDOWS = {
    'Tone0': WIN_T0,
    'Tone1': WIN_T1,
    'Tone2': WIN_T2
}

ONSET_MAP = {
    'Tone0': -0.25, # Nominal onset
    'Tone1': 0.0,
    'Tone2': 0.25
}

def load_rois(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def get_roi_indices(channel_names, roi_def, subject):
    if subject not in roi_def['subjects']: return []
    roi_chs = set()
    subj_rois = roi_def['subjects'][subject]
    if 'Auditory' in subj_rois:
        for k, ch_list in subj_rois['Auditory'].items():
            if isinstance(ch_list, list): roi_chs.update(ch_list)
    return [i for i, name in enumerate(channel_names) if name in roi_chs]

def load_data(h5_path, rois):
    data = {} 
    with h5py.File(h5_path, 'r') as hf:
        subjects = set()
        for cond in hf.keys():
            if isinstance(hf[cond], h5py.Group):
                for s in hf[cond].keys(): subjects.add(s)
        
        for subj in subjects:
            # Find channel names
            import glob
            epoch_pat = f"derivatives/epochs/*/{subj}/*.npz"
            epoch_files = glob.glob(epoch_pat)
            if not epoch_files: continue
            tmp = np.load(epoch_files[0], allow_pickle=True)
            ch_names = tmp['channel_names']
            
            roi_idx = get_roi_indices(ch_names, rois, subj)
            if not roi_idx: continue
            
            Y_list = []
            X_list = []
            
            for cond in hf.keys():
                if subj in hf[cond]:
                    g = hf[f"{cond}/{subj}"]
                    if "Y" in g and "X" in g:
                        y_raw = g["Y"][:]
                        y_roi = np.mean(y_raw[:, roi_idx, :], axis=1)
                        
                        cols = list(g.attrs["columns"])
                        x_grp = g["X"]
                        d = {}
                        for c in cols:
                            vals = x_grp[c][:]
                            d[c] = [v.decode('utf-8') if isinstance(v, bytes) else v for v in vals]
                        x_df = pd.DataFrame(d)
                        
                        Y_list.append(y_roi)
                        X_list.append(x_df)
            
            if Y_list:
                data[subj] = {
                    "Y": np.concatenate(Y_list, axis=0),
                    "X": pd.concat(X_list, axis=0, ignore_index=True)
                }
    return data

def calc_morphology(wave, times, win, tone_onset):
    """
    Calculate AUC, FWHM, RiseSlope in window.
    """
    idx = np.where((times >= win[0]) & (times <= win[1]))[0]
    if len(idx) < 3: return None
    
    seg = wave[idx]
    t_seg = times[idx]
    
    # 1. AUC (Absolute Area)
    auc = integrate.simps(np.abs(seg), t_seg)
    
    # Peak Analysis for FWHM & Slope
    # Use max absolute peak
    i_peak = np.argmax(np.abs(seg))
    amp_peak = np.abs(seg[i_peak]) # Magnitude
    t_peak = t_seg[i_peak]
    val_peak = seg[i_peak] # Signed value
    
    # 2. Rise Slope
    # (PeakAmp - val_at_onset) / (PeakTime - Onset)
    # Be careful if Onset is outside window (e.g. Tone 0 starts at -0.25 but we have data from -0.2)
    # Let's use Start of Window as anchor if onset is far. 
    # User said: "250ms -> Tone 2 Peak". This implies Window Start -> Peak.
    
    t_anchor = win[0] 
    # Interpolate amp at t_anchor
    try:
        val_anchor = np.interp(t_anchor, times, wave)
    except:
        val_anchor = seg[0]

    if t_peak > t_anchor:
        rise_slope = (np.abs(val_peak) - np.abs(val_anchor)) / (t_peak - t_anchor)
    else:
        rise_slope = 0 # Peak is at start?
        
    # 3. FWHM (Full Width Half Max)
    # Find points crossing 0.5 * amp_peak
    half_max = 0.5 * amp_peak
    
    # This is tricky for noisy ERPs. We look for crossings around the peak.
    # Take Abs curve
    abs_seg = np.abs(seg)
    
    # Left crossing
    # Search backwards from peak
    left_idx = 0
    for i in range(i_peak, -1, -1):
        if abs_seg[i] < half_max:
            left_idx = i
            break
            
    # Right crossing
    right_idx = len(abs_seg) - 1
    for i in range(i_peak, len(abs_seg)):
        if abs_seg[i] < half_max:
            right_idx = i
            break
            
    fwhm = t_seg[right_idx] - t_seg[left_idx]
    
    return {
        'AUC': auc,
        'Rise_Slope': rise_slope,
        'FWHM': fwhm,
        'Peak_Amp': val_peak,
        'Peak_Lat': t_peak - tone_onset
    }

def main():
    parser = argparse.ArgumentParser(description="Gating Latency & Morphology")
    parser.add_argument("--data_type", type=str, default="erp", choices=['erp', 'hfa'], help="Data type")
    parser.add_argument("--baseline_mode", type=str, default="local", choices=['local', 'global'], help="Baseline strategy")
    args = parser.parse_args()

    data_type = args.data_type
    suffix = "_baselocal" if args.baseline_mode == 'local' else "_baseglobal"
    
    GLM_DATA_FILE = f"derivatives/glm_data/glm_dataset_{data_type}{suffix}.h5"
    VIZ_DIR = f"derivatives/visualization/gating_latency_{data_type}{suffix}"
    
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(VIZ_DIR, exist_ok=True)
    
    rois = load_rois(ROI_JSON)
    print(f"Loading {data_type.upper()} Data ({args.baseline_mode})...")
    if not os.path.exists(GLM_DATA_FILE):
        print(f"Error: {GLM_DATA_FILE} not found.")
        return
        
    data = load_data(GLM_DATA_FILE, rois)

    # Detect FS from data file
    global FS
    FS = detect_fs_from_h5(GLM_DATA_FILE)
    print(f"Detected FS = {FS} Hz")
    
    # Time Vector — derive from actual data shape
    first_subj = next(iter(data.values()))
    n_samp = first_subj['Y'].shape[-1]  # Derived from data shape
    times = np.linspace(T_START, T_START + n_samp/FS, n_samp, endpoint=False)
    
    len_groups = {'Short': [4, 6], 'Long': [12, 16]}
    
    stats_morph = []
    
    # Difference Wave Storage
    wave_avg = {'Short': [], 'Long': []}

    for subj, d in data.items():
        X = d['X']
        Y = d['Y']
        
        for grp_name, lens in len_groups.items():
            mask = X['length'].isin(lens)
            if not mask.any(): continue
            
            y_trials = Y[mask]
            wave_avg[grp_name].append(np.mean(y_trials, axis=0))
            
            # --- Single Trial Morphology ---
            for trial_wave in y_trials:
                for tone_name, win in WINDOWS.items():
                    metrics = calc_morphology(trial_wave, times, win, ONSET_MAP[tone_name])
                    if metrics:
                        metrics['Subject'] = subj
                        metrics['Group'] = grp_name
                        metrics['Tone'] = tone_name
                        stats_morph.append(metrics)
                        
    # Save Morphology Stats
    df_morph = pd.DataFrame(stats_morph)
    df_morph.to_csv(os.path.join(OUT_DIR, f"morphology_stats_{data_type}{suffix}.csv"), index=False)
    
    print("\n--- Morphological Analysis Summary (Mean) ---")
    if not df_morph.empty:
        summary = df_morph.groupby(['Subject', 'Tone', 'Group'])[['AUC', 'FWHM', 'Rise_Slope']].mean()
        print(summary)
    
    # Difference Wave Plot (Re-implemented here for completeness)
    diff_waves = []
    
    subj_list = list(data.keys())
    if not subj_list: return

    # Ensure matched subjects
    # Assuming Carol/Boss both exist.
    
    # Grand Average
    if wave_avg['Short'] and wave_avg['Long']:
        ga_short = np.mean(wave_avg['Short'], axis=0)
        ga_long = np.mean(wave_avg['Long'], axis=0)
        ga_diff = ga_long - ga_short
        
        plt.figure(figsize=(10, 6))
        t_ms = times * 1000
        plt.plot(t_ms, ga_diff, label='Difference (Long - Short)', color='purple', linewidth=2)
        plt.axhline(0, color='k', linestyle='-', linewidth=0.5)
        plt.axvline(0, color='k', linestyle='--')
        plt.axvline(250, color='k', linestyle='--')
        
        # Highlight Windows
        colors = {'Tone0': 'blue', 'Tone1': 'green', 'Tone2': 'red'}
        for tone, win in WINDOWS.items():
            plt.axvspan(win[0]*1000, win[1]*1000, color=colors[tone], alpha=0.1, label=f"{tone} Window")
        
        plt.title(f"Difference Wave & Analysis Windows ({data_type.upper()} {args.baseline_mode})")
        plt.xlabel("Time (ms)")
        plt.ylabel("Amplitude Diff (uV)")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(VIZ_DIR, "Gating_DiffWave.png"))
        plt.close()

if __name__ == "__main__":
    main()
