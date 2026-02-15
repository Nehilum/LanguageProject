#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prepare GLM Data
================

This script loads the pre-generated predictors (CSV) and the pre-processed tone epochs (NPZ).
It matches them by Session, Trial, and Tone Position.
It applies a baseline correction (Local or Global) and saves the resulting matrices (X, Y) for GLM analysis.

Inputs:
- derivatives/epochs/**/*.npz (Tone & Sequence Epochs)
- derivatives/predictors/**/*.csv (Predictors)

Outputs:
- derivatives/glm_data/glm_dataset_{type}_{baseline_mode}.h5
  Contains groups: /Condition/Subject/X (Design Matrix), /Condition/Subject/Y (Data)
"""

import os
import glob
import numpy as np
import pandas as pd
import h5py
import argparse
from pathlib import Path

# Configuration
EPOCHS_ROOT = "derivatives/epochs"
PREDICTORS_ROOT = "derivatives/predictors"

# Baseline Params — FS is read dynamically from epoch files
DEFAULT_FS = None
BASELINE_SAMPLES = 12 # First 12 samples (~48ms) as baseline

def load_epochs(npz_path, data_type='erp'):
    """Load epochs and metadata from NPZ."""
    data = np.load(npz_path, allow_pickle=True)
    
    epochs = None
    seq_epochs = None # For Global Baseline
    seq_meta = None
    
    if data_type == 'erp':
        if 'erp_epochs' in data:
            epochs = data['erp_epochs']
            # print(f"Loaded 'erp_epochs' (LFP) from {npz_path}")
        elif 'erp_hfa' in data:
             print(f"Warning: {npz_path} missing 'erp_epochs', but found 'erp_hfa'. Skipping for ERP analysis.")
             return None, None, None, None, None
    elif data_type == 'hfa':
        if 'erp_hfa' in data:
            epochs = data['erp_hfa']
            # print(f"Loaded 'erp_hfa' (High-Gamma) from {npz_path}")
        else:
             print(f"Warning: {npz_path} missing 'erp_hfa'. Skipping for HFA analysis.")
             return None, None, None, None, None
    else:
        raise ValueError(f"Unknown data type: {data_type}")

    # Load Sequence Data for Global Baseline
    if 'seq_epochs' in data and 'seq_meta' in data:
        # Check if seq_epochs type matches request
        # data['seq_epochs'] is usually LFP.
        # data['seq_hfa'] is HFA.
        if data_type == 'erp':
             seq_epochs = data['seq_epochs']
        else:
             seq_epochs = data['seq_hfa']
        seq_meta = data['seq_meta']
    
    if epochs is None:
        return None, None, None, None, None
        
    meta = data['meta']
    if meta.shape == (): meta = meta.item()
    
    # Try to load FS if available
    fs = float(data['fs']) if 'fs' in data else FS
    
    return epochs, meta, fs, seq_epochs, seq_meta

def process_session(condition, subject, seqver_files, data_type, baseline_mode):
    """
    Process all epoch files for a Condition/Subject.
    
    For each epoch file:
      1. Load epochs (tone-level and sequence-level).
      2. Load matching predictor file(s) (parquet or CSV).
      3. Match predictor rows to epoch data via (trial_index, pos) ↔ (seq_idx, pos).
      4. Apply baseline correction (local or global).
    
    Returns:
      X_df (pd.DataFrame): Predictors for all matched epochs.
      Y_arr (np.ndarray): Neural data (N_epochs, N_channels, N_time).
      channel_names (list): Channel name strings.
      fs (float): Sampling rate in Hz.
    """
    X_list = []
    Y_list = []
    
    # Detect FS from first epoch file
    first_data = np.load(seqver_files[0], allow_pickle=True)
    if 'fs' not in first_data:
        raise RuntimeError(f"Missing 'fs' in first epoch file: {seqver_files[0]}")
    fs = float(first_data['fs'])
    print(f"  Detected FS = {fs} Hz from epoch files")
    
    # Extract channel names from first epoch file
    if 'channel_names' in first_data:
        channel_names = list(first_data['channel_names'])
        print(f"  Extracted {len(channel_names)} channel names")
    else:
        print(f"  Warning: No 'channel_names' found in epoch file")
        channel_names = None

    # Local Baseline Parameters
    # Epoch is [-0.2, 0.8]. We want [-0.05, 0.0].
    t_start = -0.2
    base_win_local = (-0.05, 0.0)
    
    b_idx_0_loc = int((base_win_local[0] - t_start) * fs)
    b_idx_1_loc = int((base_win_local[1] - t_start) * fs)
    
    # Global Baseline Parameters (Sequence Level)
    # Sequence Epoch is [-0.5, ...].
    # Baseline [-0.2, 0.0] relative to seq onset.
    base_win_global = (-0.2, 0.0)
    # Indices: -0.2s is 0.3s after start → 0.3 * fs
    #          0.0s is 0.5s after start → 0.5 * fs
    b_idx_0_glob = int(0.3 * fs)
    b_idx_1_glob = int(0.5 * fs)

    # --- Load ALL predictor files for this Condition/Subject ---
    pred_dir = os.path.join(PREDICTORS_ROOT, condition, subject)
    pred_parquet = glob.glob(os.path.join(pred_dir, "*.parquet"))
    pred_csv = glob.glob(os.path.join(pred_dir, "*.csv"))
    
    all_pred_dfs = []
    for pf in pred_parquet:
        try:
            all_pred_dfs.append(pd.read_parquet(pf))
        except Exception:
            pass
    for pf in pred_csv:
        try:
            all_pred_dfs.append(pd.read_csv(pf))
        except Exception:
            pass
    
    if not all_pred_dfs:
        print(f"  No predictor files found in {pred_dir}")
        return None, None, None, DEFAULT_FS
    
    pred_df_all = pd.concat(all_pred_dfs, ignore_index=True)
    print(f"  Loaded {len(pred_df_all)} predictor rows from {len(all_pred_dfs)} file(s)")

    # --- Loop over epoch files ---
    for ep_path in seqver_files:
        # Load epochs
        epochs, meta, fs_ep, seq_epochs, seq_meta = load_epochs(ep_path, data_type)
        if epochs is None:
            continue

        # --- DYNAMIC DIMENSION IDENTIFICATION (TONE) ---
        # Use metadata to determine expected sample count for tones
        t_range_tone = meta[0].get('epoch_time_range', (-0.2, 0.8))
        expected_tone_samples = int(round((t_range_tone[1] - t_range_tone[0]) * fs))

        # --- Determine session ID from metadata ---
        # Session ID is used to filter predictors and sequence baselines.
        # In generate_predictors.py, session_id = row index in events TSV.
        # Each NPZ file groups epochs by seqver across sessions, so we use
        # all metadata entries in the file.
        sid = str(meta[0].get('session_id', ''))
        
        # --- Filter predictors for this epoch file ---
        # Match by seqver (sequence version) since epoch files are per-seqver
        ep_basename = os.path.basename(ep_path)
        # Extract seqver from filename like "seqver-low-high_epochs.npz"
        seqver_tag = ep_basename.replace('_epochs.npz', '')  # e.g., "seqver-low-high"
        
        if 'seqver' in pred_df_all.columns:
            # Extract the version part from tag for matching
            sv_value = seqver_tag.replace('seqver-', '')
            pred_df = pred_df_all[pred_df_all['seqver'].astype(str) == sv_value].copy()
        else:
            pred_df = pred_df_all.copy()
        
        if pred_df.empty:
            print(f"  Warning: No matching predictors for {ep_basename}")
            continue
        
        print(f"  Processing {ep_basename}: {len(epochs)} epochs, {len(pred_df)} predictor rows")
        
        # All metadata indices for this file
        sess_indices = list(range(len(meta)))

        # Prepare Global Baseline map if needed
        seq_baseline_map = {}  # seq_idx -> baseline_vector (channels)
        if baseline_mode == 'global' and seq_epochs is not None:
            # --- DYNAMIC DIMENSION IDENTIFICATION (SEQUENCE) ---
            t_range_seq = seq_meta[0].get('epoch_time_range', (-0.5, 4.5))
            expected_seq_samples = int(round((t_range_seq[1] - t_range_seq[0]) * fs))

            # Map Sequence Epochs
            for idx_s in range(len(seq_meta)):
                s_data = seq_epochs[idx_s] 
                
                # Robust Transpose for Sequence Data
                if s_data.shape[0] == expected_seq_samples:
                    # (Time, Ch)
                    s_data_tc = s_data
                elif s_data.shape[1] == expected_seq_samples:
                    # (Ch, Time) -> Transpose to (Time, Ch) for slicing logic below
                    s_data_tc = s_data.T
                else:
                    print(f"Warning: Ambiguous sequence data shape {s_data.shape} for expected {expected_seq_samples} samples. Assuming (Time, Ch).")
                    s_data_tc = s_data

                if s_data_tc.shape[0] > b_idx_1_glob:
                    bl_vec = np.mean(s_data_tc[b_idx_0_glob:b_idx_1_glob, :], axis=0)  # (Ch,)
                    # Store by seq_idx
                    s_idx_val = int(seq_meta[idx_s]['seq_idx'])
                    seq_baseline_map[s_idx_val] = bl_vec
        
        # Lookup: (seq_idx, pos) -> epoch_idx
        lookup = {}
        for idx in sess_indices:
            m = meta[idx]
            key = (int(m['seq_idx']), int(m['pos']))
            lookup[key] = idx
        
        # Iterate through Predictor Rows
        for _, row in pred_df.iterrows():
            t_idx = int(row['trial_index'])
            pos = int(row['pos'])
            
            if (t_idx, pos) in lookup:
                ep_idx = lookup[(t_idx, pos)]
                raw_data = epochs[ep_idx] 
                
                # --- ROBUST TRANSPOSE (TONE) ---
                if raw_data.shape[0] == expected_tone_samples:
                    # (Time, Ch) → transpose to (Ch, Time) for legacy GLM logic
                    data_ch_time = raw_data.T
                elif raw_data.shape[1] == expected_tone_samples:
                    # Already (Ch, Time)
                    data_ch_time = raw_data
                else:
                    # Fallback for ambiguous or malformed data
                    if raw_data.shape[0] > raw_data.shape[1]:
                        data_ch_time = raw_data.T
                    else:
                        data_ch_time = raw_data
                    print(f"Warning: Ambiguous tone data shape {raw_data.shape} for expected {expected_tone_samples} samples. Fallback heuristic used.")
                
                # --- BASELINE CORRECTION ---
                if baseline_mode == 'local':
                    # Standard [-50ms, 0ms] relative to tone
                    bl_data = data_ch_time[:, b_idx_0_loc:b_idx_1_loc]
                    if bl_data.shape[1] == 0:
                         bl = data_ch_time[:, :5].mean(axis=1, keepdims=True)
                    else:
                         bl = bl_data.mean(axis=1, keepdims=True)
                    
                    data_bc = data_ch_time - bl
                    
                elif baseline_mode == 'global':
                    # Sequence Baseline [-200ms, 0ms] relative to sequence onset
                    if t_idx in seq_baseline_map:
                        bl_vec = seq_baseline_map[t_idx]  # (Ch,)
                        bl_vec = bl_vec[:, np.newaxis]  # (Ch, 1)
                        data_bc = data_ch_time - bl_vec
                    else:
                        # Fallback: use local baseline with warning
                        bl_data = data_ch_time[:, b_idx_0_loc:b_idx_1_loc]
                        bl = bl_data.mean(axis=1, keepdims=True)
                        data_bc = data_ch_time - bl
                
                else:
                    raise ValueError(f"Unknown baseline mode: {baseline_mode}")
                
                Y_list.append(data_bc)  # (Channels, Time)
                X_list.append(row.to_dict())  # Predictors
    
    if not X_list:
        return None, None, None, DEFAULT_FS
        
    return pd.DataFrame(X_list), np.array(Y_list), channel_names, fs


def main():
    parser = argparse.ArgumentParser(description="Prepare GLM Data")
    parser.add_argument("--data_type", type=str, default="erp", choices=['erp', 'hfa'], help="Data type to process (erp or hfa)")
    parser.add_argument("--baseline_mode", type=str, default="local", choices=['local', 'global'], help="Baseline strategy (local or global)")
    args = parser.parse_args()

    # Define suffix based on mode
    suffix = "_baselocal" if args.baseline_mode == 'local' else "_baseglobal"
    
    out_file = f"derivatives/glm_data/glm_dataset_{args.data_type}{suffix}.h5"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    
    print(f"Preparing GLM Dataset for: {args.data_type.upper()} ({args.baseline_mode.upper()} Baseline)")
    print(f"Output: {out_file}")
    
    # Open HDF5
    with h5py.File(out_file, 'w') as hf:
        hf.attrs['fs'] = 0.0  # placeholder, updated per-group
        
        conds = [d for d in os.listdir(PREDICTORS_ROOT) if os.path.isdir(os.path.join(PREDICTORS_ROOT, d))]
        
        for cond in conds:
            subjs = [d for d in os.listdir(os.path.join(PREDICTORS_ROOT, cond)) if os.path.isdir(os.path.join(PREDICTORS_ROOT, cond, d))]
            
            for subj in subjs:
                print(f"Processing {cond}/{subj}...")
                
                ep_dir = os.path.join(EPOCHS_ROOT, cond, subj)
                if not os.path.exists(ep_dir):
                    print(f"No epoch dir for {cond}/{subj}")
                    continue
                    
                ep_files = glob.glob(os.path.join(ep_dir, "*.npz"))
                
                # Process
                X_df, Y_arr, ch_names, detected_fs = process_session(cond, subj, ep_files, args.data_type, args.baseline_mode)
                
                if X_df is not None:
                    # Store FS as root attribute
                    if hf.attrs['fs'] == 0.0:
                        hf.attrs['fs'] = detected_fs
                        print(f"  Stored FS = {detected_fs} Hz in HDF5")
                    grp = hf.create_group(f"{cond}/{subj}")
                    grp.create_dataset("Y", data=Y_arr, compression="gzip")
                    grp.attrs["columns"] = list(X_df.columns)
                    
                    # Store channel names if available
                    if ch_names is not None:
                        dt = h5py.special_dtype(vlen=str)
                        ch_dset = grp.create_dataset("channel_names", (len(ch_names),), dtype=dt)
                        ch_dset[:] = ch_names
                        print(f"  Stored {len(ch_names)} channel names")
                    
                    x_grp = grp.create_group("X")
                    for col in X_df.columns:
                        vals = X_df[col].values
                        if vals.dtype == object:
                            dt = h5py.special_dtype(vlen=str)
                            dset = x_grp.create_dataset(col, (len(vals),), dtype=dt, compression="gzip")
                            dset[:] = vals.astype(str)
                        else:
                            x_grp.create_dataset(col, data=vals, compression="gzip")
                            
                    print(f"Saved {len(X_df)} epochs.")
                else:
                    print(f"No data matched for {cond}/{subj}")

if __name__ == "__main__":
    main()
