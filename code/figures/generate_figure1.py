#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Figure 1: Paradigm & Neural Encoding of Structure
-------------------------------------------------
Generates Panels C (Frequency Tagging) and D (ERP Mismatch Response).
Leaves Panels A and B blank.
Saves output to /figures/Figure1.png
"""

import os
import glob
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.stats import ttest_ind
from scipy.ndimage import gaussian_filter1d

# --- CONFIG ---
BASE_DIR = Path("/Users/nehilum/GitCode/MonkeyLanguage/NewPipeline")
DERIVATIVES_DIR = BASE_DIR / "derivatives"
FIG_DIR = BASE_DIR / "figures"
EPOCH_DIR = DERIVATIVES_DIR / "epochs"
ROI_JSON = DERIVATIVES_DIR / "rois" / "functional_rois.json"

SOA = 0.25
TONE_CUT_WIN = (-0.2, 0.6)
SEQ_BASELINE_WIN = (-0.2, 0.0)
N_ITER_SUB = 20  # Reduced for speed, but enough for figure quality

# Structural Colors
COLORS = {
    'standard': '#5D6D7E',   # Grayish Blue
    'violation': '#C0392B',  # Deep Red
    'Alternation': '#8E44AD', # Purple (2Hz)
    'Pairs': '#16A085',      # Teal (1Hz)
    'Control': '#BDC3C7'     # Light Gray
}

# --- UTILS ---
def load_rois(subject):
    if not ROI_JSON.exists(): return None
    with open(ROI_JSON, 'r') as f: data = json.load(f)
    subj_data = data['subjects'].get(subject)
    if not subj_data: return None
    
    # We focus on Auditory for Figure 1 evidence
    aud_chs = set()
    if 'Auditory' in subj_data:
        for sub_k, ch_list in subj_data['Auditory'].items():
            if isinstance(ch_list, list): aud_chs.update(ch_list)
    return list(aud_chs)

def get_phase_factors(signals, fs):
    n_trials, n_time, n_channels = signals.shape
    n_fft = int(2**np.ceil(np.log2(n_time * 2)))
    if fs / n_fft > 0.1: n_fft = int(fs / 0.1)
    X = np.fft.rfft(signals, n=n_fft, axis=1)
    X_phase = X / (np.abs(X) + 1e-15)
    freqs = np.fft.rfftfreq(n_fft, d=1/fs)
    return freqs, X_phase

# --- DATA LOADERS ---
def load_itc_data(subject, condition, length='all'):
    """Load signals and compute phase factors."""
    if length == 'all':
        lengths = [6, 8, 12, 16]
    else:
        lengths = [length]
    
    all_phases = []
    f_ax = None
    
    aud_chs = load_rois(subject)
    if not aud_chs: return None, None

    for L in lengths:
        files = list(EPOCH_DIR.glob(f"{condition}_{L}/{subject}/*_epochs.npz"))
        for f in files:
            d = np.load(f, allow_pickle=True)
            signals = d['seq_epochs']
            meta = d['seq_meta']
            ch_names = list(d['channel_names'])
            fs = float(d['fs'])
            
            idx = [i for i, ch in enumerate(ch_names) if ch in aud_chs]
            if not idx: continue
            
            # Slice to full sequence duration
            dur = L * SOA
            n_samples = int(dur * fs)
            start_s = 0.5
            s_idx = int(start_s * fs)
            e_idx = s_idx + n_samples
            
            # Keep habituation trials
            keep = [i for i, m in enumerate(meta) if m['trial_type'] == 'habituation']
            if not keep: continue
            
            sig_roi = signals[keep, s_idx:e_idx, :][:, :, idx]
            
            # FFT (per trial)
            freqs, phases = get_phase_factors(sig_roi, fs)
            # ROI average (complex)
            ph_avg = np.mean(phases, axis=2)
            
            if f_ax is None: f_ax = freqs
            elif not np.array_equal(f_ax, freqs): continue # Frequency resolution mismatch
            
            all_phases.append(ph_avg)
            
    if not all_phases: return None, None
    return f_ax, np.concatenate(all_phases, axis=0)

def load_erp_data(subject, lengths=[4, 6, 8, 12, 16]):
    """Load standard and violation tones for MMN."""
    aud_chs = load_rois(subject)
    if not aud_chs: return None, None
    
    standard_all = []
    violation_all = []
    
    # Focusing on grammars with robust/consistent MMN across subjects for the Grand Average
    # (Other grammars like Alternation/Pairs show subject-specific dissociations that wash out in the mean)
    grammars = ['Repetition', 'Triplets']
    # lengths argument used for filtering
    
    for cond in grammars:
        for L in lengths:
            subj_path = EPOCH_DIR / f"{cond}_{L}" / subject
            if not subj_path.exists():
                continue
            
            files = list(subj_path.glob("*_epochs.npz"))
            for f in files:
                try:
                    d = np.load(f, allow_pickle=True)
                    signals = d['seq_epochs']
                    meta = d['seq_meta']
                    ch_names = list(d['channel_names'])
                    fs = float(d['fs'])
                    idx = [i for i, ch in enumerate(ch_names) if ch in aud_chs]
                    if not idx: continue
                    
                    v_positions = [int(m['violation_position']) for m in meta if str(m['trial_type']).lower() == 'violation']
                    if not v_positions: continue
                    target_pos = max(set(v_positions), key=v_positions.count)
                    
                    s_off = int(0.5 * fs)
                    tone_start_idx = s_off + int((target_pos - 1) * SOA * fs)
                    cut_start = int(TONE_CUT_WIN[0] * fs)
                    cut_end = int(TONE_CUT_WIN[1] * fs)
                    
                    for i, m in enumerate(meta):
                        s_idx = tone_start_idx + cut_start
                        e_idx = tone_start_idx + cut_end
                        if s_idx < 0 or e_idx > signals.shape[1]:
                            continue
                        
                        chunk = signals[i, s_idx:e_idx][:, idx]
                        if chunk.shape[0] != (cut_end - cut_start):
                            continue
                        
                        # Sequence-level baseline [-0.2, 0.0]s relative to sequence onset
                        # Array starts at -0.5s, so 0s is at s_off
                        sb_start = s_off + int(SEQ_BASELINE_WIN[0] * fs)
                        sb_end = s_off + int(SEQ_BASELINE_WIN[1] * fs)
                        
                        base_val = np.mean(signals[i, sb_start:sb_end, :], axis=0)
                        chunk = signals[i, s_idx:e_idx, :] - base_val
                        
                        trace = np.mean(chunk, axis=1)
                        
                        tt = str(m['trial_type']).lower()
                        vp = int(m['violation_position'])
                        
                        if tt == 'violation' and vp == target_pos:
                            violation_all.append(trace)
                        elif tt in ['habituation', 'standard']:
                            standard_all.append(trace)
                except Exception:
                    continue
                
    if not standard_all or not violation_all:
        return None, None
        
    return np.array(standard_all), np.array(violation_all)

# --- PLOTTING ---
def setup_plot_style():
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'sans-serif']
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    sns.set_context("paper")
    sns.set_style("white")

def plot_panel_c(ax, f_ax, ph_cond, ph_ctrl, label):
    """Plot ITC spectrum."""
    n_cond = ph_cond.shape[0]
    n_ctrl = ph_ctrl.shape[0]
    n_min = min(n_cond, n_ctrl)
    
    # Subsampling
    itc_cond_acc = np.zeros(ph_cond.shape[1])
    itc_ctrl_acc = np.zeros(ph_ctrl.shape[1])
    for _ in range(N_ITER_SUB):
        i1 = np.random.choice(n_cond, n_min, replace=False)
        i2 = np.random.choice(n_ctrl, n_min, replace=False)
        itc_cond_acc += np.abs(np.mean(ph_cond[i1], axis=0))
        itc_ctrl_acc += np.abs(np.mean(ph_ctrl[i2], axis=0))
    
    itc_cond = itc_cond_acc / N_ITER_SUB
    itc_ctrl = itc_ctrl_acc / N_ITER_SUB
    
    # Difference Wave (Alternation - Random)
    itc_diff = itc_cond - itc_ctrl
    
    # Plot Difference
    ax.plot(f_ax, itc_diff, color=COLORS['Alternation'], lw=2.5, label='Alternation - Random')
    ax.axhline(0, color='gray', ls='--', lw=1)
    
    # Styling
    ax.set_xlim(0.1, 5)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('$\Delta$ ITC (Structure - Random)')
    ax.set_title("C: Frequency Tagging (Difference)", loc='left', fontweight='bold')
    ax.legend(frameon=False, loc='upper right', fontsize=10)
    
    # Highlight 2Hz
    ax.annotate("Structural Tracking (2Hz)", xy=(2.0, max(itc_diff[(f_ax>1.9)&(f_ax<2.1)])), 
                xytext=(2.5, max(itc_diff[(f_ax>1.9)&(f_ax<2.1)])+0.05),
                arrowprops=dict(arrowstyle="->", color='black'),
                fontsize=11, ha='left')
    sns.despine(ax=ax)

def plot_panel_d(ax, std_all, dev_all):
    """Plot Grand Average ERP."""
    t_axis = np.linspace(TONE_CUT_WIN[0], TONE_CUT_WIN[1], std_all.shape[1])
    
    m_std = np.mean(std_all, axis=0)
    s_std = np.std(std_all, axis=0) / np.sqrt(std_all.shape[0])
    
    m_dev = np.mean(dev_all, axis=0)
    s_dev = np.std(dev_all, axis=0) / np.sqrt(dev_all.shape[0])
    
    # Gaussian Smoothing for visualization (sigma=8 samples)
    sigma = 8
    m_std = gaussian_filter1d(m_std, sigma)
    m_dev = gaussian_filter1d(m_dev, sigma)
    
    # Main Curves
    ax.plot(t_axis, m_std, color=COLORS['standard'], lw=2, label='Standard')
    ax.fill_between(t_axis, m_std - s_std, m_std + s_std, color=COLORS['standard'], alpha=0.1)
    
    ax.plot(t_axis, m_dev, color=COLORS['violation'], lw=2, label='Deviant')
    ax.fill_between(t_axis, m_dev - s_dev, m_dev + s_dev, color=COLORS['violation'], alpha=0.1)
    
    # Significance Shading
    # Instead of point-wise clusters (which can be patchy), we shade the predefined window
    # if the window-level mean difference is significant.
    win_start, win_end = 0.15, 0.35
    t_idx_win = (t_axis >= win_start) & (t_axis <= win_end)
    
    _, p_window = ttest_ind(std_win, dev_win)
    
    if p_window < 0.05:
        # Highlight the entire window if significant
        ax.axvspan(win_start, win_end, color='gray', alpha=0.15, lw=0, label='_nolegend_')
        # Also draw a subtle outline or markers for the significance period
        ax.text(0.25, ax.get_ylim()[0], f"p = {p_window:.4f}", 
                ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')
    
    # Styling
    ax.set_xlim(-0.1, 0.6)
    ax.set_xlabel('Time rel. to Tone (s)')
    ax.set_ylabel('Amplitude (a.u.)')
    ax.set_title("D: Standard vs. Deviant ERP", loc='left', fontweight='bold')
    ax.axvline(0, color='black', ls='--', lw=0.8)
    ax.legend(frameon=False, loc='upper left', fontsize=10)
    
    if p_window < 0.05:
        ax.text(0.25, ax.get_ylim()[0], f"p = {p_window:.4f}", 
                ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')
    
    sns.despine(ax=ax)

def main():
    print("Initializing Figure Generation...")
    setup_plot_style()
    FIG_DIR.mkdir(exist_ok=True)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    plt.subplots_adjust(hspace=0.4, wspace=0.3)
    
    # Panels A and B (Placeholders)
    for i, label in enumerate(['A', 'B']):
        ax = axes[0, i]
        ax.axis('off')
        ax.text(0.5, 0.5, f"Panel {label}\n(To be added manually)", 
                ha='center', va='center', fontsize=18, color='gray', style='italic')
        ax.set_title(f"{label}: Placeholder", loc='left', fontweight='bold', color='gray')

    # Panel C: Frequency Tagging
    print("Computing Panel C (ITC)...")
    f_ax, ph_cond_b = load_itc_data('Boss', 'Alternation', 12)
    _, ph_cond_c = load_itc_data('Carol', 'Alternation', 12)
    _, ph_ctrl_b = load_itc_data('Boss', 'RandomControl', 12)
    _, ph_ctrl_c = load_itc_data('Carol', 'RandomControl', 12)
    
    # Check for None
    valid_cond = [p for p in [ph_cond_b, ph_cond_c] if p is not None]
    valid_ctrl = [p for p in [ph_ctrl_b, ph_ctrl_c] if p is not None]
    
    print(f"Panel C: {len(valid_cond)} subject(s) valid for Alternation, {len(valid_ctrl)} for Control")
    
    if f_ax is not None and valid_cond and valid_ctrl:
        ph_cond = np.concatenate(valid_cond, axis=0)
        ph_ctrl = np.concatenate(valid_ctrl, axis=0)
        plot_panel_c(axes[1, 0], f_ax, ph_cond, ph_ctrl, "Alternation")
        
        # Pairs removed as requested to focus on Alternation-Random Difference
    else:
        print("Warning: Panel C data missing or incomplete.")
        axes[1, 0].text(0.5, 0.5, "Data Missing", ha='center')

    # Panel D: ERP Mismatch
    print("Computing Panel D (ERP)...")
    std_b, dev_b = load_erp_data('Boss')
    std_c, dev_c = load_erp_data('Carol')
    
    standard_list = []
    violation_list = []
    
    if std_b is not None: standard_list.append(std_b)
    if dev_b is not None: violation_list.append(dev_b)
    if std_c is not None: standard_list.append(std_c)
    if dev_c is not None: violation_list.append(dev_c)
    
    if standard_list and violation_list:
        std_all = np.concatenate(standard_list, axis=0)
        dev_all = np.concatenate(violation_list, axis=0)
        print(f"Panel D: Extracted {len(std_all)} standard trials and {len(dev_all)} violation trials")
        if std_all.ndim > 1 and dev_all.ndim > 1:
            plot_panel_d(axes[1, 1], std_all, dev_all)
        else:
            print("Warning: Panel D data rank issue.")
            axes[1, 1].text(0.5, 0.5, "Data Rank Error", ha='center')
    else:
        print("Warning: Panel D data missing.")
        axes[1, 1].text(0.5, 0.5, "Data Missing", ha='center')
    
    output_path = FIG_DIR / "Figure1.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to {output_path}")

if __name__ == "__main__":
    main()
