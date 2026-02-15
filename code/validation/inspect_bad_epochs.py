#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validation Script: Inspect Bad Epochs
------------------------------------
Loads a preproc file, cuts epochs (with rejection tracking),
and visualizes examples of Rejected Epochs.
"""

import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import random

# Add project root/code to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from epoching.cut_epoch_unified import cut_epochs_file

def plot_bad_epoch(epoch_data, ch_names, fs, filename):
    """
    Plot signal and mask for a bad epoch.
    epoch_data: dict with 'signal', 'mask', 'meta'
    """
    sig = epoch_data['signal'] # (Time, Ch)
    mask = epoch_data['mask']  # (Time, Ch)
    meta = epoch_data['meta']
    
    t = np.arange(sig.shape[0]) / fs - 0.2
    
    # Plot
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})
    
    # 1. Signals (Butterfly)
    ax = axes[0]
    ax.plot(t, sig, linewidth=0.5, alpha=0.6, color='gray')
    
    # Highlight bad parts?
    # Where mask is True, plot in Red?
    # That's complicated for butterfly.
    # Just standard butterfly.
    
    ax.set_title(f"Bad Epoch: {meta['reject_reason']} (Pos {meta['pos']} {meta['type']})")
    ax.set_ylabel("Amplitude")
    ax.axvline(0, color='k', linestyle='--')
    
    # 2. Mask (Image)
    ax = axes[1]
    # mask is Time x Ch. Transpose for Ch x Time
    im = ax.imshow(mask.T, aspect='auto', interpolation='nearest', 
                   extent=[t[0], t[-1], 0, mask.shape[1]], origin='lower', cmap='Reds', vmin=0, vmax=1)
    ax.set_ylabel("Channel Index")
    ax.set_xlabel("Time (s)")
    ax.set_title(f"Artifact Mask (Mean Coverage: {np.mean(mask):.2f})")
    
    plt.tight_layout()
    plt.savefig(filename)
    print(f"Saved {filename}")
    plt.close(fig)

def inspect_bad(npz_file):
    print(f"Inspecting {npz_file}...")
    
    # Infer Condition/Subject/Stem
    # Path: derivatives/preproc/<Condition>/<Subject>/<Stem>_preproc.npz
    path_obj = Path(npz_file)
    stem = path_obj.stem # X_preproc
    subj = path_obj.parent.name
    cond = path_obj.parent.parent.name
    
    # Run Cut with Rejection
    dataset, chs, rejected = cut_epochs_file(path_obj, cond, subj, return_rejected=True)
    
    print(f"Good Epochs: {len(dataset)}")
    print(f"Rejected Epochs: {len(rejected)}")
    
    if not rejected:
        print("No rejected epochs found.")
        return

    # Pick random 5
    n_plot = min(5, len(rejected))
    # indices = random.sample(range(len(rejected)), n_plot)
    # Just take first 5 to be deterministic or consistent?
    indices = range(n_plot)
    
    out_dir = Path("validation_outputs")
    out_dir.mkdir(exist_ok=True)
    
    fs = 250.0 # From cut_epoch
    
    for i in indices:
        ep = rejected[i]
        fname = out_dir / f"BadEpoch_{stem}_{i}.png"
        plot_bad_epoch(ep, chs, fs, fname)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to _preproc.npz file")
    args = parser.parse_args()
    inspect_bad(args.file)
