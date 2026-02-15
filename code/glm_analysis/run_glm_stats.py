#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run GLM Statistics and Reporting
================================

Analyses the T-statistics from the GLM results and generates a summary CSV of significant clusters.

Inputs:
- derivatives/glm_results/glm_results.h5

Outputs:
- derivatives/glm_results/significant_clusters.csv
"""

import os
import h5py
import numpy as np
import pandas as pd
import argparse
from scipy.ndimage import label

def detect_fs_from_h5(h5_path):
    """Read FS from HDF5 attribute strictly."""
    with h5py.File(h5_path, 'r') as hf:
        if 'fs' in hf.attrs and hf.attrs['fs'] > 0:
            return float(hf.attrs['fs'])
    # Default to 500 Hz if attribute and npz are missing, but warn
    print(f"Warning: Could not detect 'fs' attribute in {h5_path}. Using fallback 500 Hz.")
    return 500.0

P_THRESH = 0.05
# Approximate T-threshold for p < 0.05 (two-tailed) with large DOF (>100)
# T ~ 1.96
T_THRESH = 1.96 

def get_clusters(t_series, threshold, fs):
    """
    Find clusters in 1D T-series.
    Returns list of dicts: {'start', 'end', 'mass', 'max_t'}
    """
    # Create mask
    mask = np.abs(t_series) > threshold
    
    labeled, n_clusters = label(mask)
    
    clusters = []
    for i in range(1, n_clusters + 1):
        indices = np.where(labeled == i)[0]
        if len(indices) == 0: continue
        
        start = indices[0]
        end = indices[-1]
        
        # Stats
        cluster_t = t_series[indices]
        mass = np.sum(np.abs(cluster_t))
        peak_t = cluster_t[np.argmax(np.abs(cluster_t))] # Signed peak
        
        # Start/End Time (Epoch starts at -0.2s)
        start_t = (start / fs) - 0.2
        end_t = (end / fs) - 0.2
        
        clusters.append({
            'start_idx': start,
            'end_idx': end,
            'start_time': start_t,
            'end_time': end_t,
            'cluster_mass': mass,
            'peak_t': peak_t
        })
        
    return clusters

def main():
    parser = argparse.ArgumentParser(description="Run GLM Statistics and Reporting (Quick Screening)")
    parser.add_argument("--data_type", type=str, default="erp", choices=['erp', 'hfa'], help="Data type (erp or hfa)")
    parser.add_argument("--baseline_mode", type=str, default="local", choices=['local', 'global'], help="Baseline (local or global)")
    parser.add_argument("--model", type=str, default="ModelC", help="Model name (e.g. ModelA, ModelB, ModelC, ModelD)")
    args = parser.parse_args()

    # Construct Path
    suffix = f"_base{args.baseline_mode}"
    glm_results_file = f"derivatives/glm_results/glm_results_{args.data_type}{suffix}_{args.model}.h5"
    out_csv = f"derivatives/glm_results/stats_{args.data_type}{suffix}_{args.model}.csv"

    if not os.path.exists(glm_results_file):
        print(f"Results file missing: {glm_results_file}")
        return
        
    fs = detect_fs_from_h5(glm_results_file)
    all_clusters = []
    
    with h5py.File(glm_results_file, 'r') as hf:
        # Loop through subjects in the root
        for subj in hf.keys():
            if not isinstance(hf[subj], h5py.Group): continue
            
            grp = hf[subj]
            if "ROITstats" not in grp: continue
            
            t_stats = grp["ROITstats"][:] # (N_rois, N_preds, N_time)
            roi_names = grp.attrs["roi_names"]
            pred_names = grp.attrs["predictors"]
            
            # Convert strings
            roi_names = [x.decode('utf-8') if isinstance(x, bytes) else str(x) for x in roi_names]
            pred_names = [x.decode('utf-8') if isinstance(x, bytes) else str(x) for x in pred_names]
            
            for r_idx, r_name in enumerate(roi_names):
                for p_idx, p_name in enumerate(pred_names):
                    # Get T-series
                    t_series = t_stats[r_idx, p_idx, :]
                    
                    # Find clusters
                    clusters = get_clusters(t_series, T_THRESH, fs)
                    
                    for c in clusters:
                        all_clusters.append({
                            'Subject': subj,
                            'ROI': r_name,
                            'Predictor': p_name,
                            'Start_s': c['start_time'],
                            'End_s': c['end_time'],
                            'Duration_s': c['end_time'] - c['start_time'],
                            'Peak_T': c['peak_t'],
                            'Cluster_Mass': c['cluster_mass'],
                            'Significant_unc': True # Based on fixed T threshold
                        })
                            
    if all_clusters:
        df = pd.DataFrame(all_clusters)
        df.sort_values(by=['Subject', 'ROI', 'Predictor', 'Start_s'], inplace=True)
        
        df.to_csv(out_csv, index=False)
        print(f"Saved summary to {out_csv} ({len(df)} clusters)")
    else:
        print(f"No clusters exceeding T={T_THRESH} found in {glm_results_file}")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
