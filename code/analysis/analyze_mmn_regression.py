#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MMN Regression Analysis
-----------------------
Correlates MMN metrics (Peak, AUC) with sequence complexity (MDL).
Splits analysis into Short (4, 6, 8) and Long (12, 16) sequences.

Inputs:
    - derivatives/MMN/stats_comparison_summary.csv
    - derivatives/predictors/**/predictors_*.csv

Outputs:
    - derivatives/analysis/mmn_regression/regression_stats_peak.csv
    - derivatives/analysis/mmn_regression/regression_stats_auc.csv
    - derivatives/analysis/mmn_regression/regression_plots.png
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.stats import linregress

# --- CONFIG ---
DERIVATIVES_ROOT = Path("derivatives")
MMN_STATS_FILE = DERIVATIVES_ROOT / "MMN" / "stats_comparison_summary.csv"
PREDICTORS_DIR = DERIVATIVES_ROOT / "predictors"
OUT_DIR = DERIVATIVES_ROOT / "analysis" / "mmn_regression"

SHORT_LENGTHS = [4, 6, 8]
LONG_LENGTHS = [12, 16]
SUBJECTS = ['Boss', 'Carol']

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

def perform_regression(df, metric_col, group_name, subject_name):
    """Perform linear regression for a group/subject."""
    results = []
    # Group by ROI and Window
    for (roi, win), group in df.groupby(['ROI', 'Window']):
        # Drop NaNs
        valid = group.dropna(subset=['MDL', metric_col])
        if len(valid) < 3:
            continue
            
        slope, intercept, r_value, p_value, std_err = linregress(valid['MDL'], valid[metric_col])
        
        results.append({
            'Subject': subject_name,
            'Group': group_name,
            'ROI': roi,
            'Window': win,
            'Metric': metric_col,
            'Slope': slope,
            'R': r_value,
            'R2': r_value**2,
            'p-value': p_value,
            'N': len(valid)
        })
    return results

def main():
    if not MMN_STATS_FILE.exists():
        print(f"Error: {MMN_STATS_FILE} not found. Run analysis_mmn_roi.py first.")
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Load MMN Stats
    df_raw = pd.read_csv(MMN_STATS_FILE)
    
    # 2. Add MDL
    mdl_map = load_mdl_mapping()
    df_raw['MDL'] = df_raw.apply(lambda x: mdl_map.get((x['Grammar'], x['Length']), np.nan), axis=1)
    df_raw = df_raw.dropna(subset=['MDL'])
    
    # Metrics to analyze: PRIORITIZE TONEBASE (Local Baseline)
    metrics = ['ToneBase_peak', 'ToneBase_auc', 'ToneBase_diff']
    
    all_reg_results = []
    
    # 3. Process EACH Subject separately
    for subj in SUBJECTS:
        subj_df = df_raw[df_raw['Subject'] == subj].copy()
        if subj_df.empty: continue
        
        df_short = subj_df[subj_df['Length'].isin(SHORT_LENGTHS)]
        df_long = subj_df[subj_df['Length'].isin(LONG_LENGTHS)]
        
        for m in metrics:
            all_reg_results.extend(perform_regression(df_short, m, 'Short', subj))
            all_reg_results.extend(perform_regression(df_long, m, 'Long', subj))
            
    # Save Results
    reg_df = pd.DataFrame(all_reg_results)
    reg_df.to_csv(OUT_DIR / "regression_stats_refined.csv", index=False)
            
    # 4. Plotting (Subject-specific figures)
    sns.set_context("talk")
    sns.set_style("whitegrid")
    
    plot_metrics = ['ToneBase_peak', 'ToneBase_auc']
    
    for subj in SUBJECTS:
        subj_df = df_raw[df_raw['Subject'] == subj].copy()
        if subj_df.empty: continue
        
        # Sort by MDL for cleaner plotting
        subj_df = subj_df.sort_values('MDL')
        
        fig, axes = plt.subplots(len(plot_metrics), 2, figsize=(16, 12), sharex=True)
        fig.suptitle(f"MMN-proxy Analysis: Subject {subj}", fontsize=20)
        
        for i, m in enumerate(plot_metrics):
            for j, group_name in enumerate(['Short', 'Long']):
                ax = axes[i, j]
                lengths = SHORT_LENGTHS if group_name == 'Short' else LONG_LENGTHS
                plot_df = subj_df[(subj_df['Length'].isin(lengths)) & 
                                 (subj_df['ROI'] == 'Auditory') & 
                                 (subj_df['Window'] == 'early')]
                
                if plot_df.empty: continue
                
                # Action D: Boxplot + Stripplot (Jitter)
                sns.boxplot(data=plot_df, x='MDL', y=m, ax=ax, palette="vlag", showfliers=False)
                sns.stripplot(data=plot_df, x='MDL', y=m, ax=ax, color=".3", alpha=0.5, jitter=True)
                
                # Add Regression Line (manually or via regplot on discrete points)
                # Note: regplot on discrete x still works but we want to show it over the boxes
                # We'll use numerical X for the reg line
                # sns.regplot handles this by mapping x to numeric
                sns.regplot(data=plot_df, x='MDL', y=m, ax=ax, scatter=False, color='red', truncate=False)

                # Add stats summary
                info = reg_df[(reg_df['Subject'] == subj) & (reg_df['Metric'] == m) & 
                              (reg_df['Group'] == group_name) & (reg_df['ROI'] == 'Auditory') & 
                              (reg_df['Window'] == 'early')]
                if not info.empty:
                    res = info.iloc[0]
                    ax.set_title(f"{group_name} {m}\nR={res['R']:.2f}, p={res['p-value']:.3f}")
                
                ax.set_ylabel("Amplitude" if 'peak' in m else "AUC")
                if i == len(plot_metrics)-1:
                    ax.set_xlabel("Complexity (MDL)")

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        fig.savefig(OUT_DIR / f"regression_plots_{subj}.png")
        plt.close(fig)

    print(f"Saved refined results and subject-specific plots to {OUT_DIR}")

if __name__ == "__main__":
    main()
