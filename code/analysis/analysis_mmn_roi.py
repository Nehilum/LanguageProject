#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ROI-Based MMN Analysis (Dual Baseline)
--------------------------------------
Performs ROI-averaged ERP analysis and statistical testing for MMN using TWO baseline strategies:
1. Sequence Baseline: [-0.2s, 0.0s] relative to Sequence Onset.
2. Tone Baseline: [-0.05s, 0.0s] relative to Tone Onset.

Inputs:
    - derivatives/epochs/<Condition>/<Subject>/seqver-*_epochs.npz
    - derivatives/rois/functional_rois.json

Outputs:
    - derivatives/MMN/<Grammar>_Length<L>/<Subject>_baseline-seq_butterfly.png
    - derivatives/MMN/<Grammar>_Length<L>/<Subject>_baseline-tone_butterfly.png
    - derivatives/MMN/<Grammar>_Length<L>/<Subject>_stats_compare.csv
"""

import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import ttest_rel, ttest_1samp, ttest_ind

# --- CONFIG ---
DERIVATIVES_ROOT = Path("derivatives")
if not DERIVATIVES_ROOT.exists():
    if Path("NewPipeline/derivatives").exists():
        DERIVATIVES_ROOT = Path("NewPipeline/derivatives")
    elif Path("../derivatives").exists():
        DERIVATIVES_ROOT = Path("../derivatives")

EPOCH_DIR = DERIVATIVES_ROOT / "epochs"
MMN_DIR = DERIVATIVES_ROOT / "MMN"
ROI_JSON = DERIVATIVES_ROOT / "rois" / "functional_rois.json"

STATS_WINDOWS = {
    'early': (0.100, 0.250),
    'late': (0.300, 0.500)
}

# Baseline Definitions
SEQ_BASELINE_WIN = (-0.2, 0.0) # Relative to Sequence Onset
TONE_BASELINE_WIN = (-0.05, 0.0) # Relative to Tone Onset

# Tone Analysis Window (Cut)
TONE_CUT_WIN = (-0.2, 0.6) # Relative to Tone Onset

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


COLORS = {
    'standard': 'blue',
    'violation': 'red',
    'habituation': 'green',
    'difference': 'black'
}

def load_rois(subject):
    """Load ROIs for subject from JSON."""
    if not ROI_JSON.exists():
        print(f"Error: ROI file not found at {ROI_JSON}")
        return None
    
    with open(ROI_JSON, 'r') as f:
        data = json.load(f)
    
    if subject not in data['subjects']:
        print(f"Error: Subject {subject} not in ROI file")
        return None
        
    subj_data = data['subjects'][subject]
    
    targets = {
        'Auditory': ['Auditory'],
        'S1': ['S1_Sensory'],
        'M1': ['M1_Motor']
    }
    
    roi_channels = {}
    for label, keys in targets.items():
        channels = set()
        for k in keys:
            if k in subj_data:
                sub_regions = subj_data[k]
                for sub_k, ch_list in sub_regions.items():
                   if isinstance(ch_list, list):
                       channels.update(ch_list)
        roi_channels[label] = list(channels)
        
    return roi_channels

def parse_condition_string(cond_str):
    parts = cond_str.rsplit('_', 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0], int(parts[1])
    return cond_str, 0

def run_stats(dev_trace, std_trace, time, win):
    """
    Independent t-test Dev vs Std in window, and calculate Peak/AUC.
    - Peak: Max absolute difference in window.
    - AUC: Integral of the difference (Dev - Std) over the window.
    """
    mask = (time >= win[0]) & (time <= win[1])
    if not np.any(mask): 
        return {
            't': np.nan, 'p': np.nan, 'diff': np.nan, 
            'peak': np.nan, 'auc': np.nan
        }
    
    # 1. Trial-level averages for t-test
    dev_mean_trial = np.mean(dev_trace[:, mask], axis=1)
    std_mean_trial = np.mean(std_trace[:, mask], axis=1)
    t, p = ttest_ind(dev_mean_trial, std_mean_trial, equal_var=False, nan_policy='omit')
    
    # 2. Grand averages for morphology
    dev_avg = np.mean(dev_trace, axis=0) # (T,)
    std_avg = np.mean(std_trace, axis=0) # (T,)
    diff_avg = dev_avg - std_avg
    
    win_diff = diff_avg[mask]
    
    # Peak (Max absolute difference)
    peak = win_diff[np.argmax(np.abs(win_diff))]
    
    # AUC (using trapezoidal rule)
    # Total time in ms? Usually MMN is in microvolts-ms. Let's use seconds * amplitude.
    dt = 1.0 / 500.0 # Standard DT if FS=500
    auc = np.trapz(win_diff, dx=dt)
    
    return {
        't': t, 'p': p, 'diff': np.mean(dev_mean_trial) - np.mean(std_mean_trial),
        'peak': peak, 'auc': auc
    }

def extract_and_baseline(signals, meta, fs, mode='sequence'):
    """
    Extracts tones and applies baseline.
    mode: 'sequence' (Seq Baseline -> Cut) OR 'tone' (Cut -> Tone Baseline)
    Returns: data_map {'standard': (N, T, C), ...}
    """
    # 1. Determine Target Position (Modal Violation Position)
    positions = [int(m['violation_position']) for m in meta if m['trial_type'] == 'violation']
    if not positions: target_pos = 1
    else: target_pos = max(set(positions), key=positions.count)
    
    # 2. Preparation
    epoch_pre = 0.5 # Sequence epoch starts at -0.5s
    seq_offset_samp = int(epoch_pre * fs)
    
    # Tone Cut Indices
    s_start = int(TONE_CUT_WIN[0] * fs)
    s_end = int(TONE_CUT_WIN[1] * fs)
    n_samps_cut = s_end - s_start
    
    extracted = {k: [] for k in COLORS if k != 'difference'}
    
    # Sequence Baseline Calculation (if mode='sequence')
    # Baseline [-0.2, 0.0] relative to Sequence Onset
    # Index relative to 0 (Seq Onset)
    sb_start = int(SEQ_BASELINE_WIN[0] * fs)
    sb_end = int(SEQ_BASELINE_WIN[1] * fs)
    # Absolute index in array (0 is at -0.5s)
    # 0s is at seq_offset_samp
    
    abs_sb_start = seq_offset_samp + sb_start
    abs_sb_end = seq_offset_samp + sb_end
    
    # Tone Baseline Calculation (if mode='tone')
    # Relative to Tone Onset (0 inside cut)
    # In cut array, 0 is at -TONE_CUT_WIN[0] index.
    # Cut starts at TONE_CUT_WIN[0] (-0.2s).
    # Baseline starts at -0.05s.
    # Offset from start of cut = (-0.05) - (-0.2) = 0.15s.
    tb_start_idx = int((TONE_BASELINE_WIN[0] - TONE_CUT_WIN[0]) * fs)
    tb_end_idx = int((TONE_BASELINE_WIN[1] - TONE_CUT_WIN[0]) * fs)
    if tb_start_idx < 0: tb_start_idx = 0
    
    for i, m in enumerate(meta):
        # Identify Condition
        ttype = m['trial_type']
        v_pos = int(m.get('violation_position', 0))
        
        cond_label = None
        current_pos = -1
        
        if v_pos > 0:
            if v_pos == target_pos:
                cond_label = 'violation'
                current_pos = v_pos
            else: continue
        else:
            cond_label = 'standard'
            current_pos = target_pos
            
        if ttype == 'habituation':
             cond_label = 'habituation'
             current_pos = target_pos
        
        if not cond_label: continue
        
        # Get Full Sequence Signal
        raw_seq = signals[i] # (T_seq, C)
        
        # Apply Sequence Baseline if needed
        if mode == 'sequence':
            # Check bounds
            if abs_sb_start < 0: continue
            base_val = np.mean(raw_seq[abs_sb_start:abs_sb_end, :], axis=0)
            seq_processed = raw_seq - base_val
        else:
            seq_processed = raw_seq # No BC yet
            
        # Cut Tone
        tone_onset_s = (current_pos - 1) * 0.25
        tone_onset_idx = seq_offset_samp + int(tone_onset_s * fs)
        
        start_idx = tone_onset_idx + s_start
        end_idx = tone_onset_idx + s_end
        
        if start_idx < 0 or end_idx > seq_processed.shape[0]: continue
        
        tone_cut = seq_processed[start_idx:end_idx, :]
        
        # Apply Tone Baseline if needed
        if mode == 'tone':
            base_val = np.mean(tone_cut[tb_start_idx:tb_end_idx, :], axis=0)
            tone_cut = tone_cut - base_val
            
        extracted[cond_label].append(tone_cut)
        
    # Stack
    for k in extracted:
        if extracted[k]:
            extracted[k] = np.stack(extracted[k], axis=0) # (N, T, C)
        else:
            # Create empty with correct shape if possible, else None
            extracted[k] = None
            
    return extracted

def plot_butterfly_and_mean(title, cond_data, ch_names, rois, time_axis, out_prefix):
    """Generates Butterfly and ROI Means plots."""
    
    fig_butt, axes_butt = plt.subplots(3, 3, figsize=(15, 12), sharex=True, sharey=True)
    fig_mean, axes_mean = plt.subplots(3, 1, figsize=(8, 12), sharex=True)
    
    roi_names = ['Auditory', 'S1', 'M1']
    
    # Store means for stats later? No, we return nothing here, just plot.
    
    for r_idx, r_name in enumerate(roi_names):
        if r_name not in rois: continue
        roi_chs = rois[r_name]
        indices = [i for i, x in enumerate(ch_names) if x in roi_chs]
        if not indices: continue
        
        # 1. Butterfly
        cols = ['violation', 'standard', 'habituation']
        for c_idx, c_name in enumerate(cols):
            ax = axes_butt[r_idx, c_idx]
            dat = cond_data[c_name]
            if dat is not None and dat.shape[0] > 0:
                sub_dat = dat[:, :, indices]
                mean_traces = np.mean(sub_dat, axis=0)
                ax.plot(time_axis, mean_traces, color=COLORS[c_name], alpha=0.5, linewidth=0.8)
                ax.set_title(f"{r_name} - {c_name} (N={dat.shape[0]})")
            
            if r_idx == 2: ax.set_xlabel("Time (s)")
            if c_idx == 0: ax.set_ylabel("Amplitude")
            ax.axvline(0, color='k', ls='--', alpha=0.3)
            ax.axhline(0, color='k', lw=0.5, alpha=0.3)

        # 2. Mean Plot
        ax_m = axes_mean[r_idx]
        
        for c_name in cols:
            dat = cond_data[c_name]
            if dat is not None and dat.shape[0] > 1:
                sub_dat = dat[:, :, indices]
                # ROI Mean -> (N, T)
                roi_mean = np.mean(sub_dat, axis=2)
                m = np.mean(roi_mean, axis=0)
                s = np.std(roi_mean, axis=0) / np.sqrt(roi_mean.shape[0])
                
                label = c_name.capitalize()
                ax_m.plot(time_axis, m, color=COLORS[c_name], label=label)
                ax_m.fill_between(time_axis, m-s, m+s, color=COLORS[c_name], alpha=0.2)
        
        ax_m.set_title(f"{r_name}")
        ax_m.legend(loc='upper right', fontsize='small')
        ax_m.axvline(0, color='k', ls='--', alpha=0.3)
        ax_m.axhline(0, color='k', lw=0.5, alpha=0.3)

    fig_butt.suptitle(f"{title} - Butterfly", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig_butt.savefig(f"{out_prefix}_butterfly.png")
    plt.close(fig_butt)
    
    fig_mean.suptitle(f"{title} - ROI Means", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig_mean.savefig(f"{out_prefix}_mean.png")
    plt.close(fig_mean)

def main():
    if not EPOCH_DIR.exists(): return
    
    stats_comparison = []

    for cond_path in EPOCH_DIR.iterdir():
        if not cond_path.is_dir(): continue
        grammar, length = parse_condition_string(cond_path.name)
        
        for subj_path in cond_path.iterdir():
            if not subj_path.is_dir(): continue
            subject = subj_path.name
            
            # Load
            files = list(subj_path.glob("*_epochs.npz"))
            if not files: continue
            
            all_signals = []
            all_meta = []
            ch_names = None
            fs = None
            
            for f in files:
                d = np.load(f, allow_pickle=True)
                if 'seq_epochs' in d:
                    sig = d['seq_epochs']
                else: continue
                
                all_signals.append(sig)
                all_meta.extend(d['seq_meta'])
                if ch_names is None: ch_names = d['channel_names']
                if fs is None:
                    if 'fs' not in d:
                        raise RuntimeError(f"Missing 'fs' in {f}")
                    fs = float(d['fs'])
                
            if not all_signals: continue
            full_signals = np.concatenate(all_signals, axis=0)
            
            rois = load_rois(subject)
            if not rois: continue
            
            # --- Analysis pipelines ---
            modes = ['sequence', 'tone']
            
            # Output Dir
            out_folder = MMN_DIR / f"{grammar}_Length{length}"
            out_folder.mkdir(parents=True, exist_ok=True)
            
            # Dictionary to hold results for comparison
            # results[roi][window][mode] = (t, p, diff)
            comp_data = {} 
            
            for mode in modes:
                # 1. Extract & Baseline
                cond_data = extract_and_baseline(full_signals, all_meta, fs, mode=mode)
                
                # Check data
                if cond_data['violation'] is None or cond_data['standard'] is None:
                    continue
                    
                # Time Axis (Cut window)
                # TONE_CUT_WIN = (-0.2, 0.6)
                # Samples
                n_samps = cond_data['standard'].shape[1]
                t_axis = np.linspace(TONE_CUT_WIN[0], TONE_CUT_WIN[1], n_samps)
                
                # 2. Plotting
                title = f"{subject} {grammar} L{length} ({mode.capitalize()} Baseline)"
                out_prefix = out_folder / f"{subject}_baseline-{mode}"
                plot_butterfly_and_mean(title, cond_data, ch_names, rois, t_axis, str(out_prefix))
                
                # 3. Stats
                roi_names = ['Auditory', 'S1', 'M1']
                for r_name in roi_names:
                    if r_name not in rois: continue
                    roi_chs = rois[r_name]
                    indices = [i for i, x in enumerate(ch_names) if x in roi_chs]
                    
                    # ROI Average (N, T)
                    dev_roi = np.mean(cond_data['violation'][:, :, indices], axis=2)
                    std_roi = np.mean(cond_data['standard'][:, :, indices], axis=2)
                    
                    for win_name, win in STATS_WINDOWS.items():
                        stats_res = run_stats(dev_roi, std_roi, t_axis, win)
                        
                        # Store
                        key = (r_name, win_name)
                        if key not in comp_data: comp_data[key] = {}
                        comp_data[key][mode] = stats_res
                        
            # Compile Comparison CSV for this Subject/Condition
            for (r_name, w_name), res in comp_data.items():
                row = {
                    'Subject': subject,
                    'Grammar': grammar,
                    'Length': length,
                    'ROI': r_name,
                    'Window': w_name
                }
                # Add Sequence stats
                if 'sequence' in res:
                    s = res['sequence']
                    row['SeqBase_t'] = s['t']
                    row['SeqBase_p'] = s['p']
                    row['SeqBase_diff'] = s['diff']
                    row['SeqBase_peak'] = s['peak']
                    row['SeqBase_auc'] = s['auc']
                
                # Add Tone stats
                if 'tone' in res:
                    s = res['tone']
                    row['ToneBase_t'] = s['t']
                    row['ToneBase_p'] = s['p']
                    row['ToneBase_diff'] = s['diff']
                    row['ToneBase_peak'] = s['peak']
                    row['ToneBase_auc'] = s['auc']
                    
                stats_comparison.append(row)
                
    # Save CSV
    if stats_comparison:
        df = pd.DataFrame(stats_comparison)
        # Save overarching summary in MMN dir
        df.to_csv(MMN_DIR / "stats_comparison_summary.csv", index=False)
        
        # Also split by condition for folder placement
        for (g, l), group in df.groupby(['Grammar', 'Length']):
             out_f = MMN_DIR / f"{g}_Length{l}"
             out_f.mkdir(exist_ok=True)
             group.to_csv(out_f / "stats_comparison.csv", index=False)

if __name__ == "__main__":
    main()
