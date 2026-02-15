#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Phase 2: Epoching (Unified: Sequence & Tone)
--------------------------------------------
Goal: Segment data into:
    1. SEQUENCE EPOCHS [-0.5, 4.5]s (for Frequency Tagging)
    2. TONE EPOCHS [-0.2, 0.8]s (for GLM/ERP, centered on each tone)

Inputs:
    - derivatives/preproc/<Condition>/<Subject>/*_preproc.npz
    - data/bids_events/<Condition>/<Subject>/*_events.tsv

Outputs:
    - derivatives/epochs/<Condition>/<Subject>/seqver-<SeqVer>_epochs.npz
      Keys: 'seq_epochs', 'erp_epochs', 'seq_meta', 'meta' (tone meta), 'channel_names', 'fs'

Metadata (Tone Level):
    - pos: 1..16
    - is_viol: 0 or 1 (True if this specific tone is the breach)
    - violation_position: 0 (if standard seq) or 1..16
    - trial_type: standard/violation/habituation
"""

import os
import sys
import json
import glob
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from collections import defaultdict, Counter

# --- CONFIG ---
# Sequence: 16 tones * 0.25 SOA = 4.0s
SEQ_EPOCH_WIN = (-0.5, 4.5)
TONE_EPOCH_WIN = (-0.2, 0.8)
SOA = 0.25
BAD_EPOCH_THR = 0.5  # Reject if >50% of epoch is artifact

# Paths
current_dir = Path(__file__).resolve().parent
PROJECT_ROOT = current_dir.parent.parent
DATA_ROOT = PROJECT_ROOT / "data"
DERIVATIVES_ROOT = PROJECT_ROOT / "derivatives"
PREPROC_ROOT = DERIVATIVES_ROOT / "preproc"
EPOCH_OUT_DIR = DERIVATIVES_ROOT / "epochs"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_events(subject, condition, file_stem):
    """Load matching events.tsv."""
    events_path = DATA_ROOT / "bids_events" / condition / subject / f"{file_stem}_events.tsv"
    if not events_path.exists():
        candidates = list(DATA_ROOT.glob(f"bids_events/*/{subject}/{file_stem}_events.tsv"))
        if candidates:
            return pd.read_csv(candidates[0], sep='\t')
        return None
    return pd.read_csv(events_path, sep='\t')

def get_good_indices(all_channels, bad_channels):
    """Return indices of channels that are NOT in bad_channels."""
    return [i for i, ch in enumerate(all_channels) if ch not in bad_channels]

def cut_epochs_file(npz_file, condition, subject, return_rejected=False):
    """
    Process a single preproc file.
    Returns:
        (seq_dataset, tone_dataset, good_ch_names)
    """
    rejected_dataset = []
    try:
        data = np.load(npz_file, allow_pickle=True)
        signals = data['signals_cmr']
        hfa = data['hfa_cmr']
        mask = data['artifact_mask']
        fs = float(data['fs'])
        ch_names = data['channel_names']

        bad_chs = set(data['bad_channels'])

        good_idx = get_good_indices(ch_names, bad_chs)
        good_ch_names = [ch_names[i] for i in good_idx]
        signals = signals[:, good_idx]
        hfa = hfa[:, good_idx]
        mask = mask[:, good_idx]

        # Load Events
        file_stem = npz_file.stem.replace('_preproc', '')
        df_events = load_events(subject, condition, file_stem)
        if df_events is None:
            logger.warning(f"No events for {npz_file.name}")
            return None

        if 'sequence_version' in df_events.columns:
            seq_ver = str(df_events.iloc[0]['sequence_version'])
        else:
             seq_ver = 'unknown'

        seq_dataset = []
        tone_dataset = []

        # Sample Params
        seq_win_samps = (int(SEQ_EPOCH_WIN[0]*fs), int(SEQ_EPOCH_WIN[1]*fs))
        tone_win_samps = (int(TONE_EPOCH_WIN[0]*fs), int(TONE_EPOCH_WIN[1]*fs))
        soa_samps = int(SOA * fs)

        # Iterate Sequences
        for idx, row in df_events.iterrows():
            seq_onset = float(row['onset'])
            seq_len = int(row['length'])
            ttype = row['trial_type']

            # Metadata parsing
            # violation_position: 0 for standard/habituation, 1-16 for deviation
            # Note: 'violation' trial type might be used for Standards in some pipelines if pos=0
            # But usually 'standard' or 'habituation'.

            # Check column existence
            if 'violation_position' in row and not pd.isna(row['violation_position']):
                seq_viol_pos = int(row['violation_position'])
            elif 'value' in row and not pd.isna(row['value']):
                 seq_viol_pos = int(row['value'])
            else:
                 seq_viol_pos = 0

            viol_type = str(row.get('violation_type', 'none')) if 'violation_type' in row else 'none'
            grammar = str(row.get('grammar', 'unknown'))

            # --- 1. Sequence Epoch ---
            seq_samp = int(seq_onset * fs)
            s_start = seq_samp + seq_win_samps[0]
            s_end = seq_samp + seq_win_samps[1]

            if s_start < 0 or s_end > signals.shape[0]:
                continue

            ep_sig = signals[s_start:s_end, :]
            ep_hfa = hfa[s_start:s_end, :]
            ep_mask = mask[s_start:s_end, :]

            # Sequence Artifact Check
            if np.mean(ep_mask) > BAD_EPOCH_THR:
                continue # Skip this sequence (and its tones)

            seq_meta = {
                'session_id': file_stem,
                'seq_idx': idx,
                'seq_ver': seq_ver,
                'condition': condition,
                'subject': subject,
                'trial_type': ttype,
                'violation_position': seq_viol_pos,
                'violation_type': viol_type,
                'length': seq_len,
                'grammar': grammar,
                'epoch_type': 'sequence',
                'epoch_time_range': SEQ_EPOCH_WIN
            }

            seq_dataset.append({
                'signal': ep_sig.astype(np.float32),
                'hfa': ep_hfa.astype(np.float32),
                'meta': seq_meta
            })

            # --- 2. Tone Epochs ---
            # Loop 1 to Length
            for pos in range(1, seq_len + 1):
                # Tone Onset relative to Sequence Onset
                # Tone 1 is at 0ms (seq_onset), Tone 2 at 250ms...
                # offset = (pos - 1) * SOA

                tone_samp_rel = (pos - 1) * soa_samps
                tone_onset_abs = seq_samp + tone_samp_rel

                t_start = tone_onset_abs + tone_win_samps[0]
                t_end = tone_onset_abs + tone_win_samps[1]

                # Check bounds
                if t_start < 0 or t_end > signals.shape[0]:
                    continue

                tone_sig = signals[t_start:t_end, :]
                tone_hfa = hfa[t_start:t_end, :]
                tone_mask = mask[t_start:t_end, :]

                # Tone Artifact Check (Strict? Or use same THR?)
                # If sequence passed, tone is likely okay, but let's check local artifact
                if np.mean(tone_mask) > BAD_EPOCH_THR:
                    # We can choose to drop individual tones even if sequence is kept
                    continue

                # Meta Logic for Position Matching
                is_this_viol = 0
                if ttype == 'violation' and seq_viol_pos > 0:
                    if pos == seq_viol_pos:
                        is_this_viol = 1

                tone_meta = {
                    'session_id': file_stem,
                    'seq_idx': idx,
                    'pos': pos,
                    'is_viol': is_this_viol,            # 1 if this tone is the deviant
                    'violation_position': seq_viol_pos, # Parent seq property
                    'trial_type': ttype,                # Parent seq property
                    'condition': condition,
                    'subject': subject,
                    'tone_idx': (idx * 100) + pos,      # Unique ID attempt
                    'epoch_type': 'tone',
                    'epoch_time_range': TONE_EPOCH_WIN
                }

                tone_dataset.append({
                    'signal': tone_sig.astype(np.float32), # RAW
                    'hfa': tone_hfa.astype(np.float32),    # RAW
                    'meta': tone_meta
                })

        return seq_dataset, tone_dataset, good_ch_names

    except Exception as e:
        logger.error(f"Error processing {npz_file}: {e}")
        return None

def merge_and_save(seq_list, tone_list, ch_names_list, output_name):
    """
    Merge epochs for a group and save.
    """
    if not seq_list and not tone_list: return

    # 1. Align Channels (Intersection)
    common_chs = set(ch_names_list[0])
    for chs in ch_names_list[1:]:
        common_chs.intersection_update(chs)

    common_chs = sorted(list(common_chs))

    # Process Sequences
    final_seq_sig, final_seq_hfa, final_seq_meta = [], [], []
    for sess_items, sess_chs in zip(seq_list, ch_names_list):
        ch_idx_map = [sess_chs.index(ch) for ch in common_chs]
        for item in sess_items:
            final_seq_sig.append(item['signal'][:, ch_idx_map])
            final_seq_hfa.append(item['hfa'][:, ch_idx_map])
            final_seq_meta.append(item['meta'])

    # Process Tones
    final_tone_sig, final_tone_hfa, final_tone_meta = [], [], []
    for sess_items, sess_chs in zip(tone_list, ch_names_list):
        ch_idx_map = [sess_chs.index(ch) for ch in common_chs]
        for item in sess_items:
            final_tone_sig.append(item['signal'][:, ch_idx_map])
            final_tone_hfa.append(item['hfa'][:, ch_idx_map])
            final_tone_meta.append(item['meta'])

    # Metadata extraction for path
    # Use first available meta
    if final_seq_meta:
        ref_meta = final_seq_meta[0]
    elif final_tone_meta:
        ref_meta = final_tone_meta[0]
    else:
        return

    c0 = ref_meta['condition']
    s0 = ref_meta['subject']
    sver = ref_meta.get('seq_ver', output_name)

    out_dir = EPOCH_OUT_DIR / c0 / s0
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"seqver-{sver}_epochs.npz"

    # Stack
    # Handle empty lists just in case
    if final_seq_sig:
        arr_seq_sig = np.stack(final_seq_sig, axis=0)
        arr_seq_hfa = np.stack(final_seq_hfa, axis=0)
    else:
        arr_seq_sig, arr_seq_hfa = None, None

    if final_tone_sig:
        arr_tone_sig = np.stack(final_tone_sig, axis=0)
        arr_tone_hfa = np.stack(final_tone_hfa, axis=0)
    else:
        arr_tone_sig, arr_tone_hfa = None, None

    # Determine actual FS from the first epoch's data shape and known time range
    # The epoch files were created from preproc files which store fs.
    # We pass fs through from the caller instead.
    # For now, infer from tone epoch shape: tone window is 1.0s (-0.2 to 0.8)
    tone_dur = TONE_EPOCH_WIN[1] - TONE_EPOCH_WIN[0]
    if final_tone_sig:
        actual_fs = arr_tone_sig.shape[1] / tone_dur
    elif final_seq_sig:
        seq_dur = SEQ_EPOCH_WIN[1] - SEQ_EPOCH_WIN[0]
        actual_fs = arr_seq_sig.shape[1] / seq_dur
    else:
        raise ValueError("Could not determine sampling rate: no valid epochs found.")

    np.savez_compressed(
        out_file,
        seq_epochs=arr_seq_sig, # Legacy name consideration? No, better be explicit.
        seq_hfa=arr_seq_hfa,
        seq_meta=final_seq_meta,

        erp_epochs=arr_tone_sig, # GLM expects 'erp_epochs' or similar.
                             # Wait, prepare_glm_data.py looks for 'erp_epochs'.
                             # But usually 'erp_epochs' implies HFA for GLM?
                             # No, prepare_glm_data loads it and does baseline correction.
                             # It loads 'erp_epochs'. Let's stick to that name for Tones.
        erp_hfa=arr_tone_hfa,
        meta=final_tone_meta,    # GLM script reads 'meta' and expects tone-level keys (pos)

        channel_names=common_chs,
        fs=actual_fs
    )
    logger.info(f"Saved {out_file}: {len(final_seq_meta)} Seqs, {len(final_tone_meta)} Tones.")


def main():
    # Identify Groups: (Condition, Subject)
    to_process = defaultdict(list)

    if not PREPROC_ROOT.exists():
        logger.error(f"Preproc root not found: {PREPROC_ROOT}")
        return

    for cond_dir in PREPROC_ROOT.iterdir():
        if not cond_dir.is_dir(): continue
        for subj_dir in cond_dir.iterdir():
            if not subj_dir.is_dir(): continue

            files = list(subj_dir.glob("*_preproc.npz"))
            if files:
                to_process[(cond_dir.name, subj_dir.name)].extend(files)

    for (cond, subj), files in to_process.items():
        logger.info(f"Processing Group: {cond}/{subj} ({len(files)} files)")

        # Load and Group by SeqVer
        ver_groups = defaultdict(list) # SeqVer -> list of (seq_list, tone_list, ch_names)

        for f in files:
            res = cut_epochs_file(f, cond, subj)
            if res:
                s_ds, t_ds, chs = res
                if not s_ds and not t_ds: continue

                # Get version from first item
                if s_ds: sver = s_ds[0]['meta']['seq_ver']
                elif t_ds: sver = 'unknown' # extraction from tone meta if needed

                ver_groups[sver].append((s_ds, t_ds, chs))

        # Merge per version
        for sver, items in ver_groups.items():
            seq_lists = [x[0] for x in items]
            tone_lists = [x[1] for x in items]
            ch_lists = [x[2] for x in items]
            merge_and_save(seq_lists, tone_lists, ch_lists, sver)

if __name__ == "__main__":
    main()
