#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze Gating Coupling (HFA -> ERP)
=====================================

Tests if the "X" shape in HFA at 250ms mechanistically causes the suppression in ERP at 280ms.
Generates:
1. Gating Mechanism Plot (HFA vs ERP timecourses).
2. Trial-by-Trial Correlation Stats (HFA 250ms vs ERP 280ms).

Analysis Logic:
- Load trial-level data for both HFA and ERP.
- Filter key ROIs (Auditory).
- Extract single-trial amplitudes in critical windows.
- Correlate per Subject & Length Condition.
"""

import os
import json
import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import argparse

import argparse

# Config
# Default values
DEFAULT_HFA_FILE = "derivatives/glm_data/glm_dataset_hfa_baselocal.h5"
DEFAULT_ERP_FILE = "derivatives/glm_data/glm_dataset_erp_baselocal.h5"
ROI_JSON = "derivatives/rois/functional_rois.json"
OUT_DIR = "derivatives/analysis/gating"
# VIZ_DIR dynamic

# Time Definitions (strictly read from data)
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
# Helper to get index
def get_idx(time_s):
    return int(round((time_s - T_START) * FS))

# Visualization Window
T_PLOT = (-0.05, 0.45)

# Correlation Windows (widened to 45ms for stability)
# HFA "X" peak: 250ms ± 22.5ms -> [0.2275, 0.2725]
WIN_HFA = (0.2275, 0.2725)
# ERP Suppression: 280ms ± 22.5ms -> [0.2575, 0.3025]
WIN_ERP = (0.2575, 0.3025)

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
    """Load data and extract Auditory ROI averages per subject."""
    data = {} # {subj: {X: df, Y: array}}
    
    with h5py.File(h5_path, 'r') as hf:
        subjects = set()
        for cond in hf.keys():
            if isinstance(hf[cond], h5py.Group):
                for s in hf[cond].keys(): subjects.add(s)
        
        for subj in subjects:
            # Get Channel Names from H5 file directly (no more glob!)
            ch_names = None
            for cond in hf.keys():
                if subj in hf[cond]:
                    g = hf[f"{cond}/{subj}"]
                    if "channel_names" in g:
                        ch_names = [name.decode('utf-8') if isinstance(name, bytes) else name 
                                   for name in g["channel_names"][:]]
                        break
            
            if ch_names is None:
                print(f"Warning: No channel_names found in H5 for {subj}, skipping.")
                continue
            
            roi_idx = get_roi_indices(ch_names, rois, subj)
            if not roi_idx: continue
            
            Y_list = []
            X_list = []
            
            for cond in hf.keys():
                if subj in hf[cond]:
                    g = hf[f"{cond}/{subj}"]
                    if "Y" in g and "X" in g:
                        y_raw = g["Y"][:]
                        y_roi = np.mean(y_raw[:, roi_idx, :], axis=1) # (N, Time)
                        
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

def main():
    parser = argparse.ArgumentParser(description="Gating Coupling Analysis (HFA -> ERP)")
    parser.add_argument("--baseline_mode", type=str, default="local", choices=['local', 'global'], help="Baseline strategy")
    args = parser.parse_args()
    
    suffix = "_baselocal" if args.baseline_mode == 'local' else "_baseglobal"
    
    HFA_FILE = f"derivatives/glm_data/glm_dataset_hfa{suffix}.h5"
    ERP_FILE = f"derivatives/glm_data/glm_dataset_erp{suffix}.h5"
    VIZ_DIR = f"derivatives/visualization/gating_coupling{suffix}"
    
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(VIZ_DIR, exist_ok=True)
    
    rois = load_rois(ROI_JSON)
    
    print(f"Loading HFA Data ({args.baseline_mode})...")
    if not os.path.exists(HFA_FILE):
        print(f"Error: {HFA_FILE} not found.")
        return
    hfa_data = load_data(HFA_FILE, rois)
    
    print(f"Loading ERP Data ({args.baseline_mode})...")
    if not os.path.exists(ERP_FILE):
        print(f"Error: {ERP_FILE} not found.")
        return
    erp_data = load_data(ERP_FILE, rois)
    
    # Common Subjects
    subjects = list(set(hfa_data.keys()) & set(erp_data.keys()))
    print(f"Analyzing Subjects: {subjects}")
    
    # Time Vector (Determined dynamically from data shape)
    FS = detect_fs_from_h5(HFA_FILE)
    n_samp = hfa_data[subjects[0]]['Y'].shape[-1]
    times = np.linspace(T_START, T_START + n_samp/FS, n_samp, endpoint=False)
    
    stats_rows = []
    
    for subj in subjects:
        # Align trials
        # WARNING: HFA and ERP datasets might be sorted differently if concatenated differently.
        # But prepare_glm produces them in same order usually.
        # We must assume 1-to-1 mapping via X columns (trial_id if available?).
        # 'X' contains condition info. We correlate WITHIN Length Group.
        
        X_hfa = hfa_data[subj]['X']
        Y_hfa = hfa_data[subj]['Y']
        X_erp = erp_data[subj]['X']
        Y_erp = erp_data[subj]['Y']
        
        # Verify alignment by checking Length column matches
        if not np.array_equal(X_hfa['length'], X_erp['length']):
            print(f"Warning: Trial mismatch for {subj}. Skipping coupling correlation.")
            continue
            
        # Define Groups
        # Short: 4, 6
        # Long: 12, 16
        len_groups = {
            'Short': [4, 6],
            'Long': [12, 16]
        }
        
        # --- Visualization Data Preparation ---
        # Need Mean +/- SEM for each Group
        # Time Axis filtering
        t_plot_idx = np.where((times >= T_PLOT[0]) & (times <= T_PLOT[1]))[0]
        times_plot = times[t_plot_idx]
        
        viz_data = {'HFA': {}, 'ERP': {}} # {Group: (Mean, SEM)}
        
        for grp_name, lens in len_groups.items():
            mask = X_hfa['length'].isin(lens)
            if not mask.any(): continue
            
            # Extract Timecourses
            hfa_sub = Y_hfa[mask][:, t_plot_idx]
            erp_sub = Y_erp[mask][:, t_plot_idx]
            
            # Mean and SEM
            viz_data['HFA'][grp_name] = (np.mean(hfa_sub, axis=0), stats.sem(hfa_sub, axis=0))
            viz_data['ERP'][grp_name] = (np.mean(erp_sub, axis=0), stats.sem(erp_sub, axis=0))
            
            # --- Coupling Analysis ---
            # Extract scalar values
            idx_hfa_win = np.where((times >= WIN_HFA[0]) & (times <= WIN_HFA[1]))[0]
            idx_erp_win = np.where((times >= WIN_ERP[0]) & (times <= WIN_ERP[1]))[0]
            
            vec_hfa = np.mean(Y_hfa[mask][:, idx_hfa_win], axis=1)
            vec_erp = np.mean(Y_erp[mask][:, idx_erp_win], axis=1)
            
            # Use Spearman correlation (non-parametric) because:
            # - HFA is log-power (non-linear scale)
            # - ERP is voltage (linear scale)
            # - Relationship may be non-linear
            r, p = stats.spearmanr(vec_hfa, vec_erp)
            
            stats_rows.append({
                'Subject': subj,
                'Group': grp_name,
                'Rho_value': r,  # Spearman's rho instead of Pearson's r
                'P_value': p,
                'N_trials': len(vec_hfa)
            })
            
        # --- Plotting Mechanism Plot ---
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10), sharex=True)
        
        # Colors
        c_short = '#1f77b4' # Blue
        c_long = '#d62728'  # Red
        
        # Panel 1: HFA
        for grp, col in zip(['Short', 'Long'], [c_short, c_long]):
            if grp in viz_data['HFA']:
                m, s = viz_data['HFA'][grp]
                ax1.plot(times_plot * 1000, m, color=col, label=grp, linewidth=2)
                ax1.fill_between(times_plot * 1000, m-s, m+s, color=col, alpha=0.2)
        
        # Gating Window & Lines
        for ax in [ax1, ax2]:
            ax.axvline(0, color='k', linestyle='--', alpha=0.5)
            ax.axvline(250, color='k', linestyle='--', alpha=0.5)
            ax.axvspan(250, 310, color='gray', alpha=0.15, label='Gating Window' if ax==ax1 else "")
        
        ax1.set_ylabel("HFA Amplitude (z-score)")
        ax1.set_title(f"Subject {subj}: Gating Mechanism")
        ax1.legend(loc='upper right')
        
        # Annotate X shape (approx)
        ax1.text(250, ax1.get_ylim()[1]*0.9, '"X" Crossover', ha='center', fontsize=10, style='italic')
        
        # Panel 2: ERP
        for grp, col in zip(['Short', 'Long'], [c_short, c_long]):
            if grp in viz_data['ERP']:
                m, s = viz_data['ERP'][grp]
                ax2.plot(times_plot * 1000, m, color=col, label=grp, linewidth=2)
                ax2.fill_between(times_plot * 1000, m-s, m+s, color=col, alpha=0.2)
        
        ax2.set_ylabel("ERP Amplitude (uV)")
        ax2.set_xlabel("Time from Tone Onset (ms)")
        ax2.text(290, ax2.get_ylim()[0]*0.9, 'Suppression Separation', ha='center', fontsize=10, style='italic')
        
        plt.tight_layout()
        plt.savefig(os.path.join(VIZ_DIR, f"Mechanism_Plot_{subj}.png"), dpi=300)
        plt.close()
        
    # Save Stats
    df_stats = pd.DataFrame(stats_rows)
    df_stats.to_csv(os.path.join(OUT_DIR, f"coupling_stats{suffix}.csv"), index=False)
    print("Coupling Analysis Complete.")
    print(df_stats)

if __name__ == "__main__":
    main()
