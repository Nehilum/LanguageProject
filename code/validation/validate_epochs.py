#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validation Script: Epoching (Phase 2)
------------------------------------
Visualizes Averaged Epochs (ERPs) and Stratified Selection Matching.
"""

import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter

def plot_erp(erp_data, fs, ch_names, title, filename):
    """Plot Grand Average ERP and Channel Traces."""
    # erp_data: (Epochs, Time, Channels)
    # Average across epochs
    evoked = np.mean(erp_data, axis=0) # (Time, Channels)
    
    t = np.arange(evoked.shape[0]) / fs - 0.2 # -0.2s start
    
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))
    
    # Butterfly Plot
    ax = axes[0]
    ax.plot(t, evoked, linewidth=0.5, alpha=0.8)
    ax.set_title(f"{title} - Butterfly Plot ({erp_data.shape[0]} epochs)")
    ax.set_ylabel("Amplitude")
    ax.axvline(0, color='k', linestyle='--')
    
    # Global Field Power
    gfp = np.std(evoked, axis=1)
    ax = axes[1]
    ax.plot(t, gfp, color='k', linewidth=1.5)
    ax.fill_between(t, gfp, color='k', alpha=0.1)
    ax.set_title("Global Field Power (GFP)")
    ax.set_xlabel("Time (s)")
    ax.axvline(0, color='k', linestyle='--')
    
    plt.tight_layout()
    plt.savefig(filename)
    print(f"Saved {filename}")

def plot_matching(meta, title, filename):
    """Plot Session Counts for Standard vs Violation."""
    # Extract session and type
    sessions = [m['session_id'] for m in meta]
    types = [m['type'] for m in meta]
    
    # Count (Sess, Type)
    c = Counter(zip(sessions, types))
    
    # Unique sessions
    unique_sess = sorted(list(set(sessions)))
    
    viol_counts = [c[(s, 'violation')] for s in unique_sess]
    std_counts = [c[(s, 'standard')] for s in unique_sess]
    hab_counts = [c[(s, 'habituation')] for s in unique_sess]
    
    x = np.arange(len(unique_sess))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width, viol_counts, width, label='Violation')
    ax.bar(x, std_counts, width, label='Standard')
    ax.bar(x + width, hab_counts, width, label='Habituation')
    
    ax.set_ylabel('Trial Count')
    ax.set_title(f"{title} - Stratified Selection Check")
    ax.set_xticks(x)
    ax.set_xticklabels(unique_sess, rotation=90)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(filename)
    print(f"Saved {filename}")

def validate_epochs(npz_file):
    print(f"Validating {npz_file}...")
    data = np.load(npz_file, allow_pickle=True)
    erp = data['erp_epochs']
    meta = data['meta']
    fs = data['fs']
    ch_names = data['channel_names']
    
    cond = meta[0]['condition']
    subj = meta[0]['subject']
    ver = meta[0]['seq_ver']
    
    out_dir = Path("validation_outputs")
    out_dir.mkdir(exist_ok=True)
    
    # 1. ERP
    plot_erp(erp, fs, ch_names, f"ERP: {subj} {cond} {ver}", out_dir / f"ERP_{subj}_{ver}.png")
    
    # 2. Matching
    plot_matching(meta, f"Matching: {subj} {cond} {ver}", out_dir / f"Match_{subj}_{ver}.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to epochs.npz file")
    args = parser.parse_args()
    validate_epochs(args.file)
