#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sensor-Based ERP Visualization
------------------------------
Generates grid plots (32 channels) for:
1. Full Sequence Average (-0.5s to 4.5s)
2. Target Tone Average (-0.2s to 0.6s)

Inputs:
    - derivatives/epochs/<Condition>/<Subject>/seqver-*_epochs.npz

Outputs:
    - derivatives/visualization/<Grammar>/<Subject>_Length<L>_sensor_sequence.png
    - derivatives/visualization/<Grammar>/<Subject>_Length<L>_sensor_tone.png
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import argparse

# --- CONFIG ---
DERIVATIVES_ROOT = Path("derivatives")
if not DERIVATIVES_ROOT.exists():
    if Path("../derivatives").exists():
        DERIVATIVES_ROOT = Path("../derivatives")
    elif Path("NewPipeline/derivatives").exists():
        DERIVATIVES_ROOT = Path("NewPipeline/derivatives")

EPOCH_DIR = DERIVATIVES_ROOT / "epochs"
VIZ_DIR = DERIVATIVES_ROOT / "visualization"

CONDITION_COLORS = {
    'standard': 'blue',
    'violation': 'red',
    'habituation': 'green'
}

# Time params for plots
SEQ_TIME_RANGE = (-0.5, 4.5)
TONE_TIME_RANGE = (-0.2, 0.6) # Plot window for tone (relative to tone onset)
TONE_BASELINE = (-0.05, 0.0)  # For visual baseline correction of tone plot
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


def parse_condition_string(cond_str):
    parts = cond_str.rsplit('_', 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0], int(parts[1])
    return cond_str, 0

def get_time_axis(n_samples, flim):
    return np.linspace(flim[0], flim[1], n_samples)

def plot_sensor_grid(data_map, ch_names, user_title, out_path, time_axis):
    """
    Plots a grid of 32 channels.
    data_map: {'standard': (N, T, C), ...}
    """
    n_chs = len(ch_names)
    n_cols = 8
    n_rows = int(np.ceil(n_chs / n_cols))

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 12), sharex=True, sharey=True)
    axes = axes.flatten()

    for i, ax in enumerate(axes):
        if i >= n_chs:
            ax.axis('off')
            continue

        ch = ch_names[i]

        for cond, color in CONDITION_COLORS.items():
            dat = data_map.get(cond)
            if dat is not None and dat.shape[0] > 0:
                # Average
                mean_wave = np.mean(dat[:, :, i], axis=0)
                sem_wave = np.std(dat[:, :, i], axis=0) / np.sqrt(dat.shape[0])

                ax.plot(time_axis, mean_wave, color=color, label=cond, linewidth=1)
                ax.fill_between(time_axis, mean_wave - sem_wave, mean_wave + sem_wave, color=color, alpha=0.2)

        ax.set_title(ch, fontsize=8)
        ax.axvline(0, color='k', linestyle='--', alpha=0.5, linewidth=0.8)
        # Mark baseline 0 line
        ax.axhline(0, color='k', linewidth=0.5, alpha=0.3)

    # Global Labels
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right')

    plt.suptitle(user_title, fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved {out_path}")

def extract_tones(signals, meta, fs):
    """
    Extracts tone epochs from full sequence signals.
    Returns data_map {'standard': ..., 'violation': ...}
    """
    # Tone Window
    t_start = TONE_TIME_RANGE[0]
    t_end = TONE_TIME_RANGE[1]

    s_start = int(t_start * fs)
    s_end = int(t_end * fs)
    n_samps = s_end - s_start

    # Baseline for Tone Plot (local baseline)
    b_start = int(TONE_BASELINE[0] * fs)
    b_end = int(TONE_BASELINE[1] * fs) # usually 0

    # Sequence Epoch Window (needed to find 0 time)
    # The epoch starts at -0.5s relative to Sequence Onset.
    # So index 0 is -0.5s.
    # Sequence Onset (0s) is at index offset = 0.5 * fs = 125.
    seq_pre_time = -SEQ_TIME_RANGE[0] # 0.5s
    seq_offset_samp = int(seq_pre_time * fs)

    extracted = {k: [] for k in CONDITION_COLORS}

    for i, m in enumerate(meta):
        # We only care about matching positions?
        # User: "Standard No-violation trials... matching position".
        # But for 'standard' visual we usually aggregate all valid positions or just match?
        # Let's aggregate for now.

        ttype = m['trial_type']
        v_pos = int(m['violation_position'])

        # Determine Target Tone Position (1-indexed)
        # If Violation: target is v_pos
        # If Standard: target is... ?
        # Usually we compare violation vs standard AT THE SAME POSITION.
        # But here we want a general plot?
        # If we just plot "Standard", which tone do we plot?
        #   A. All tones? (Messy)
        #   B. The tone at the 'violation position' of the matching deviant condition?
        #      (Requires knowing the 'block' context, but we are mixing blocks)
        #   C. Just use the 'violation' trials to identify the position of interest?

        # Let's assume we align to the "deviant position" if available.
        # But 'standard' trials have v_pos=0.
        # WE NEED Matching Info.
        # Current logic in `cut_epoch_unified.py` saved `viol_pos` for violations.
        # What about standards? Standards are standards.

        # Heuristic:
        #   Collect all violations. Find the common position (e.g. 9).
        #   Then for standards, extract Position 9.
        pass # Just logic comment

    # Actually, to be robust:
    # We should iterate meaningful positions.
    # But usually a block has a fixed violation position (e.g. 9).
    # Let's find the 'modal' violation position for this dataset.

    positions = [int(m['violation_position']) for m in meta if m['trial_type'] == 'violation']
    if not positions:
        # No violations? Maybe habituation only?
        target_pos = 1
    else:
        target_pos =  max(set(positions), key=positions.count) # Most common pos

    print(f"  Extracting tones at Position {target_pos}...")

    for i, m in enumerate(meta):
        ttype = m['trial_type'] # 'violation', 'habituation' (standard usually labeled as ?)
        # In new cut_epoch, type is in `meta['trial_type']`.
        # Wait, `cut_epoch` writes `violation_type` and `trial_type`.
        # Standard trials have `trial_type='violation'` but `violation_position=0`?
        # Or `trial_type='standard'`?
        # Let's check `cut_epoch_unified.py`...
        # It copies `trial_type` from events.tsv.
        # Usually BIDS events have 'violation' for the whole block? Or 'standard' for std blocks.

        # Let's rely on `violation_position`.
        # If pos > 0: It is a deviant trial.
        # If pos == 0: It is a standard trial.

        v_pos = int(m.get('violation_position', 0))

        cond_label = None
        current_pos = -1

        if v_pos > 0:
            # This is a deviant trial (or at least contains a deviation)
            # Deviation is at `v_pos`.
            if v_pos == target_pos:
                cond_label = 'violation'
                current_pos = v_pos
            else:
                continue # Ignore mixed deviations (if any)
        else:
            # This is a standard trial (v_pos=0)
            cond_label = 'standard'
            current_pos = target_pos # We extract the SAME position to compare

        if m.get('trial_type') == 'habituation':
             cond_label = 'habituation'
             current_pos = target_pos # Match same position

        if not cond_label: continue

        # Calculate Sample Index of Tone Onset
        # Tone 1 starts at 0s (relative to Seq Onset).
        # Tone N starts at (N-1)*SOA.
        # SOA = 0.25s.

        tone_onset_s = (current_pos - 1) * 0.25
        tone_onset_idx = seq_offset_samp + int(tone_onset_s * fs)

        start_idx = tone_onset_idx + s_start
        end_idx = tone_onset_idx + s_end

        if start_idx < 0 or end_idx > signals.shape[1]:
            continue

        # Cutting
        raw_tone = signals[i, start_idx:end_idx, :]

        # Apply Baseline (Tone-based -50ms)
        # s_start is -0.2s (-50 samples).
        # baseline (-0.05 to 0.0) is inside this window.
        # Relative to cut start (-0.2s):
        #   -0.05s is at +0.15s from start.
        # 0.2s pre-stim = 50 samples.
        # -0.05s = 12 samples from 0.
        # Let's use `b_start` logic relative to tone onset.

        # Rel indices within the cut:
        # cut starts at t_start (-0.2).
        # baseline starts at -0.05.
        # offset = (-0.05 - (-0.2)) * fs = 0.15 * 250 = 37.5 -> 37 samples.

        bl_start_rel = int((TONE_BASELINE[0] - TONE_TIME_RANGE[0]) * fs)
        bl_end_rel = int((TONE_BASELINE[1] - TONE_TIME_RANGE[0]) * fs)

        if bl_start_rel < 0: bl_start_rel = 0

        base_mean = np.mean(raw_tone[bl_start_rel:bl_end_rel, :], axis=0)
        bc_tone = raw_tone - base_mean

        extracted[cond_label].append(bc_tone)

    # Stack
    for k in extracted:
        if extracted[k]:
            extracted[k] = np.stack(extracted[k], axis=0) # (N, T, C)
        else:
            extracted[k] = None

    return extracted

def main():
    if not EPOCH_DIR.exists(): return

    for cond_path in EPOCH_DIR.iterdir():
        if not cond_path.is_dir(): continue
        grammar, length = parse_condition_string(cond_path.name)

        for subj_path in cond_path.iterdir():
            if not subj_path.is_dir(): continue
            subject = subj_path.name

            # Load Data
            files = list(subj_path.glob("*_epochs.npz"))
            if not files: continue

            all_signals = []
            all_meta = []
            ch_names = None
            fs = None

            for f in files:
                d = np.load(f, allow_pickle=True)
                if 'fs' not in d:
                    raise RuntimeError(f"Missing 'fs' in {f}")
                fs = float(d['fs'])
                # Check keys
                if 'signal' in d:
                    sig = d['signal'] # (N, T, C)
                elif 'erp_epochs' in d:
                    # Old format, likely not sequence based or is it?
                    # The user said scripts are for old version.
                    # We assume we are running on NEW data now.
                    # If old data, skip or warn?
                    print(f"Skipping {f.name} (Legacy Format)")
                    continue
                else: continue

                all_signals.append(sig)
                all_meta.extend(d['meta'])
                if ch_names is None: ch_names = d['channel_names']

            if not all_signals: continue

            full_signals = np.concatenate(all_signals, axis=0) # (TotalN, T, C)

            # 1. Sequence Plot
            # Group by Condition
            # For Sequence Plot, we separate 'standard' sequences (v_pos=0) vs 'violation' sequences (v_pos>0)
            seq_data_map = {k: [] for k in CONDITION_COLORS}

            for i, m in enumerate(all_meta):
                v_pos = int(m.get('violation_position', 0))
                ttype = m.get('trial_type', '')

                label = 'standard'
                if v_pos > 0: label = 'violation'
                if ttype == 'habituation': label = 'habituation'

                seq_data_map[label].append(full_signals[i])

            for k in seq_data_map:
                if seq_data_map[k]: seq_data_map[k] = np.stack(seq_data_map[k], axis=0)
                else: seq_data_map[k] = None

            # Time Axis Sequence
            t_axis_seq = get_time_axis(full_signals.shape[1], SEQ_TIME_RANGE)

            out_seq = VIZ_DIR / grammar / f"{subject}_Length{length}_sensor_sequence.png"
            plot_sensor_grid(seq_data_map, ch_names, f"{subject} L{length} Sequence", out_seq, t_axis_seq)

            # 2. Tone Plot
            # Extract Tones
            tone_data_map = extract_tones(full_signals, all_meta, fs)

            # Time Axis Tone
            # We need length of extracted tone
            # TONE_TIME_RANGE = (-0.2, 0.6) -> 0.8s -> 200 samples
            # Verify shape from first valid data
            sample_shape = 0
            for k, v in tone_data_map.items():
                if v is not None:
                    sample_shape = v.shape[1]
                    break

            if sample_shape > 0:
                t_axis_tone = get_time_axis(sample_shape, TONE_TIME_RANGE)
                out_tone = VIZ_DIR / grammar / f"{subject}_Length{length}_sensor_tone.png"
                plot_sensor_grid(tone_data_map, ch_names, f"{subject} L{length} Tone (Target)", out_tone, t_axis_tone)

if __name__ == "__main__":
    main()
