#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Figure 2: Individual Strategy (Simplified)
------------------------------------------
Panel A: Neural Gating (GLM Slopes) - Grouped Bar Plot
Panel B: Prediction Failure (MMN Proxy) - Boxplot + Stripplot (Boss)

Inputs:
    - derivatives/analysis/mmn_regression/regression_stats_refined.csv
    - derivatives/MMN/stats_comparison_summary.csv
    - derivatives/predictors/**/predictors_*.csv (For MDL mapping)

Outputs:
    - figures/Figure2_IndividualStrategy.png
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# --- CONFIG ---
DERIVATIVES_ROOT = Path("derivatives")
OUT_DIR = Path("figures") # Updated output directory
OUT_FILE = OUT_DIR / "Figure2_IndividualStrategy.png"

# Panel A Input
REG_STATS_FILE = DERIVATIVES_ROOT / "analysis" / "mmn_regression" / "regression_stats_refined.csv"

# Panel B Input
MMN_STATS_FILE = DERIVATIVES_ROOT / "MMN" / "stats_comparison_summary.csv"
PREDICTORS_DIR = DERIVATIVES_ROOT / "predictors"

SHORT_LENGTHS = [4, 6, 8]
LONG_LENGTHS = [12, 16]

def load_mdl_mapping():
    """Extract (Grammar, Length) -> MDL mapping from predictor CSVs."""
    mapping = {}
    csv_files = list(PREDICTORS_DIR.glob("**/*.csv"))
    for f in csv_files:
        try:
            df = pd.read_csv(f, usecols=['grammar', 'length', 'mdl'], nrows=2)
            if not df.empty:
                g = df['grammar'].iloc[0]
                l = int(df['length'].iloc[0])
                m = df['mdl'].iloc[0]
                mapping[(g, l)] = m
        except Exception:
            continue
    return mapping

def plot_subject_mmn_regression(subject, df_plot, gs, row, fig, share_y_ax=None):
    """Plot trial-level MMN regression for Short and Long sequences for a specific subject."""
    ax1 = fig.add_subplot(gs[row, 1], sharey=share_y_ax)
    ax2 = fig.add_subplot(gs[row, 2], sharey=ax1)
    
    # Filter for Subject, Auditory, Early
    df_subj = df_plot[
        (df_plot['Subject'] == subject) &
        (df_plot['ROI'] == 'Auditory') &
        (df_plot['Window'] == 'early')
    ].copy()
    
    # Split Data
    df_short = df_subj[df_subj['Length'].isin(SHORT_LENGTHS)].copy()
    df_long = df_subj[df_subj['Length'].isin(LONG_LENGTHS)].copy()
    
    # --- Short ---
    unique_mdls_s = sorted(df_short['MDL'].unique())
    mdl_to_idx_s = {m: i for i, m in enumerate(unique_mdls_s)}
    df_short['MDL_idx'] = df_short['MDL'].map(mdl_to_idx_s)

    sns.boxplot(data=df_short, x='MDL', y='ToneBase_peak', ax=ax1, color='#1f77b4', boxprops=dict(alpha=.3), showfliers=False)
    sns.stripplot(data=df_short, x='MDL', y='ToneBase_peak', ax=ax1, color='#1f77b4', alpha=0.6, jitter=True)
    sns.regplot(data=df_short, x='MDL_idx', y='ToneBase_peak', ax=ax1, scatter=False, color='#1f77b4', line_kws={'linewidth': 4})
    
    ax1.axhline(0, color='black', linewidth=1, linestyle='--', alpha=0.5)
    ax1.set_title(f"{subject}: Short (4-8)", fontsize=12, color='#1f77b4', fontweight='bold')
    ax1.set_xlabel("Complexity (MDL)")
    ax1.set_ylabel("MMN Amp (uV)" if subject == 'Boss' else "")
    ax1.set_xticklabels(unique_mdls_s)

    # --- Long ---
    unique_mdls_l = sorted(df_long['MDL'].unique())
    mdl_to_idx_l = {m: i for i, m in enumerate(unique_mdls_l)}
    df_long['MDL_idx'] = df_long['MDL'].map(mdl_to_idx_l)

    sns.boxplot(data=df_long, x='MDL', y='ToneBase_peak', ax=ax2, color='#d62728', boxprops=dict(alpha=.3), showfliers=False)
    sns.stripplot(data=df_long, x='MDL', y='ToneBase_peak', ax=ax2, color='#d62728', alpha=0.6, jitter=True)
    sns.regplot(data=df_long, x='MDL_idx', y='ToneBase_peak', ax=ax2, scatter=False, color='#d62728', line_kws={'linewidth': 4})
    
    ax2.axhline(0, color='black', linewidth=1, linestyle='--', alpha=0.5)
    ax2.set_title(f"{subject}: Long (12-16)", fontsize=12, color='#d62728', fontweight='bold')
    ax2.set_xlabel("Complexity (MDL)")
    ax2.set_ylabel("")
    ax2.set_yticklabels([])
    ax2.set_xticklabels(unique_mdls_l)
    
    return ax1

def generate_figure():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    fig = plt.figure(figsize=(18, 12)) 
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
    
    # --- Panel A: Neural Gating (Column 0, Rows 0 & 1) ---
    ax_a = fig.add_subplot(gs[:, 0])
    print("Generating Panel A...")
    
    if REG_STATS_FILE.exists():
        df_reg = pd.read_csv(REG_STATS_FILE)
        df_a = df_reg[
            (df_reg['ROI'] == 'Auditory') & 
            (df_reg['Metric'] == 'ToneBase_peak') &
            (df_reg['Window'] == 'early')
        ].copy()
        
        strat_colors = {'Efficiency': '#2ca02c', 'Recruitment': '#ff7f0e'}
        df_a['Strategy'] = df_a['Subject'].map({'Boss': 'Efficiency', 'Carol': 'Recruitment'})
        
        sns.barplot(data=df_a, x='Subject', y='Slope', hue='Group', 
                    palette={'Short': '#1f77b4', 'Long': '#d62728'},
                    ax=ax_a, edgecolor='black')
        
        for i, subj in enumerate(['Boss', 'Carol']):
            strat = 'Efficiency Mode' if subj == 'Boss' else 'Recruitment Mode'
            color = strat_colors['Efficiency'] if subj == 'Boss' else strat_colors['Recruitment']
            ax_a.text(i, ax_a.get_ylim()[1]*0.9, strat, ha='center', fontsize=14, fontweight='bold', color=color)
        
        ax_a.axhline(0, color='black', linewidth=1.5, linestyle='-')
        ax_a.set_title("Neural Gating Slopes", fontsize=16, fontweight='bold')
        ax_a.set_ylabel("Encoding Strength (Slope)")
        ax_a.legend(title="Seq Type", loc='lower center', frameon=True)
    else:
        ax_a.text(0.5, 0.5, "Stats Missing", ha='center')

    # --- Panel B/C: Trial-level MMN (Columns 1 & 2) ---
    print("Generating Trial-level Plots...")
    if MMN_STATS_FILE.exists():
        df_mmn = pd.read_csv(MMN_STATS_FILE)
        mdl_map = load_mdl_mapping()
        df_mmn['MDL'] = df_mmn.apply(lambda x: mdl_map.get((x['Grammar'], x['Length']), np.nan), axis=1)
        df_plot = df_mmn.dropna(subset=['MDL']).copy()
        
        # Plot Boss
        ax_boss = plot_subject_mmn_regression('Boss', df_plot, gs, 0, fig)
        
        # Plot Carol (Shared Y with Boss for comparison)
        plot_subject_mmn_regression('Carol', df_plot, gs, 1, fig, share_y_ax=ax_boss)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.suptitle("Individual Strategies for Handling Sequence Complexity", fontsize=20, fontweight='bold')
    plt.savefig(OUT_FILE)
    print(f"Figure saved to {OUT_FILE}")

if __name__ == "__main__":
    generate_figure()
