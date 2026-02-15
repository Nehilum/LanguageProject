#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run Cluster-Based Permutation Test for GLM
==========================================

This script performs a cluster-based permutation test on the GLM analysis
to corrected for multiple comparisons across time and channels.

It specifically tests the significance of the "Complexity" (MDL) effect or other specified predictors.

Methodology (Maris & Oostenveld, 2007):
1. Compute the Observed T-Map for the predictor of interest.
2. Identify clusters of significant T-values (uncorrected p < 0.05).
3. Calculate the "Cluster Mass" (sum of T-values) for each observed cluster.
4. Permutation Loop (N=1000):
   a. Shuffle the predictor column in the Design Matrix X.
   b. Re-fit the GLM.
   c. Identify the Maximum Cluster Mass in this permuted T-Map.
5. Build the Null Distribution of Maximum Cluster Masses.
6. Calculate the p-value for each observed cluster:
   p = (number of null_max_masses > observed_mass) / N_permutations

Inputs:
- derivatives/glm_data/glm_dataset_{type}.h5 (Data Y and Design Matrix X)
- derivatives/rois/functional_rois.json (ROI definitions)

Outputs:
- derivatives/glm_results/permutation_clusters_{type}.csv
"""

import os
import h5py
import json
import argparse
import logging
import numpy as np
import pandas as pd
from scipy.ndimage import label
from scipy import stats
from functools import lru_cache

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Config
ROI_JSON = "derivatives/rois/functional_rois.json"

# Parameters
N_PERMS = 1000
P_THRESH_UNC = 0.05
# T_THRESH will be calculated dynamically based on degrees of freedom
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


def load_rois(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def get_channel_names_from_dataset(grp):
    """Retrieve channel names from attributes or linked file if available."""
    # The prepare_glm_data script didn't explicitly save channel names in H5 attributes per group.
    # But usually dimension order is known.
    # We might need to load from the original inputs if not present.
    # run_glm_hierarchical.py loaded them from the first .npz file.
    # We'll duplicate that logic if needed, or check attributes.
    if "channel_names" in grp.attrs:
         return grp.attrs["channel_names"]
    return None

def build_design_matrix(X_df, model_type):
    """
    Construct the design matrix. Must match run_glm_hierarchical.py exactly.
    """
    X_out = X_df.copy()
    
    # 1. Length Centering
    if 'length' in X_out.columns:
        l_mean = X_out['length'].astype(float).mean()
        X_out['Length_c'] = X_out['length'].astype(float) - l_mean
    
    # 2. Surprisal
    if 'surprisal' in X_out.columns:
        X_out['Surprisal'] = pd.to_numeric(X_out['surprisal'], errors='coerce').fillna(0)
    
    # 3. Interaction
    if 'Length_c' in X_out.columns and 'Surprisal' in X_out.columns:
        X_out['Interaction'] = X_out['Length_c'] * X_out['Surprisal']
    
    # 4. Nuisance
    if 'tone_id' in X_out.columns: X_out['ToneID'] = X_out['tone_id'].astype(float)
    if 'repetition' in X_out.columns: X_out['Repetition'] = X_out['repetition'].astype(float)
    if 'pos' in X_out.columns: 
        X_out['Position'] = X_out['pos'].astype(float)
        X_out['Position_c'] = X_out['Position'] - X_out['Position'].mean()
    if 'trial_type' in X_out.columns:
        X_out['IsHab'] = (X_out['trial_type'] == 'habituation').astype(float)
    
    # 5. MDL & Deviant
    if 'mdl' in X_out.columns:
        X_out['MDL'] = pd.to_numeric(X_out['mdl'], errors='coerce').fillna(0)
    else:
        X_out['MDL'] = 0.0

    X_out['IsDeviant'] = 0.0
    if 'trial_type' in X_out.columns and 'pos' in X_out.columns and 'violation_position' in X_out.columns:
        is_viol_trial = (X_out['trial_type'] == 'violation')
        # Ensure violation_position is numeric
        v_pos = pd.to_numeric(X_out['violation_position'], errors='coerce').fillna(0)
        is_at_viol_pos = (X_out['pos'] == v_pos)
        X_out.loc[is_viol_trial & is_at_viol_pos, 'IsDeviant'] = 1.0

    X_out['Intercept'] = 1.0
    
    # Select Predictors
    if model_type == 'ModelA':
        predictors = ['Intercept', 'IsHab', 'ToneID', 'Repetition']
    elif model_type == 'ModelB':
        predictors = ['Intercept', 'IsHab', 'ToneID', 'Repetition', 'Position_c', 'Length_c', 'Surprisal', 'Interaction']
    elif model_type == 'ModelC':
        predictors = ['Intercept', 'IsHab', 'ToneID', 'Repetition', 'Position_c', 'IsDeviant', 'MDL']
    elif model_type == 'ModelD':
        # Competition: MDL + Surprisal
        predictors = ['Intercept', 'IsHab', 'ToneID', 'Repetition', 'Position_c', 'Length_c', 'Surprisal', 'MDL']
    else:
        raise ValueError(f"Unknown model: {model_type}")

    # Check for NaNs
    X_mat = X_out[predictors].values
    if np.isnan(X_mat).any():
        X_mat = np.nan_to_num(X_mat)
        
    return X_mat, predictors

def fit_glm_fast(X, Y):
    """
    Optimized GLM fit using pinv.
    Returns Betas and T-stats.
    """
    n_trials, n_ch, n_time = Y.shape
    n_preds = X.shape[1]
    
    # Reshape Y: (N_trials, N_features=Ch*Time)
    Y_reshaped = Y.reshape(n_trials, -1)
    
    # Precompute X stuff
    # X_pinv = (X.T X)^-1 X.T
    try:
        XT_X_inv = np.linalg.inv(X.T @ X)
    except np.linalg.LinAlgError:
        XT_X_inv = np.linalg.pinv(X.T @ X)
        
    X_pinv = XT_X_inv @ X.T
    
    # Beta
    Betas_flat = X_pinv @ Y_reshaped # (N_preds, N_features)
    
    # Residuals
    Y_pred = X @ Betas_flat
    Residuals = Y_reshaped - Y_pred # (N_trials, N_features)
    
    # RSS / MSE
    RSS = np.sum(Residuals**2, axis=0)
    df = n_trials - n_preds
    MSE = RSS / df
    
    # SE
    diag_XT_X_inv = np.diag(XT_X_inv) # (N_preds,)
    SE_beta = np.sqrt(np.outer(diag_XT_X_inv, MSE)) # (N_preds, N_features)
    
    # T-stats
    # Avoid division by zero
    T_stats_flat = np.divide(Betas_flat, SE_beta, out=np.zeros_like(Betas_flat), where=SE_beta!=0)
    
    # Reshape
    T_stats = T_stats_flat.reshape(n_preds, n_ch, n_time)
    
    return T_stats

def get_clusters(t_series, threshold):
    """
    1D Clustering on T-series.
    """
    mask = np.abs(t_series) > threshold
    labeled, n_clusters = label(mask)
    
    clusters = []
    for i in range(1, n_clusters + 1):
        indices = np.where(labeled == i)[0]
        if len(indices) == 0: continue
        
        # Mass
        cluster_t = t_series[indices]
        mass = np.sum(np.abs(cluster_t))
        start = indices[0]
        end = indices[-1]
        
        clusters.append({
            'mass': mass,
            'start': start,
            'end': end,
            'indices': indices
        })
    return clusters

def run_permutation(subj, cond, Y_all, X_df_all, roi_indices_map, model, target_pred, n_perms):
    """
    Run permutation test for a single Subject.
    
    IMPORTANT: We pool Y within each ROI *before* fitting the GLM to ensure
    T-statistics have proper statistical interpretation. This means we run
    the permutation loop per-ROI rather than once globally.
    """
    logger.info(f"Starting permutation for {subj} ({len(X_df_all)} trials, {n_perms} perms)")
    
    # 1. Build Design Matrix
    X_mat, pred_names = build_design_matrix(X_df_all, model)
    
    if target_pred not in pred_names:
        logger.error(f"Predictor '{target_pred}' not found in model {model}. Available: {pred_names}")
        return []
    
    pred_idx = pred_names.index(target_pred)
    
    # Calculate Dynamic T-threshold
    df = X_mat.shape[0] - X_mat.shape[1]
    t_thresh = stats.t.ppf(1 - P_THRESH_UNC / 2, df)
    logger.info(f"Using dynamic T-threshold: {t_thresh:.4f} (df={df}, p<{P_THRESH_UNC})")

    final_output = []
    
    # --- Per-ROI analysis: pool Y, then fit GLM ---
    for roi_name, ch_indices in roi_indices_map.items():
        if not ch_indices:
            continue
        
        # Pool Y within ROI: mean across channels → (N_trials, 1, N_time)
        Y_roi = np.mean(Y_all[:, ch_indices, :], axis=1, keepdims=True)
        
        logger.info(f"  ROI '{roi_name}': {len(ch_indices)} channels pooled → fitting GLM")
        
        # 2. Fit observed GLM on pooled ROI signal
        T_obs_roi = fit_glm_fast(X_mat, Y_roi)  # (N_preds, 1, N_time)
        roi_t_obs = T_obs_roi[pred_idx, 0, :]    # (N_time,)
        
        # Get observed clusters
        clusters = get_clusters(roi_t_obs, t_thresh)
        
        if not clusters:
            logger.info(f"    No observed clusters for ROI '{roi_name}' (uncorrected)")
            continue
        
        logger.info(f"    Found {len(clusters)} observed cluster(s). Running {n_perms} permutations...")
        
        # 3. Permutation Loop
        null_max_masses = np.zeros(n_perms)
        target_col_data = X_mat[:, pred_idx].copy()
        X_mat_perm = X_mat.copy()
        
        for k in range(n_perms):
            if k % 100 == 0:
                logger.info(f"      Permutation {k}/{n_perms}")
            
            # Shuffle target predictor column
            np.random.shuffle(target_col_data)
            X_mat_perm[:, pred_idx] = target_col_data
            
            # Fit on pooled ROI signal
            T_perm_roi = fit_glm_fast(X_mat_perm, Y_roi)
            roi_t_perm = T_perm_roi[pred_idx, 0, :]
            
            # Find max cluster mass
            clusters_p = get_clusters(roi_t_perm, t_thresh)
            if clusters_p:
                null_max_masses[k] = max([c['mass'] for c in clusters_p])
            else:
                null_max_masses[k] = 0.0
        
        # 4. Calculate P-values for each observed cluster
        for c in clusters:
            p_val = np.sum(null_max_masses >= c['mass']) / n_perms
            
            final_output.append({
                'Subject': subj,
                'ROI': roi_name,
                'Cluster_ID': f"{roi_name}_{c['start']}",
                'Start_TP': c['start'],
                'End_TP': c['end'],
                'Obs_Mass': c['mass'],
                'P_Value_Corrected': p_val,
                'Null_95th': np.percentile(null_max_masses, 95),
                'N_ROI_Channels': len(ch_indices),
            })
        
        # Restore original X_mat column for next ROI
        X_mat_perm[:, pred_idx] = X_mat[:, pred_idx]
        
    return final_output

def main():
    parser = argparse.ArgumentParser(description="Run GLM Permutation Test")
    parser.add_argument("--model", type=str, default="ModelC", help="Model to test (ModelA/B/C/D)")
    parser.add_argument("--predictor", type=str, default="MDL", help="Predictor to test (e.g. MDL, Surprisal, Length_c, ToneID, Repetition)")
    parser.add_argument("--n_perms", type=int, default=1000, help="Number of permutations")
    parser.add_argument("--tmin", type=float, default=None, help="Start time in seconds (e.g. 0.0)")
    parser.add_argument("--tmax", type=float, default=None, help="End time in seconds (e.g. 0.3)")
    parser.add_argument("--data_type", type=str, default="erp", choices=['erp', 'hfa'], help="Data type to process (erp or hfa)")
    parser.add_argument("--baseline_mode", type=str, default="local", choices=['local', 'global'], help="Baseline correction strategy (local or global)")
    args = parser.parse_args()
    
    baseline_suffix = f"_base{args.baseline_mode}"
    glm_data_file = f"derivatives/glm_data/glm_dataset_{args.data_type}{baseline_suffix}.h5"
    out_csv = f"derivatives/glm_results/permutation_clusters_{args.data_type}{baseline_suffix}.csv"
    
    if args.model:
         out_csv = out_csv.replace('.csv', f'_{args.model}.csv')

    if not os.path.exists(glm_data_file):
        logger.error(f"Input file not found: {glm_data_file}")
        return
        
    # Load ROIs
    roi_data = load_rois(ROI_JSON)
    
    all_significant_clusters = []
    
    # 1. Scan HDF5 for Subjects
    subjects = set()
    with h5py.File(glm_data_file, 'r') as hf_in:
        for cond in hf_in.keys():
            if isinstance(hf_in[cond], h5py.Group):
                for subj in hf_in[cond].keys():
                    subjects.add(subj)
    
    logger.info(f"Found subjects: {list(subjects)}")
    
    with h5py.File(glm_data_file, 'r') as hf:
        # Detect FS from HDF5 attribute
        global FS
        if 'fs' in hf.attrs:
            FS = float(hf.attrs['fs'])
            logger.info(f"Detected FS = {FS} Hz from HDF5 attributes")
        else:
             # Fallback if attribute missing
             FS = 500.0
             logger.warning(f"FS attribute missing in {glm_data_file}. Defaulting to {FS} Hz")

        for subj in subjects:
            logger.info(f"\nProcessing Subject: {subj} (Concatenated)...")
            
            # Gather Data for this Subject across ALL conditions
            Y_list = []
            X_df_list = []
            
            for cond in hf.keys():
                if not isinstance(hf[cond], h5py.Group): continue
                if subj in hf[cond]:
                    grp = hf[f"{cond}/{subj}"]
                    
                    # Load Data
                    if "Y" not in grp: continue
                    Y_part = grp["Y"][:]
                    
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
                    
                    # Append
                    Y_list.append(Y_part)
                    X_df_list.append(X_part)
            
            if not Y_list:
                logger.warning(f"No data found for subject {subj}")
                continue
                
            # Concatenate
            Y_all = np.concatenate(Y_list, axis=0)
            X_df_all = pd.concat(X_df_list, axis=0, ignore_index=True)
            
            logger.info(f"  Total Data: {len(X_df_all)} epochs, {Y_all.shape[1]} channels")

            # Slice Time Window if requested
            EPOCH_TMIN = -0.2 # Actual epoch starts at -0.2s
            
            if args.tmin is not None or args.tmax is not None:
                if FS is None:
                    # Should not happen with detection above
                    FS = 500.0
                    logger.warning("FS is None during slicing, using fallback 500.0")

                t_start_idx = 0
                t_end_idx = Y_all.shape[2]
                
                if args.tmin is not None:
                    # Correct offset calculation: (target_time - epoch_start) * sampling_rate
                    t_start_idx = int(round((args.tmin - EPOCH_TMIN) * FS))
                    t_start_idx = max(0, t_start_idx)
                    
                if args.tmax is not None:
                    t_end_idx = int(round((args.tmax - EPOCH_TMIN) * FS))
                    t_end_idx = min(Y_all.shape[2], t_end_idx)
                    
                if t_start_idx >= t_end_idx:
                    logger.error(f"Invalid time window indices: {t_start_idx} to {t_end_idx} (tmin={args.tmin}, tmax={args.tmax}, epoch_tmin={EPOCH_TMIN}, fs={FS})")
                    continue
                    
                logger.info(f"  Slicing data: {args.tmin}s (idx {t_start_idx}) to {args.tmax}s (idx {t_end_idx}) | Epoch Tmin: {EPOCH_TMIN}s, FS: {FS}Hz")
                Y_all = Y_all[:, :, t_start_idx:t_end_idx]

                
            # Determine ROIs for this subject
            if subj not in roi_data['subjects']:
                logger.warning(f"No ROI data for {subj}")
                continue
                
            subj_rois = roi_data['subjects'][subj]
            
            # Get channel names (Best Effort lookup)
            # Find ANY condition that has this subject to get channel names
            # We assume channels are consistent across conditions for the same subject
            sample_cond = [c for c in hf.keys() if subj in hf[c]][0]
            
            # Helper to find .npz
            import glob
            pat = f"derivatives/epochs/{sample_cond}/{subj}/*.npz"
            fs = glob.glob(pat)
            if fs:
                try:
                    tmp = np.load(fs[0], allow_pickle=True)
                    ch_names = tmp['channel_names']
                    ch_names = [str(c) for c in ch_names]
                except:
                     ch_names = [f"CH{i+1:02d}" for i in range(Y_all.shape[1])]
            else:
                logger.warning("Could not find channel names file. Using indexes.")
                ch_names = [f"CH{i+1:02d}" for i in range(Y_all.shape[1])]
            
            # Map ROIs to Indices
            roi_indices_map = {}
            target_rois = {'Auditory': ['Auditory'], 'S1': ['S1_Sensory'], 'M1': ['M1_Motor']}
            
            for r_label, r_keys in target_rois.items():
                 r_chs = set()
                 for k in r_keys:
                     if k in subj_rois:
                         for _, clist in subj_rois[k].items():
                             if isinstance(clist, list): r_chs.update(clist)
                 
                 indices = [i for i, name in enumerate(ch_names) if name in r_chs]
                 if indices:
                     roi_indices_map[r_label] = indices
            
            # RUN PERMUTATION
            results = run_permutation(subj, "AllConditions", Y_all, X_df_all, roi_indices_map, args.model, args.predictor, args.n_perms)
            
            all_significant_clusters.extend(results)
                
    # Save
    if all_significant_clusters:
        df_out = pd.DataFrame(all_significant_clusters)
        # Filter for significant
        df_sig = df_out[df_out['P_Value_Corrected'] < 0.05]
        
        logger.info(f"Found {len(df_sig)} significant clusters (p<0.05 corrected).")
        df_out.to_csv(out_csv, index=False)
        logger.info(f"Saved full results to {out_csv}")
    else:
        logger.info("No clusters processed.")

if __name__ == "__main__":
    main()
