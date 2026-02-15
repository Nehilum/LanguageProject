#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validation Script: Preprocessing (Phase 1)
-----------------------------------------
Visualizes Raw (Remapped + Filtered) vs CMR signals.
"""

import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from pathlib import Path
from scipy.signal import welch

# Add project root/code to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from preprocessing.run_daily_preproc import (
    load_remapping, apply_remapping, 
    butter_bandpass_sos, bandpass_filter, notch_filter,
    LOWCUT, HIGHCUT, NOTCH_FREQS, FILTER_ORDER, TARGET_FS,
    load_impedance, get_bad_channels_impedance, load_functional_rois_and_bad,
    HARD_EXCLUDE_CHS
)

def plot_signals(raw, cmr, fs, ch_names, title, filename):
    """Plot Raw vs CMR for selected channels (100s - 110s)."""
    n_ch = len(ch_names)
    
    # Slice 100s to 110s
    t_start = 100.0
    t_end = 110.0
    idx_start = int(t_start * fs)
    idx_end = int(t_end * fs)
    
    # Check bounds
    if idx_start >= raw.shape[0]:
        print("Warning: Signal shorter than 100s. Plotting last 10s.")
        idx_start = max(0, raw.shape[0] - int(10*fs))
        idx_end = raw.shape[0]
    elif idx_end > raw.shape[0]:
        idx_end = raw.shape[0]

    raw_seg = raw[idx_start:idx_end, :]
    cmr_seg = cmr[idx_start:idx_end, :]
    t_seg = np.arange(idx_start, idx_end) / fs
    
    # Plot all provided channels (expected to be good ones)
    fig, axes = plt.subplots(n_ch, 1, figsize=(15, 2 * n_ch), sharex=True)
    if n_ch == 1: axes = [axes]
    
    for i in range(n_ch):
        ax = axes[i]
        # Raw might be different scale? 
        # Normalize/Demin? No, plot raw values.
        ax.plot(t_seg, raw_seg[:, i], label='Raw (Filt)', alpha=0.7, linewidth=0.8)
        ax.plot(t_seg, cmr_seg[:, i], label='CMR', alpha=0.7, linewidth=0.8)
        ax.set_ylabel(f"{ch_names[i]}")
        if i == 0:
            ax.legend(loc='upper right')
        
    plt.suptitle(f"{title} (100-110s)")
    plt.xlabel("Time (s)")
    plt.tight_layout()
    plt.savefig(filename)
    print(f"Saved {filename}")

def validate_preproc(npz_file):
    print(f"Validating {npz_file}...")
    data = np.load(npz_file, allow_pickle=True)
    signals_cmr = data['signals_cmr']
    fs_cmr = data['fs']
    ch_names_cmr = data['channel_names']
    bad_channels_list = list(data['bad_channels'])
    
    # Find Raw File
    parts = Path(npz_file).parts
    try:
        subj_idx = parts.index('preproc') + 2
        subject_name = parts[subj_idx]
        mat_stem = Path(npz_file).name.replace('_preproc.npz', '')
    except:
        print("Could not infer subject from path. Please provide standard path structure.")
        return

    # Find mat file
    mat_root = Path(npz_file).resolve().parents[4] / "data" / "matfiles" / subject_name
    mat_file = list(mat_root.glob(f"{mat_stem}.mat"))[0]
    print(f"Loading Raw: {mat_file}")
    
    # Load Raw
    mat = sio.loadmat(mat_file, squeeze_me=True, struct_as_record=False)
    raw = mat['data_st'].signals
    fs_raw = float(mat['data_st'].sampling_rate)
    raw_ch_names = mat['data_st'].channel_names
    if isinstance(raw_ch_names, (np.ndarray, list)):
             raw_ch_names = [str(x).strip() for x in raw_ch_names]
             
    if raw.shape[0] < raw.shape[1]: raw = raw.T
    
    # Filter for CHxx
    ch_indices = [i for i, name in enumerate(raw_ch_names) if name.startswith("CH") and len(name) <= 4]
    raw = raw[:, ch_indices]
    ch_names_raw = [raw_ch_names[i] for i in ch_indices]
    
    # --- REMAP ---
    remap = load_remapping(subject_name)
    # create dummy impedance
    dummy_imp = np.zeros(len(ch_names_raw))
    raw, ch_names_raw, _ = apply_remapping(raw, ch_names_raw, dummy_imp, remap)
    
    # Check if names match
    if not np.array_equal(ch_names_raw, ch_names_cmr):
        print("WARNING: Channel names do not match!")
        
    # Process Raw (Filter only)
    sos = butter_bandpass_sos(LOWCUT, HIGHCUT, fs_raw, order=FILTER_ORDER)
    raw_bp = bandpass_filter(raw, sos)
    raw_notch = notch_filter(raw_bp, fs_raw, NOTCH_FREQS)
    
    # Resample Raw to match CMR fs
    from scipy.signal import resample
    num = int(len(raw_notch) * 250 / fs_raw)
    raw_res = resample(raw_notch, num, axis=0)
    
    # Align length
    min_len = min(len(raw_res), len(signals_cmr))
    raw_res = raw_res[:min_len]
    signals_cmr = signals_cmr[:min_len]
    
    # Filter Good Channels for Plotting
    # Identify Good Channels (Sorted Index)
    good_indices = [i for i, name in enumerate(ch_names_cmr) if name not in bad_channels_list]
    
    # Pick first 10 good channels
    plot_indices = good_indices[:10]
    plot_names = [ch_names_cmr[i] for i in plot_indices]
    
    raw_plot = raw_res[:, plot_indices]
    cmr_plot = signals_cmr[:, plot_indices]
    
    print(f"Plotting Good Channels: {plot_names}")
    
    # Plot
    out_dir = Path("validation_outputs")
    out_dir.mkdir(exist_ok=True)
    plot_signals(raw_plot, cmr_plot, 250, plot_names, f"Raw vs CMR ({subject_name})", out_dir / f"{mat_stem}_trace.png")
    
    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to _preproc.npz file")
    args = parser.parse_args()
    validate_preproc(args.file)
