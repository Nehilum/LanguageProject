#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze Baseline State (Plan A)
===============================

Analyzes the raw voltage in the pre-stimulus baseline window [-50ms, 0ms] 
to test for "Proactive State" effects.

Hypothesis: 
    Baseline Voltage ~ Position + MDL

Inputs:
    - derivatives/epochs/**/*.npz (Raw ERP Epochs)
    - derivatives/predictors/**/*.csv (Trial Metadata)

Outputs:
    - derivatives/baseline_state/baseline_stats.csv
    - derivatives/baseline_state/baseline_plots/*.png
"""

import os
import glob
import json
import argparse
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path

# Config
DERIVATIVES_DIR = "derivatives"
EPOCHS_ROOT = os.path.join(DERIVATIVES_DIR, "epochs")
PREDICTORS_ROOT = os.path.join(DERIVATIVES_DIR, "predictors")
OUT_DIR = os.path.join(DERIVATIVES_DIR, "baseline_state")
ROI_JSON = os.path.join(DERIVATIVES_DIR, "rois", "functional_rois.json")

# Baseline Window (Pre-Correction)
WIN_BASE = (-0.05, 0.0) 
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


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_rois():
    if not os.path.exists(ROI_JSON):
        return None
    with open(ROI_JSON, 'r') as f:
        return json.load(f)

def get_roi_indices(channel_names, roi_def, subject):
    if subject not in roi_def['subjects']:
        return []
    
    roi_chs = set()
    subj_rois = roi_def['subjects'][subject]
    
    if 'Auditory' in subj_rois:
        for k, ch_list in subj_rois['Auditory'].items():
            if isinstance(ch_list, list):
                roi_chs.update(ch_list)
    
    indices = [i for i, name in enumerate(channel_names) if name in roi_chs]
    return indices

def load_epochs(npz_path):
    data = np.load(npz_path, allow_pickle=True)
    if 'erp_epochs' not in data: return None, None, None
    return data['erp_epochs'], data['meta'], float(data.get('fs', FS))

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    # Load ROIs
    roi_data = load_rois()
    if not roi_data:
        logger.error("ROI file not found.")
        return

    # Find Conditions
    conds = [d for d in os.listdir(EPOCHS_ROOT) if os.path.isdir(os.path.join(EPOCHS_ROOT, d))]
    
    all_stats = []
    
    for cond in conds:
        # Parse Length from Condition Name (e.g. "Pairs_4", "Alternation_12")
        try:
           if '_' not in cond: continue
           cond_base, length_str = cond.rsplit('_', 1)
           length = int(length_str)
        except ValueError:
           logging.warning(f"Skipping {cond}: Could not parse length.")
           continue
           
        subjs = [d for d in os.listdir(os.path.join(EPOCHS_ROOT, cond)) if os.path.isdir(os.path.join(EPOCHS_ROOT, cond, d))]
        
        for subj in subjs:
            logger.info(f"Processing {cond}/{subj}...")
            
            # Epochs
            ep_files = glob.glob(os.path.join(EPOCHS_ROOT, cond, subj, "*.npz"))
            
            # Need predictors to get MDL?
            # Or use metadata in epochs if MDL is there?
            # 'meta' in epochs usually has 'seq_idx', 'pos'.
            # We need to map to MDL.
            # Let's load predictors first to build lookup.
            
            # Load Predictors with Session ID
            pred_files = glob.glob(os.path.join(PREDICTORS_ROOT, cond, subj, "*.csv"))
            if not pred_files:
                logger.warning(f"No predictors for {cond}/{subj} in {PREDICTORS_ROOT}")
                continue
            
            logger.info(f"Found {len(pred_files)} predictors for {cond}/{subj}")

            pred_dfs = []
            for pf in pred_files:
                # Extract Session ID
                try:
                    fname = os.path.basename(pf)
                    parts = fname.split('_')
                    # format: predictors_seqver-ver_sid.csv
                    # sid is last part
                    sid_part = parts[-1].replace(".csv", "")
                    logger.info(f"Parsed SID: {sid_part} from {fname}")
                except Exception as e:
                    logger.warning(f"Could not parse session ID from {pf}: {e}")
                    continue
                    
                tmp_df = pd.read_csv(pf)
                tmp_df['session_id'] = sid_part # Add column
                pred_dfs.append(tmp_df)
            
            if not pred_dfs: continue
            
            df_pred = pd.concat(pred_dfs, ignore_index=True)
            logger.info(f"Predictor DF size: {len(df_pred)}")

            # Load Epochs
            for ep_f in ep_files:
                epochs, meta, fs = load_epochs(ep_f)
                if epochs is None: 
                     logger.warning(f"Failed to load epochs from {ep_f}")
                     continue
                
                if len(meta) > 0:
                     logger.info(f"Epoch Meta SID example: {meta[0]['session_id']}")

                if epochs is None: continue
                
                # Check indices for baseline
                # Epoch starts at -0.2s usually.
                # 0.0s is at 0.2 * FS = 50 samples.
                # Baseline -0.05 to 0.0 is 0.15s to 0.2s relative to epoch start?
                # No. Epoch is [-0.2, 0.8].
                # -0.05 relative to 0 is at -0.05 - (-0.2) = 0.15s from start.
                # 0.15 * 250 = 37.5 -> 37 samples.
                # 0.0 relative to 0 is at 0.0 - (-0.2) = 0.2s from start.
                # 0.2 * 250 = 50 samples.
                
                b_start = int(0.15 * fs)
                b_end = int(0.20 * fs)
                
                if b_start < 0: b_start = 0
                
                # Extract Baseline Voltage
                # (N, T, Ch) -> (N, Ch)
                base_volts = np.mean(epochs[:, b_start:b_end, :], axis=1)
                
                # ROI Mask
                # Load ch_names
                d = np.load(ep_f, allow_pickle=True)
                ch_names = d['channel_names']
                roi_idx = get_roi_indices(ch_names, roi_data, subj)
                
                if not roi_idx: continue
                
                # Average ROI
                # (N,)
                roi_base = np.mean(base_volts[:, roi_idx], axis=1)
                
                # Match to Metadata
                for i, m in enumerate(meta):
                    sid = m['session_id']
                    seq_idx = int(m['seq_idx'])
                    pos = int(m['pos'])
                    ttype = m['trial_type']
                    
                    # Find in Predictors
                    # Match on trial_index (seq_idx) and pos
                    # Filter predictor df for this session
                    # Need to map session_id filename part to sid?
                    # prepare_glm_data.py logic: "predictors_seqver-<ver>_<sid>.csv"
                    # We can try to look up in loaded df_pred if it has session info.
                    # Or simpler: if we just want Position and trial_type, we have it in meta!
                    # BUT MDL is critical. MDL is in predictors.
                    
                    # Assume df_pred has 'trial_index' == seq_idx and 'pos' == pos.
                    # And 'trial_type' matches.
                    
                    match = df_pred[
                        (df_pred['trial_index'] == seq_idx) & 
                        (df_pred['pos'] == pos) &
                        (df_pred['session_id'].astype(str) == str(sid))
                    ]
                    
                    if match.empty: continue
                    
                    row = match.iloc[0]
                    mdl = row.get('mdl', 0)
                    
                    all_stats.append({
                        'Subject': subj,
                        'Condition': cond_base,
                        'Length': length,
                        'Position': pos,
                        'TrialType': ttype,
                        'MDL': mdl,
                        'Voltage': roi_base[i]
                    })
                    
    # Analysis
    if not all_stats:
        logger.warning("No data extracted.")
        return
        
    df = pd.DataFrame(all_stats)
    
    # Filter Standard/Habituation only? Or Include Deviants (proactive should be same)?
    # Usually analyze Standards.
    df = df[df['TrialType'] != 'violation']
    
    # Save Raw
    df.to_csv(os.path.join(OUT_DIR, "baseline_raw_data.csv"), index=False)
    
    # Linear Regression per Subject/Length
    # Voltage ~ Position + MDL
    reg_stats = []
    
    for subj in df['Subject'].unique():
        for length in df['Length'].unique():
            sub_df = df[(df['Subject'] == subj) & (df['Length'] == length)]
            if sub_df.empty: continue
            
            # Regression
            # Handle multiple predictors or just Position?
            # Hypothesis: "Baseline_Voltage should show a linear increase or decrease as Position increases."
            # Also "Slopes should differ between Low/High MDL".
            # MDL is constant within Length for a given Grammar... BUT we have mixed Grammars here?
            # "Condition" usually includes Grammar (Pairs_Length4).
            # So MDL is constant for a Condition!
            # We cannot regress MDL within a Condition.
            
            # We can regress Position.
            slope, intercept, r, p, se = stats.linregress(sub_df['Position'], sub_df['Voltage'])
            
            # Get MDL of this condition (Average)
            avg_mdl = sub_df['MDL'].mean()
            grammar = sub_df['Condition'].iloc[0] # Roughly
            
            reg_stats.append({
                'Subject': subj,
                'Length': length,
                'Grammar': grammar,
                'MDL': avg_mdl,
                'Pos_Slope': slope,
                'Pos_P': p,
                'Pos_R': r
            })
            
            # Plot
            plt.figure()
            sns.regplot(data=sub_df, x='Position', y='Voltage', scatter_kws={'alpha':0.1})
            plt.title(f"{subj} L{length} ({grammar}) MDL={avg_mdl:.1f}")
            plt.savefig(os.path.join(OUT_DIR, f"Reg_Pos_{subj}_{grammar}_L{length}.png"))
            plt.close()
            
    df_reg = pd.DataFrame(reg_stats)
    df_reg.to_csv(os.path.join(OUT_DIR, "baseline_regression_stats.csv"), index=False)
    logger.info("Saved baseline regression stats.")

    # Cross-Condition Plot: Slope vs MDL
    plt.figure()
    sns.scatterplot(data=df_reg, x='MDL', y='Pos_Slope', hue='Subject', style='Length', s=100)
    plt.title("Baseline Slope (Voltage/Position) vs MDL")
    plt.savefig(os.path.join(OUT_DIR, "Summary_Slope_vs_MDL.png"))
    plt.close()

if __name__ == "__main__":
    main()
