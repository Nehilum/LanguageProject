#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Frequency Tagging Analysis
==========================

Analyzes neural entrainment to abstract structures (Pairs, Alternation, etc.) by computing
the Power Spectral Density (PSD) of sequence epochs.

Hypothesis:
- Base Rate (4Hz): Present in all conditions (Sensory).
- Alternation (2Hz): ABAB
- Pairs (1Hz): AABB
- Quadruplets (0.5Hz): AAAABBBB

Method:
- Load Sequence Epochs (-0.5s to 4.5s).
- Filter for 'habituation' (Standard) trials.
- Slice signal to [0, Sequence_Duration].
- Compute PSD using Welch's method.
- Contrast: PSD(Target) - PSD(RandomControl).
- Pool across ROIs (Auditory).

Inputs:
- derivatives/epochs/<Condition>/<Subject>/seqver-*_epochs.npz
- derivatives/rois/functional_rois.json

Outputs:
- derivatives/frequency/PSD_plots/*.png
- derivatives/frequency/frequency_stats.csv
"""

import os
import glob
import json
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.signal import welch

# Config
DERIVATIVES_DIR = "derivatives"
EPOCH_DIR = os.path.join(DERIVATIVES_DIR, "epochs")
ROI_FILE = os.path.join(DERIVATIVES_DIR, "rois", "functional_rois.json")
OUT_DIR = os.path.join(DERIVATIVES_DIR, "frequency")
FIG_DIR = os.path.join(OUT_DIR, "PSD_plots")

# FS is read strictly from data headers
FS = None

def detect_fs_from_h5(h5_path):
    """Read FS from HDF5 attribute strictly."""
    import h5py
    with h5py.File(h5_path, 'r') as hf:
        if 'fs' in hf.attrs and hf.attrs['fs'] > 0:
            return float(hf.attrs['fs'])
    raise RuntimeError(f"Could not detect 'fs' attribute in {h5_path}")

def detect_fs_from_npz(npz_path):
    """Read FS from epoch .npz file strictly."""
    import numpy as np
    data = np.load(npz_path, allow_pickle=True)
    if 'fs' not in data:
        raise RuntimeError(f"Missing 'fs' in {npz_path}")
    return float(data['fs'])

SOA = 0.25

# Target Frequencies to check
TARGET_FREQS = {
    'Base': 4.0,
    'Alternation': 2.0,
    'Pairs': 1.0,
    'Quads': 0.5
}

# Conditions and their expected structural frequency
# (Condition, Control_Condition, Structural_Freq)
COMPARISONS = [
    ('Alternation', 'RandomControl', 2.0),
    ('Pairs', 'RandomControl', 1.0),
    ('Quadruplets', 'RandomControl', 0.5), # Quadruplets might need special handling
    ('PairsAndAlternation1', 'RandomControl', 1.0), # Pairs + Alt
    ('PairsAndAlternation2', 'RandomControl', 1.0)
]

# Lengths to analyze
LENGTHS = [16, 12, 8, 6, 4]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_rois():
    if not os.path.exists(ROI_FILE):
        return None
    with open(ROI_FILE, 'r') as f:
        return json.load(f)

def get_channel_indices(channel_names, roi_def, subject):
    """Get indices of channels belonging to Auditory ROI."""
    if not roi_def or subject not in roi_def['subjects']:
        return None

    subj_rois = roi_def['subjects'][subject]
    if 'Auditory' not in subj_rois:
        return None

    aud_chs = set()
    for k, v in subj_rois['Auditory'].items():
        if isinstance(v, list):
            aud_chs.update(v)

    indices = [i for i, ch in enumerate(channel_names) if ch in aud_chs]
    return indices

def compute_psd(signals, fs, nperseg=None):
    """
    Compute PSD using Welch's method.
    Returns (freqs, psd_mean).
    psd_mean shape: (n_channels, n_freqs)
    """
    # signals: (n_trials, n_time, n_channels)
    # We want to compute PSD for each trial and channel, then average over trials.

    # Transpose to (n_trials, n_channels, n_time) for scipy
    sig_trans = np.transpose(signals, (0, 2, 1))

    # Flatten trials and channels? No, keep channels separate for ROI pooling.
    # Welch can handle n-d arrays. axis=-1 is time.

    if nperseg is None:
        nperseg = sig_trans.shape[-1] # Use full length (rectangular window -> Periodogram-like)

    freqs, psd = welch(sig_trans, fs=fs, nperseg=nperseg, axis=-1, average='mean')

    # psd: (n_trials, n_channels, n_freqs)
    # Average over trials
    psd_mean = np.mean(psd, axis=0) # (n_channels, n_freqs)

    return freqs, psd_mean

def load_and_process_group(condition, length, subject, roi_data, fs):
    """
    Load epochs for a specific Condition_Length/Subject.
    
    Uses per-length nperseg (= full sequence duration) to maximize
    frequency resolution. This enables resolving 0.5 Hz for length-16,
    0.625 Hz for length-12, etc.
    
    Returns: (freqs, psd_roi_avg) or None
    """
    full_cond = f"{condition}_{length}"
    search_path = os.path.join(EPOCH_DIR, full_cond, subject, "*_epochs.npz")
    files = glob.glob(search_path)

    if not files:
        # logger.warning(f"No files found for {full_cond}/{subject}")
        return None

    all_psds = []
    freqs = None

    for f in files:
        try:
            data = np.load(f, allow_pickle=True)
            signals = data['seq_epochs'] # (N, Time, Ch)
            meta = data['seq_meta']
            ch_names = data['channel_names']

            # Filter Habituation (Standard)
            keep_idx = []
            for i, m in enumerate(meta):
                if m['trial_type'] == 'habituation':
                    keep_idx.append(i)

            if not keep_idx: continue

            signals = signals[keep_idx]

            # Slice Time
            # Window: 0s to Length*SOA
            # FS is read strictly from file
            if 'fs' not in data:
                raise RuntimeError(f"Missing 'fs' in {f}")
            fs_local = float(data['fs'])

            # Slice Time
            # Window: 0s to Length*SOA
            total_dur = length * SOA
            n_samples = int(total_dur * fs_local)

            # Epoch starts at -0.5s.
            # 0.0s is at index: 0.5 * fs_local
            start_idx = int(0.5 * fs_local)
            end_idx = start_idx + n_samples

            if end_idx > signals.shape[1]:
                logger.warning(f"Signal too short for {length} tones. shape={signals.shape}")
                continue

            signals_sliced = signals[:, start_idx:end_idx, :]

            # ROI Selection
            roi_idx = get_channel_indices(ch_names, roi_data, subject)
            if not roi_idx:
                # Fallback to all channels if no ROI? or Skip.
                # Let's Skip to be specific.
                continue

            signals_roi = signals_sliced[:, :, roi_idx] # (N, T, Ch_ROI)

            # Compute PSD with per-length nperseg (= full sliced signal)
            # This gives frequency resolution of 1/(length*SOA) Hz
            nperseg_local = signals_roi.shape[1]  # Use full signal length
            f_ax, psd = compute_psd(signals_roi, fs_local, nperseg=nperseg_local)

            if freqs is None:
                freqs = f_ax

            # Average over ROI channels
            psd_roi_avg = np.mean(psd, axis=0) # (n_freqs,)
            all_psds.append(psd_roi_avg)

        except Exception as e:
            logger.error(f"Error loading {f}: {e}")

    if not all_psds:
        return None

    # Average over sessions (files)
    grand_avg_psd = np.mean(np.stack(all_psds, axis=0), axis=0)
    return freqs, grand_avg_psd

def get_power_at_freq(freqs, psd, target_f, width=0.2):
    """Integrate power around target frequency."""
    # Simple nearest neighbor or small window sum
    # Index of target
    idx = np.argmin(np.abs(freqs - target_f))
    return psd[idx] # Peak value

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)

    roi_data = load_rois()
    if not roi_data:
        logger.error("ROI file not found.")
        return

    # Detect FS
    any_epoch_file = glob.glob(os.path.join(EPOCH_DIR, "*/*/*_epochs.npz"))
    if not any_epoch_file:
        logger.error("No epoch files found, cannot determine sampling rate.")
        return
    fs = detect_fs_from_npz(any_epoch_file[0])
    
    # Per-length nperseg: frequency resolution = 1/(length*SOA) Hz
    # Length 4 → 1.0s → 1.0 Hz resolution
    # Length 8 → 2.0s → 0.5 Hz resolution
    # Length 16 → 4.0s → 0.25 Hz resolution
    for length in LENGTHS:
        nperseg_l = int(length * SOA * fs)
        logger.info(f"  Length {length}: nperseg={nperseg_l} samples, resolution={fs/nperseg_l:.2f} Hz")

    subjects = ['Boss', 'Carol'] # Or detect

    stats_rows = []

    for subj in subjects:
        for length in LENGTHS:
            logger.info(f"Processing Subject: {subj}, Length: {length}")

            # Load RandomControl Baseline
            res_ctrl = load_and_process_group('RandomControl', length, subj, roi_data, fs=fs)
            if res_ctrl is None:
                continue
            freqs_ctrl, psd_ctrl = res_ctrl

            # Iterate Comparisons
            for cond_base, ctrl_name, target_f in COMPARISONS:
                # Skip if control is not RandomControl (future proofing)
                if ctrl_name != 'RandomControl': continue

                # Load Condition
                res_cond = load_and_process_group(cond_base, length, subj, roi_data, fs=fs)

                # Handle cases like PairsAndAlternation1 which might not exist for all lengths
                if res_cond is None: continue

                freqs, psd_cond = res_cond

                # Check freqs match (should be identical if length is same)
                if len(freqs) != len(freqs_ctrl):
                    logger.warning(f"Freq mismatch for {cond_base} vs {ctrl_name}")
                    continue

                # Contrast: Difference
                # psd_diff = psd_cond - psd_ctrl
                # Optional: Relative Change (PSD_cond - PSD_ctrl) / PSD_ctrl
                # Let's stick to raw Difference for now as requested.
                psd_diff = psd_cond - psd_ctrl

                # Extract Stats
                # Base Rate (4Hz)
                p_4hz_cond = get_power_at_freq(freqs, psd_cond, 4.0)
                p_4hz_ctrl = get_power_at_freq(freqs, psd_ctrl, 4.0)

                # Target Freq
                # Determine target freq based on condition name if generic loop
                # Using the defined table for now.
                p_target_cond = get_power_at_freq(freqs, psd_cond, target_f)
                p_target_ctrl = get_power_at_freq(freqs, psd_ctrl, target_f)

                stats_rows.append({
                    'Subject': subj,
                    'Condition': cond_base,
                    'Control': ctrl_name,
                    'Length': length,
                    'Target_Freq': target_f,
                    'Power_Cond': p_target_cond,
                    'Power_Ctrl': p_target_ctrl,
                    'Diff_Score': p_target_cond - p_target_ctrl,
                    'Power_4Hz_Cond': p_4hz_cond,
                    'Power_4Hz_Ctrl': p_4hz_ctrl
                })

                # Plot
                plt.figure(figsize=(10, 6))
                plt.plot(freqs, psd_cond, label=f'{cond_base} {length}', color='red')
                plt.plot(freqs, psd_ctrl, label=f'RandomControl {length}', color='gray', linestyle='--')
                plt.plot(freqs, psd_diff, label='Difference', color='blue', alpha=0.5)

                plt.axvline(target_f, color='green', linestyle=':', label=f'Target {target_f}Hz')
                plt.axvline(4.0, color='black', linestyle=':', label='Base 4Hz')

                plt.xlim(0.1, 10)
                plt.xlabel('Frequency (Hz)')
                plt.ylabel('Power Spectral Density')
                plt.title(f"{subj}: {cond_base} vs Random (L={length})")
                plt.legend()
                plt.grid(True, alpha=0.3)

                fig_name = f"{subj}_{cond_base}_{length}_PSD.png"
                plt.savefig(os.path.join(FIG_DIR, fig_name))
                plt.close()
    # Save Stats
    if stats_rows:
        df = pd.DataFrame(stats_rows)
        csv_path = os.path.join(OUT_DIR, "frequency_stats.csv")
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved stats to {csv_path}")
    else:
        logger.warning("No stats generated.")

if __name__ == "__main__":
    main()
