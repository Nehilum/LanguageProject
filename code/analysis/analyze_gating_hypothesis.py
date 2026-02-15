#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze Gating Hypothesis (Length x MDL)
========================================

Tests if Sequence Length gates the neural processing of Complexity (MDL).
Hypothesis: High MDL is suppressed only in Long sequences.

Features:
- Supports ERP and HFA data types.
- Partial Regression: Controls for Position, ToneID, Repetition, Surprisal confounds.
- Windowed Analysis (Early/Late) -> gating_stats.csv
- Sliding Window Analysis (Time-Resolved) -> gating_sliding_stats.csv
- Waveform Extraction -> gating_waveforms.csv

Outputs:
1. gating_waveforms_{type}.csv
2. gating_stats_{type}.csv
3. gating_sliding_stats_{type}.csv
4. Plots
"""

import os
import json
import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path
import argparse

# Config
ROI_JSON = "derivatives/rois/functional_rois.json"

# Time Windows (s) relative to tone onset
WIN_EARLY = (0.05, 0.25)
WIN_LATE = (0.25, 0.50)
BASELINE = (-0.05, 0.0) 

def load_rois(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def get_roi_indices(channel_names, roi_def, subject):
    """Get indices for Auditory ROI."""
    if subject not in roi_def['subjects']:
        return []
    
    # Target: Auditory
    roi_chs = set()
    subj_rois = roi_def['subjects'][subject]
    
    if 'Auditory' in subj_rois:
        for k, ch_list in subj_rois['Auditory'].items():
            if isinstance(ch_list, list):
                roi_chs.update(ch_list)
    
    indices = [i for i, name in enumerate(channel_names) if name in roi_chs]
    return indices

def residualize(target, nuisance_mat):
    """Remove variance explained by nuisance regressors from target via OLS.
    
    Returns residuals of target after regressing out nuisance_mat.
    """
    # Add intercept to nuisance
    N = len(target)
    X_nuis = np.column_stack([np.ones(N), nuisance_mat])
    # OLS: target = X_nuis @ beta + residual
    beta, _, _, _ = np.linalg.lstsq(X_nuis, target, rcond=None)
    residual = target - X_nuis @ beta
    return residual

def build_nuisance_matrix(X_sub):
    """Build nuisance matrix from available confound columns."""
    nuisance_cols = []
    for col in ['pos', 'tone_id', 'repetition', 'surprisal']:
        if col in X_sub.columns:
            vals = pd.to_numeric(X_sub[col], errors='coerce').fillna(0).values
            nuisance_cols.append(vals)
    if nuisance_cols:
        return np.column_stack(nuisance_cols)
    else:
        return np.zeros((len(X_sub), 1))

def get_mdl_bins(df_sub, n_bins=3):
    """Bin MDL into Low/Med/High."""
    unique_mdl = np.sort(df_sub['mdl'].unique())
    if len(unique_mdl) < 3:
        bin_map = {unique_mdl[0]: 'Low', unique_mdl[-1]: 'High'}
        return df_sub['mdl'].map(bin_map)
    else:
        try:
            return pd.qcut(df_sub['mdl'], q=n_bins, labels=['Low', 'Medium', 'High'])
        except ValueError:
             return pd.cut(df_sub['mdl'], bins=n_bins, labels=['Low', 'Medium', 'High'])

def main():
    parser = argparse.ArgumentParser(description="Gating Analysis")
    parser.add_argument("--data_type", type=str, default="erp", choices=['erp', 'hfa'], help="Data type (erp or hfa)")
    parser.add_argument("--baseline_mode", type=str, default="local", choices=['local', 'global'], help="Baseline strategy (local or global)")
    args = parser.parse_args()
    
    data_type = args.data_type
    suffix = "_baselocal" if args.baseline_mode == 'local' else "_baseglobal"
    
    GLM_DATA_FILE = f"derivatives/glm_data/glm_dataset_{data_type}{suffix}.h5"
    OUT_DIR = f"derivatives/analysis/gating"
    VIZ_DIR = f"derivatives/visualization/gating_{data_type}{suffix}"
    
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(VIZ_DIR, exist_ok=True)
    
    print(f"Running Gating Analysis for: {data_type.upper()} ({args.baseline_mode.upper()} Baseline)")
    
    # Containers
    stats_rows = []
    wave_rows = []
    sliding_rows = []
    
    rois = load_rois(ROI_JSON)
    
    if not os.path.exists(GLM_DATA_FILE):
        print(f"Error: {GLM_DATA_FILE} not found.")
        return

    with h5py.File(GLM_DATA_FILE, 'r') as hf:
        subjects = set()
        for cond in hf.keys():
            if isinstance(hf[cond], h5py.Group):
                for s in hf[cond].keys():
                    subjects.add(s)
        
        print(f"Subjects: {list(subjects)}")
        
        for subj in subjects:
            print(f"Processing {subj}...")
            
            Y_list = []
            X_list = []
            
            # Find an epoch file for ch_names
            import glob
            epoch_pat = f"derivatives/epochs/*/{subj}/*.npz"
            epoch_files = glob.glob(epoch_pat)
            if not epoch_files:
                print(f"No epoch files found for {subj}")
                continue
            
            # Load ch_names
            tmp = np.load(epoch_files[0], allow_pickle=True)
            ch_names = tmp['channel_names']
            # Load fs from epoch file strictly
            if 'fs' not in tmp:
                raise RuntimeError(f"Missing 'fs' in epoch file: {epoch_files[0]}")
            fs = float(tmp['fs'])
            
            # Time Axis
            # Determine n_samples and times from GLM data shape later
            
            # Load Data
            for cond in hf.keys():
                if subj in hf[cond]:
                    g = hf[f"{cond}/{subj}"]
                    if "Y" in g and "X" in g:
                        y_data = g["Y"][:]
                        x_grp = g["X"]
                        cols = list(g.attrs["columns"])
                        d = {}
                        for c in cols:
                            vals = x_grp[c][:]
                            if vals.dtype.kind == 'S':
                                d[c] = [v.decode('utf-8') for v in vals]
                            else:
                                d[c] = vals
                        x_df = pd.DataFrame(d)
                        Y_list.append(y_data)
                        X_list.append(x_df)
                        
                        # Dynamically handle time axis based on data shape
                        n_samples = y_data.shape[-1]
                        t_start = -0.2
                        times = np.linspace(t_start, t_start + n_samples/fs, n_samples, endpoint=False)
            
            if not Y_list: continue
            
            Y_all = np.concatenate(Y_list, axis=0)
            X_all = pd.concat(X_list, axis=0, ignore_index=True)
            
            # ROI Masking
            roi_idx = get_roi_indices(ch_names, rois, subj)
            if not roi_idx:
                print(f"Warning: No Auditory ROI for {subj}")
                continue
            
            Y_roi = np.mean(Y_all[:, roi_idx, :], axis=1) # (N, Time)
            
            # Analyze by Length
            lengths = sorted(X_all['length'].unique())
            
            for length in lengths:
                idx_len = X_all.index[X_all['length'] == length].tolist()
                idx_len = [i for i in idx_len]
                if not idx_len: continue
                
                Y_sub = Y_roi[idx_len, :]
                X_sub = X_all.iloc[idx_len].copy()
                X_sub['mdl'] = pd.to_numeric(X_sub['mdl'], errors='coerce')
                
                if X_sub['mdl'].nunique() < 2:
                    print(f"Skipping Length {length} (Single MDL value)")
                    continue
                
                # --- Build Nuisance Matrix for Partial Regression ---
                nuisance_mat = build_nuisance_matrix(X_sub)
                mdl_vals = X_sub['mdl'].values.astype(float)
                mdl_resid = residualize(mdl_vals, nuisance_mat)
                
                # --- Sliding Window Partial Regression ---
                # Controls for Position, ToneID, Repetition, Surprisal
                # Range -50ms to 600ms.
                
                t_mask_sliding = (times >= -0.05) & (times <= 0.6)
                idx_sliding = np.where(t_mask_sliding)[0]
                
                for t_idx in idx_sliding:
                    time_val = times[t_idx]
                    amp_t = Y_sub[:, t_idx]
                    
                    # Partial regression: residualize amplitude, then regress on residualized MDL
                    amp_resid = residualize(amp_t, nuisance_mat)
                    slope_t, inter_t, r_t, p_t, se_t = stats.linregress(mdl_resid, amp_resid)
                    
                    sliding_rows.append({
                        'Subject': subj,
                        'Time_ms': time_val * 1000,
                        'Condition': f"Length_{length}",
                        'Length': length,
                        'Slope_MDL': slope_t,
                        'T_value': slope_t / se_t if se_t > 0 else 0,
                        'P_value': p_t
                    })
                
                # --- Stationary Stats (Windowed) with Partial Regression ---
                idx_early = np.where((times >= WIN_EARLY[0]) & (times <= WIN_EARLY[1]))[0]
                idx_late = np.where((times >= WIN_LATE[0]) & (times <= WIN_LATE[1]))[0]
                
                amp_early = np.mean(Y_sub[:, idx_early], axis=1)
                amp_late = np.mean(Y_sub[:, idx_late], axis=1)
                
                # Partial Regression (controlling for confounds)
                amp_early_resid = residualize(amp_early, nuisance_mat)
                amp_late_resid = residualize(amp_late, nuisance_mat)
                slope_e, _, _, p_e, _ = stats.linregress(mdl_resid, amp_early_resid)
                slope_l, _, _, p_l, _ = stats.linregress(mdl_resid, amp_late_resid)
                
                # Suppression Index
                unique_mdls = X_sub['mdl'].unique()
                mask_low = X_sub['mdl'] == X_sub['mdl'].min()
                mask_high = X_sub['mdl'] == X_sub['mdl'].max()
                
                if len(unique_mdls) > 2:
                    try:
                        bins = pd.qcut(X_sub['mdl'], 3, labels=['Low', 'Mid', 'High'])
                        mask_low = bins == 'Low'
                        mask_high = bins == 'High'
                    except: pass
                
                si_early = np.mean(amp_early[mask_low]) - np.mean(amp_early[mask_high])
                si_late = np.mean(amp_late[mask_low]) - np.mean(amp_late[mask_high])
                
                stats_rows.append({
                    'Subject': subj, 'ROI': 'Auditory', 'Length': length, 'Window': 'Early',
                    'Slope_MDL': slope_e, 'P_value': p_e, 'Suppression_Index': si_early
                })
                stats_rows.append({
                    'Subject': subj, 'ROI': 'Auditory', 'Length': length, 'Window': 'Late',
                    'Slope_MDL': slope_l, 'P_value': p_l, 'Suppression_Index': si_late
                })
                
                # --- Waveforms ---
                if len(unique_mdls) < 3:
                     groups = {'Low': Y_sub[mask_low].mean(axis=0), 'High': Y_sub[mask_high].mean(axis=0)}
                else:
                     try:
                        bins = pd.qcut(X_sub['mdl'], 3, labels=['Low', 'Medium', 'High'])
                     except:
                        bins = pd.cut(X_sub['mdl'], 3, labels=['Low', 'Medium', 'High'])
                     groups = {}
                     for b_label in ['Low', 'Medium', 'High']:
                         mask = bins == b_label
                         if mask.any(): groups[b_label] = Y_sub[mask].mean(axis=0)
                
                for grp_name, wave_data in groups.items():
                     for t_i, val in enumerate(wave_data):
                         wave_rows.append({
                             'Time': times[t_i], 'Subject': subj, 'Length': length,
                             'MDL_Bin': grp_name, 'Amplitude': val
                         })

    # Save CSVs
    df_stats = pd.DataFrame(stats_rows)
    df_wave = pd.DataFrame(wave_rows)
    df_sliding = pd.DataFrame(sliding_rows)
    
    df_stats.to_csv(os.path.join(OUT_DIR, f"gating_stats_{data_type}{suffix}.csv"), index=False)
    df_wave.to_csv(os.path.join(OUT_DIR, f"gating_waveforms_{data_type}{suffix}.csv"), index=False)
    df_sliding.to_csv(os.path.join(OUT_DIR, f"gating_sliding_stats_{data_type}{suffix}.csv"), index=False)
    
    print(f"Saved stats to {OUT_DIR}")
    
    # --- Plotting ---
    # 1. Gating Curve
    if not df_stats.empty:
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df_stats, x='Length', y='Slope_MDL', hue='Window', style='Subject', markers=True)
        plt.axhline(0, color='k', linestyle='--')
        plt.title(f"Gating Effect ({data_type.upper()}): MDL Slope")
        plt.savefig(os.path.join(VIZ_DIR, "Gating_Slopes.png"))
        plt.close()
    
    # 2. Sliding Window Slopes (Time-Resolved)
    if not df_sliding.empty:
        # Plot Short (4,6) vs Long (12,16) Aggregated?
        # Create a 'Length_Group'
        df_sliding['Length_Group'] = df_sliding['Length'].apply(lambda x: 'Short' if x <= 6 else 'Long')
        
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df_sliding, x='Time_ms', y='Slope_MDL', hue='Length_Group', style='Subject')
        plt.axhline(0, color='k')
        plt.axvline(0, color='k', linestyle='--')
        plt.title(f"Time-Resolved MDL Slope ({data_type.upper()})")
        plt.savefig(os.path.join(VIZ_DIR, "Gating_Sliding_Slope.png"))
        plt.close()

    # 3. Split-Split Waveforms
    if not df_wave.empty:
        for subj in df_wave['Subject'].unique():
            df_s = df_wave[df_wave['Subject'] == subj]
            g = sns.FacetGrid(df_s, col="Length", hue="MDL_Bin", col_wrap=4, height=4, palette="viridis")
            g.map(sns.lineplot, "Time", "Amplitude")
            g.add_legend()
            g.fig.suptitle(f"{subj} ({data_type.upper()}): MDL Effect by Length", y=1.02)
            g.savefig(os.path.join(VIZ_DIR, f"SplitPlot_{subj}.png"))
            plt.close()

if __name__ == "__main__":
    main()
