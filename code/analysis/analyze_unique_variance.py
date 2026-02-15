#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze Unique Variance (Delta R^2)
==================================

Computes the unique variance explained by MDL and Surprisal at each time point.
Delta R^2 = R^2_full - R^2_reduced

Full Model: Neural ~ Intercept + IsHab + ToneID + Repetition + Position_c + Surprisal + MDL
Reduced MDL: Neural ~ Intercept + IsHab + ToneID + Repetition + Position_c + Surprisal
Reduced Surprisal: Neural ~ Intercept + IsHab + ToneID + Repetition + Position_c + MDL

Output: derivatives/analysis/unique_variance/unique_variance_{type}_{base}.h5
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
# N_PERM will be set via argparse, default to 200

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

def build_design_matrix(X_df):
    """
    Construct the full design matrix and return subsets for reduced models.
    """
    # 1. Length Centering
    l_mean = X_df['length'].mean()
    X_df['Length_c'] = X_df['length'] - l_mean
    
    # 2. Surprisal
    X_df['Surprisal'] = pd.to_numeric(X_df['surprisal'], errors='coerce').fillna(0)
    
    # 3. Nuisance
    X_df['ToneID'] = X_df['tone_id'].astype(float)
    X_df['Repetition'] = X_df['repetition'].astype(float)
    X_df['Position'] = X_df['pos'].astype(float)
    X_df['Position_c'] = X_df['Position'] - X_df['Position'].mean()
    X_df['IsHab'] = (X_df['trial_type'] == 'habituation').astype(float)
    
    # MDL
    if 'mdl' in X_df.columns:
        X_df['MDL'] = pd.to_numeric(X_df['mdl'], errors='coerce').fillna(0)
    else:
        X_df['MDL'] = 0.0

    # Intercept
    X_df['Intercept'] = 1.0
    
    # Base predictors (nuisance + position)
    base_preds = ['Intercept', 'IsHab', 'ToneID', 'Repetition', 'Position_c']
    
    full_preds = base_preds + ['Surprisal', 'MDL']
    red_mdl_preds = base_preds + ['Surprisal']
    red_surp_preds = base_preds + ['MDL']
    
    return X_df, full_preds, red_mdl_preds, red_surp_preds

def compute_r2(X, Y):
    """
    Compute R^2 for each channel and time point.
    Y: (N_trials, N_channels, N_time)
    X: (N_trials, N_preds)
    Returns: R2 (N_channels, N_time), condition_number
    """
    n_trials, n_ch, n_time = Y.shape
    n_preds = X.shape[1]
    
    # Check collinearity via condition number
    cond_num = np.linalg.cond(X)
    
    # OLS
    X_pinv = np.linalg.pinv(X) # (N_preds, N_trials)
    
    R2 = np.zeros((n_ch, n_time))
    
    for ch in range(n_ch):
        # Y_ch: (N_trials, N_time)
        Y_ch = Y[:, ch, :]
        
        # Betas: (N_preds, N_time)
        Betas = X_pinv @ Y_ch
        
        # Residuals: (N_trials, N_time)
        Y_pred = X @ Betas
        RSS = np.sum((Y_ch - Y_pred)**2, axis=0) # (N_time,)
        
        # Total Sum of Squares
        Y_mean = np.mean(Y_ch, axis=0)
        TSS = np.sum((Y_ch - Y_mean)**2, axis=0) # (N_time,)
        
        R2[ch, :] = 1 - RSS / (TSS + 1e-10)
        
    return R2, cond_num

def main():
    parser = argparse.ArgumentParser(description="Analyze Unique Variance (Delta R^2)")
    parser.add_argument("--data_type", type=str, default="erp", choices=['erp', 'hfa'])
    parser.add_argument("--baseline_mode", type=str, default="local", choices=['local', 'global'])
    parser.add_argument("--n_perm", type=int, default=200, help="Number of permutations (0 to skip)")
    args = parser.parse_args()
    
    n_perm = args.n_perm
    suffix = "_baselocal" if args.baseline_mode == 'local' else "_baseglobal"
    glm_data_file = f"derivatives/glm_data/glm_dataset_{args.data_type}{suffix}.h5"
    out_dir = "derivatives/analysis/unique_variance"
    os.makedirs(out_dir, exist_ok=True)
    out_file = f"{out_dir}/unique_variance_{args.data_type}{suffix}.h5"
    diagnostics_file = f"{out_dir}/collinearity_diagnostics_{args.data_type}{suffix}.csv"
    
    if not os.path.exists(glm_data_file):
        print(f"GLM data missing: {glm_data_file}")
        return

    print(f"Loading data from {glm_data_file}")
    roi_data = load_rois(ROI_JSON)
    
    subjects = set()
    with h5py.File(glm_data_file, 'r') as hf_in:
        for cond in hf_in.keys():
            if isinstance(hf_in[cond], h5py.Group):
                for subj in hf_in[cond].keys():
                    subjects.add(subj)
    
    # Track collinearity diagnostics
    diagnostics_rows = []
    
    with h5py.File(out_file, 'w') as hf_out:
        with h5py.File(glm_data_file, 'r') as hf_in:
            for subj in subjects:
                print(f"Processing Subject: {subj}")
                
                # Gather Data
                Y_list = []
                X_df_list = []
                for cond in hf_in.keys():
                    if subj in hf_in[cond]:
                        grp = hf_in[f"{cond}/{subj}"]
                        if "Y" not in grp: continue
                        Y_list.append(grp["Y"][:])
                        
                        cols = list(grp.attrs["columns"])
                        data_dict = {}
                        for col in cols:
                            ds = grp["X"][col][:]
                            if ds.dtype.kind in ['S', 'O']:
                                data_dict[col] = [x.decode('utf-8') if isinstance(x, bytes) else str(x) for x in ds]
                            else:
                                data_dict[col] = ds
                        X_df_list.append(pd.DataFrame(data_dict))
                
                if not Y_list: continue
                
                Y_all = np.concatenate(Y_list, axis=0) # (N, Ch, Time)
                X_df_all = pd.concat(X_df_list, axis=0, ignore_index=True)
                
                # Build matrices
                X_df_all, full_p, red_mdl_p, red_surp_p = build_design_matrix(X_df_all)
                
                X_full = X_df_all[full_p].values
                X_red_mdl = X_df_all[red_mdl_p].values
                X_red_surp = X_df_all[red_surp_p].values
                
                print("  Computing R2 for Full Model...")
                r2_full, cond_full = compute_r2(X_full, Y_all)
                
                print("  Computing R2 for Reduced MDL...")
                r2_red_mdl, cond_red_mdl = compute_r2(X_red_mdl, Y_all)
                
                print("  Computing R2 for Reduced Surprisal...")
                r2_red_surp, cond_red_surp = compute_r2(X_red_surp, Y_all)
                
                # Check for high collinearity (condition number > 30 is concerning)
                high_collinearity = cond_full > 30
                if high_collinearity:
                    print(f"  WARNING: High collinearity detected! Condition number = {cond_full:.1f}")
                    print(f"           Results may be unreliable. Consider regularization or predictor orthogonalization.")
                
                # Record diagnostics
                diagnostics_rows.append({
                    'Subject': subj,
                    'DataType': args.data_type,
                    'BaselineMode': args.baseline_mode,
                    'CondNum_Full': cond_full,
                    'CondNum_ReducedMDL': cond_red_mdl,
                    'CondNum_ReducedSurprisal': cond_red_surp,
                    'HighCollinearity_Warning': high_collinearity,
                    'N_Trials': len(X_df_all)
                })
                
                delta_r2_mdl = r2_full - r2_red_mdl
                delta_r2_surp = r2_full - r2_red_surp
                
                # Save Channel-wise results
                subj_grp = hf_out.create_group(subj)
                subj_grp.create_dataset("Channel_DeltaR2_MDL", data=delta_r2_mdl, compression="gzip")
                subj_grp.create_dataset("Channel_DeltaR2_Surp", data=delta_r2_surp, compression="gzip")
                
                # Save collinearity diagnostics as attributes
                subj_grp.attrs['condition_number_full'] = cond_full
                subj_grp.attrs['condition_number_reduced_mdl'] = cond_red_mdl
                subj_grp.attrs['condition_number_reduced_surprisal'] = cond_red_surp
                subj_grp.attrs['high_collinearity_warning'] = high_collinearity
                
                # ROI Aggregation
                sample_cond = [c for c in hf_in.keys() if subj in hf_in[c]][0]
                ch_names = get_channel_names(sample_cond, subj)
                
                if ch_names is not None and subj in roi_data['subjects']:
                    subj_rois = roi_data['subjects'][subj]
                    targets = {'Auditory': ['Auditory'], 'S1': ['S1_Sensory'], 'M1': ['M1_Motor']}
                    
                    roi_mdl_list = []
                    roi_surp_list = []
                    roi_names_list = []
                    
                    for label, keys in targets.items():
                        roi_chs = set()
                        for k in keys:
                            if k in subj_rois:
                                for sub_k, ch_list in subj_rois[k].items():
                                    if isinstance(ch_list, list): roi_chs.update(ch_list)
                        
                        indices = [i for i, name in enumerate(ch_names) if name in roi_chs]
                        if indices:
                            roi_mdl_list.append(np.mean(delta_r2_mdl[indices, :], axis=0))
                            roi_surp_list.append(np.mean(delta_r2_surp[indices, :], axis=0))
                            roi_names_list.append(label)
                        else:
                            roi_mdl_list.append(np.zeros(delta_r2_mdl.shape[1]))
                            roi_surp_list.append(np.zeros(delta_r2_surp.shape[1]))
                            roi_names_list.append(label)
                    
                    subj_grp.create_dataset("ROI_DeltaR2_MDL", data=np.stack(roi_mdl_list), compression="gzip")
                    subj_grp.create_dataset("ROI_DeltaR2_Surp", data=np.stack(roi_surp_list), compression="gzip")
                    subj_grp.attrs["roi_names"] = roi_names_list
                    print(f"  Saved ROI stats: {roi_names_list}")
                    
                    # --- Permutation Test for ROI-averaged ΔR² ---
                    if n_perm > 0:
                        print(f"  Running {n_perm} permutations for ROI ΔR² significance...")
                        
                        obs_roi_mdl = np.stack(roi_mdl_list)  # (N_ROI, N_time)
                        obs_roi_surp = np.stack(roi_surp_list)
                        
                        perm_roi_mdl = np.zeros((n_perm, len(roi_names_list), obs_roi_mdl.shape[1]))
                        perm_roi_surp = np.zeros_like(perm_roi_mdl)
                        
                        for p_iter in range(n_perm):
                            # Shuffle MDL column
                            X_perm = X_full.copy()
                            mdl_col_idx = full_p.index('MDL')
                            X_perm[:, mdl_col_idx] = np.random.permutation(X_perm[:, mdl_col_idx])
                            
                            # Shuffle Surprisal column
                            X_perm_surp = X_full.copy()
                            surp_col_idx = full_p.index('Surprisal')
                            X_perm_surp[:, surp_col_idx] = np.random.permutation(X_perm_surp[:, surp_col_idx])
                            
                            # Recompute R² with permuted full model
                            r2_perm_full_mdl, _ = compute_r2(X_perm, Y_all)
                            delta_perm_mdl = r2_perm_full_mdl - r2_red_mdl
                            
                            r2_perm_full_surp, _ = compute_r2(X_perm_surp, Y_all)
                            delta_perm_surp = r2_perm_full_surp - r2_red_surp
                            
                            # ROI average
                            for r_idx, (label, keys) in enumerate(targets.items()):
                                roi_chs_p = set()
                                for k in keys:
                                    if k in subj_rois:
                                        for sub_k, ch_list in subj_rois[k].items():
                                            if isinstance(ch_list, list): roi_chs_p.update(ch_list)
                                p_indices = [i for i, name in enumerate(ch_names) if name in roi_chs_p]
                                if p_indices:
                                    perm_roi_mdl[p_iter, r_idx, :] = np.mean(delta_perm_mdl[p_indices, :], axis=0)
                                    perm_roi_surp[p_iter, r_idx, :] = np.mean(delta_perm_surp[p_indices, :], axis=0)
                        
                        # P-values: proportion of permuted ΔR² >= observed ΔR²
                        p_val_mdl = np.mean(perm_roi_mdl >= obs_roi_mdl[np.newaxis, :, :], axis=0)
                        p_val_surp = np.mean(perm_roi_surp >= obs_roi_surp[np.newaxis, :, :], axis=0)
                        
                        subj_grp.create_dataset("ROI_PValue_MDL", data=p_val_mdl, compression="gzip")
                        subj_grp.create_dataset("ROI_PValue_Surp", data=p_val_surp, compression="gzip")
                        subj_grp.attrs["n_permutations"] = n_perm
                        print(f"  Saved permutation p-values ({n_perm} perms)")
                    else:
                        print("  Skipping permutations (n_perm=0)")
                        subj_grp.attrs["n_permutations"] = 0

    # Save collinearity diagnostics to CSV
    if diagnostics_rows:
        df_diagnostics = pd.DataFrame(diagnostics_rows)
        df_diagnostics.to_csv(diagnostics_file, index=False)
        print(f"\nCollinearity diagnostics saved to {diagnostics_file}")
        print("\nCollinearity Summary:")
        print(df_diagnostics.to_string())
        
        # Alert if any subject has high collinearity
        if df_diagnostics['HighCollinearity_Warning'].any():
            print("\n⚠️  WARNING: High collinearity detected in one or more subjects!")
            print("   Results may be unreliable. See diagnostics file for details.")
    
    print(f"\nFinished. Results saved to {out_file}")

if __name__ == "__main__":
    main()
