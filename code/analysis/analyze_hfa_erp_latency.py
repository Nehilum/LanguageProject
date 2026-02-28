#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HFA–ERP Latency Analysis
=========================

Tests whether Short sequences are processed faster by examining the
temporal lag between HFA peak (auditory cortical firing) and ERP peak
(postsynaptic potentials / cognitive integration) on a trial-by-trial basis.

Method:
1. For each trial, find t_HFA = peak time of HFA envelope (100–300 ms window).
2. Find t_ERP = peak time of |ERP| (100–300 ms window).
3. Compute Δt = t_ERP − t_HFA per trial.
4. Compare Δt between Short and Long trials (Mann-Whitney U).
5. Compare Δt variance (Levene's test) for Precision hypothesis.

Outputs:
- derivatives/analysis/gating/latency_hfa_erp_stats.csv
- derivatives/visualization/latency_hfa_erp_{baseline}/Latency_Dist_{subj}.png
"""

import os
import json
import h5py
import glob
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.ndimage import gaussian_filter1d

# ── Config ──────────────────────────────────────────────────────────────
ROI_JSON = "derivatives/rois/functional_rois.json"
OUT_DIR = "derivatives/analysis/gating"
FS = 250.0  # Default, overridden by data files if available

def detect_fs_from_h5(h5_path, default_fs=250.0):
    """Read FS from HDF5 attribute, or infer from Y shape (1.0s epoch)."""
    import h5py
    with h5py.File(h5_path, 'r') as hf:
        if 'fs' in hf.attrs and hf.attrs['fs'] > 0:
            return float(hf.attrs['fs'])
        # Infer from first Y dataset shape
        for cond in hf.keys():
            for subj in hf[cond].keys():
                if 'Y' in hf[f"{cond}/{subj}"]:
                    n_time = hf[f"{cond}/{subj}/Y"].shape[-1]
                    return float(n_time)  # 1.0s epoch → n_time = FS
    return default_fs
T_START = -0.2  # Epoch start (s)

# Peak-detection windows (seconds)
PEAK_WIN = (0.10, 0.30)  # 100–300 ms post-onset

# Length grouping
LEN_GROUPS = {
    'Short': [4, 6],
    'Long': [12, 16]
}


# ── Helpers ─────────────────────────────────────────────────────────────
def get_idx(t_s):
    idx = int(round((t_s - T_START) * FS))
    return max(0, idx)


def fractional_area_latency(signal, fraction=0.5):
    """Find time at which cumulative |signal| reaches fraction of total area.
    
    More robust than peak detection for noisy single-trial ECoG data.
    Returns the index into the signal array.
    """
    cumulative = np.cumsum(np.abs(signal))
    total = cumulative[-1]
    if total == 0:
        return len(signal) // 2
    threshold = fraction * total
    idx = np.searchsorted(cumulative, threshold)
    return min(idx, len(signal) - 1)


def smooth_signal(signal, fs, sigma_ms=10.0):
    """Apply Gaussian smoothing with sigma in milliseconds."""
    sigma_samples = sigma_ms / 1000.0 * fs
    return gaussian_filter1d(signal, sigma=sigma_samples)


def load_rois(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)


def get_auditory_indices(channel_names, roi_def, subject):
    """Return channel indices for Auditory ROI."""
    if subject not in roi_def['subjects']:
        return []
    subj_rois = roi_def['subjects'][subject]
    roi_chs = set()
    if 'Auditory' in subj_rois:
        for _, ch_list in subj_rois['Auditory'].items():
            if isinstance(ch_list, list):
                roi_chs.update(ch_list)
    return [i for i, name in enumerate(channel_names) if name in roi_chs]


def load_subject_data(h5_path, rois):
    """Load all trials for each subject, averaged within Auditory ROI."""
    data = {}
    with h5py.File(h5_path, 'r') as hf:
        # Discover subjects
        subjects = set()
        for cond in hf.keys():
            if isinstance(hf[cond], h5py.Group):
                for s in hf[cond].keys():
                    subjects.add(s)

        for subj in subjects:
            # Get channel names
            epoch_files = glob.glob(f"derivatives/epochs/*/{subj}/*.npz")
            if not epoch_files:
                continue
            tmp = np.load(epoch_files[0], allow_pickle=True)
            ch_names = [str(c) for c in tmp['channel_names']]

            roi_idx = get_auditory_indices(ch_names, rois, subj)
            if not roi_idx:
                continue

            Y_list, X_list = [], []
            for cond in hf.keys():
                if subj in hf[cond]:
                    g = hf[f"{cond}/{subj}"]
                    if "Y" not in g or "X" not in g:
                        continue
                    y_raw = g["Y"][:]
                    y_roi = np.mean(y_raw[:, roi_idx, :], axis=1)  # (N, Time)

                    cols = list(g.attrs["columns"])
                    x_grp = g["X"]
                    d = {}
                    for c in cols:
                        vals = x_grp[c][:]
                        d[c] = [v.decode('utf-8') if isinstance(v, bytes) else v
                                for v in vals]
                    X_list.append(pd.DataFrame(d))
                    Y_list.append(y_roi)

            if Y_list:
                data[subj] = {
                    "Y": np.concatenate(Y_list, axis=0),
                    "X": pd.concat(X_list, axis=0, ignore_index=True)
                }
    return data


# ── Main ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="HFA–ERP Latency Analysis")
    parser.add_argument("--baseline_mode", type=str, default="local",
                        choices=['local', 'global'],
                        help="Baseline correction strategy")
    args = parser.parse_args()

    suffix = f"_base{args.baseline_mode}"
    hfa_file = f"derivatives/glm_data/glm_dataset_hfa{suffix}.h5"
    erp_file = f"derivatives/glm_data/glm_dataset_erp{suffix}.h5"
    viz_dir = f"derivatives/visualization/latency_hfa_erp{suffix}"

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(viz_dir, exist_ok=True)

    rois = load_rois(ROI_JSON)

    # ── Load Data ───────────────────────────────────────────────────
    print(f"Loading HFA data ({args.baseline_mode} baseline)...")
    if not os.path.exists(hfa_file):
        print(f"Error: {hfa_file} not found.")
        return

    # Detect FS from data files
    global FS
    FS = detect_fs_from_h5(hfa_file)
    print(f"Detected FS = {FS} Hz")

    hfa_data = load_subject_data(hfa_file, rois)

    print(f"Loading ERP data ({args.baseline_mode} baseline)...")
    if not os.path.exists(erp_file):
        print(f"Error: {erp_file} not found.")
        return
    erp_data = load_subject_data(erp_file, rois)

    subjects = sorted(set(hfa_data.keys()) & set(erp_data.keys()))
    print(f"Subjects: {subjects}")

    # Time vector
    n_samp = hfa_data[subjects[0]]["Y"].shape[1]
    times = np.linspace(T_START, T_START + n_samp / FS, n_samp, endpoint=False)

    # Peak-detection index range
    idx_lo = get_idx(PEAK_WIN[0])
    idx_hi = get_idx(PEAK_WIN[1])

    stats_rows = []

    for subj in subjects:
        X_hfa = hfa_data[subj]['X']
        Y_hfa = hfa_data[subj]['Y']
        X_erp = erp_data[subj]['X']
        Y_erp = erp_data[subj]['Y']

        # Verify alignment
        if len(X_hfa) != len(X_erp):
            print(f"Warning: trial count mismatch for {subj} "
                  f"(HFA={len(X_hfa)}, ERP={len(X_erp)}). Skipping.")
            continue

        n_trials = len(X_hfa)
        print(f"  {subj}: {n_trials} trials")

        # ── Per-trial peak detection (with smoothing) ──────────────
        # Smoothing (σ=10ms) reduces noise-driven peak jitter
        t_hfa_peaks = np.full(n_trials, np.nan)
        t_erp_peaks = np.full(n_trials, np.nan)

        for i in range(n_trials):
            # HFA: find peak of smoothed envelope amplitude
            hfa_win = Y_hfa[i, idx_lo:idx_hi]
            if len(hfa_win) > 0:
                hfa_smooth = smooth_signal(hfa_win, FS, sigma_ms=10.0)
                pk = np.argmax(hfa_smooth) + idx_lo
                t_hfa_peaks[i] = times[pk]

            # ERP: fractional area latency (50% AUC) on smoothed signal
            # More robust than raw peak for noisy single-trial ERPs
            erp_win = Y_erp[i, idx_lo:idx_hi]
            if len(erp_win) > 0:
                erp_smooth = smooth_signal(erp_win, FS, sigma_ms=10.0)
                fa_idx = fractional_area_latency(erp_smooth, fraction=0.5)
                t_erp_peaks[i] = times[fa_idx + idx_lo]

        # Δt = t_ERP − t_HFA  (positive = ERP lags HFA)
        delta_t = t_erp_peaks - t_hfa_peaks

        # ── Group comparison ────────────────────────────────────────
        lengths = X_hfa['length'].astype(int).values

        for grp_name, grp_lens in LEN_GROUPS.items():
            mask = np.isin(lengths, grp_lens) & np.isfinite(delta_t)
            dt_grp = delta_t[mask]
            t_hfa_grp = t_hfa_peaks[mask]
            t_erp_grp = t_erp_peaks[mask]

            stats_rows.append({
                'Subject': subj,
                'Group': grp_name,
                'N_trials': int(mask.sum()),
                'DeltaT_mean_ms': float(np.mean(dt_grp)) * 1000,
                'DeltaT_median_ms': float(np.median(dt_grp)) * 1000,
                'DeltaT_std_ms': float(np.std(dt_grp)) * 1000,
                'HFA_peak_mean_ms': float(np.mean(t_hfa_grp)) * 1000,
                'ERP_peak_mean_ms': float(np.mean(t_erp_grp)) * 1000,
            })

        # ── Statistical tests (Short vs Long) ──────────────────────
        mask_s = np.isin(lengths, LEN_GROUPS['Short']) & np.isfinite(delta_t)
        mask_l = np.isin(lengths, LEN_GROUPS['Long']) & np.isfinite(delta_t)
        dt_short = delta_t[mask_s]
        dt_long = delta_t[mask_l]

        # Mann-Whitney U on Δt (location shift)
        u_stat, u_p = stats.mannwhitneyu(dt_short, dt_long,
                                         alternative='two-sided')

        # Levene's test on Δt (variance/precision)
        lev_stat, lev_p = stats.levene(dt_short, dt_long)

        stats_rows.append({
            'Subject': subj,
            'Group': 'Short_vs_Long',
            'N_trials': int(mask_s.sum() + mask_l.sum()),
            'DeltaT_mean_ms': float(np.mean(dt_short) - np.mean(dt_long)) * 1000,
            'DeltaT_median_ms': float(np.median(dt_short) - np.median(dt_long)) * 1000,
            'DeltaT_std_ms': np.nan,
            'HFA_peak_mean_ms': np.nan,
            'ERP_peak_mean_ms': np.nan,
            'U_stat': u_stat,
            'U_pvalue': u_p,
            'Levene_stat': lev_stat,
            'Levene_pvalue': lev_p,
        })

        print(f"    Short Δt: {np.mean(dt_short)*1000:.1f} ± {np.std(dt_short)*1000:.1f} ms  "
              f"(N={mask_s.sum()})")
        print(f"    Long  Δt: {np.mean(dt_long)*1000:.1f} ± {np.std(dt_long)*1000:.1f} ms  "
              f"(N={mask_l.sum()})")
        print(f"    Mann-Whitney p = {u_p:.4e}")
        print(f"    Levene p = {lev_p:.4e}")

        # ── Visualization ───────────────────────────────────────────
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # Panel 1: Δt distribution (histogram)
        ax = axes[0]
        bins = np.linspace(-0.15, 0.15, 40)
        ax.hist(dt_short * 1000, bins=bins * 1000, alpha=0.6,
                color='#1f77b4', label=f'Short (N={mask_s.sum()})', density=True)
        ax.hist(dt_long * 1000, bins=bins * 1000, alpha=0.6,
                color='#d62728', label=f'Long (N={mask_l.sum()})', density=True)
        ax.axvline(0, color='k', linestyle='--', alpha=0.5)
        ax.set_xlabel('Δt = t_ERP − t_HFA (ms)')
        ax.set_ylabel('Density')
        ax.set_title(f'{subj}: Δt Distribution')
        ax.legend()

        # Panel 2: Δt vs trial index (stability over time)
        ax = axes[1]
        ax.scatter(np.where(mask_s)[0], dt_short * 1000, s=1,
                   alpha=0.3, c='#1f77b4', label='Short')
        ax.scatter(np.where(mask_l)[0], dt_long * 1000, s=1,
                   alpha=0.3, c='#d62728', label='Long')
        ax.set_xlabel('Trial index')
        ax.set_ylabel('Δt (ms)')
        ax.set_title(f'{subj}: Δt Stability')
        ax.axhline(0, color='k', linestyle='--', alpha=0.5)
        ax.legend()

        # Panel 3: Peak latency comparison (box plot)
        ax = axes[2]
        plot_data = pd.DataFrame({
            'Group': (['Short'] * mask_s.sum()) + (['Long'] * mask_l.sum()),
            'HFA peak (ms)': np.concatenate([t_hfa_peaks[mask_s],
                                              t_hfa_peaks[mask_l]]) * 1000,
            'ERP peak (ms)': np.concatenate([t_erp_peaks[mask_s],
                                              t_erp_peaks[mask_l]]) * 1000,
            'Δt (ms)': np.concatenate([dt_short, dt_long]) * 1000,
        })
        sns.boxplot(data=plot_data, x='Group', y='Δt (ms)', ax=ax,
                    palette={'Short': '#1f77b4', 'Long': '#d62728'},
                    showfliers=False)
        ax.axhline(0, color='k', linestyle='--', alpha=0.5)
        ax.set_title(f'{subj}: Δt by Group\n'
                     f'U p={u_p:.2e}, Levene p={lev_p:.2e}')

        plt.tight_layout()
        plt.savefig(os.path.join(viz_dir, f"Latency_Dist_{subj}.png"), dpi=300)
        plt.close()
        print(f"    Saved plot to {viz_dir}/Latency_Dist_{subj}.png")

    # ── Save Stats ──────────────────────────────────────────────────
    df_stats = pd.DataFrame(stats_rows)
    out_path = os.path.join(OUT_DIR, f"latency_hfa_erp_stats{suffix}.csv")
    df_stats.to_csv(out_path, index=False)
    print(f"\nSaved results to {out_path}")
    print(df_stats.to_string())


if __name__ == "__main__":
    main()
