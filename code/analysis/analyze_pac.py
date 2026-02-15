#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase–Amplitude Coupling (PAC) Analysis
========================================

Tests whether the phase of slow oscillations (theta/delta, centered on the
4 Hz tone rate) modulates the amplitude of HFA (70–150 Hz), and whether
this coupling differs between Short and Long sequence conditions.

Method (Tort et al., 2010 — Modulation Index):
1. Extract phase φ(t) from ERP signal via bandpass filtering + Hilbert transform.
2. Use HFA envelope A(t) directly from the HFA data.
3. Divide phase into N_BINS (18 × 20°) and compute mean A per bin.
4. MI = KL-divergence(observed distribution, uniform) / log(N_BINS).
5. Compare MI_Short vs MI_Long (Mann-Whitney U).
6. Permutation test: shuffle phase-amplitude pairing (N_SURR surrogates).

Outputs:
- derivatives/analysis/gating/pac_stats_{baseline}.csv
- derivatives/visualization/pac_{baseline}/PAC_Polar_{subj}.png

References:
- Tort, A. B., et al. (2010). Measuring phase–amplitude coupling between
  neuronal oscillations of different frequencies. J. Neurophysiol.
"""

import os
import json
import h5py
import glob
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy import stats
from scipy.signal import butter, filtfilt, hilbert

# ── Config ──────────────────────────────────────────────────────────────
ROI_JSON = "derivatives/rois/functional_rois.json"
OUT_DIR = "derivatives/analysis/gating"
FS = None  # Disciplined reading from data

def detect_fs_from_h5(h5_path):
    """Read FS from HDF5 attribute strictly."""
    import h5py
    with h5py.File(h5_path, 'r') as hf:
        if 'fs' in hf.attrs and hf.attrs['fs'] > 0:
            return float(hf.attrs['fs'])
    raise RuntimeError(f"Could not detect 'fs' attribute in {h5_path}")
T_START = -0.2

# PAC Parameters
N_BINS = 18           # Phase bins (20° each)
N_SURR = 200          # Surrogate shuffles for significance
ANALYSIS_WIN = (0.0, 0.8)  # Only analyse post-onset data (s)
N_BOOTSTRAP = 100     # Bootstrap iterations for subsampled group MI

# Default frequency bands
DEFAULT_PHASE_LOW = 4.0    # Hz  (lower edge of bandpass for phase)
DEFAULT_PHASE_HIGH = 8.0   # Hz  (upper edge — centered on 4 Hz tone rate)

# Length grouping
LEN_GROUPS = {
    'Short': [4, 6],
    'Long': [12, 16]
}


# ── Helpers ─────────────────────────────────────────────────────────────
def get_idx(t_s, fs):
    return max(0, int(round((t_s - T_START) * fs)))


def load_rois(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)


def get_auditory_indices(channel_names, roi_def, subject):
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
    """Load trial-level data averaged within Auditory ROI."""
    data = {}
    with h5py.File(h5_path, 'r') as hf:
        subjects = set()
        for cond in hf.keys():
            if isinstance(hf[cond], h5py.Group):
                for s in hf[cond].keys():
                    subjects.add(s)

        for subj in subjects:
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
                    y_roi = np.mean(y_raw[:, roi_idx, :], axis=1)

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


# ── PAC Functions ───────────────────────────────────────────────────────
def bandpass_filter(signal, lo, hi, fs, order=3):
    """Apply zero-phase Butterworth bandpass filter.

    If *hi* ≥ Nyquist the filter degenerates to a high-pass; if *lo* ≤ 0
    it degenerates to a low-pass.  We handle both edge-cases and also
    check that the resulting *b, a* coefficients yield a stable filter.
    """
    nyq = fs / 2.0
    low = lo / nyq
    high = hi / nyq

    # Clamp to valid Butterworth range (0, 1) exclusive
    low = max(low, 1e-5)
    high = min(high, 1.0 - 1e-5)

    if low >= high:
        raise ValueError(
            f"bandpass_filter: low={lo} Hz >= high={hi} Hz after clamping "
            f"(Nyquist = {nyq} Hz)"
        )

    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal, axis=-1)


def extract_phase(signal, lo, hi, fs, pad_sec=0.5):
    """Bandpass → Hilbert → instantaneous phase (−π … π) with mirror padding.

    Mirror padding is used to mitigate edge artifacts caused by filtering
    and Hilbert transform on short data segments.
    """
    if pad_sec > 0:
        pad_samples = int(pad_sec * fs)
        # Ensure pad_samples is not longer than the signal itself
        pad_samples = min(pad_samples, signal.shape[-1] - 1)
        
        # Mirror padding
        padded_signal = np.pad(signal, (pad_samples, pad_samples), mode='reflect')
        
        # Filter and Hilbert on padded signal
        filtered = bandpass_filter(padded_signal, lo, hi, fs)
        analytic = hilbert(filtered, axis=-1)
        
        # Crop back to original size
        analytic_cropped = analytic[pad_samples:-pad_samples]
        return np.angle(analytic_cropped)
    else:
        filtered = bandpass_filter(signal, lo, hi, fs)
        analytic = hilbert(filtered, axis=-1)
        return np.angle(analytic)


def compute_mi(phase, amplitude, n_bins=N_BINS):
    """Tort Modulation Index.

    MI = KL(P || U) / log(N_BINS)
    where P is the normalised mean-amplitude-per-phase-bin distribution
    and U is a uniform distribution.
    """
    # Handle negative amplitudes (e.g. from baseline subtraction)
    # MI requires a probability distribution, so values must be non-negative.
    # We shift amplitude to be strictly positive if needed.
    min_amp = np.min(amplitude)
    if min_amp < 0:
        # Shift so min is 0 (plus epsilon to avoid all-zeros)
        # This preserves the *shape* of modulation but changes the baseline.
        # Alternatively, we could use the raw envelope if available, but here we work with provided Y.
        amplitude_pos = amplitude - min_amp + 1e-9
    else:
        amplitude_pos = amplitude

    bin_edges = np.linspace(-np.pi, np.pi, n_bins + 1)
    mean_amp = np.zeros(n_bins)

    for b in range(n_bins):
        mask = (phase >= bin_edges[b]) & (phase < bin_edges[b + 1])
        if mask.any():
            mean_amp[b] = np.mean(amplitude_pos[mask])
        else:
            mean_amp[b] = 0.0

    # Normalise to probability distribution
    total = mean_amp.sum()
    if total <= 0:
        return 0.0, mean_amp

    P = mean_amp / total
    # Replace zeros for log safety
    P_safe = np.where(P > 0, P, 1e-15)
    U = 1.0 / n_bins

    # KL divergence
    kl = np.sum(P_safe * np.log(P_safe / U))
    mi = kl / np.log(n_bins)
    return mi, mean_amp


def compute_surrogate_mi(phase, amplitude, n_surr=N_SURR, n_bins=N_BINS):
    """Compute MI for time-shifted surrogates."""
    n = len(phase)
    mi_surr = np.zeros(n_surr)
    for k in range(n_surr):
        # Random circular shift of amplitude relative to phase
        shift = np.random.randint(n // 4, 3 * n // 4)
        amp_shifted = np.roll(amplitude, shift)
        mi_surr[k], _ = compute_mi(phase, amp_shifted, n_bins)
    return mi_surr


# ── Main ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="PAC Analysis (Tort MI)")
    parser.add_argument("--baseline_mode", type=str, default="local",
                        choices=['local', 'global'],
                        help="Baseline correction strategy")
    parser.add_argument("--freq_low", type=float, default=DEFAULT_PHASE_LOW,
                        help="Lower edge of phase frequency band (Hz)")
    parser.add_argument("--freq_high", type=float, default=DEFAULT_PHASE_HIGH,
                        help="Upper edge of phase frequency band (Hz)")
    args = parser.parse_args()

    suffix = f"_base{args.baseline_mode}"
    erp_file = f"derivatives/glm_data/glm_dataset_erp{suffix}.h5"
    hfa_file = f"derivatives/glm_data/glm_dataset_hfa{suffix}.h5"
    viz_dir = f"derivatives/visualization/pac{suffix}"

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(viz_dir, exist_ok=True)

    rois = load_rois(ROI_JSON)

    # ── Load ────────────────────────────────────────────────────────
    print(f"Loading ERP data ({args.baseline_mode} baseline)...")
    if not os.path.exists(erp_file):
        print(f"Error: {erp_file} not found.")
        return

    # Detect FS from data files
    global FS
    FS = detect_fs_from_h5(erp_file)
    print(f"Detected FS = {FS} Hz")

    erp_data = load_subject_data(erp_file, rois)

    print(f"Loading HFA data ({args.baseline_mode} baseline)...")
    if not os.path.exists(hfa_file):
        print(f"Error: {hfa_file} not found.")
        return
    hfa_data = load_subject_data(hfa_file, rois)

    subjects = sorted(set(erp_data.keys()) & set(hfa_data.keys()))
    print(f"Subjects: {subjects}")
    print(f"Phase band: {args.freq_low}–{args.freq_high} Hz")

    # Time indices for analysis window
    idx_lo = get_idx(ANALYSIS_WIN[0], FS)
    idx_hi = get_idx(ANALYSIS_WIN[1], FS)

    stats_rows = []

    for subj in subjects:
        X_erp = erp_data[subj]['X']
        Y_erp = erp_data[subj]['Y']   # (N_trials, N_time)
        Y_hfa = hfa_data[subj]['Y']

        if len(Y_erp) != len(Y_hfa):
            print(f"  Warning: trial mismatch for {subj}. Skipping.")
            continue

        n_trials = len(Y_erp)
        lengths = X_erp['length'].astype(int).values
        print(f"  {subj}: {n_trials} trials")

        # ── Per-trial PAC ───────────────────────────────────────────
        mi_all = np.full(n_trials, np.nan)
        phase_amp_short = []
        phase_amp_long = []

        for i in range(n_trials):
            erp_seg = Y_erp[i, idx_lo:idx_hi]
            hfa_seg = Y_hfa[i, idx_lo:idx_hi]

            if len(erp_seg) < 20:
                continue

            try:
                phase_i = extract_phase(erp_seg, args.freq_low,
                                        args.freq_high, FS)
                mi_i, amp_dist_i = compute_mi(phase_i, hfa_seg)
                mi_all[i] = mi_i

                # Accumulate for group polar histograms
                if lengths[i] in LEN_GROUPS['Short']:
                    phase_amp_short.append((phase_i, hfa_seg))
                elif lengths[i] in LEN_GROUPS['Long']:
                    phase_amp_long.append((phase_i, hfa_seg))
            except Exception:
                continue

        # ── Group Statistics ────────────────────────────────────────
        for grp_name, grp_lens in LEN_GROUPS.items():
            mask = np.isin(lengths, grp_lens) & np.isfinite(mi_all)
            mi_grp = mi_all[mask]
            if len(mi_grp) == 0:
                continue

            stats_rows.append({
                'Subject': subj,
                'Group': grp_name,
                'N_trials': int(mask.sum()),
                'MI_mean': float(np.mean(mi_grp)),
                'MI_median': float(np.median(mi_grp)),
                'MI_std': float(np.std(mi_grp)),
            })

        # Short vs Long comparison
        mask_s = np.isin(lengths, LEN_GROUPS['Short']) & np.isfinite(mi_all)
        mask_l = np.isin(lengths, LEN_GROUPS['Long']) & np.isfinite(mi_all)
        mi_short = mi_all[mask_s]
        mi_long = mi_all[mask_l]

        if len(mi_short) > 0 and len(mi_long) > 0:
            u_stat, u_p = stats.mannwhitneyu(mi_short, mi_long,
                                             alternative='two-sided')

            # Surrogate significance: pool all trials, compute group-level MI
            # ── Bootstrap-subsampled group-level PAC ───────────────
            # Equalise N between Short and Long to remove sample-size bias
            if phase_amp_short and phase_amp_long:
                n_short = len(phase_amp_short)
                n_long = len(phase_amp_long)
                n_sub = min(n_short, n_long)

                print(f"    Group-level MI: subsampling to N={n_sub} "
                      f"(Short={n_short}, Long={n_long}), "
                      f"{N_BOOTSTRAP} iterations")

                mi_boot_short = np.zeros(N_BOOTSTRAP)
                mi_boot_long = np.zeros(N_BOOTSTRAP)
                # Accumulate surrogate MIs across bootstrap iterations
                mi_surr_short_all = []
                mi_surr_long_all = []
                # Store amp distributions from last iteration for plotting
                amp_dist_short_last = np.zeros(N_BINS)
                amp_dist_long_last = np.zeros(N_BINS)

                for b_iter in range(N_BOOTSTRAP):
                    # Subsample both to n_sub
                    idx_s = np.random.choice(n_short, n_sub, replace=False)
                    idx_l = np.random.choice(n_long, n_sub, replace=False)

                    phase_s_sub = np.concatenate([phase_amp_short[j][0]
                                                  for j in idx_s])
                    amp_s_sub = np.concatenate([phase_amp_short[j][1]
                                                for j in idx_s])
                    phase_l_sub = np.concatenate([phase_amp_long[j][0]
                                                  for j in idx_l])
                    amp_l_sub = np.concatenate([phase_amp_long[j][1]
                                                for j in idx_l])

                    mi_s, ad_s = compute_mi(phase_s_sub, amp_s_sub)
                    mi_l, ad_l = compute_mi(phase_l_sub, amp_l_sub)
                    mi_boot_short[b_iter] = mi_s
                    mi_boot_long[b_iter] = mi_l
                    amp_dist_short_last = ad_s
                    amp_dist_long_last = ad_l
                    
                    # Compute surrogates on this N-equalized subsample
                    # (consistent with the observed MI statistic)
                    surr_s = compute_surrogate_mi(phase_s_sub, amp_s_sub)
                    surr_l = compute_surrogate_mi(phase_l_sub, amp_l_sub)
                    mi_surr_short_all.append(surr_s)
                    mi_surr_long_all.append(surr_l)

                mi_group_short = float(np.mean(mi_boot_short))
                mi_group_long = float(np.mean(mi_boot_long))
                amp_dist_short = amp_dist_short_last
                amp_dist_long = amp_dist_long_last

                # Aggregate surrogates across bootstrap iterations
                # Compare mean observed MI against surrogate distribution
                mi_surr_short = np.concatenate(mi_surr_short_all)
                mi_surr_long = np.concatenate(mi_surr_long_all)

                p_surr_short = np.mean(mi_surr_short >= mi_group_short)
                p_surr_long = np.mean(mi_surr_long >= mi_group_long)

            else:
                mi_group_short = mi_group_long = np.nan
                amp_dist_short = amp_dist_long = np.zeros(N_BINS)
                p_surr_short = p_surr_long = np.nan
                mi_boot_short = mi_boot_long = np.array([])

            stats_rows.append({
                'Subject': subj,
                'Group': 'Short_vs_Long',
                'N_trials': int(mask_s.sum() + mask_l.sum()),
                'MI_mean': float(np.mean(mi_short) - np.mean(mi_long)),
                'MI_median': np.nan,
                'MI_std': np.nan,
                'U_stat': u_stat,
                'U_pvalue': u_p,
                'MI_group_Short': mi_group_short,
                'MI_group_Long': mi_group_long,
                'MI_group_Short_std': float(np.std(mi_boot_short)) if len(mi_boot_short) > 0 else np.nan,
                'MI_group_Long_std': float(np.std(mi_boot_long)) if len(mi_boot_long) > 0 else np.nan,
                'N_subsampled': int(min(len(phase_amp_short), len(phase_amp_long))) if phase_amp_short and phase_amp_long else 0,
                'N_bootstrap': N_BOOTSTRAP,
                'P_surr_Short': p_surr_short,
                'P_surr_Long': p_surr_long,
            })

            print(f"    Short MI: {np.mean(mi_short):.6f} ± {np.std(mi_short):.6f}  "
                  f"(N={mask_s.sum()})")
            print(f"    Long  MI: {np.mean(mi_long):.6f} ± {np.std(mi_long):.6f}  "
                  f"(N={mask_l.sum()})")
            print(f"    Mann-Whitney p = {u_p:.4e}")
            print(f"    Group-level MI (N-equalised, {N_BOOTSTRAP} boots): "
                  f"Short={mi_group_short:.6f}±{np.std(mi_boot_short):.6f} "
                  f"(surr p={p_surr_short:.3f}), "
                  f"Long={mi_group_long:.6f}±{np.std(mi_boot_long):.6f} "
                  f"(surr p={p_surr_long:.3f})")

            # ── Visualization ───────────────────────────────────────
            fig, axes = plt.subplots(1, 3, figsize=(16, 5))

            # Panel 1: Polar histogram (Short)
            ax = axes[0]
            ax = fig.add_subplot(1, 3, 1, projection='polar')
            axes[0].set_visible(False)  # hide the rectangular axis
            bin_centers = np.linspace(-np.pi + np.pi / N_BINS,
                                      np.pi - np.pi / N_BINS, N_BINS)
            width = 2 * np.pi / N_BINS
            if np.sum(amp_dist_short) > 0:
                norm_amp = amp_dist_short / np.sum(amp_dist_short)
            else:
                norm_amp = amp_dist_short
            ax.bar(bin_centers, norm_amp, width=width, alpha=0.7,
                   color='#1f77b4', edgecolor='k', linewidth=0.5)
            ax.set_title(f'Short (MI={mi_group_short:.4f})\n'
                         f'p_surr={p_surr_short:.3f}',
                         pad=15)

            # Panel 2: Polar histogram (Long)
            ax = fig.add_subplot(1, 3, 2, projection='polar')
            axes[1].set_visible(False)
            if np.sum(amp_dist_long) > 0:
                norm_amp = amp_dist_long / np.sum(amp_dist_long)
            else:
                norm_amp = amp_dist_long
            ax.bar(bin_centers, norm_amp, width=width, alpha=0.7,
                   color='#d62728', edgecolor='k', linewidth=0.5)
            ax.set_title(f'Long (MI={mi_group_long:.4f})\n'
                         f'p_surr={p_surr_long:.3f}',
                         pad=15)

            # Panel 3: MI distribution comparison
            ax = axes[2]
            bins = np.linspace(0, max(mi_all[np.isfinite(mi_all)]) * 1.1, 40)
            ax.hist(mi_short, bins=bins, alpha=0.6, color='#1f77b4',
                    label='Short', density=True)
            ax.hist(mi_long, bins=bins, alpha=0.6, color='#d62728',
                    label='Long', density=True)
            ax.set_xlabel('Modulation Index (MI)')
            ax.set_ylabel('Density')
            ax.set_title(f'{subj}: MI Distribution\n'
                         f'U p={u_p:.2e}')
            ax.legend()

            fig.suptitle(f'{subj}: Phase ({args.freq_low}–{args.freq_high} Hz)'
                         f' × HFA Amplitude',
                         fontsize=13, fontweight='bold')
            plt.tight_layout()
            plt.savefig(os.path.join(viz_dir, f"PAC_Polar_{subj}.png"),
                        dpi=300)
            plt.close()
            print(f"    Saved plot to {viz_dir}/PAC_Polar_{subj}.png")

    # ── Save Stats ──────────────────────────────────────────────────
    df_stats = pd.DataFrame(stats_rows)
    out_path = os.path.join(OUT_DIR, f"pac_stats{suffix}.csv")
    df_stats.to_csv(out_path, index=False)
    print(f"\nSaved results to {out_path}")
    print(df_stats.to_string())


if __name__ == "__main__":
    main()
