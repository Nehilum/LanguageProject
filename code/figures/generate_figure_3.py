#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Figure 3 Generation: The Dynamical Mechanism
=============================================
Panel A: Neural State Trajectory (PCA) (Calculated on the fly / Cached)
Panel B: State Separation (Euclidean Distance) (From Stats CSV)
Panel C: Individual Strategies (Morphology - Boss vs. Carol) (From ERP CSV)

Author: Antigravity
Date: 2026-02-15
"""

import os
import json
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path
from sklearn.decomposition import PCA
from scipy.ndimage import gaussian_filter1d
from scipy.spatial.distance import euclidean

# --- CONFIG ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
EPOCHS_ROOT = PROJECT_ROOT / "derivatives" / "epochs"
ROI_JSON = PROJECT_ROOT / "derivatives" / "rois" / "functional_rois.json"
TRAJ_STATS_DIR = PROJECT_ROOT / "derivatives" / "analysis" / "trajectory"
ERP_CSV = PROJECT_ROOT / "derivatives" / "analysis" / "gating" / "gating_waveforms_erp_baseglobal.csv"
OUT_DIR = PROJECT_ROOT / "figures"
CACHE_FILE = TRAJ_STATS_DIR / "pca_coords_cache.npz"

# Constants
SUBJECTS = ['Boss', 'Carol']
BASELINE_WIN = (-0.2, 0.0)
SMOOTH_SIGMA_MS = 20
CMAP_SHORT = 'Blues'
CMAP_LONG = 'Reds'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- UTILS ---

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

def load_trials(subject, cond_lengths, roi_chs):
    """Load and process trials for a specific subject and condition lengths."""
    trials_list = []
    fs = None
    common_chs = None
    
    # Find directories matching lengths
    files_found = 0
    for d in EPOCHS_ROOT.iterdir():
        if not d.is_dir(): continue
        try:
            length = int(d.name.split('_')[-1])
            if length in cond_lengths:
                subj_dir = d / subject
                if not subj_dir.exists(): continue
                
                for npz_f in subj_dir.glob("*.npz"):
                    try:
                        data = np.load(npz_f, allow_pickle=True)
                        if 'seq_epochs' not in data or data['seq_epochs'] is None: continue
                        if data['seq_epochs'].size == 0: continue
                        
                        file_chs = list(data['channel_names'])
                        roi_idx = [i for i, ch in enumerate(file_chs) if ch in roi_chs]
                        if not roi_idx: continue
                        
                        roi_ch_names = [file_chs[i] for i in roi_idx]
                        curr_fs = float(data['fs'])
                        if fs is None: fs = curr_fs
                        
                        epochs = data['seq_epochs'][:, :, roi_idx]
                        
                        if common_chs is None:
                            common_chs = set(roi_ch_names)
                        else:
                            common_chs.intersection_update(roi_ch_names)
                            
                        trials_list.append((epochs, roi_ch_names, curr_fs))
                        files_found += 1
                    except Exception as e:
                        logger.warning(f"Error loading {npz_f}: {e}")
                        continue
        except (ValueError, IndexError):
            continue
            
    if not trials_list or not common_chs:
        logger.warning(f"No valid data found for {subject} lengths {cond_lengths}")
        return None, None
        
    common_chs = sorted(list(common_chs))
    final_trials = []
    
    b_start = int(0.3 * fs) # -0.2s relative to start (-0.5s) -> 0.3s into epoch
    b_end = int(0.5 * fs)   # 0.0s relative to start (-0.5s) -> 0.5s into epoch
    
    sigma = (SMOOTH_SIGMA_MS / 1000.0) * fs
    
    for epochs, names, f_rate in trials_list:
        ch_idx = [names.index(ch) for ch in common_chs]
        sub_epochs = epochs[:, :, ch_idx] # (N, Time, Ch)
        
        # Baseline Correction & Smoothing
        for i in range(sub_epochs.shape[0]):
            trial_data = sub_epochs[i]
            baseline = trial_data[b_start:b_end, :].mean(axis=0)
            trial_bc = trial_data - baseline
            trial_smooth = gaussian_filter1d(trial_bc, sigma, axis=0)
            final_trials.append(trial_smooth)
            
    return np.array(final_trials), fs

def get_pca_trajectories(roi_data, force_recalc=False):
    """Calculates PCA trajectories or loads from cache."""
    cache_path = CACHE_FILE
    
    if cache_path.exists() and not force_recalc:
        logger.info(f"Loading PCA trajectories from cache: {cache_path}")
        return np.load(cache_path, allow_pickle=True)['data'].item()
    
    logger.info("Recalculating PCA trajectories...")
    results = {}
    
    for subject in SUBJECTS:
        logger.info(f"Processing PCA for {subject}")
        roi_chs = get_auditory_channels(subject, roi_data)
        
        trials_short, fs_s = load_trials(subject, [4, 6], roi_chs)
        trials_long, fs_l = load_trials(subject, [12, 16], roi_chs)
        
        if trials_short is None or trials_long is None:
            continue
            
        # Time alignment
        min_time = min(trials_short.shape[1], trials_long.shape[1])
        trials_short = trials_short[:, :min_time, :]
        trials_long = trials_long[:, :min_time, :]
        
        avg_short = trials_short.mean(axis=0)
        avg_long = trials_long.mean(axis=0)
        
        # Common PCA
        combined = np.vstack([avg_short, avg_long])
        pca = PCA(n_components=3)
        pca.fit(combined)
        
        pc_short = pca.transform(avg_short)
        pc_long = pca.transform(avg_long)
        
        # Project all trials to get variance
        # (N_trials, Time, Ch) -> (N_trials, Time, PCs)
        pc_trials_short = np.array([pca.transform(t) for t in trials_short])
        pc_trials_long = np.array([pca.transform(t) for t in trials_long])
        
        # Calculate SEM in PC space
        sem_short = pc_trials_short.std(axis=0) / np.sqrt(len(trials_short))
        sem_long = pc_trials_long.std(axis=0) / np.sqrt(len(trials_long))
        
        time_vec = np.linspace(-0.5, -0.5 + min_time/fs_s, min_time)
        
        results[subject] = {
            'pc_short': pc_short,
            'pc_long': pc_long,
            'sem_short': sem_short,
            'sem_long': sem_long,
            'time_vec': time_vec,
            'var_explained': pca.explained_variance_ratio_
        }
    
    # Save cache
    os.makedirs(TRAJ_STATS_DIR, exist_ok=True)
    np.savez_compressed(cache_path, data=results)
    logger.info(f"Saved PCA cache to {cache_path}")
    
    return results

def plot_manifold(ax, x, y, sem_x, sem_y, cmap_name, label=None, linewidth=3):
    """Plots a trajectory with a surrounding 'manifold' (tube) indicating variance."""
    # 1. Plot the "Manifold" (Volume)
    # We use multiple layers of alpha to create a soft edge / bubble effect
    for sigma in [1.0, 2.0]:
        ax.fill(np.concatenate([x - sigma*sem_x, (x + sigma*sem_y)[::-1]]),
                np.concatenate([y - sigma*sem_y, (y + sigma*sem_x)[::-1]]),
                color=plt.get_cmap(cmap_name)(0.5), alpha=0.15/sigma)
    
    # 2. Plot the Gradient Line (Core)
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    norm = plt.Normalize(0, len(x))
    lc = LineCollection(segments, cmap=cmap_name, norm=norm, alpha=1.0)
    lc.set_array(np.arange(len(x)))
    lc.set_linewidth(linewidth)
    line = ax.add_collection(lc)
    
    # 3. Add arrow at end
    color = plt.get_cmap(cmap_name)(0.8)
    ax.arrow(x[-2], y[-2], x[-1]-x[-2], y[-1]-y[-2], 
             head_width=0.1*np.ptp(x), head_length=0.12*np.ptp(x), 
             fc=color, ec=color, length_includes_head=True, zorder=10)
    
    # Dummy plot for legend
    ax.plot([], [], color=color, label=label, linewidth=linewidth)
    return line

# --- PLOTTING ---

def generate_figure(pca_data):
    logger.info("Generating Figure 3...")
    
    fig = plt.figure(figsize=(18, 14))
    gs = gridspec.GridSpec(3, 2, height_ratios=[1, 0.7, 0.7], hspace=0.35, wspace=0.15)
    
    # Colors
    color_short = '#1f77b4' # Muted Blue
    color_long = '#d62728'  # Muted Red
    
    # --- PANEL A: Neural State Trajectory ---
    for i, subject in enumerate(SUBJECTS):
        ax = fig.add_subplot(gs[0, i])
        
        if subject not in pca_data:
            ax.text(0.5, 0.5, "Data Missing", ha='center')
            continue
            
        data = pca_data[subject]
        pc_short = data['pc_short']
        pc_long = data['pc_long']
        time = data['time_vec']
        var = data['var_explained']
        
        # Determine plot range for scaling arrow
        x_range = np.ptp(np.concatenate([pc_short[:, 0], pc_long[:, 0]]))
        y_range = np.ptp(np.concatenate([pc_short[:, 1], pc_long[:, 1]]))
        
        # Plot Manifolds
        plot_manifold(ax, pc_short[:, 0], pc_short[:, 1], 
                      data['sem_short'][:, 0], data['sem_short'][:, 1], 
                      'Blues', label='Short (Competent)', linewidth=3)
        plot_manifold(ax, pc_long[:, 0], pc_long[:, 1], 
                      data['sem_long'][:, 0], data['sem_long'][:, 1], 
                      'Reds', label='Long (Overload)', linewidth=3)
        
        # Mark Key Events
        # Tone 0 at t=0
        idx_t0 = np.argmin(np.abs(time - 0.0))
        ax.scatter(pc_short[idx_t0, 0], pc_short[idx_t0, 1], marker='X', color='black', s=100, zorder=20, label='Tone 0')
        ax.scatter(pc_long[idx_t0, 0], pc_long[idx_t0, 1], marker='X', color='black', s=100, zorder=20)
        
        # Mark Start
        ax.scatter(pc_short[0, 0], pc_short[0, 1], marker='o', color='gray', s=50, zorder=15, alpha=0.5, label='Start (-0.5s)')
        ax.scatter(pc_long[0, 0], pc_long[0, 1], marker='o', color='gray', s=50, zorder=15, alpha=0.5)

        ax.set_title(f"{subject}: Neural State Trajectory (PCA)", fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel(f"PC1 ({var[0]*100:.1f}%)", fontsize=11)
        ax.set_ylabel(f"PC2 ({var[1]*100:.1f}%)", fontsize=11)
        
        # Adjust limits
        ax.autoscale(enable=True, axis='both', tight=False)
        ax.margins(0.1)
        
        if i == 0:
            ax.legend(loc='upper right', frameon=True)
            ax.text(-0.1, 1.1, "A", transform=ax.transAxes, fontsize=20, fontweight='bold')
            
        ax.grid(True, linestyle=':', alpha=0.4)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    # --- PANEL B: State Separation (Euclidean Distance) ---
    for i, subject in enumerate(SUBJECTS):
        ax = fig.add_subplot(gs[1, i])
        
        stats_file = TRAJ_STATS_DIR / f"Trajectory_Stats_{subject}.csv"
        if not stats_file.exists():
            ax.text(0.5, 0.5, "Stats Missing", ha='center')
            continue
            
        df = pd.read_csv(stats_file)
        
        # Plot Distance
        ax.plot(df['time'], df['distance'], color='k', linewidth=2, label='Euclidean Distance')
        
        # Highlight significance (p < 0.05) - Assuming 'sig' col is boolean or string 'True'
        sig_mask = df['sig'].astype(str) == 'True'
        if sig_mask.any():
            sig_times = df.loc[sig_mask, 'time']
            # Find contiguous regions for clean shading
            # Simple fill between
            y_max = df['distance'].max()
            ax.fill_between(df['time'], 0, y_max*1.1, where=sig_mask, color='#ffdddd', alpha=0.5, label='Significant (p<0.05)')
            
        ax.axvline(0, color='gray', linestyle='--', alpha=0.7)
        ax.set_title(f"{subject}: State Separation (Short vs Long)", fontsize=13)
        ax.set_xlabel("Time from Sequence Onset (s)", fontsize=11)
        ax.set_ylabel("Euclidean Distance (a.u.)", fontsize=11)
        ax.set_xlim(-0.5, df['time'].max())
        ax.set_ylim(0, df['distance'].max() * 1.1)
        
        if i == 0:
            ax.legend(loc='upper left', frameon=False)
            ax.text(-0.1, 1.1, "B", transform=ax.transAxes, fontsize=20, fontweight='bold')
            
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    # --- PANEL C: Individual Strategies (ERP) ---
    # Load ERP data
    if ERP_CSV.exists():
        erp_df = pd.read_csv(ERP_CSV)
        
        for i, subject in enumerate(SUBJECTS):
            ax = fig.add_subplot(gs[2, i])
            
            sub_df = erp_df[erp_df['Subject'] == subject]
            
            # Group Short (Length 4, 6) vs Long (Length 12, 16)
            # Assuming 'Length' column exists and 'Time' column exists
            # We need to map Length to condition manually if needed
            # Lengths: 4, 6, 8 (Short), 12, 16 (Long)
            
            short_mask = sub_df['Length'].isin([4, 6, 8])
            long_mask = sub_df['Length'].isin([12, 16])
            
            # Aggregate Mean and SEM
            # We want time-course means.
            # Group by Time and ConditionGroup
            
            # Create a copy to avoid SettingWithCopy warning
            s_short = sub_df[short_mask].copy()
            s_long = sub_df[long_mask].copy()
            
            # Group by Time and calculate mean/sem
            # NOTE: There might be multiple trials or ModelBins in this CSV.
            # The CSV seems to be 'gating_waveforms...', which usually contains aggregated waveforms.
            # Let's check structure. Assuming columns: Time, Subject, Length, Amplitude (or similar)
            
            # Calculate stats
            stats_short = s_short.groupby('Time')['Amplitude'].agg(['mean', 'sem']).reset_index()
            stats_long = s_long.groupby('Time')['Amplitude'].agg(['mean', 'sem']).reset_index()
            
            # Plot Short
            ax.plot(stats_short['Time'], stats_short['mean'], color=color_short, linewidth=2, label='Short (4-8)')
            ax.fill_between(stats_short['Time'], 
                            stats_short['mean'] - stats_short['sem'], 
                            stats_short['mean'] + stats_short['sem'], 
                            color=color_short, alpha=0.2)
                            
            # Plot Long
            ax.plot(stats_long['Time'], stats_long['mean'], color=color_long, linewidth=2, label='Long (12-16)')
            ax.fill_between(stats_long['Time'], 
                            stats_long['mean'] - stats_long['sem'], 
                            stats_long['mean'] + stats_long['sem'], 
                            color=color_long, alpha=0.2)
            
            ax.axvline(0, color='gray', linestyle='--', alpha=0.7)
            ax.axhline(0, color='black', linewidth=0.5)
            
            # Descriptions based on hypothesis
            desc = "Efficiency Mode" if subject == 'Boss' else "Enhancement Mode"
            ax.set_title(f"{subject}: ERP Morphology ({desc})", fontsize=13)
            ax.set_xlabel("Time relative to Tone Onset (s)", fontsize=11)
            ax.set_ylabel("Amplitude (uV)", fontsize=11)
            ax.set_xlim(-0.05, 0.4) # Zoom in on the response
            
            if i == 0:
                ax.legend(loc='upper right', frameon=False)
                ax.text(-0.1, 1.1, "C", transform=ax.transAxes, fontsize=20, fontweight='bold')
                
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
    else:
        logger.warning(f"ERP CSV not found at {ERP_CSV}")

    # Finalize
    fig.suptitle('The Dynamical Mechanism: Regime Shift and Individual Strategies', fontsize=18, fontweight='bold', y=0.98)
    
    out_path = OUT_DIR / "Figure3_DynamicalMechanism.png"
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    logger.info(f"Figure saved to {out_path}")

def main():
    roi_data = load_rois()
    if not roi_data: return
    
    # 1. Get PCA Data (Calc or Cache)
    pca_data = get_pca_trajectories(roi_data)
    
    # 2. Generate Figure
    generate_figure(pca_data)

if __name__ == "__main__":
    main()
