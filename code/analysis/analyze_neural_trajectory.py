#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neural State Trajectory Analysis
================================
Goal: Visualize the population dynamics of the auditory cortex 
to identify "Regime Shift" before sequence onset.

1. Load Sequence Epochs [-0.5, 4.5]s
2. Filter for Auditory ROI
3. Global Baseline Correction [-0.2, 0]s
4. PCA projection (Short vs Long)
5. Permutation test for trajectory separation
"""

import os
import glob
import json
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.decomposition import PCA
from scipy.ndimage import gaussian_filter1d
from scipy.spatial.distance import euclidean

# --- CONFIG ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
EPOCHS_ROOT = PROJECT_ROOT / "derivatives" / "epochs"
ROI_JSON = PROJECT_ROOT / "derivatives" / "rois" / "functional_rois.json"
OUT_DIR = PROJECT_ROOT / "derivatives" / "analysis" / "trajectory"

# Baseline Window relative to sequence onset (0.0s)
# Epoch is [-0.5, 4.5]s
BASELINE_WIN = (-0.2, 0.0)
SMOOTH_SIGMA_MS = 20 # Sigma for gaussian smoothing

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_rois():
    if not ROI_JSON.exists():
        logger.error(f"ROI file not found at {ROI_JSON}")
        return None
    with open(ROI_JSON, 'r') as f:
        return json.load(f)

def get_auditory_channels(subject, roi_data):
    if subject not in roi_data['subjects']:
        return []
    aud_rois = roi_data['subjects'][subject].get('Auditory', {})
    channels = []
    for region, ch_list in aud_rois.items():
        if isinstance(ch_list, list):
            channels.extend(ch_list)
    return sorted(list(set(channels)))

def process_subject_trajectories(subject, roi_data):
    logger.info(f"Processing Trajectories for {subject}")
    aud_chs = get_auditory_channels(subject, roi_data)
    if not aud_chs:
        logger.warning(f"No auditory channels found for {subject}")
        return
    
    # Identify Short vs Long Condition Directories
    all_cond_dirs = [d for d in EPOCHS_ROOT.iterdir() if d.is_dir()]
    short_conds = []
    long_conds = []
    
    for d in all_cond_dirs:
        try:
            length = int(d.name.split('_')[-1])
            if length in [4, 6]:
                short_conds.append(d)
            elif length in [12, 16]:
                long_conds.append(d)
        except (ValueError, IndexError):
            continue
            
    def load_trials(cond_dirs):
        trials_list = []
        fs = None
        common_chs = None
        
        for cd in cond_dirs:
            subj_dir = cd / subject
            if not subj_dir.exists(): continue
            
            for npz_f in subj_dir.glob("*.npz"):
                data = np.load(npz_f, allow_pickle=True)
                if 'seq_epochs' not in data or data['seq_epochs'] is None: continue
                
                # Check for empty data
                if data['seq_epochs'].size == 0: continue
                
                # Align channels
                file_chs = list(data['channel_names'])
                roi_idx = [i for i, ch in enumerate(file_chs) if ch in aud_chs]
                if not roi_idx: continue
                
                roi_ch_names = [file_chs[i] for i in roi_idx]
                
                # Data: (N_trials, Time, Ch)
                curr_fs = float(data['fs'])
                if fs is None: fs = curr_fs
                
                # Global Baseline [-0.2, 0.0]s
                # Epoch starts at -0.5s. 0.0s is at 0.5 * fs.
                b_start = int(0.3 * fs)
                b_end = int(0.5 * fs)
                
                epochs = data['seq_epochs'][:, :, roi_idx]
                
                # Subselect common channels across all files if possible
                # For now, let's keep all ROI channels that exist in this file
                # and average later or pad. Better: only use channels that exist in ALL files of this subject.
                if common_chs is None:
                    common_chs = set(roi_ch_names)
                else:
                    common_chs.intersection_update(roi_ch_names)
                    
                trials_list.append((epochs, roi_ch_names, curr_fs))
        
        if not trials_list or not common_chs:
            return None, None
            
        common_chs = sorted(list(common_chs))
        logger.info(f"  {subject}: Found {len(common_chs)} common auditory channels.")
        
        final_trials = []
        for epochs, names, f_rate in trials_list:
            ch_idx = [names.index(ch) for ch in common_chs]
            sub_epochs = epochs[:, :, ch_idx]
            
            # Baseline Correction per trial
            # Baseline is mean of [-0.2, 0.0]s relative to Tone 0
            b_start = int(0.3 * f_rate)
            b_end = int(0.5 * f_rate)
            
            for i in range(sub_epochs.shape[0]):
                trial_data = sub_epochs[i] # (Time, Ch)
                baseline = trial_data[b_start:b_end, :].mean(axis=0)
                trial_bc = trial_data - baseline
                
                # Smoothing
                sigma = (SMOOTH_SIGMA_MS / 1000.0) * f_rate
                trial_smooth = gaussian_filter1d(trial_bc, sigma, axis=0)
                
                final_trials.append(trial_smooth)
        
        return np.array(final_trials), fs # (N, Time, Ch)

    trials_short, fs_s = load_trials(short_conds)
    trials_long, fs_l = load_trials(long_conds)
    
    if trials_short is None or trials_long is None:
        logger.warning(f"Could not load enough data for {subject}")
        return

    # Ensure same time window (truncation/padding)
    # Both should be at same FS (500Hz usually)
    min_time = min(trials_short.shape[1], trials_long.shape[1])
    trials_short = trials_short[:, :min_time, :]
    trials_long = trials_long[:, :min_time, :]
    
    # PCA
    # 1. Condition Averaging
    avg_short = trials_short.mean(axis=0) # (Time, Ch)
    avg_long = trials_long.mean(axis=0)   # (Time, Ch)
    
    # Combined for PCA fitting
    # We want a common subspace
    combined = np.vstack([avg_short, avg_long]) # (2*Time, Ch)
    
    pca = PCA(n_components=3)
    pca.fit(combined)
    
    pc_short = pca.transform(avg_short) # (Time, 3)
    pc_long = pca.transform(avg_long)   # (Time, 3)
    
    # Statistical Validation: Permutation Test
    obs_dist = np.array([euclidean(pc_short[t, :], pc_long[t, :]) for t in range(min_time)])
    
    n_perms = 500
    perm_dists = []
    
    combined_trials = np.vstack([trials_short, trials_long])
    n_short = trials_short.shape[0]
    
    logger.info(f"  Running {n_perms} permutations...")
    for p in range(n_perms):
        idx = np.random.permutation(combined_trials.shape[0])
        p_short = combined_trials[idx[:n_short]].mean(axis=0)
        p_long = combined_trials[idx[n_short:]].mean(axis=0)
        
        # Project using the same PCA
        pp_short = pca.transform(p_short)
        pp_long = pca.transform(p_long)
        
        p_dist = np.array([euclidean(pp_short[t, :], pp_long[t, :]) for t in range(min_time)])
        perm_dists.append(p_dist)
        
    perm_dists = np.array(perm_dists) # (n_perms, Time)
    p_vals = np.mean(perm_dists >= obs_dist, axis=0)
    
    # Time axis
    time_vec = np.linspace(-0.5, -0.5 + min_time/fs_s, min_time)
    
    # --- VISUALIZATION ---
    os.makedirs(OUT_DIR, exist_ok=True)
    
    # 1. Trajectory Plot (PC1 vs PC2)
    plt.figure(figsize=(10, 8))
    
    def plot_traj(pc, label, color_map, start_t, end_t):
        # Time markers
        # We'll use a gradient or scatter dots
        # Tone 0 is at t=0
        idx_t0 = np.argmin(np.abs(time_vec - 0.0))
        
        plt.plot(pc[:, 0], pc[:, 1], color='gray', alpha=0.3)
        sns.scatterplot(x=pc[:, 0], y=pc[:, 1], hue=time_vec, palette=color_map, s=20, edgecolor=None, legend=False)
        
        # Mark Start, Tone 0, and End
        plt.scatter(pc[0, 0], pc[0, 1], marker='o', s=100, facecolors='none', edgecolors='green', label=f'{label} Start (-0.5s)')
        plt.scatter(pc[idx_t0, 0], pc[idx_t0, 1], marker='X', s=150, color='red', label=f'{label} Tone 0 (0s)')
        plt.plot(pc[:, 0], pc[:, 1], label=label, linewidth=2, alpha=0.7)

    plot_traj(pc_short, 'Short (4/6)', 'Blues', -0.5, time_vec[-1])
    plot_traj(pc_long, 'Long (12/16)', 'Reds', -0.5, time_vec[-1])
    
    plt.title(f"Neural Population Trajectories: {subject}\nPCA on Auditory ROI")
    plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
    plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plot_path = OUT_DIR / f"Trajectory_PC_{subject}.png"
    plt.savefig(plot_path, dpi=300)
    plt.close()
    
    # 2. Distance Plot
    plt.figure(figsize=(10, 5))
    plt.plot(time_vec, obs_dist, color='black', label='Observed Distance')
    
    # Null distribution stats
    mean_null = perm_dists.mean(axis=0)
    std_null = perm_dists.std(axis=0)
    plt.fill_between(time_vec, mean_null - 2*std_null, mean_null + 2*std_null, color='gray', alpha=0.2, label='95% Null Dist')
    
    # Significance markers
    sig_mask = p_vals < 0.05
    plt.plot(time_vec[sig_mask], [obs_dist.max()*1.05]*np.sum(sig_mask), '|', color='red', label='p < 0.05')
    
    plt.axvline(0, color='red', linestyle='--', alpha=0.5, label='Tone 0 Onset')
    plt.title(f"Euclidean Distance between Trajectories: {subject}")
    plt.xlabel("Time (s)")
    plt.ylabel("Distance (a.u.)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    dist_path = OUT_DIR / f"Trajectory_Distance_{subject}.png"
    plt.savefig(dist_path, dpi=300)
    plt.close()
    
    # Save statistics
    stats_df = pd.DataFrame({
        'time': time_vec,
        'distance': obs_dist,
        'p_val': p_vals,
        'sig': sig_mask
    })
    stats_df.to_csv(OUT_DIR / f"Trajectory_Stats_{subject}.csv", index=False)
    
    logger.info(f"  Saved outputs to {OUT_DIR}")

def main():
    roi_data = load_rois()
    if not roi_data: return
    
    subjects = ['Boss', 'Carol']
    for subj in subjects:
        process_subject_trajectories(subj, roi_data)

if __name__ == "__main__":
    main()
