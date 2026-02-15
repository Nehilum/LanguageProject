#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run Hierarchical GLM Analysis
=============================

This script performs the two-level GLM analysis:
1. Level 1 (Channel-wise): Fit GLM for each channel and timepoint.
   Y ~ Intercept + Length_centered + Surprisal + Interaction + ToneID + Repetition + Position + Habituation
2. Level 2 (ROI Aggregation): Average betas within functional ROIs.

Inputs:
- derivatives/glm_data/glm_dataset_{type}.h5 (Data & Design Matrix)
- derivatives/rois/functional_rois.json (ROI definitions)
- derivatives/epochs/**/*.npz (For channel names)

Outputs:
- derivatives/glm_results/glm_results_{type}.h5
  Contains Betas for Channels and ROIs.
"""

import os
import glob
import json
import h5py
import numpy as np
import pandas as pd
import argparse
from pathlib import Path

# Config
ROI_JSON = "derivatives/rois/functional_rois.json"
EPOCH_ROOT = "derivatives/epochs"

def load_rois(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def get_channel_names(condition, subject):
    """Load channel names from the first available NPZ file."""
    search_pat = os.path.join(EPOCH_ROOT, condition, subject, "*.npz")
    files = glob.glob(search_pat)
    if not files: return None
    
    try:
        data = np.load(files[0], allow_pickle=True)
        if 'channel_names' in data:
            return data['channel_names']
    except Exception as e:
        print(f"Error loading channel names: {e}")
    return None

def build_design_matrix(X_df, model_type):
    """
    Construct the design matrix for GLM based on model type.
    """
    # 1. Length Centering
    l_mean = X_df['length'].mean()
    X_df['Length_c'] = X_df['length'] - l_mean
    
    # 2. Surprisal
    X_df['Surprisal'] = pd.to_numeric(X_df['surprisal'], errors='coerce').fillna(0)
    
    # 3. Interaction
    X_df['Interaction'] = X_df['Length_c'] * X_df['Surprisal']
    
    # 4. Nuisance
    X_df['ToneID'] = X_df['tone_id'].astype(float)
    X_df['Repetition'] = X_df['repetition'].astype(float)
    X_df['Position'] = X_df['pos'].astype(float)
    X_df['Position_c'] = X_df['Position'] - X_df['Position'].mean()
    X_df['IsHab'] = (X_df['trial_type'] == 'habituation').astype(float)
    
    # 5. MDL (LoT Complexity) & Deviant
    # Ensure MDL is numeric
    if 'mdl' in X_df.columns:
        X_df['MDL'] = pd.to_numeric(X_df['mdl'], errors='coerce').fillna(0)
        # Center MDL? Optional but good for intercept interpretation.
        # Prompt says "Global Complexity (LoT/MDL)".
    else:
        # Fallback if missing
        X_df['MDL'] = 0.0

    # Deviant: Is this a violation trial?
    # Note: 'violation_position' > 0 means it HAS a deviant.
    # But usually we model the *local* deviant event?
    # Prompt says "Deviant (Binary)".
    # 'trial_type' == 'violation' applies to the whole sequence.
    # The 'is_viol' flag in tone metadata tracks if THIS tone is the deviant.
    # GLM dataset `X` usually contains session/trial level metadata.
    # If X_df has a column 'is_viol' or if we need to derive it.
    # generate_predictors.py saves 'trial_type' and 'violation_position'.
    # It does NOT seem to save 'is_viol' per tone in parquet?
    # Wait, `generate_predictors.parquet` has 'pos', 'trial_type', 'violation_position'.
    # We can derive `IsDeviant`.
    
    X_df['IsDeviant'] = 0.0
    # If trial_type is violation AND pos == violation_position
    # Ensure types match.
    # violation_position might be 0 for standard.
    is_viol_trial = (X_df['trial_type'] == 'violation')
    is_at_viol_pos = (X_df['pos'] == X_df['violation_position'])
    X_df.loc[is_viol_trial & is_at_viol_pos, 'IsDeviant'] = 1.0

    # Intercept
    X_df['Intercept'] = 1.0
    
    # Select Predictors based on Model
    if model_type == 'ModelA':
        # Sensory Baseline: Intercept, Trial Stage, Tone Identity, Repetition
        predictors = ['Intercept', 'IsHab', 'ToneID', 'Repetition']
    elif model_type == 'ModelB':
        # Cognitive Core: Length, Surprisal, Interaction, Item Position
        # + Controls from A? Assuming cumulative for valid GLM control.
        # But Prompt Table listed specific sets.
        # "Isolate cognitive effects" -> usually means testing B over A.
        # I will include controls to avoid adaptation confounds as requested in "Implementation Constraints".
        # "Control for Adaptation: Ensure Item Position is regressed out".
        predictors = ['Intercept', 'IsHab', 'ToneID', 'Repetition', 'Position_c', 'Length_c', 'Surprisal', 'Interaction']
    elif model_type == 'ModelC':
        # Structural Logic: Deviant, Global Complexity (MDL).
        # Should also include controls.
        predictors = ['Intercept', 'IsHab', 'ToneID', 'Repetition', 'Position_c', 'IsDeviant', 'MDL']
    elif model_type == 'ModelD':
        # Competition: MDL + Surprisal
        # y ~ Intercept + ToneID + IsHab + Repetition + Position_c + Length_c + Surprisal + MDL
        predictors = ['Intercept', 'IsHab', 'ToneID', 'Repetition', 'Position_c', 'Length_c', 'Surprisal', 'MDL']
    else:
        raise ValueError(f"Unknown model: {model_type}")

    # Check for NaNs
    X_mat = X_df[predictors].values
    if np.isnan(X_mat).any():
        print(f"Warning: NaNs in design matrix for {model_type}. Filling with 0.")
        X_mat = np.nan_to_num(X_mat)
        
    return X_mat, predictors

def fit_glm(X, Y):
    """
    Fit OLS: Y = X * Beta + E
    Y: (N_trials, N_channels, N_time)
    X: (N_trials, N_preds)
    
    Returns: Betas (N_preds, N_channels, N_time)
    """
    n_trials, n_ch, n_time = Y.shape
    n_preds = X.shape[1]
    
    # Reshape Y to (N_trials, N_features) where N_features = N_ch * N_time
    Y_reshaped = Y.reshape(n_trials, -1)
    
    # OLS: Beta = (X^T X)^-1 X^T Y
    # Use pseudo-inverse for stability
    # B = pinv(X) @ Y
    X_pinv = np.linalg.pinv(X)
    
    Betas_flat = X_pinv @ Y_reshaped # (N_preds, N_ch * N_time)
    
    # --- Compute Stats (T-values) ---
    # Residuals: E = Y - X * Beta
    Y_pred = X @ Betas_flat
    Residuals = Y_reshaped - Y_pred
    
    # Degree of Freedom
    df = n_trials - n_preds
    
    # Mean Squared Error: RSS / df
    RSS = np.sum(Residuals**2, axis=0) # (N_features,)
    MSE = RSS / df
    
    # Standard Error of Betas
    # Var(Beta) = MSE * diag((X^T X)^-1)
    # Be careful with dimensions here.
    # XT_X_inv = (X^T X)^-1
    # Use pinv for stability if X is rank deficient
    XT_X_inv = np.linalg.pinv(X.T @ X)
    diag_XT_X_inv = np.diag(XT_X_inv) # (N_preds,)
    
    # SE_beta = sqrt(MSE * diag_XT_X_inv) -> (N_preds, N_features)
    # We broaden dimensions for broadcasting
    SE_beta = np.sqrt(np.outer(diag_XT_X_inv, MSE))
    
    # T-stats = Beta / SE
    T_stats_flat = Betas_flat / SE_beta
    
    # Reshape back
    Betas = Betas_flat.reshape(n_preds, n_ch, n_time)
    T_stats = T_stats_flat.reshape(n_preds, n_ch, n_time)
    
    return Betas, T_stats

def main():
    parser = argparse.ArgumentParser(description="Run GLM Hierarchical Analysis")
    parser.add_argument("--data_type", type=str, default="erp", choices=['erp', 'hfa'], help="Data type to process (erp or hfa)")
    parser.add_argument("--baseline_mode", type=str, default="local", choices=['local', 'global'], help="Baseline strategy (local or global)")
    args = parser.parse_args()
    
    suffix = "_baselocal" if args.baseline_mode == 'local' else "_baseglobal"
    
    glm_data_file = f"derivatives/glm_data/glm_dataset_{args.data_type}{suffix}.h5"
    out_file = f"derivatives/glm_results/glm_results_{args.data_type}{suffix}.h5"
    
    if not os.path.exists(glm_data_file):
        print(f"GLM data missing: {glm_data_file}")
        return

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    
    print(f"Running GLM for: {args.data_type.upper()} ({args.baseline_mode.upper()} Baseline)")
    print(f"Input: {glm_data_file}")
    print(f"Output: {out_file}")
    
    try:
        roi_data = load_rois(ROI_JSON)
    except Exception as e:
        print(f"Error loading ROIs: {e}")
        return

    # Group files by Subject
    # Structure in HDF5: /Condition/Subject/
    # We want to iterate Subjects, and for each Subject, gather ALL Conditions.
    
    # 1. Scan HDF5 for Subjects
    subjects = set()
    with h5py.File(glm_data_file, 'r') as hf_in:
        for cond in hf_in.keys():
            if isinstance(hf_in[cond], h5py.Group):
                for subj in hf_in[cond].keys():
                    subjects.add(subj)
    
    print(f"Found subjects: {list(subjects)}")

    # MODELS TO RUN
    MODELS = ['ModelA', 'ModelB', 'ModelC', 'ModelD']

    for model in MODELS:
        print(f"\n=== Running {model} ===")
        out_file_model = out_file.replace('.h5', f'_{model}.h5')
        
        with h5py.File(out_file_model, 'w') as hf_out:
            
            with h5py.File(glm_data_file, 'r') as hf_in:
                for subj in subjects:
                    print(f"Analyzing Subject: {subj} (All Conditions)...")
                    
                    # Gather Data for this Subject
                    Y_list = []
                    X_df_list = []
                    
                    # Check all conditions for this subject
                    for cond in hf_in.keys():
                        if subj in hf_in[cond]:
                            grp = hf_in[f"{cond}/{subj}"]
                            
                            # Load Y
                            if "Y" not in grp: continue
                            Y_part = grp["Y"][:] # (N, Ch, Time)
                            Y_list.append(Y_part)
                            
                            # Load X
                            if "X" not in grp: continue
                            x_grp = grp["X"]
                            cols = list(grp.attrs["columns"])
                            
                            data_dict = {}
                            for col in cols:
                                ds = x_grp[col][:]
                                if ds.dtype.kind == 'S' or ds.dtype.kind == 'O':
                                    data_dict[col] = [x.decode('utf-8') if isinstance(x, bytes) else str(x) for x in ds]
                                else:
                                    data_dict[col] = ds
                            
                            X_part = pd.DataFrame(data_dict)
                            # Add Condition/Session info if needed? 
                            # X_part['Condition'] = cond
                            X_df_list.append(X_part)
                            
                    if not Y_list:
                        print(f"  No data for {subj}")
                        continue
                        
                    # Concatenate
                    Y_all = np.concatenate(Y_list, axis=0)
                    X_df_all = pd.concat(X_df_list, axis=0, ignore_index=True)
                    
                    print(f"  Total Data: {len(X_df_all)} epochs")
                    
                    # Build Design Matrix (Now Length/MDL vary!)
                    X_mat, pred_names = build_design_matrix(X_df_all, model)
                    
                    # Check rank?
                    # fit_glm uses pinv so it's safe, but check collinearity manually if desired.
                    
                    # Fit GLM
                    print(f"  Fitting GLM...")
                    betas, t_stats = fit_glm(X_mat, Y_all)
                    
                    # Save (Under Subject directly? Or imply 'AllConditions')
                    # User expects /Condition/Subject? No, level 1 is usually Subject level if concatenated.
                    # Prompt says "Analysis that better align with our experimental design...".
                    # Prompt says "Run the GLM independently for each channel."
                    # It implies ONE GLM per Subject.
                    # Output: derivatives/glm_results/glm_results.h5 -> /Subject/ChannelBetas
                    
                    out_grp = hf_out.create_group(f"{subj}")
                    out_grp.create_dataset("ChannelBetas", data=betas, compression="gzip")
                    out_grp.create_dataset("ChannelTstats", data=t_stats, compression="gzip")
                    out_grp.attrs["predictors"] = pred_names
                    
                    # Get Channel Names (Limit: must be consistent across sessions)
                    # We assume same subject = same channels.
                    # Pick from first available condition
                    # get_channel_names needs condition.
                    # We can pick any condition in hf_in that has this subject.
                    sample_cond = [c for c in hf_in.keys() if subj in hf_in[c]][0]
                    ch_names = get_channel_names(sample_cond, subj)
                    
                    if ch_names is not None:
                        out_grp.attrs["channel_names"] = [str(c) for c in ch_names]
                        
                        # Level 2 (ROI)
                        if subj in roi_data['subjects']:
                            subj_rois = roi_data['subjects'][subj]
                            targets = {'Auditory': ['Auditory'], 'S1': ['S1_Sensory'], 'M1': ['M1_Motor']}
                            roi_betas = []
                            roi_tstats = []
                            roi_names_list = []
                            
                            for roi_label, roi_keys in targets.items():
                                roi_chs = set()
                                for k in roi_keys:
                                    if k in subj_rois:
                                        for sub_k, ch_list in subj_rois[k].items():
                                            if isinstance(ch_list, list): roi_chs.update(ch_list)
                                
                                indices = [i for i, name in enumerate(ch_names) if name in roi_chs]
                                
                                if indices:
                                    # Fix: Pool signal before GLM to avoid averaging T-statistics
                                    # HFA: Mean signal, ERP: RMS signal
                                    roi_y_raw = Y_all[:, indices, :] # (N_trials, N_roi_chs, N_time)
                                    
                                    if args.data_type == 'hfa':
                                        roi_y_pooled = np.mean(roi_y_raw, axis=1, keepdims=True)
                                    else: # erp
                                        # Root Mean Square (RMS) across channels
                                        roi_y_pooled = np.sqrt(np.mean(roi_y_raw**2, axis=1, keepdims=True))
                                    
                                    # Fit GLM on pooled signal: returns (N_preds, 1, N_time)
                                    roi_b_res, roi_t_res = fit_glm(X_mat, roi_y_pooled)
                                    
                                    roi_betas.append(roi_b_res[:, 0, :])
                                    roi_tstats.append(roi_t_res[:, 0, :])
                                    roi_names_list.append(roi_label)
                                else:
                                    # Pad with zeros if ROI has no channels
                                    n_preds = betas.shape[0]
                                    n_time = betas.shape[2]
                                    roi_betas.append(np.zeros((n_preds, n_time)))
                                    roi_tstats.append(np.zeros((n_preds, n_time)))
                                    roi_names_list.append(roi_label)
                                    
                            if roi_betas:
                                roi_betas_arr = np.stack(roi_betas, axis=0)
                                roi_tstats_arr = np.stack(roi_tstats, axis=0)
                                out_grp.create_dataset("ROIBetas", data=roi_betas_arr, compression="gzip")
                                out_grp.create_dataset("ROITstats", data=roi_tstats_arr, compression="gzip")
                                out_grp.attrs["roi_names"] = roi_names_list
                                print(f"  Saved ROI stats for {roi_names_list}")
        print(f"Saved {out_file_model}")

if __name__ == "__main__":
    main()
