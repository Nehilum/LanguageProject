#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Regime Shift Schematic
===============================
Visualizes the "Sustained State" and "Precision Hypothesis".

Panels:
A. Pre-stimulus State (-200 to 0ms): Baseline Variance/Power differences.
B. Morphology (Tone 1): Sharpening (FWHM) vs Blurring. Annotated with arrows/tangents.
C. Precision Hypothesis (Conceptual): Gaussian distributions (High vs Low Precision).
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

OUT_DIR = "derivatives/gating/plots"
os.makedirs(OUT_DIR, exist_ok=True)

def generate_schematic():
    fig = plt.figure(figsize=(15, 5))
    gs = fig.add_gridspec(1, 3)
    
    # --- Panel A: Pre-stimulus State (Simulated Data for Schematic) ---
    ax1 = fig.add_subplot(gs[0, 0])
    
    t_base = np.linspace(-0.2, 0, 100)
    # Short: Low variance, tight baseline
    noise_short = np.random.normal(0, 0.5, 100)
    # Long: High variance, noisy baseline
    noise_long = np.random.normal(0, 1.5, 100)
    
    ax1.plot(t_base * 1000, noise_short, color='blue', alpha=0.6, label='Short (Low Var)')
    ax1.plot(t_base * 1000, noise_long, color='red', alpha=0.6, label='Long (High Var)')
    
    ax1.set_title("A. Pre-stimulus State (Proactive)", loc='left', fontweight='bold')
    ax1.set_xlabel("Time (ms)")
    ax1.set_ylabel("Amplitude (uV)")
    ax1.legend()
    ax1.set_ylim(-4, 4)
    ax1.axvline(0, color='k', linestyle='--')
    ax1.text(-100, 3, "Baseline Separation", ha='center')
    
    # --- Panel B: Morphology (Simulated/Idealized ERP for Clarity) ---
    ax2 = fig.add_subplot(gs[0, 1])
    
    t_erp = np.linspace(0, 0.2, 200)
    # Short: Sharp peak
    erp_short = 5 * np.exp(-((t_erp - 0.1)**2) / (2 * 0.015**2))
    # Long: Wide, lower peak
    erp_long = 3 * np.exp(-((t_erp - 0.1)**2) / (2 * 0.035**2))
    
    ax2.plot(t_erp * 1000, erp_short, color='blue', linewidth=2, label='Short')
    ax2.plot(t_erp * 1000, erp_long, color='red', linewidth=2, label='Long')
    
    # FWHM Arrows
    # Short FWHM
    hm_short = 2.5
    t1_s = 0.1 - 0.015 * np.sqrt(2 * np.log(5/2.5))
    t2_s = 0.1 + 0.015 * np.sqrt(2 * np.log(5/2.5))
    ax2.annotate('', xy=(t1_s*1000, hm_short), xytext=(t2_s*1000, hm_short),
                 arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
    ax2.text(100, hm_short+0.2, "Narrow FWHM", color='blue', ha='center', fontsize=8)

    # Long FWHM
    hm_long = 1.5
    t1_l = 0.1 - 0.035 * np.sqrt(2 * np.log(3/1.5))
    t2_l = 0.1 + 0.035 * np.sqrt(2 * np.log(3/1.5))
    ax2.annotate('', xy=(t1_l*1000, hm_long), xytext=(t2_l*1000, hm_long),
                 arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax2.text(100, hm_long-0.5, "Wide FWHM", color='red', ha='center', fontsize=8)

    # Rise Slope Tangent (Visual)
    # Short Start to Peak
    ax2.plot([50, 100], [0, 5], color='blue', linestyle=':', alpha=0.5)
    # Long Start to Peak
    ax2.plot([50, 100], [0, 3], color='red', linestyle=':', alpha=0.5)
    
    ax2.set_title("B. Morphology (Sharpening)", loc='left', fontweight='bold')
    ax2.set_xlabel("Time (ms)")
    ax2.legend()
    
    # --- Panel C: Precision Hypothesis (Conceptual) ---
    ax3 = fig.add_subplot(gs[0, 2])
    
    x = np.linspace(-4, 4, 100)
    # Short: High Precision (Low Variance)
    pdf_short = stats.norm.pdf(x, 0, 0.8)
    # Long: Low Precision (High Variance)
    pdf_long = stats.norm.pdf(x, 0, 2.0)
    
    ax3.plot(x, pdf_short, color='blue', linewidth=2, label='Short (High Precision)')
    ax3.fill_between(x, pdf_short, color='blue', alpha=0.1)
    
    ax3.plot(x, pdf_long, color='red', linewidth=2, label='Long (Low Precision)')
    ax3.fill_between(x, pdf_long, color='red', alpha=0.1)
    
    ax3.set_title("C. Precision Hypothesis", loc='left', fontweight='bold')
    ax3.set_xlabel("Prediction Error")
    ax3.set_ylabel("Probability Density")
    ax3.set_yticks([]) # Conceptual
    ax3.legend(loc='upper right', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "Regime_Shift_Schematic.png"), dpi=300)
    plt.close()
    print("Schematic Generated.")

if __name__ == "__main__":
    generate_schematic()
