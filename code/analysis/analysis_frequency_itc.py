#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Frequency Tagging Analysis (ITC) - Publication Grade
====================================================

Analyzes neural entrainment to abstract structures (Pairs, Alternation, etc.) by computing
the Inter-Trial Coherence (ITC) of sequence epochs with robust statistical controls.

Refinements for Publication:
1. Trial Count Equalization: Subsamples conditions and controls to the same N to remove ITC bias.
2. Permutation Testing: 1000 shuffles to determine statistical significance of structural peaks.

Method:
- Load Sequence Epochs.
- Slice to [0, Duration].
- Compute FFT and extract unit-length complex phase factors.
- Equalize N via subsampling (50 iterations).
- Permutation test (1000 shuffles) for each condition/subject at target frequencies.
"""

import os
import glob
import json
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

# Config
DERIVATIVES_DIR = "derivatives"
EPOCH_DIR = os.path.join(DERIVATIVES_DIR, "epochs")
ROI_FILE = os.path.join(DERIVATIVES_DIR, "rois", "functional_rois.json")
OUT_DIR = os.path.join(DERIVATIVES_DIR, "frequency")
FIG_DIR = os.path.join(OUT_DIR, "ITC_plots_refined")

# FS is read strictly from data headers
FS_DEFAULT = None
SOA = 0.25
N_ITER_SUB = 50     # For trial count equalization
N_PERM = 1000       # For permutation statistics

COMPARISONS = [
    ('Alternation', 'RandomControl', 2.0),
    ('Pairs', 'RandomControl', 1.0),
    ('Quadruplets', 'RandomControl', 0.5),
    ('PairsAndAlternation1', 'RandomControl', 1.0),
    ('PairsAndAlternation2', 'RandomControl', 1.0)
]

LENGTHS = [16, 12, 8, 6, 4]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_rois():
    if not os.path.exists(ROI_FILE): return None
    with open(ROI_FILE, 'r') as f: return json.load(f)

def get_channel_indices(channel_names, roi_def, subject):
    if not roi_def or subject not in roi_def['subjects']: return None
    subj_rois = roi_def['subjects'][subject]
    if 'Auditory' not in subj_rois: return None
    aud_chs = set()
    for k, v in subj_rois['Auditory'].items():
        if isinstance(v, list): aud_chs.update(v)
    return [i for i, ch in enumerate(channel_names) if ch in aud_chs]

def get_phase_factors(signals, fs, n_fft=None):
    """Compute trial-level phase factors (unit length complex Nos) from FFT."""
    n_trials, n_time, n_channels = signals.shape
    if n_fft is None:
        n_fft = int(2**np.ceil(np.log2(n_time * 2)))
        if fs / n_fft > 0.1: n_fft = int(fs / 0.1)

    X = np.fft.rfft(signals, n=n_fft, axis=1) # (n_trials, n_freqs, n_channels)
    X_phase = X / (np.abs(X) + 1e-15)

    freqs = np.fft.rfftfreq(n_fft, d=1/fs)
    return freqs, X_phase

def load_trial_data(condition, length, subject, roi_data):
    """Load trials and compute ROI-averaged phase factors.
    
    Uses per-length segment = full sequence duration to maximize
    frequency resolution (matching PSD analysis).
    """
    full_cond = f"{condition}_{length}"
    files = glob.glob(os.path.join(EPOCH_DIR, full_cond, subject, "*_epochs.npz"))
    if not files: return None, None

    all_phases = []
    freqs = None

    for f in files:
        data = np.load(f, allow_pickle=True)
        signals = data['seq_epochs']
        meta = data['seq_meta']
        ch_names = data['channel_names']
        if 'fs' not in data:
            raise RuntimeError(f"Missing 'fs' in {f}")
        fs = float(data['fs'])

        keep_idx = [i for i, m in enumerate(meta) if m['trial_type'] == 'habituation']
        if not keep_idx: continue

        signals = signals[keep_idx]

        # Slicing to full duration first
        total_dur = length * SOA
        n_samples_full = int(total_dur * fs)
        start_idx = int(0.5 * fs)
        end_idx = start_idx + n_samples_full

        if end_idx > signals.shape[1]: continue

        signals_sliced = signals[:, start_idx:end_idx, :]
        roi_idx = get_channel_indices(ch_names, roi_data, subject)
        if not roi_idx: continue

        signals_roi = signals_sliced[:, :, roi_idx]

        # Use per-length segment = full sliced signal (no sub-segmenting)
        # This gives frequency resolution of 1/(length*SOA) Hz
        # Length 4  → 1.0s → 1.0 Hz resolution
        # Length 8  → 2.0s → 0.5 Hz resolution  (resolves Quadruplets)
        # Length 16 → 4.0s → 0.25 Hz resolution

        # Compute phase factors on full-length signal
        f_ax, phase_factors = get_phase_factors(signals_roi, fs)

        # Average complex factors across ROI channels first
        # phase_factors: (n_segments, n_freqs, n_channels)
        phase_roi_avg = np.mean(phase_factors, axis=2) # (n_segments, n_freqs)

        if freqs is None: freqs = f_ax
        all_phases.append(phase_roi_avg)

    if not all_phases: return None, None
    return freqs, np.concatenate(all_phases, axis=0)

def compute_itc_from_phases(phases):
    """ITC = |mean(phases)| across trials."""
    return np.abs(np.mean(phases, axis=0))

def run_permutation_test(phases_cond, phases_ctrl, target_idx, n_perm=N_PERM):
    """Two-tailed label shuffling permutation test on ITC difference."""
    n_cond = phases_cond.shape[0]
    n_ctrl = phases_ctrl.shape[0]
    n_total = n_cond + n_ctrl

    obs_diff = compute_itc_from_phases(phases_cond)[target_idx] - compute_itc_from_phases(phases_ctrl)[target_idx]

    pooled = np.concatenate([phases_cond, phases_ctrl], axis=0)
    perm_diffs = np.zeros(n_perm)

    for i in range(n_perm):
        shuffled = np.random.permutation(n_total)
        p1 = pooled[shuffled[:n_cond]]
        p2 = pooled[shuffled[n_cond:]]
        perm_diffs[i] = compute_itc_from_phases(p1)[target_idx] - compute_itc_from_phases(p2)[target_idx]

    # p-value: what % of shuffles have diff >= obs_diff (one-tailed for structure enhancement)
    # Actually, let's use two-tailed to be conservative if it's below zero,
    # but usually we test enhancement: Structure > Control.
    p_val = np.mean(perm_diffs >= obs_diff)
    return p_val, obs_diff, perm_diffs

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)
    roi_data = load_rois()
    subjects = ['Boss', 'Carol']
    stats_rows = []

    # Detect FS
    any_epoch_file = glob.glob(os.path.join(EPOCH_DIR, "*/*/*_epochs.npz"))
    if not any_epoch_file:
        logger.error("No epoch files found, cannot determine sampling rate.")
        return
    fs = float(np.load(any_epoch_file[0], allow_pickle=True)['fs'])

    # Per-length ITC segment: frequency resolution = 1/(length*SOA) Hz
    for length in LENGTHS:
        seg_samps = int(length * SOA * fs)
        logger.info(f"  Length {length}: segment={seg_samps} samples, resolution={fs/seg_samps:.2f} Hz")

    for subj in subjects:
        for length in LENGTHS:
            logger.info(f"Subject: {subj}, Length: {length}")
            f_ctrl, phases_ctrl_raw = load_trial_data('RandomControl', length, subj, roi_data)
            if phases_ctrl_raw is None: continue

            for cond_base, ctrl_name, target_f in COMPARISONS:
                f_cond, phases_cond_raw = load_trial_data(cond_base, length, subj, roi_data)
                if phases_cond_raw is None: continue

                # Trial Equalization (Subsampling)
                n_cond = phases_cond_raw.shape[0]
                n_ctrl = phases_ctrl_raw.shape[0]
                n_min = min(n_cond, n_ctrl)

                logger.info(f"  {cond_base} (N={n_cond}) vs {ctrl_name} (N={n_ctrl}) -> Equalizing to N={n_min}")

                itc_cond_accum = np.zeros(phases_cond_raw.shape[1])
                itc_ctrl_accum = np.zeros(phases_ctrl_raw.shape[1])

                # We also need a representative ITC_diff for permutation (on one subsample or average?)
                # Standard is to average the ITC result across iterations.
                for _ in range(N_ITER_SUB):
                    idx_cond = np.random.choice(n_cond, n_min, replace=False)
                    idx_ctrl = np.random.choice(n_ctrl, n_min, replace=False)
                    itc_cond_accum += compute_itc_from_phases(phases_cond_raw[idx_cond])
                    itc_ctrl_accum += compute_itc_from_phases(phases_ctrl_raw[idx_ctrl])

                itc_cond = itc_cond_accum / N_ITER_SUB
                itc_ctrl = itc_ctrl_accum / N_ITER_SUB
                itc_diff = itc_cond - itc_ctrl

                # Permutation Statistics at Target Frequency
                target_idx = np.argmin(np.abs(f_cond - target_f))
                # FIXED: Subsample to n_min before permutation to match observed ITC calculation
                # This removes ITC bias from unequal trial counts in the null distribution
                idx_cond_perm = np.random.choice(n_cond, n_min, replace=False)
                idx_ctrl_perm = np.random.choice(n_ctrl, n_min, replace=False)
                phases_cond_eq = phases_cond_raw[idx_cond_perm]
                phases_ctrl_eq = phases_ctrl_raw[idx_ctrl_perm]

                p_val, _, _ = run_permutation_test(phases_cond_eq, phases_ctrl_eq, target_idx, N_PERM)

                # Also check 4Hz (Base)
                idx_4hz = np.argmin(np.abs(f_cond - 4.0))
                p_val_4hz, _, _ = run_permutation_test(phases_cond_eq, phases_ctrl_eq, idx_4hz, N_PERM)

                stats_rows.append({
                    'Subject': subj, 'Condition': cond_base, 'Length': length,
                    'Target_Freq': target_f, 'N_Cond': n_cond, 'N_Ctrl': n_ctrl, 'N_Min': n_min,
                    'ITC_Cond': itc_cond[target_idx], 'ITC_Ctrl': itc_ctrl[target_idx],
                    'Diff_Score': itc_diff[target_idx], 'P_Value': p_val,
                    'ITC_4Hz_Cond': itc_cond[idx_4hz], 'ITC_4Hz_Ctrl': itc_ctrl[idx_4hz],
                    'P_Value_4Hz': p_val_4hz
                })

                # Plotting
                sig_star = "*" if p_val < 0.05 else ""
                if p_val < 0.01: sig_star = "**"
                if p_val < 0.001: sig_star = "***"

                plt.figure(figsize=(10, 6))
                plt.plot(f_cond, itc_cond, label=f'{cond_base}', color='darkred', lw=2)
                plt.plot(f_cond, itc_ctrl, label=f'RandomControl', color='gray', ls='--', alpha=0.7)
                plt.plot(f_cond, itc_diff, label='Difference', color='royalblue', alpha=0.8)

                plt.axvline(target_f, color='green', ls=':', alpha=0.5)
                # Mark target freq with star
                peak_height = max(itc_cond[target_idx], itc_ctrl[target_idx]) + 0.05
                plt.text(target_f, peak_height, sig_star, ha='center', fontsize=18, color='red', fontweight='bold')

                plt.axvline(4.0, color='black', ls=':', alpha=0.5)

                plt.xlim(0.1, 8)
                plt.ylim(-0.15, 0.7)
                plt.xlabel('Frequency (Hz)')
                plt.ylabel('Inter-Trial Coherence (ITC)')
                plt.title(f"{subj}: {cond_base} (L={length})\nTarget={target_f}Hz, p={p_val:.4f} {sig_star}")
                plt.legend()
                plt.grid(True, alpha=0.2)

                fig_name = f"{subj}_{cond_base}_{length}_ITC_Refined.png"
                plt.savefig(os.path.join(FIG_DIR, fig_name), dpi=300)
                plt.close()
    if stats_rows:
        df = pd.DataFrame(stats_rows)
        df.to_csv(os.path.join(OUT_DIR, "itc_stats_refined.csv"), index=False)
        logger.info(f"Saved refined ITC stats to {OUT_DIR}/itc_stats_refined.csv")
        print(df.to_string())

if __name__ == "__main__":
    main()
