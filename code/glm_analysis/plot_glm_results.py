#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot GLM Results
================

Plots the beta time-courses for key predictors (Surprisal, Interaction) averaged within ROIs.

Inputs:
- derivatives/glm_results/glm_results.h5

Outputs:
- derivatives/glm_results/figures/<Condition>/<Subject>_GLM-Betas.png
"""

import os
import h5py
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def detect_fs_from_h5(h5_path):
    """Read FS from HDF5 attribute strictly."""
    with h5py.File(h5_path, 'r') as hf:
        if 'fs' in hf.attrs and hf.attrs['fs'] > 0:
            return float(hf.attrs['fs'])
    print(f"Warning: Could not detect 'fs' attribute in {h5_path}. Using fallback 500 Hz.")
    return 500.0

PLOT_PREDICTORS = ['Length_c', 'Surprisal', 'Interaction', 'Repetition', 'MDL', 'IsDeviant']
ROI_NAMES = ['Auditory', 'S1', 'M1']

COLORS = {
    'Length_c': 'green',
    'Surprisal': 'red',
    'Interaction': 'purple',
    'Repetition': 'blue',
    'MDL': 'orange',
    'IsDeviant': 'cyan'
}

def load_results(h5_path, subject):
    with h5py.File(h5_path, 'r') as hf:
        if subject not in hf: return None, None, None
        
        grp = hf[subject]
        if "ROIBetas" not in grp: return None, None, None
        
        betas = grp["ROIBetas"][:] # (N_rois, N_preds, N_time)
        pred_names = grp.attrs["predictors"]
        roi_names = grp.attrs["roi_names"]
        
        # Convert byte strings if needed
        pred_names = [x.decode('utf-8') if isinstance(x, bytes) else str(x) for x in pred_names]
        roi_names = [x.decode('utf-8') if isinstance(x, bytes) else str(x) for x in roi_names]
        
        return betas, pred_names, roi_names

def plot_betas(betas, pred_names, roi_names, subject, out_path, fs):
    """
    Plot betas for selected predictors.
    betas: (N_rois, N_preds, N_time)
    """
    n_rois = len(roi_names)
    n_time = betas.shape[2]
    
    # Time axis (Epoch starts at -0.2s)
    t = np.linspace(-0.2, -0.2 + n_time/fs, n_time, endpoint=False)
    
    fig, axes = plt.subplots(n_rois, 1, figsize=(10, 3*n_rois), sharex=True, sharey=False)
    if n_rois == 1: axes = [axes]
    
    for r_idx, r_name in enumerate(roi_names):
        ax = axes[r_idx]
        
        found_any = False
        for p_name in PLOT_PREDICTORS:
            if p_name in pred_names:
                p_idx = pred_names.index(p_name)
                trace = betas[r_idx, p_idx, :]
                
                ax.plot(t, trace, label=p_name, color=COLORS.get(p_name, 'black'), alpha=0.8)
                found_any = True
                
        ax.set_title(f"ROI: {r_name}")
        ax.axhline(0, color='k', lw=0.5)
        ax.set_ylabel("Beta (a.u.)")
        if found_any and r_idx == 0: ax.legend(loc='upper right', fontsize='small')
        
    axes[-1].set_xlabel("Time (s)")
    fig.suptitle(f"GLM Weights: {subject}")
    
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Plot GLM Results (Quick Screening)")
    parser.add_argument("--data_type", type=str, default="erp", choices=['erp', 'hfa'], help="Data type (erp or hfa)")
    parser.add_argument("--baseline_mode", type=str, default="local", choices=['local', 'global'], help="Baseline (local or global)")
    parser.add_argument("--model", type=str, default="ModelC", help="Model name (e.g. ModelA, ModelB, ModelC, ModelD)")
    args = parser.parse_args()

    # Construct Paths
    suffix = f"_base{args.baseline_mode}"
    glm_results_file = f"derivatives/glm_results/glm_results_{args.data_type}{suffix}_{args.model}.h5"
    out_root = f"derivatives/glm_results/figures_{args.data_type}{suffix}_{args.model}"

    if not os.path.exists(glm_results_file):
        print(f"Results file missing: {glm_results_file}")
        return
        
    os.makedirs(out_root, exist_ok=True)
    fs = detect_fs_from_h5(glm_results_file)
    
    with h5py.File(glm_results_file, 'r') as hf:
        subjects = [k for k in hf.keys() if isinstance(hf[k], h5py.Group)]
            
    for subj in subjects:
        betas, pred_names, roi_names = load_results(glm_results_file, subj)
        if betas is not None:
            out_path = os.path.join(out_root, f"{subj}_GLM_Betas.png")
            plot_betas(betas, pred_names, roi_names, subj, out_path, fs)

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
