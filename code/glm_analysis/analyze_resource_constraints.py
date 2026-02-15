#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Resource Constraints Analysis
=============================

Investigates the "Vanishing MMN" phenomenon and the "Length-induced Resource Constraint" hypothesis.

Modules:
1. Reconstructed ERPs: Visualizes the suppression of MMN in Long (16) vs Short (4) sequences.
   Formula: MMN_pred(t, L) = Beta_Surprisal(t) + Beta_Interaction(t) * (L - EMPIRICAL_MEAN)
   Empirical Mean of Length = 10.69 (User specified)

2. Beta Decay: Quantifies the effective Surprisal amplitude as a function of Length.
   Beta_eff(L) = Beta_Surprisal + Beta_Interaction * (L - 10.69)

3. S1-Auditory Correlation: Tests the trade-off between S1 "Counting" (Position) and Auditory MMN (Surprisal).
   Correlation between Peak Amplitude of S1_Position and Auditory_Surprisal.

Inputs:
- A specified GLM results HDF5 file.

Outputs:
- Figures and CSV files detailing the analyses into a specified output directory.
"""

import os
import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
import argparse

# --- Configuration ---
EMPIRICAL_MEAN_LENGTH = 10.69

# Time window for MMN Peak (e.g., 100-300ms)
MMN_WINDOW = (0.1, 0.3)
# Time window for S1 Position Accumulation
POS_WINDOW = (0.0, 0.5)


def detect_fs_from_h5(h5_path):
    """Read FS from HDF5 attribute strictly."""
    with h5py.File(h5_path, 'r') as hf:
        if 'fs' in hf.attrs and hf.attrs['fs'] > 0:
            return float(hf.attrs['fs'])
    raise RuntimeError(f"Could not detect 'fs' attribute in {h5_path}")

def get_peak_amplitude(beta_trace, fs, window):
    """
    Find peak amplitude in a window, preserving the sign.
    """
    t = np.arange(len(beta_trace)) / fs
    mask = (t >= window[0]) & (t <= window[1])

    if not np.any(mask):
        return 0.0

    trace_win = beta_trace[mask]
    idx_max = np.argmax(np.abs(trace_win))
    return trace_win[idx_max]

def main(input_file, output_dir):
    """Main function to run all resource constraint analyses."""
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}")
        return

    fig_dir = os.path.join(output_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)
    print(f"Results will be saved to: {output_dir}")
    print(f"Figures will be saved to: {fig_dir}")

    # Detect sampling frequency from the input file
    try:
        fs = detect_fs_from_h5(input_file)
        print(f"Detected sampling frequency: {fs} Hz")
    except RuntimeError as e:
        print(f"Error: {e}")
        return

    # Data Containers
    erp_data = []
    decay_data = []
    corr_data_s1_pos = []
    corr_data_aud_surp = []
    corr_meta = []

    with h5py.File(input_file, 'r') as hf:
        subjects = list(hf.keys())
        print(f"Processing subjects: {subjects}")

        for subj in subjects:
            grp = hf[subj]

            if "ROIBetas" not in grp: continue

            betas = grp["ROIBetas"][:]
            roi_names = [x.decode('utf-8') for x in grp.attrs["roi_names"]]
            pred_names = [x.decode('utf-8') for x in grp.attrs["predictors"]]

            n_time = betas.shape[2]
            t_axis = np.arange(n_time) / fs

            # --- Modules 1 & 2: Auditory Surprisal Dynamics ---
            if 'Auditory' in roi_names and 'Surprisal' in pred_names and 'Interaction' in pred_names:
                r_idx = roi_names.index('Auditory')
                p_surp_idx = pred_names.index('Surprisal')
                p_int_idx = pred_names.index('Interaction')

                b_surp = betas[r_idx, p_surp_idx, :]
                b_int = betas[r_idx, p_int_idx, :]

                # Reconstructed ERPs (L4 vs L16)
                erp_short = b_surp + b_int * (4 - EMPIRICAL_MEAN_LENGTH)
                erp_long = b_surp + b_int * (16 - EMPIRICAL_MEAN_LENGTH)

                for ti, val in enumerate(erp_short):
                    erp_data.append({'Subject': subj, 'Length_Type': 'Short (L=4)', 'Time_s': t_axis[ti], 'Amplitude': val})
                for ti, val in enumerate(erp_long):
                    erp_data.append({'Subject': subj, 'Length_Type': 'Long (L=16)', 'Time_s': t_axis[ti], 'Amplitude': val})

                # Beta Decay (All Lengths)
                for L in [4, 6, 8, 12, 16]:
                    eff_beta_trace = b_surp + b_int * (L - EMPIRICAL_MEAN_LENGTH)
                    peak_amp = get_peak_amplitude(eff_beta_trace, fs, MMN_WINDOW)
                    decay_data.append({'Subject': subj, 'Length': L, 'Effective_Beta_Peak': peak_amp})

                peak_surp = get_peak_amplitude(b_surp, fs, MMN_WINDOW)
                corr_data_aud_surp.append(peak_surp)

            # --- Module 3: S1 Position ---
            if 'S1' in roi_names and 'Position_c' in pred_names:
                r_idx_s1 = roi_names.index('S1')
                p_pos_idx = pred_names.index('Position_c')
                b_pos = betas[r_idx_s1, p_pos_idx, :]
                peak_pos = get_peak_amplitude(b_pos, fs, POS_WINDOW)

                if 'Auditory' in roi_names and 'Surprisal' in pred_names: # Check that we have a pair
                    corr_data_s1_pos.append(peak_pos)
                    corr_meta.append({'Subject': subj})

    # --- Save & Plot ---
    if erp_data:
        df_erp = pd.DataFrame(erp_data)
        df_erp.to_csv(os.path.join(output_dir, "reconstructed_erp.csv"), index=False)
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df_erp, x='Time_s', y='Amplitude', hue='Length_Type', style='Subject', errorbar=('ci', 68))
        plt.title("Reconstructed MMN: Short vs Long Sequences")
        plt.savefig(os.path.join(fig_dir, "reconstructed_erp_L4_vs_L16.png"))
        plt.close()
        print("Saved Module 1 (Reconstructed ERP) results.")

    if decay_data:
        df_decay = pd.DataFrame(decay_data)
        df_decay.to_csv(os.path.join(output_dir, "beta_decay.csv"), index=False)
        plt.figure(figsize=(8, 6))
        sns.regplot(data=df_decay, x='Length', y='Effective_Beta_Peak', scatter_kws={'alpha':0.5})
        sns.scatterplot(data=df_decay, x='Length', y='Effective_Beta_Peak', hue='Subject')
        plt.title("Decay of MMN Amplitude with Sequence Length")
        plt.savefig(os.path.join(fig_dir, "beta_decay_curve.png"))
        plt.close()
        print("Saved Module 2 (Beta Decay) results.")

    if len(corr_data_s1_pos) == len(corr_data_aud_surp) and corr_data_s1_pos:
        df_corr = pd.DataFrame(corr_meta)
        df_corr['S1_Position_Beta'] = corr_data_s1_pos
        df_corr['Auditory_Surprisal_Beta'] = corr_data_aud_surp
        df_corr.to_csv(os.path.join(output_dir, "roi_correlation.csv"), index=False)

        r_val, p_val = pearsonr(df_corr['S1_Position_Beta'], df_corr['Auditory_Surprisal_Beta'])
        plt.figure(figsize=(8, 6))
        sns.regplot(data=df_corr, x='S1_Position_Beta', y='Auditory_Surprisal_Beta', color='purple')
        sns.scatterplot(data=df_corr, x='S1_Position_Beta', y='Auditory_Surprisal_Beta', hue='Subject', s=100)
        plt.title(f"Resource Trade-off: S1 Counting vs Auditory MMN\nR={r_val:.2f}, p={p_val:.3f}")
        plt.savefig(os.path.join(fig_dir, "roi_correlation.png"))
        plt.close()
        print("Saved Module 3 (ROI Correlation) results.")
    else:
        print("Not enough paired data for ROI correlation.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze resource constraints from GLM results.")
    parser.add_argument(
        '--input_file',
        type=str,
        required=True,
        help="Path to the input GLM results HDF5 file (e.g., from Model C)."
    )
    parser.add_argument(
        '--output_dir',
        type=str,
        default="derivatives/glm_results",
        help="Path to save the output CSV and figure files."
    )
    args = parser.parse_args()

    main(args.input_file, args.output_dir)
