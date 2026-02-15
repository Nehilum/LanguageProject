#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot Unique Variance (Delta R^2)
===============================

Plots the timecourse of unique variance explained by MDL and Surprisal.
Data is read from derivatives/analysis/unique_variance/unique_variance_{type}_{base}.h5

Output: derivatives/visualization/unique_variance/
"""

import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
import argparse

def plot_roi_unique_variance(results_h5, out_dir, data_type, baseline):
    with h5py.File(results_h5, 'r') as hf:
        subjects = sorted(list(hf.keys())) # Boss, Carol
        if not subjects:
            print("No subjects found in results file.")
            return
            
        if 'fs' in hf.attrs:
            fs = float(hf.attrs['fs'])
        else:
            # Fallback: Try to find fs in the source GLM dataset to avoid "repairing" results
            print(f"Warning: 'fs' missing in {results_h5}. Attempting to find in source data...")
            suffix = "_baselocal" if baseline == 'local' else "_baseglobal"
            source_h5 = f"derivatives/glm_data/glm_dataset_{data_type}{suffix}.h5"
            if os.path.exists(source_h5):
                with h5py.File(source_h5, 'r') as hf_src:
                    if 'fs' in hf_src.attrs:
                        fs = float(hf_src.attrs['fs'])
                    else:
                        raise RuntimeError(f"Could not find 'fs' in results or source file: {source_h5}")
            else:
                raise RuntimeError(f"Results missing 'fs' and source file not found: {source_h5}")
        
        print(f"Using FS = {fs} Hz")
        
        roi_names = hf[subjects[0]].attrs["roi_names"]
        n_time = hf[subjects[0]]["ROI_DeltaR2_MDL"].shape[1]
        time_ms = (np.arange(n_time) / fs - 0.2) * 1000
        
        for r_idx, roi_name in enumerate(roi_names):
            fig, axes = plt.subplots(2, 1, figsize=(10, 10), sharex=True)
            
            for s_idx, subj in enumerate(subjects):
                ax = axes[s_idx]
                mdl_data = hf[subj]["ROI_DeltaR2_MDL"][r_idx, :] * 100
                surp_data = hf[subj]["ROI_DeltaR2_Surp"][r_idx, :] * 100
                
                # Plot Surprisal (Blue) and MDL (Red)
                ax.plot(time_ms, surp_data, color='blue', linewidth=2, label='Unique Surprisal $\Delta R^2$')
                ax.plot(time_ms, mdl_data, color='red', linewidth=2, label='Unique MDL $\Delta R^2$')
                
                ax.axvline(0, color='black', linestyle='--')
                ax.axhline(0, color='black', alpha=0.3)
                ax.set_title(f"Subject: {subj}")
                ax.set_ylabel('$\Delta R^2$ (%)')
                ax.grid(True, alpha=0.2)
                ax.legend(loc='upper right')
                
                # Highlights for Peaks (Optional but helpful)
                # ax.set_ylim(0, max(np.max(mdl_data), np.max(surp_data)) * 1.2)

            axes[1].set_xlabel('Time (ms)')
            plt.xlim(-250, 500) # As requested
            plt.suptitle(f'Time-Resolved Unique Variance: {roi_name} ({data_type.upper()}, {baseline} baseline)', fontsize=14)
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            
            out_name = f"{out_dir}/{roi_name}_UniqueVariance_{data_type}_{baseline}.png"
            plt.savefig(out_name, dpi=300)
            plt.close()
            print(f"Saved plot: {out_name}")

def main():
    parser = argparse.ArgumentParser(description="Plot Unique Variance")
    parser.add_argument("--data_type", type=str, default="erp", choices=['erp', 'hfa'])
    parser.add_argument("--baseline_mode", type=str, default="local", choices=['local', 'global'])
    args = parser.parse_args()
    
    suffix = "_baselocal" if args.baseline_mode == 'local' else "_baseglobal"
    results_h5 = f"derivatives/analysis/unique_variance/unique_variance_{args.data_type}{suffix}.h5"
    out_dir = "derivatives/visualization/unique_variance"
    os.makedirs(out_dir, exist_ok=True)
    
    if not os.path.exists(results_h5):
        print(f"Results file missing: {results_h5}")
        return
        
    plot_roi_unique_variance(results_h5, out_dir, args.data_type, args.baseline_mode)

if __name__ == "__main__":
    main()
