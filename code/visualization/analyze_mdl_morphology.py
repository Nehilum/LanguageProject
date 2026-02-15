#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze MDL Morphology
======================

Quantitatively verify the MDL Split ERPs.
1. Load Data (GLM H5).
2. Split into Low/Med/High MDL.
3. Calculate Mean Amplitude in windows:
   - Early (0-200ms)
   - Transition (200-300ms) - Around SOA
   - Late 1 (300-500ms)
   - Late 2 (500-800ms)
4. Stats:
   - One-way ANOVA per window.
   - T-test: High vs Low.
   - Trend Check: Is Mean(High) > Mean(Low)?
"""

import os
import json
import h5py
import numpy as np
import pandas as pd
import scipy.stats as stats

# Config
GLM_DATA_FILE = "derivatives/glm_data/glm_dataset.h5"
ROI_JSON = "derivatives/rois/functional_rois.json"
SOA = 250 # ms

def load_rois(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def load_data_from_h5(glm_file, subject, roi_data):
    # (Same loading logic as plot_mdl_split_erp.py)
    # Copied for standalone execution
    Y_list = []
    MDL_list = []
    subj_rois = roi_data['subjects'].get(subject)
    if not subj_rois: return None, None, None
    
    with h5py.File(glm_file, 'r') as f:
        channel_names = None
        for cond in f.keys():
            if subject in f[cond]:
                grp = f[f"{cond}/{subject}"]
                if "channel_names" in grp.attrs: channel_names = grp.attrs["channel_names"]
                if "Y" not in grp: continue
                Y_part = grp["Y"][:]
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
                X_df = pd.DataFrame(data_dict)
                if 'mdl' in X_df.columns:
                    mdl_part = pd.to_numeric(X_df['mdl'], errors='coerce').fillna(0).values
                else:
                    mdl_part = np.zeros(len(X_df))
                Y_list.append(Y_part)
                MDL_list.append(mdl_part)
                
    if not Y_list: return None, None, None
    Y_all = np.concatenate(Y_list, axis=0)
    MDL_all = np.concatenate(MDL_list, axis=0)
    
    # Fallback for channel names
    if channel_names is None:
        import glob
        pat = f"derivatives/epochs/*/{subject}/*.npz"
        files = glob.glob(pat)
        if files:
            d = np.load(files[0], allow_pickle=True)
            if 'channel_names' in d: channel_names = d['channel_names']
    
    if channel_names is None: return None, None, None
    if isinstance(channel_names[0], bytes): channel_names = [c.decode('utf-8') for c in channel_names]

    roi_indices = {}
    targets = {'Auditory': ['Auditory'], 'S1': ['S1_Sensory'], 'M1': ['M1_Motor']}
    for label, keys in targets.items():
        roi_chs = set()
        for k in keys:
            if k in subj_rois:
                for sub_k, ch_list in subj_rois[k].items():
                    if isinstance(ch_list, list): roi_chs.update(ch_list)
        indices = [i for i, name in enumerate(channel_names) if name in roi_chs]
        roi_indices[label] = indices
        
    return Y_all, MDL_all, roi_indices

def get_mean_amp(data, t_vec, start, end):
    mask = (t_vec >= start) & (t_vec <= end)
    return np.mean(data[:, mask], axis=1)

def analyze_subject(epochs, mdl, roi_indices, subject):
    print(f"\n--- Analysis for {subject} ---")
    
    # Time vector
    n_time = epochs.shape[2]
    t = np.linspace(-200, 800, n_time)
    
    # Groups
    q33 = np.quantile(mdl, 0.33)
    q66 = np.quantile(mdl, 0.66)
    
    idx_low = (mdl <= q33)
    idx_med = (mdl > q33) & (mdl <= q66)
    idx_high = (mdl > q66)
    
    print(f"Counts: Low={np.sum(idx_low)}, Med={np.sum(idx_med)}, High={np.sum(idx_high)}")
    
    windows = [
        ("N1/P2 (0-200ms)", 0, 200),
        ("SOA Transition (200-300ms)", 200, 300),
        ("Second Tone (300-500ms)", 300, 500),
        ("Late / Third Tone (500-800ms)", 500, 800)
    ]
    
    for roi_name, indices in roi_indices.items():
        if not indices: continue
        if roi_name != "Auditory": continue # Focus on Auditory as per user request
        
        print(f"\nROI: {roi_name}")
        roi_data = np.mean(epochs[:, indices, :], axis=1) # (N, Time)
        
        for curr_win in windows:
            name, start, end = curr_win
            
            amp_low = get_mean_amp(roi_data[idx_low], t, start, end)
            amp_med = get_mean_amp(roi_data[idx_med], t, start, end)
            amp_high = get_mean_amp(roi_data[idx_high], t, start, end)
            
            # 1. ANOVA
            f_stat, p_val = stats.f_oneway(amp_low, amp_med, amp_high)
            
            # 2. T-test High vs Low
            t_stat, p_ttest = stats.ttest_ind(amp_high, amp_low)
            
            # 3. Direction
            m_low = np.mean(amp_low)
            m_med = np.mean(amp_med)
            m_high = np.mean(amp_high)
            
            direction = "Mixed"
            if m_high > m_med > m_low: direction = "Linear Increase (L < M < H)"
            elif m_high < m_med < m_low: direction = "Linear Decrease (L > M > H)"
            elif m_high > m_low: direction = "High > Low"
            elif m_high < m_low: direction = "High < Low"
            
            sig_mark = "**" if p_val < 0.001 else ("*" if p_val < 0.05 else "ns")
            
            print(f"  Window {name}:")
            print(f"    Means: L={m_low:.2f}, M={m_med:.2f}, H={m_high:.2f}")
            print(f"    ANOVA p={p_val:.2e} {sig_mark}, High-Low p={p_ttest:.2e}")
            print(f"    Trend: {direction}")
            
            # Check deviation from 0
            # If means are close to 0, effect size matters
            # Cohen's d for High vs Low
            d = (m_high - m_low) / np.sqrt((np.std(amp_high)**2 + np.std(amp_low)**2) / 2)
            print(f"    Effect Size (d): {d:.3f}")

def main():
    roi_data = load_rois(ROI_JSON)
    subjects = roi_data['subjects'].keys()
    
    for subj in subjects:
        epochs, mdl, roi_indices = load_data_from_h5(GLM_DATA_FILE, subj, roi_data)
        if epochs is None: continue
        analyze_subject(epochs, mdl, roi_indices, subj)

if __name__ == "__main__":
    main()
