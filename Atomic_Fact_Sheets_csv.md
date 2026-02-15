# Atomic Fact Sheets — CSV Data

**Generated:** 2026-02-15T10:55 JST  
**Total CSV files audited:** 81  
**Sampling Rate (FS):** 500 Hz (2 ms resolution)  

---

## Step B: Quick Screening (Uncorrected GLM Stats)

**Script:** `run_glm_stats.py`  
**Description:** Uncorrected T>1.96 temporal cluster identification across ROI-level T-statistics.

### B: stats_erp_baseglobal_ModelA.csv
- **Target File**: `derivatives/glm_results/stats_erp_baseglobal_ModelA.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Predictor', 'Start_s', 'End_s', 'Duration_s', 'Peak_T', 'Cluster_Mass', 'Significant_unc']`
    - Shape: 302 rows × 9 columns
- **Full Data Table / Statistical Summary**:

**Shape: 302 rows × 9 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Start_s | 302 | 0.290093 | 0.295142 | -0.2 | 0.0455 | 0.31 | 0.5325 | 0.798 |
| End_s | 302 | 0.342007 | 0.290036 | -0.196 | 0.089 | 0.366 | 0.58 | 0.798 |
| Duration_s | 302 | 0.0519139 | 0.187471 | 0 | 0.002 | 0.006 | 0.0155 | 0.998 |
| Peak_T | 302 | 6.29853 | 42.5226 | -34.2605 | -2.44974 | 2.21564 | 3.01797 | 369.175 |
| Cluster_Mass | 302 | 3047.04 | 20397.9 | 1.96244 | 4.4783 | 10.3 | 26.2975 | 174906 |

- **Metadata Check**:
    - FS: 500 Hz (implicit, T-stats computed per 2ms timepoint)
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 3 → `['Auditory', 'M1', 'S1']`
    - Unique Predictor: 4 → `['Intercept', 'IsHab', 'Repetition', 'ToneID']`
- **Anomalies**: None detected.

---

### B: stats_erp_baseglobal_ModelB.csv
- **Target File**: `derivatives/glm_results/stats_erp_baseglobal_ModelB.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Predictor', 'Start_s', 'End_s', 'Duration_s', 'Peak_T', 'Cluster_Mass', 'Significant_unc']`
    - Shape: 729 rows × 9 columns
- **Full Data Table / Statistical Summary**:

**Shape: 729 rows × 9 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Start_s | 729 | 0.300568 | 0.295657 | -0.2 | 0.038 | 0.33 | 0.542 | 0.798 |
| End_s | 729 | 0.336982 | 0.291925 | -0.2 | 0.086 | 0.364 | 0.574 | 0.798 |
| Duration_s | 729 | 0.0364143 | 0.139311 | 0 | 0.002 | 0.006 | 0.014 | 0.998 |
| Peak_T | 729 | 1.02167 | 17.5251 | -34.2357 | -2.76546 | -2.06647 | 2.6786 | 228.572 |
| Cluster_Mass | 729 | 844.978 | 8173.21 | 1.9607 | 4.24702 | 10.006 | 22.6264 | 107681 |

- **Metadata Check**:
    - FS: 500 Hz (implicit, T-stats computed per 2ms timepoint)
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 3 → `['Auditory', 'M1', 'S1']`
    - Unique Predictor: 8 → `['Interaction', 'Intercept', 'IsHab', 'Length_c', 'Position_c', 'Repetition', 'Surprisal', 'ToneID']`
- **Anomalies**: None detected.

---

### B: stats_erp_baseglobal_ModelC.csv
- **Target File**: `derivatives/glm_results/stats_erp_baseglobal_ModelC.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Predictor', 'Start_s', 'End_s', 'Duration_s', 'Peak_T', 'Cluster_Mass', 'Significant_unc']`
    - Shape: 646 rows × 9 columns
- **Full Data Table / Statistical Summary**:

**Shape: 646 rows × 9 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Start_s | 646 | 0.283833 | 0.300628 | -0.2 | 0.0225 | 0.29 | 0.5415 | 0.798 |
| End_s | 646 | 0.321136 | 0.298616 | -0.196 | 0.0705 | 0.33 | 0.5755 | 0.798 |
| Duration_s | 646 | 0.0373034 | 0.143709 | 0 | 0.002 | 0.008 | 0.016 | 0.998 |
| Peak_T | 646 | 1.12747 | 20.102 | -34.1554 | -2.93409 | -2.15431 | 2.51281 | 249.435 |
| Cluster_Mass | 646 | 1022.16 | 9441.61 | 1.96239 | 4.43857 | 11.3759 | 25.8345 | 118190 |

- **Metadata Check**:
    - FS: 500 Hz (implicit, T-stats computed per 2ms timepoint)
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 3 → `['Auditory', 'M1', 'S1']`
    - Unique Predictor: 7 → `['Intercept', 'IsDeviant', 'IsHab', 'MDL', 'Position_c', 'Repetition', 'ToneID']`
- **Anomalies**: None detected.

---

### B: stats_erp_baseglobal_ModelD.csv
- **Target File**: `derivatives/glm_results/stats_erp_baseglobal_ModelD.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Predictor', 'Start_s', 'End_s', 'Duration_s', 'Peak_T', 'Cluster_Mass', 'Significant_unc']`
    - Shape: 707 rows × 9 columns
- **Full Data Table / Statistical Summary**:

**Shape: 707 rows × 9 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Start_s | 707 | 0.296025 | 0.300699 | -0.2 | 0.034 | 0.312 | 0.55 | 0.798 |
| End_s | 707 | 0.337429 | 0.297338 | -0.2 | 0.076 | 0.36 | 0.594 | 0.798 |
| Duration_s | 707 | 0.0414031 | 0.157146 | 0 | 0.002 | 0.006 | 0.014 | 0.998 |
| Peak_T | 707 | 1.3696 | 15.9574 | -34.1251 | -2.58972 | 2.03661 | 2.86373 | 201.506 |
| Cluster_Mass | 707 | 815.519 | 7388.34 | 1.96023 | 4.38762 | 10.4732 | 23.1266 | 95256 |

- **Metadata Check**:
    - FS: 500 Hz (implicit, T-stats computed per 2ms timepoint)
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 3 → `['Auditory', 'M1', 'S1']`
    - Unique Predictor: 8 → `['Intercept', 'IsHab', 'Length_c', 'MDL', 'Position_c', 'Repetition', 'Surprisal', 'ToneID']`
- **Anomalies**: None detected.

---

### B: stats_erp_baselocal_ModelA.csv
- **Target File**: `derivatives/glm_results/stats_erp_baselocal_ModelA.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Predictor', 'Start_s', 'End_s', 'Duration_s', 'Peak_T', 'Cluster_Mass', 'Significant_unc']`
    - Shape: 270 rows × 9 columns
- **Full Data Table / Statistical Summary**:

**Shape: 270 rows × 9 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Start_s | 270 | 0.266874 | 0.293311 | -0.2 | 0.0065 | 0.279 | 0.496 | 0.798 |
| End_s | 270 | 0.322659 | 0.292982 | -0.198 | 0.085 | 0.348 | 0.5555 | 0.798 |
| Duration_s | 270 | 0.0557852 | 0.197469 | 0 | 0.002 | 0.006 | 0.016 | 0.998 |
| Peak_T | 270 | 7.21446 | 47.7382 | -36.2601 | -2.48442 | 2.13546 | 3.05875 | 368.676 |
| Cluster_Mass | 270 | 3486.82 | 22017.8 | 1.9644 | 4.61985 | 10.4524 | 29.6371 | 177217 |

- **Metadata Check**:
    - FS: 500 Hz (implicit, T-stats computed per 2ms timepoint)
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 3 → `['Auditory', 'M1', 'S1']`
    - Unique Predictor: 4 → `['Intercept', 'IsHab', 'Repetition', 'ToneID']`
- **Anomalies**: None detected.

---

### B: stats_erp_baselocal_ModelB.csv
- **Target File**: `derivatives/glm_results/stats_erp_baselocal_ModelB.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Predictor', 'Start_s', 'End_s', 'Duration_s', 'Peak_T', 'Cluster_Mass', 'Significant_unc']`
    - Shape: 680 rows × 9 columns
- **Full Data Table / Statistical Summary**:

**Shape: 680 rows × 9 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Start_s | 680 | 0.291244 | 0.292478 | -0.2 | 0.0385 | 0.289 | 0.526 | 0.798 |
| End_s | 680 | 0.327921 | 0.291112 | -0.2 | 0.09 | 0.342 | 0.563 | 0.798 |
| Duration_s | 680 | 0.0366765 | 0.139763 | 0 | 0.002 | 0.006 | 0.014 | 0.998 |
| Peak_T | 680 | 1.48435 | 19.1466 | -36.2744 | -2.66875 | 1.98512 | 2.65893 | 226.765 |
| Cluster_Mass | 680 | 921.719 | 8639.4 | 1.96052 | 4.41702 | 10.2916 | 23.8521 | 108892 |

- **Metadata Check**:
    - FS: 500 Hz (implicit, T-stats computed per 2ms timepoint)
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 3 → `['Auditory', 'M1', 'S1']`
    - Unique Predictor: 8 → `['Interaction', 'Intercept', 'IsHab', 'Length_c', 'Position_c', 'Repetition', 'Surprisal', 'ToneID']`
- **Anomalies**: None detected.

---

### B: stats_erp_baselocal_ModelC.csv
- **Target File**: `derivatives/glm_results/stats_erp_baselocal_ModelC.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Predictor', 'Start_s', 'End_s', 'Duration_s', 'Peak_T', 'Cluster_Mass', 'Significant_unc']`
    - Shape: 593 rows × 9 columns
- **Full Data Table / Statistical Summary**:

**Shape: 593 rows × 9 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Start_s | 593 | 0.266927 | 0.297088 | -0.2 | -0.004 | 0.272 | 0.514 | 0.798 |
| End_s | 593 | 0.306712 | 0.29735 | -0.2 | 0.046 | 0.304 | 0.554 | 0.798 |
| Duration_s | 593 | 0.0397841 | 0.14621 | 0 | 0.002 | 0.008 | 0.018 | 0.998 |
| Peak_T | 593 | 1.71475 | 22.2839 | -36.298 | -2.86893 | -2.04956 | 2.71109 | 248.444 |
| Cluster_Mass | 593 | 1137.17 | 10048 | 1.9622 | 4.71794 | 12.028 | 28.9546 | 119703 |

- **Metadata Check**:
    - FS: 500 Hz (implicit, T-stats computed per 2ms timepoint)
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 3 → `['Auditory', 'M1', 'S1']`
    - Unique Predictor: 7 → `['Intercept', 'IsDeviant', 'IsHab', 'MDL', 'Position_c', 'Repetition', 'ToneID']`
- **Anomalies**: None detected.

---

### B: stats_erp_baselocal_ModelD.csv
- **Target File**: `derivatives/glm_results/stats_erp_baselocal_ModelD.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Predictor', 'Start_s', 'End_s', 'Duration_s', 'Peak_T', 'Cluster_Mass', 'Significant_unc']`
    - Shape: 693 rows × 9 columns
- **Full Data Table / Statistical Summary**:

**Shape: 693 rows × 9 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Start_s | 693 | 0.289737 | 0.297534 | -0.2 | 0.016 | 0.3 | 0.538 | 0.798 |
| End_s | 693 | 0.329911 | 0.295954 | -0.2 | 0.058 | 0.346 | 0.58 | 0.798 |
| Duration_s | 693 | 0.0401732 | 0.152185 | 0 | 0.002 | 0.006 | 0.014 | 0.998 |
| Peak_T | 693 | 1.43805 | 17.077 | -36.1453 | -2.58629 | 2.06106 | 2.72777 | 200.002 |
| Cluster_Mass | 693 | 844.194 | 7602.48 | 1.96044 | 4.37977 | 10.2407 | 22.3287 | 95722.5 |

- **Metadata Check**:
    - FS: 500 Hz (implicit, T-stats computed per 2ms timepoint)
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 3 → `['Auditory', 'M1', 'S1']`
    - Unique Predictor: 8 → `['Intercept', 'IsHab', 'Length_c', 'MDL', 'Position_c', 'Repetition', 'Surprisal', 'ToneID']`
- **Anomalies**: None detected.

---

### B: stats_hfa_baseglobal_ModelA.csv
- **Target File**: `derivatives/glm_results/stats_hfa_baseglobal_ModelA.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Predictor', 'Start_s', 'End_s', 'Duration_s', 'Peak_T', 'Cluster_Mass', 'Significant_unc']`
    - Shape: 411 rows × 9 columns
- **Full Data Table / Statistical Summary**:

**Shape: 411 rows × 9 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Start_s | 411 | 0.280234 | 0.297401 | -0.2 | 0.02 | 0.262 | 0.535 | 0.788 |
| End_s | 411 | 0.294141 | 0.29776 | -0.2 | 0.03 | 0.276 | 0.546 | 0.798 |
| Duration_s | 411 | 0.0139075 | 0.0226382 | 0 | 0.004 | 0.006 | 0.012 | 0.13 |
| Peak_T | 411 | 0.721984 | 3.55376 | -9.02032 | -2.42078 | 2.14744 | 2.83179 | 13.6987 |
| Cluster_Mass | 411 | 28.8152 | 56.6502 | 1.96002 | 5.99202 | 9.80578 | 19.8311 | 383.016 |

- **Metadata Check**:
    - FS: 500 Hz (implicit, T-stats computed per 2ms timepoint)
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 3 → `['Auditory', 'M1', 'S1']`
    - Unique Predictor: 4 → `['Intercept', 'IsHab', 'Repetition', 'ToneID']`
- **Anomalies**: None detected.

---

### B: stats_hfa_baseglobal_ModelB.csv
- **Target File**: `derivatives/glm_results/stats_hfa_baseglobal_ModelB.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Predictor', 'Start_s', 'End_s', 'Duration_s', 'Peak_T', 'Cluster_Mass', 'Significant_unc']`
    - Shape: 817 rows × 9 columns
- **Full Data Table / Statistical Summary**:

**Shape: 817 rows × 9 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Start_s | 817 | 0.288149 | 0.292739 | -0.2 | 0.024 | 0.282 | 0.55 | 0.79 |
| End_s | 817 | 0.298245 | 0.292504 | -0.2 | 0.036 | 0.292 | 0.554 | 0.796 |
| Duration_s | 817 | 0.0100955 | 0.0154665 | 0 | 0.002 | 0.006 | 0.01 | 0.114 |
| Peak_T | 817 | 0.061962 | 3.01231 | -7.68791 | -2.5449 | 1.97483 | 2.6069 | 10.2475 |
| Cluster_Mass | 817 | 18.1676 | 32.5642 | 1.96 | 4.54387 | 9.36225 | 16.9602 | 381.466 |

- **Metadata Check**:
    - FS: 500 Hz (implicit, T-stats computed per 2ms timepoint)
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 3 → `['Auditory', 'M1', 'S1']`
    - Unique Predictor: 8 → `['Interaction', 'Intercept', 'IsHab', 'Length_c', 'Position_c', 'Repetition', 'Surprisal', 'ToneID']`
- **Anomalies**: None detected.

---

### B: stats_hfa_baseglobal_ModelC.csv
- **Target File**: `derivatives/glm_results/stats_hfa_baseglobal_ModelC.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Predictor', 'Start_s', 'End_s', 'Duration_s', 'Peak_T', 'Cluster_Mass', 'Significant_unc']`
    - Shape: 685 rows × 9 columns
- **Full Data Table / Statistical Summary**:

**Shape: 685 rows × 9 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Start_s | 685 | 0.288044 | 0.297503 | -0.2 | 0.024 | 0.278 | 0.546 | 0.798 |
| End_s | 685 | 0.299518 | 0.297037 | -0.2 | 0.028 | 0.286 | 0.56 | 0.798 |
| Duration_s | 685 | 0.0114745 | 0.0175783 | 0 | 0.004 | 0.006 | 0.012 | 0.136 |
| Peak_T | 685 | 0.0417275 | 3.15815 | -9.22671 | -2.68133 | 1.97398 | 2.65522 | 10.2379 |
| Cluster_Mass | 685 | 20.9581 | 37.864 | 1.96061 | 6.25762 | 9.95533 | 18.7261 | 381.026 |

- **Metadata Check**:
    - FS: 500 Hz (implicit, T-stats computed per 2ms timepoint)
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 3 → `['Auditory', 'M1', 'S1']`
    - Unique Predictor: 7 → `['Intercept', 'IsDeviant', 'IsHab', 'MDL', 'Position_c', 'Repetition', 'ToneID']`
- **Anomalies**: None detected.

---

### B: stats_hfa_baseglobal_ModelD.csv
- **Target File**: `derivatives/glm_results/stats_hfa_baseglobal_ModelD.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Predictor', 'Start_s', 'End_s', 'Duration_s', 'Peak_T', 'Cluster_Mass', 'Significant_unc']`
    - Shape: 885 rows × 9 columns
- **Full Data Table / Statistical Summary**:

**Shape: 885 rows × 9 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Start_s | 885 | 0.287214 | 0.291571 | -0.2 | 0.034 | 0.282 | 0.536 | 0.794 |
| End_s | 885 | 0.297566 | 0.291336 | -0.198 | 0.042 | 0.29 | 0.542 | 0.798 |
| Duration_s | 885 | 0.0103525 | 0.014752 | 0 | 0.004 | 0.006 | 0.012 | 0.138 |
| Peak_T | 885 | -0.0592773 | 3.02776 | -7.7661 | -2.69402 | -1.97349 | 2.60562 | 10.2467 |
| Cluster_Mass | 885 | 18.1462 | 29.3408 | 1.96045 | 6.20767 | 10.0844 | 17.9017 | 381.315 |

- **Metadata Check**:
    - FS: 500 Hz (implicit, T-stats computed per 2ms timepoint)
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 3 → `['Auditory', 'M1', 'S1']`
    - Unique Predictor: 8 → `['Intercept', 'IsHab', 'Length_c', 'MDL', 'Position_c', 'Repetition', 'Surprisal', 'ToneID']`
- **Anomalies**: None detected.

---

### B: stats_hfa_baselocal_ModelA.csv
- **Target File**: `derivatives/glm_results/stats_hfa_baselocal_ModelA.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Predictor', 'Start_s', 'End_s', 'Duration_s', 'Peak_T', 'Cluster_Mass', 'Significant_unc']`
    - Shape: 418 rows × 9 columns
- **Full Data Table / Statistical Summary**:

**Shape: 418 rows × 9 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Start_s | 418 | 0.269933 | 0.305554 | -0.2 | -0.014 | 0.248 | 0.5405 | 0.788 |
| End_s | 418 | 0.282828 | 0.305538 | -0.196 | -0.008 | 0.262 | 0.5495 | 0.794 |
| Duration_s | 418 | 0.0128947 | 0.0208227 | 0 | 0.004 | 0.006 | 0.012 | 0.116 |
| Peak_T | 418 | 0.360043 | 3.56134 | -5.94237 | -2.62777 | 1.97951 | 2.72 | 14.4958 |
| Cluster_Mass | 418 | 26.8753 | 57.9087 | 1.96008 | 6.26243 | 10.1225 | 18.4189 | 398.072 |

- **Metadata Check**:
    - FS: 500 Hz (implicit, T-stats computed per 2ms timepoint)
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 3 → `['Auditory', 'M1', 'S1']`
    - Unique Predictor: 4 → `['Intercept', 'IsHab', 'Repetition', 'ToneID']`
- **Anomalies**: None detected.

---

### B: stats_hfa_baselocal_ModelB.csv
- **Target File**: `derivatives/glm_results/stats_hfa_baselocal_ModelB.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Predictor', 'Start_s', 'End_s', 'Duration_s', 'Peak_T', 'Cluster_Mass', 'Significant_unc']`
    - Shape: 797 rows × 9 columns
- **Full Data Table / Statistical Summary**:

**Shape: 797 rows × 9 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Start_s | 797 | 0.28006 | 0.296112 | -0.2 | 0.006 | 0.274 | 0.544 | 0.798 |
| End_s | 797 | 0.289295 | 0.296552 | -0.198 | 0.008 | 0.284 | 0.55 | 0.798 |
| Duration_s | 797 | 0.00923463 | 0.0149798 | 0 | 0.002 | 0.006 | 0.01 | 0.118 |
| Peak_T | 797 | -0.0618446 | 2.9514 | -5.96341 | -2.54493 | -1.98504 | 2.46559 | 10.7664 |
| Cluster_Mass | 797 | 16.8878 | 34.4993 | 1.96003 | 4.28053 | 9.01627 | 15.3193 | 383.698 |

- **Metadata Check**:
    - FS: 500 Hz (implicit, T-stats computed per 2ms timepoint)
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 3 → `['Auditory', 'M1', 'S1']`
    - Unique Predictor: 8 → `['Interaction', 'Intercept', 'IsHab', 'Length_c', 'Position_c', 'Repetition', 'Surprisal', 'ToneID']`
- **Anomalies**: None detected.

---

### B: stats_hfa_baselocal_ModelC.csv
- **Target File**: `derivatives/glm_results/stats_hfa_baselocal_ModelC.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Predictor', 'Start_s', 'End_s', 'Duration_s', 'Peak_T', 'Cluster_Mass', 'Significant_unc']`
    - Shape: 707 rows × 9 columns
- **Full Data Table / Statistical Summary**:

**Shape: 707 rows × 9 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Start_s | 707 | 0.276289 | 0.296956 | -0.2 | -0.006 | 0.258 | 0.54 | 0.798 |
| End_s | 707 | 0.285661 | 0.297105 | -0.198 | 0 | 0.268 | 0.549 | 0.798 |
| Duration_s | 707 | 0.00937199 | 0.0127664 | 0 | 0.002 | 0.006 | 0.01 | 0.118 |
| Peak_T | 707 | 0.301514 | 2.98342 | -6.989 | -2.53406 | 2.0526 | 2.63963 | 10.0004 |
| Cluster_Mass | 707 | 16.7332 | 28.9177 | 1.96456 | 4.70266 | 9.27748 | 16.285 | 383.797 |

- **Metadata Check**:
    - FS: 500 Hz (implicit, T-stats computed per 2ms timepoint)
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 3 → `['Auditory', 'M1', 'S1']`
    - Unique Predictor: 7 → `['Intercept', 'IsDeviant', 'IsHab', 'MDL', 'Position_c', 'Repetition', 'ToneID']`
- **Anomalies**: None detected.

---

### B: stats_hfa_baselocal_ModelD.csv
- **Target File**: `derivatives/glm_results/stats_hfa_baselocal_ModelD.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Predictor', 'Start_s', 'End_s', 'Duration_s', 'Peak_T', 'Cluster_Mass', 'Significant_unc']`
    - Shape: 892 rows × 9 columns
- **Full Data Table / Statistical Summary**:

**Shape: 892 rows × 9 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Start_s | 892 | 0.280173 | 0.297232 | -0.2 | 0.005 | 0.276 | 0.538 | 0.798 |
| End_s | 892 | 0.288984 | 0.297606 | -0.198 | 0.006 | 0.284 | 0.548 | 0.798 |
| Duration_s | 892 | 0.00881166 | 0.0120308 | 0 | 0.002 | 0.006 | 0.01 | 0.118 |
| Peak_T | 892 | 0.073989 | 2.91904 | -6.04175 | -2.57473 | 1.97607 | 2.58157 | 9.99922 |
| Cluster_Mass | 892 | 15.52 | 26.3926 | 1.96028 | 4.57401 | 9.40686 | 15.5421 | 383.594 |

- **Metadata Check**:
    - FS: 500 Hz (implicit, T-stats computed per 2ms timepoint)
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 3 → `['Auditory', 'M1', 'S1']`
    - Unique Predictor: 8 → `['Intercept', 'IsHab', 'Length_c', 'MDL', 'Position_c', 'Repetition', 'Surprisal', 'ToneID']`
- **Anomalies**: None detected.

---

## Step D: Gating Hypothesis (Complexity × Length)

**Script:** `analyze_gating_hypothesis.py`  
**Description:** Partial regression of Neural Response ~ MDL, controlling confounds, split by Short/Long.

### D (Gating Stats (Regime Shift Summary)): gating_stats_erp_baseglobal.csv
- **Target File**: `derivatives/analysis/gating/gating_stats_erp_baseglobal.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Length', 'Window', 'Slope_MDL', 'P_value', 'Suppression_Index']`
    - Shape: 20 rows × 7 columns
- **Full Data Table / Statistical Summary**:

**Shape: 20 rows × 7 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Length | 20 | 9.2 | 4.42005 | 4 | 6 | 8 | 12 | 16 |
| Slope_MDL | 20 | -0.0876546 | 0.166476 | -0.520922 | -0.0788583 | -0.030254 | 0.00531949 | 0.070868 |
| P_value | 20 | 0.205946 | 0.242879 | 2.46735e-10 | 3.02667e-05 | 0.151462 | 0.309493 | 0.643862 |
| Suppression_Index | 20 | 0.299967 | 0.600196 | -0.276642 | -0.0784447 | 0.0956828 | 0.536441 | 1.83189 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 1 → `['Auditory']`
- **Anomalies**: None detected.

---

### D (Gating Stats (Regime Shift Summary)): gating_stats_erp_baselocal.csv
- **Target File**: `derivatives/analysis/gating/gating_stats_erp_baselocal.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Length', 'Window', 'Slope_MDL', 'P_value', 'Suppression_Index']`
    - Shape: 20 rows × 7 columns
- **Full Data Table / Statistical Summary**:

**Shape: 20 rows × 7 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Length | 20 | 9.2 | 4.42005 | 4 | 6 | 8 | 12 | 16 |
| Slope_MDL | 20 | 0.0772497 | 0.327625 | -0.428394 | -0.0314706 | -0.00182785 | 0.0787285 | 1.01568 |
| P_value | 20 | 0.28684 | 0.340943 | 1.23499e-09 | 0.0120313 | 0.129415 | 0.547317 | 0.982628 |
| Suppression_Index | 20 | 0.0165527 | 1.12833 | -2.69734 | -0.244602 | -0.0409611 | 0.458591 | 2.40217 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 1 → `['Auditory']`
- **Anomalies**: None detected.

---

### D (Gating Stats (Regime Shift Summary)): gating_stats_hfa_baseglobal.csv
- **Target File**: `derivatives/analysis/gating/gating_stats_hfa_baseglobal.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Length', 'Window', 'Slope_MDL', 'P_value', 'Suppression_Index']`
    - Shape: 20 rows × 7 columns
- **Full Data Table / Statistical Summary**:

**Shape: 20 rows × 7 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Length | 20 | 9.2 | 4.42005 | 4 | 6 | 8 | 12 | 16 |
| Slope_MDL | 20 | 0.00480352 | 0.0161947 | -0.0312585 | -0.0025258 | 0.00231141 | 0.0147034 | 0.048204 |
| P_value | 20 | 0.152709 | 0.222412 | 2.14422e-05 | 0.00918769 | 0.0561438 | 0.193024 | 0.817382 |
| Suppression_Index | 20 | -0.0214742 | 0.0532741 | -0.125837 | -0.0484028 | -0.017805 | 0.00371363 | 0.078117 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 1 → `['Auditory']`
- **Anomalies**: None detected.

---

### D (Gating Stats (Regime Shift Summary)): gating_stats_hfa_baselocal.csv
- **Target File**: `derivatives/analysis/gating/gating_stats_hfa_baselocal.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'ROI', 'Length', 'Window', 'Slope_MDL', 'P_value', 'Suppression_Index']`
    - Shape: 20 rows × 7 columns
- **Full Data Table / Statistical Summary**:

**Shape: 20 rows × 7 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Length | 20 | 9.2 | 4.42005 | 4 | 6 | 8 | 12 | 16 |
| Slope_MDL | 20 | 0.00590279 | 0.0181126 | -0.0121723 | -0.00125122 | 0.000983976 | 0.00608054 | 0.0694503 |
| P_value | 20 | 0.482194 | 0.316491 | 0.00661181 | 0.23297 | 0.384693 | 0.781121 | 0.985669 |
| Suppression_Index | 20 | -0.0184495 | 0.0566006 | -0.20635 | -0.0176935 | -0.00265152 | 0.00389026 | 0.0371898 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique ROI: 1 → `['Auditory']`
- **Anomalies**: None detected.

---

### D (Gating Sliding Stats (Time-Resolved Slopes)): gating_sliding_stats_erp_baseglobal.csv
- **Target File**: `derivatives/analysis/gating/gating_sliding_stats_erp_baseglobal.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'Time_ms', 'Condition', 'Length', 'Slope_MDL', 'T_value', 'P_value']`
    - Shape: 3240 rows × 7 columns
- **Full Data Table / Statistical Summary**:

**Shape: 3240 rows × 7 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Time_ms | 3240 | 275 | 187.089 | -48 | 113.5 | 275 | 436.5 | 598 |
| Length | 3240 | 9.2 | 4.3088 | 4 | 6 | 8 | 12 | 16 |
| Slope_MDL | 3240 | -0.0827065 | 0.34306 | -1.78939 | -0.132694 | -0.0233045 | 0.0546666 | 1.29798 |
| T_value | 3240 | -0.433719 | 2.14272 | -7.31659 | -1.91967 | -0.537086 | 1.0513 | 6.71893 |
| P_value | 3240 | 0.257536 | 0.294043 | 2.86986e-13 | 0.0109806 | 0.126055 | 0.45384 | 0.997723 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: 2 → `['Boss', 'Carol']`
- **Anomalies**: None detected.

---

### D (Gating Sliding Stats (Time-Resolved Slopes)): gating_sliding_stats_erp_baselocal.csv
- **Target File**: `derivatives/analysis/gating/gating_sliding_stats_erp_baselocal.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'Time_ms', 'Condition', 'Length', 'Slope_MDL', 'T_value', 'P_value']`
    - Shape: 3240 rows × 7 columns
- **Full Data Table / Statistical Summary**:

**Shape: 3240 rows × 7 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Time_ms | 3240 | 275 | 187.089 | -48 | 113.5 | 275 | 436.5 | 598 |
| Length | 3240 | 9.2 | 4.3088 | 4 | 6 | 8 | 12 | 16 |
| Slope_MDL | 3240 | 0.0821979 | 0.433419 | -1.29113 | -0.0694614 | -0.00010093 | 0.1239 | 2.47943 |
| T_value | 3240 | 0.137668 | 2.20041 | -7.827 | -1.29853 | -0.00298846 | 1.42924 | 7.51839 |
| P_value | 3240 | 0.29518 | 0.3089 | 5.84737e-15 | 0.0144123 | 0.176747 | 0.537141 | 0.999789 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: 2 → `['Boss', 'Carol']`
- **Anomalies**: None detected.

---

### D (Gating Sliding Stats (Time-Resolved Slopes)): gating_sliding_stats_hfa_baseglobal.csv
- **Target File**: `derivatives/analysis/gating/gating_sliding_stats_hfa_baseglobal.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'Time_ms', 'Condition', 'Length', 'Slope_MDL', 'T_value', 'P_value']`
    - Shape: 3240 rows × 7 columns
- **Full Data Table / Statistical Summary**:

**Shape: 3240 rows × 7 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Time_ms | 3240 | 275 | 187.089 | -48 | 113.5 | 275 | 436.5 | 598 |
| Length | 3240 | 9.2 | 4.3088 | 4 | 6 | 8 | 12 | 16 |
| Slope_MDL | 3240 | 0.00500803 | 0.0225011 | -0.102515 | -0.00270171 | 0.00211193 | 0.0115047 | 0.1197 |
| T_value | 3240 | 0.467215 | 1.53842 | -4.45945 | -0.604431 | 0.489908 | 1.59499 | 4.96699 |
| P_value | 3240 | 0.340448 | 0.306283 | 6.85099e-07 | 0.053681 | 0.258174 | 0.588522 | 0.999889 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: 2 → `['Boss', 'Carol']`
- **Anomalies**: None detected.

---

### D (Gating Sliding Stats (Time-Resolved Slopes)): gating_sliding_stats_hfa_baselocal.csv
- **Target File**: `derivatives/analysis/gating/gating_sliding_stats_hfa_baselocal.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'Time_ms', 'Condition', 'Length', 'Slope_MDL', 'T_value', 'P_value']`
    - Shape: 3240 rows × 7 columns
- **Full Data Table / Statistical Summary**:

**Shape: 3240 rows × 7 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Time_ms | 3240 | 275 | 187.089 | -48 | 113.5 | 275 | 436.5 | 598 |
| Length | 3240 | 9.2 | 4.3088 | 4 | 6 | 8 | 12 | 16 |
| Slope_MDL | 3240 | 0.0061073 | 0.0242131 | -0.0812687 | -0.00293123 | 0.00130153 | 0.00760184 | 0.140946 |
| T_value | 3240 | 0.321754 | 1.24525 | -4.34732 | -0.546975 | 0.290248 | 1.20788 | 4.64763 |
| P_value | 3240 | 0.415706 | 0.3052 | 3.4281e-06 | 0.133808 | 0.37099 | 0.673357 | 0.999797 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: 2 → `['Boss', 'Carol']`
- **Anomalies**: None detected.

---

### D (Gating Waveforms): gating_waveforms_erp_baseglobal.csv
- **Target File**: `derivatives/analysis/gating/gating_waveforms_erp_baseglobal.csv`
- **Data Structure Discovery**:
    - Columns: `['Time', 'Subject', 'Length', 'MDL_Bin', 'Amplitude']`
    - Shape: 15000 rows × 5 columns
- **Full Data Table / Statistical Summary**:

**Shape: 15000 rows × 5 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Time | 15000 | 0.299 | 0.288684 | -0.2 | 0.0495 | 0.299 | 0.5485 | 0.798 |
| Length | 15000 | 9.2 | 4.30828 | 4 | 6 | 8 | 12 | 16 |
| Amplitude | 15000 | -0.146795 | 2.1028 | -8.60266 | -1.31503 | -0.0437318 | 1.25571 | 7.06934 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: 2 → `['Boss', 'Carol']`
- **Anomalies**: None detected.

---

### D (Gating Waveforms): gating_waveforms_erp_baselocal.csv
- **Target File**: `derivatives/analysis/gating/gating_waveforms_erp_baselocal.csv`
- **Data Structure Discovery**:
    - Columns: `['Time', 'Subject', 'Length', 'MDL_Bin', 'Amplitude']`
    - Shape: 15000 rows × 5 columns
- **Full Data Table / Statistical Summary**:

**Shape: 15000 rows × 5 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Time | 15000 | 0.299 | 0.288684 | -0.2 | 0.0495 | 0.299 | 0.5485 | 0.798 |
| Length | 15000 | 9.2 | 4.30828 | 4 | 6 | 8 | 12 | 16 |
| Amplitude | 15000 | -0.227397 | 2.32908 | -7.17146 | -1.74309 | -0.257069 | 1.10958 | 8.9807 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: 2 → `['Boss', 'Carol']`
- **Anomalies**: None detected.

---

### D (Gating Waveforms): gating_waveforms_hfa_baseglobal.csv
- **Target File**: `derivatives/analysis/gating/gating_waveforms_hfa_baseglobal.csv`
- **Data Structure Discovery**:
    - Columns: `['Time', 'Subject', 'Length', 'MDL_Bin', 'Amplitude']`
    - Shape: 15000 rows × 5 columns
- **Full Data Table / Statistical Summary**:

**Shape: 15000 rows × 5 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Time | 15000 | 0.299 | 0.288684 | -0.2 | 0.0495 | 0.299 | 0.5485 | 0.798 |
| Length | 15000 | 9.2 | 4.30828 | 4 | 6 | 8 | 12 | 16 |
| Amplitude | 15000 | 0.0307364 | 0.0734808 | -0.245721 | -0.0141885 | 0.0242985 | 0.069806 | 0.357872 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: 2 → `['Boss', 'Carol']`
- **Anomalies**: None detected.

---

### D (Gating Waveforms): gating_waveforms_hfa_baselocal.csv
- **Target File**: `derivatives/analysis/gating/gating_waveforms_hfa_baselocal.csv`
- **Data Structure Discovery**:
    - Columns: `['Time', 'Subject', 'Length', 'MDL_Bin', 'Amplitude']`
    - Shape: 15000 rows × 5 columns
- **Full Data Table / Statistical Summary**:

**Shape: 15000 rows × 5 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Time | 15000 | 0.299 | 0.288684 | -0.2 | 0.0495 | 0.299 | 0.5485 | 0.798 |
| Length | 15000 | 9.2 | 4.30828 | 4 | 6 | 8 | 12 | 16 |
| Amplitude | 15000 | 0.0146517 | 0.0674114 | -0.398449 | -0.0190299 | 0.010496 | 0.0486308 | 0.278371 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: 2 → `['Boss', 'Carol']`
- **Anomalies**: None detected.

---

## Step E: HFA–ERP Amplitude Coupling

**Script:** `analyze_gating_coupling.py`  
**Description:** Trial-by-trial Pearson r between HFA (240–260ms) and ERP (270–290ms) in Auditory ROI.

### E: coupling_stats_baseglobal.csv
- **Target File**: `derivatives/analysis/gating/coupling_stats_baseglobal.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'Group', 'Rho_value', 'P_value', 'N_trials']`
    - Shape: 4 rows × 5 columns
- **Full Data Table**:

| Subject | Group | Rho_value | P_value | N_trials |
| --- | --- | --- | --- | --- |
| Carol | Short | -0.0528132 | 3.07227e-07 | 9384 |
| Carol | Long | -0.0435226 | 2.61591e-22 | 49776 |
| Boss | Short | 0.0137143 | 0.184045 | 9384 |
| Boss | Long | 0.0209603 | 2.91455e-06 | 49776 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: `['Boss', 'Carol']`
    - Unique Group: `['Long', 'Short']`
- **Anomalies**: None detected.

---

### E: coupling_stats_baselocal.csv
- **Target File**: `derivatives/analysis/gating/coupling_stats_baselocal.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'Group', 'Rho_value', 'P_value', 'N_trials']`
    - Shape: 4 rows × 5 columns
- **Full Data Table**:

| Subject | Group | Rho_value | P_value | N_trials |
| --- | --- | --- | --- | --- |
| Carol | Short | -0.040382 | 9.11851e-05 | 9384 |
| Carol | Long | -0.0454365 | 3.59235e-24 | 49776 |
| Boss | Short | 0.0166588 | 0.106603 | 9384 |
| Boss | Long | 0.0239466 | 9.12958e-08 | 49776 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: `['Boss', 'Carol']`
    - Unique Group: `['Long', 'Short']`
- **Anomalies**: None detected.

---

## Step G: Phase–Amplitude Coupling (PAC)

**Script:** `analyze_pac.py`  
**Description:** Tort MI, 200 surrogates, 100 bootstrap iterations, Mirror Padding (0.5s), 18 phase bins.

### G: pac_stats_baseglobal.csv
- **Target File**: `derivatives/analysis/gating/pac_stats_baseglobal.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'Group', 'N_trials', 'MI_mean', 'MI_median', 'MI_std', 'U_stat', 'U_pvalue', 'MI_group_Short', 'MI_group_Long', 'MI_group_Short_std', 'MI_group_Long_std', 'N_subsampled', 'N_bootstrap', 'P_surr_Short', 'P_surr_Long']`
    - Shape: 6 rows × 16 columns
- **Full Data Table**:

| Subject | Group | N_trials | MI_mean | MI_median | MI_std | U_stat | U_pvalue | MI_group_Short | MI_group_Long | MI_group_Short_std | MI_group_Long_std | N_subsampled | N_bootstrap | P_surr_Short | P_surr_Long |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Boss | Short | 9384 | 0.00767434 | 0.0067941 | 0.00451176 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |
| Boss | Long | 49776 | 0.00795518 | 0.0069136 | 0.00497491 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |
| Boss | Short_vs_Long | 59160 | -0.000280846 | nan | nan | 2.27485e+08 | 6.44455e-05 | 7.84454e-07 | 2.92853e-07 | 1.44793e-11 | 9.85672e-08 | 9384 | 100 | 0 | 0.0003 |
| Carol | Short | 9384 | 0.0106418 | 0.00928496 | 0.00658134 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |
| Carol | Long | 49776 | 0.0108135 | 0.0093108 | 0.0068721 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |
| Carol | Short_vs_Long | 59160 | -0.00017165 | nan | nan | 2.31304e+08 | 0.139029 | 1.41165e-06 | 8.31499e-07 | 1.82556e-11 | 9.12506e-08 | 9384 | 100 | 0 | 0 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: `['Boss', 'Carol']`
    - Unique Group: `['Long', 'Short', 'Short_vs_Long']`
- **Anomalies**: NaN values detected: {'MI_median': 2, 'MI_std': 2, 'U_stat': 4, 'U_pvalue': 4, 'MI_group_Short': 4, 'MI_group_Long': 4, 'MI_group_Short_std': 4, 'MI_group_Long_std': 4, 'N_subsampled': 4, 'N_bootstrap': 4, 'P_surr_Short': 4, 'P_surr_Long': 4}

---

### G: pac_stats_baselocal.csv
- **Target File**: `derivatives/analysis/gating/pac_stats_baselocal.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'Group', 'N_trials', 'MI_mean', 'MI_median', 'MI_std', 'U_stat', 'U_pvalue', 'MI_group_Short', 'MI_group_Long', 'MI_group_Short_std', 'MI_group_Long_std', 'N_subsampled', 'N_bootstrap', 'P_surr_Short', 'P_surr_Long']`
    - Shape: 6 rows × 16 columns
- **Full Data Table**:

| Subject | Group | N_trials | MI_mean | MI_median | MI_std | U_stat | U_pvalue | MI_group_Short | MI_group_Long | MI_group_Short_std | MI_group_Long_std | N_subsampled | N_bootstrap | P_surr_Short | P_surr_Long |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Boss | Short | 9384 | 0.00767434 | 0.0067941 | 0.00451176 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |
| Boss | Long | 49776 | 0.00795518 | 0.0069136 | 0.00497491 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |
| Boss | Short_vs_Long | 59160 | -0.000280846 | nan | nan | 2.27485e+08 | 6.44469e-05 | 6.95219e-08 | 3.60497e-08 | 4.45653e-12 | 1.78174e-08 | 9384 | 100 | 0 | 0.00605 |
| Carol | Short | 9384 | 0.0106418 | 0.00928496 | 0.00658134 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |
| Carol | Long | 49776 | 0.0108135 | 0.0093108 | 0.0068721 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |
| Carol | Short_vs_Long | 59160 | -0.00017165 | nan | nan | 2.31304e+08 | 0.13903 | 2.05511e-07 | 3.97615e-07 | 7.00006e-12 | 1.69372e-07 | 9384 | 100 | 0 | 0 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: `['Boss', 'Carol']`
    - Unique Group: `['Long', 'Short', 'Short_vs_Long']`
- **Anomalies**: NaN values detected: {'MI_median': 2, 'MI_std': 2, 'U_stat': 4, 'U_pvalue': 4, 'MI_group_Short': 4, 'MI_group_Long': 4, 'MI_group_Short_std': 4, 'MI_group_Long_std': 4, 'N_subsampled': 4, 'N_bootstrap': 4, 'P_surr_Short': 4, 'P_surr_Long': 4}

---

## Step H: Waveform Morphology (Latency, RSI & Shape)

**Script:** `analyze_gating_latency_rsi.py`  
**Description:** AUC, FWHM, Rise Slope, Peak Latency per Short/Long, per tone window.

### H: morphology_stats_erp_baseglobal.csv
- **Target File**: `derivatives/analysis/gating/morphology_stats_erp_baseglobal.csv`
- **Data Structure Discovery**:
    - Columns: `['AUC', 'Rise_Slope', 'FWHM', 'Peak_Amp', 'Peak_Lat', 'Subject', 'Group', 'Tone']`
    - Shape: 354960 rows × 8 columns
- **Full Data Table / Statistical Summary**:

**Shape: 354960 rows × 8 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AUC | 354960 | 2.2778 | 0.859494 | 0.433958 | 1.68817 | 2.1287 | 2.6898 | 14.4821 |
| Rise_Slope | 354960 | 561.303 | 844.583 | -11626.3 | 176.29 | 303.026 | 595.663 | 39915 |
| FWHM | 354960 | 0.0183971 | 0.00792555 | 0.002 | 0.014 | 0.018 | 0.022 | 0.108 |
| Peak_Amp | 354960 | 1.19736 | 41.267 | -144.807 | -36.3154 | 19.3789 | 37.6065 | 163.117 |
| Peak_Lat | 354960 | 0.117439 | 0.0513919 | 0 | 0.076 | 0.122 | 0.16 | 0.2 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique Group: 2 → `['Long', 'Short']`
    - Unique Tone: 3 → `['Tone0', 'Tone1', 'Tone2']`
- **Anomalies**: None detected.

---

### H: morphology_stats_erp_baselocal.csv
- **Target File**: `derivatives/analysis/gating/morphology_stats_erp_baselocal.csv`
- **Data Structure Discovery**:
    - Columns: `['AUC', 'Rise_Slope', 'FWHM', 'Peak_Amp', 'Peak_Lat', 'Subject', 'Group', 'Tone']`
    - Shape: 354960 rows × 8 columns
- **Full Data Table / Statistical Summary**:

**Shape: 354960 rows × 8 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AUC | 354960 | 2.54217 | 1.07865 | 0.565676 | 1.82504 | 2.33915 | 3.01046 | 26.6606 |
| Rise_Slope | 354960 | 587.757 | 855.716 | -9657.45 | 185.592 | 323.817 | 634.454 | 39915 |
| FWHM | 354960 | 0.0203848 | 0.0100991 | 0.002 | 0.014 | 0.018 | 0.024 | 0.2 |
| Peak_Amp | 354960 | 0.00628102 | 44.3784 | -212.445 | -39.3617 | -20.6559 | 39.7217 | 234.555 |
| Peak_Lat | 354960 | 0.116164 | 0.050841 | 0 | 0.076 | 0.12 | 0.158 | 0.2 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique Group: 2 → `['Long', 'Short']`
    - Unique Tone: 3 → `['Tone0', 'Tone1', 'Tone2']`
- **Anomalies**: None detected.

---

### H: morphology_stats_hfa_baseglobal.csv
- **Target File**: `derivatives/analysis/gating/morphology_stats_hfa_baseglobal.csv`
- **Data Structure Discovery**:
    - Columns: `['AUC', 'Rise_Slope', 'FWHM', 'Peak_Amp', 'Peak_Lat', 'Subject', 'Group', 'Tone']`
    - Shape: 354960 rows × 8 columns
- **Full Data Table / Statistical Summary**:

**Shape: 354960 rows × 8 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AUC | 354960 | 0.182615 | 0.143615 | 0.0417493 | 0.123465 | 0.155372 | 0.198582 | 4.00605 |
| Rise_Slope | 354960 | 51.7902 | 97.1515 | -3144.74 | 13.2828 | 25.5122 | 54.0367 | 2878.37 |
| FWHM | 354960 | 0.0167979 | 0.0125648 | 0.002 | 0.012 | 0.014 | 0.018 | 0.2 |
| Peak_Amp | 354960 | 2.18604 | 3.92148 | -20.0511 | -1.58304 | 2.6454 | 3.84746 | 69.1699 |
| Peak_Lat | 354960 | 0.117058 | 0.0517846 | 0 | 0.076 | 0.118 | 0.162 | 0.2 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique Group: 2 → `['Long', 'Short']`
    - Unique Tone: 3 → `['Tone0', 'Tone1', 'Tone2']`
- **Anomalies**: None detected.

---

### H: morphology_stats_hfa_baselocal.csv
- **Target File**: `derivatives/analysis/gating/morphology_stats_hfa_baselocal.csv`
- **Data Structure Discovery**:
    - Columns: `['AUC', 'Rise_Slope', 'FWHM', 'Peak_Amp', 'Peak_Lat', 'Subject', 'Group', 'Tone']`
    - Shape: 354960 rows × 8 columns
- **Full Data Table / Statistical Summary**:

**Shape: 354960 rows × 8 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AUC | 354960 | 0.191986 | 0.161735 | 0.0401617 | 0.126211 | 0.161156 | 0.210417 | 6.98542 |
| Rise_Slope | 354960 | 52.1524 | 95.8957 | -3144.74 | 13.7012 | 25.9792 | 54.8686 | 2878.37 |
| FWHM | 354960 | 0.0176524 | 0.0136623 | 0.002 | 0.012 | 0.014 | 0.018 | 0.2 |
| Peak_Amp | 354960 | 2.11421 | 3.98352 | -36.6776 | -1.65695 | 2.68162 | 3.88503 | 68.4271 |
| Peak_Lat | 354960 | 0.116422 | 0.0512159 | 0 | 0.076 | 0.118 | 0.16 | 0.2 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: 2 → `['Boss', 'Carol']`
    - Unique Group: 2 → `['Long', 'Short']`
    - Unique Tone: 3 → `['Tone0', 'Tone1', 'Tone2']`
- **Anomalies**: None detected.

---

## Step I: Frequency Tagging (PSD & ITC)

### I (PSD Statistics)
**Script:** `analysis_frequency.py`

#### I: frequency_stats.csv
- **Target File**: `derivatives/frequency/frequency_stats.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'Condition', 'Control', 'Length', 'Target_Freq', 'Power_Cond', 'Power_Ctrl', 'Diff_Score', 'Power_4Hz_Cond', 'Power_4Hz_Ctrl']`
    - Shape: 32 rows × 10 columns
- **Full Data Table**:

**Shape: 32 rows × 10 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Length | 32 | 11.5 | 3.6983 | 6 | 8 | 12 | 16 | 16 |
| Target_Freq | 32 | 1.15625 | 0.53033 | 0.5 | 1 | 1 | 1.25 | 2 |
| Power_Cond | 32 | 26.4822 | 8.77622 | 6.74405 | 21.4266 | 27.3809 | 32.1977 | 40.7675 |
| Power_Ctrl | 32 | 30.4512 | 9.47239 | 6.12812 | 25.9902 | 34.5659 | 36.3712 | 44.1802 |
| Diff_Score | 32 | -3.96897 | 4.92095 | -14.9319 | -5.84995 | -3.4369 | -0.325974 | 5.45737 |
| Power_4Hz_Cond | 32 | 36.2863 | 7.18847 | 25.8467 | 30.8706 | 34.8903 | 40.6928 | 54.1956 |
| Power_4Hz_Ctrl | 32 | 35.431 | 5.09941 | 29.0985 | 30.8153 | 34.8214 | 40.0343 | 44.4316 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: `['Boss', 'Carol']`
    - Unique Condition: `['Alternation', 'Pairs', 'PairsAndAlternation1', 'PairsAndAlternation2', 'Quadruplets']`
    - Unique Control: `['RandomControl']`
- **Anomalies**: None detected.

---

### I (ITC Statistics (Refined))
**Script:** `analysis_frequency_itc.py`

#### I: itc_stats_refined.csv
- **Target File**: `derivatives/frequency/itc_stats_refined.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'Condition', 'Length', 'Target_Freq', 'N_Cond', 'N_Ctrl', 'N_Min', 'ITC_Cond', 'ITC_Ctrl', 'Diff_Score', 'P_Value', 'ITC_4Hz_Cond', 'ITC_4Hz_Ctrl', 'P_Value_4Hz']`
    - Shape: 32 rows × 14 columns
- **Full Data Table**:

**Shape: 32 rows × 14 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Length | 32 | 11.5 | 3.6983 | 6 | 8 | 12 | 16 | 16 |
| Target_Freq | 32 | 1.15625 | 0.53033 | 0.5 | 1 | 1 | 1.25 | 2 |
| N_Cond | 32 | 58.125 | 7.37804 | 30 | 60 | 60 | 60 | 60 |
| N_Ctrl | 32 | 60 | 0 | 60 | 60 | 60 | 60 | 60 |
| N_Min | 32 | 58.125 | 7.37804 | 30 | 60 | 60 | 60 | 60 |
| ITC_Cond | 32 | 0.0767254 | 0.0374541 | 0.0113877 | 0.0452056 | 0.0801176 | 0.104392 | 0.165314 |
| ITC_Ctrl | 32 | 0.0777287 | 0.0371431 | 0.0198648 | 0.0476046 | 0.0823153 | 0.105281 | 0.153374 |
| Diff_Score | 32 | -0.00100329 | 0.0475621 | -0.088715 | -0.0202855 | -0.00399716 | 0.0278496 | 0.127369 |
| P_Value | 32 | 0.507094 | 0.25771 | 0.04 | 0.288 | 0.5415 | 0.62425 | 0.931 |
| ITC_4Hz_Cond | 32 | 0.267224 | 0.107019 | 0.093227 | 0.168139 | 0.252583 | 0.372483 | 0.447381 |
| ITC_4Hz_Ctrl | 32 | 0.288582 | 0.0741201 | 0.161321 | 0.248044 | 0.310996 | 0.356089 | 0.368421 |
| P_Value_4Hz | 32 | 0.558031 | 0.333755 | 0.015 | 0.25225 | 0.535 | 0.90725 | 1 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: `['Boss', 'Carol']`
    - Unique Condition: `['Alternation', 'Pairs', 'PairsAndAlternation1', 'PairsAndAlternation2', 'Quadruplets']`
- **Anomalies**: None detected.

---

## Step J: Additional Analyses

### J.1: Baseline State — Regression Stats
**Script:** `analyze_baseline_state.py`

#### J: baseline_regression_stats.csv
- **Target File**: `derivatives/baseline_state/baseline_regression_stats.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'Length', 'Grammar', 'MDL', 'Pos_Slope', 'Pos_P', 'Pos_R']`
    - Shape: 10 rows × 7 columns
- **Full Data Table**:

| Subject | Length | Grammar | MDL | Pos_Slope | Pos_P | Pos_R |
| --- | --- | --- | --- | --- | --- | --- |
| Carol | 12 | Pairs | 10 | 0.0908993 | 0.000139872 | 0.0352557 |
| Carol | 4 | Pairs | 4.75 | 0.549331 | 0.00552673 | 0.0667207 |
| Carol | 16 | Alternation | 12.7059 | 0.0133274 | 0.37115 | 0.00737978 |
| Carol | 6 | Alternation | 5.6 | 0.216685 | 0.019847 | 0.040919 |
| Carol | 8 | Alternation | 6.16667 | 0.185007 | 0.000545994 | 0.0479994 |
| Boss | 12 | Pairs | 10 | 0.0396815 | 0.121835 | 0.014326 |
| Boss | 4 | Pairs | 4.75 | 0.638784 | 0.00133923 | 0.0770999 |
| Boss | 16 | Alternation | 12.7059 | 0.0430515 | 0.0146197 | 0.0201464 |
| Boss | 6 | Alternation | 5.6 | 0.204016 | 0.0222103 | 0.0401734 |
| Boss | 8 | Alternation | 6.16667 | 0.00848252 | 0.871814 | 0.00224158 |

- **Anomalies**: None detected.

---

### J.2: Baseline State — Raw Data
**Script:** `analyze_baseline_state.py`

#### J: baseline_raw_data.csv
- **Target File**: `derivatives/baseline_state/baseline_raw_data.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'Condition', 'Length', 'Position', 'TrialType', 'MDL', 'Voltage']`
    - Shape: 73008 rows × 7 columns
- **Full Data Table / Statistical Summary**:

**Shape: 73008 rows × 7 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Length | 73008 | 12.1302 | 3.8624 | 4 | 8 | 12 | 16 | 16 |
| Position | 73008 | 6.56509 | 4.14142 | 1 | 3 | 6 | 10 | 16 |
| MDL | 73008 | 9.90533 | 5.59298 | 3 | 6 | 6 | 14 | 23 |
| Voltage | 73008 | 0.0699532 | 9.12037 | -111.862 | -5.42091 | 0.236544 | 5.83379 | 75.9262 |

- **Anomalies**: None detected.

---

### J.3: Neural Trajectory
**Script:** `analyze_neural_trajectory.py`

#### J: Trajectory_Stats_Boss.csv
- **Target File**: `derivatives/analysis/trajectory/Trajectory_Stats_Boss.csv`
- **Data Structure Discovery**:
    - Columns: `['time', 'distance', 'p_val', 'sig']`
    - Shape: 2500 rows × 4 columns
- **Full Data Table / Statistical Summary**:

**Shape: 2500 rows × 4 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| time | 2500 | 2 | 1.44424 | -0.5 | 0.75 | 2 | 3.25 | 4.5 |
| distance | 2500 | 3.38793 | 2.5678 | 0.0792458 | 1.5408 | 2.67152 | 4.39833 | 12.8721 |
| p_val | 2500 | 0.166363 | 0.278264 | 0 | 0 | 0.01 | 0.206 | 1 |

- **Metadata Check**:
    - FS: 500 Hz
- **Anomalies**: None detected.

---

#### J: Trajectory_Stats_Carol.csv
- **Target File**: `derivatives/analysis/trajectory/Trajectory_Stats_Carol.csv`
- **Data Structure Discovery**:
    - Columns: `['time', 'distance', 'p_val', 'sig']`
    - Shape: 2500 rows × 4 columns
- **Full Data Table / Statistical Summary**:

**Shape: 2500 rows × 4 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| time | 2500 | 2 | 1.44424 | -0.5 | 0.75 | 2 | 3.25 | 4.5 |
| distance | 2500 | 5.71491 | 4.04552 | 0.126705 | 2.5403 | 4.93658 | 7.96634 | 20.0909 |
| p_val | 2500 | 0.0881392 | 0.223516 | 0 | 0 | 0 | 0.008 | 0.994 |

- **Metadata Check**:
    - FS: 500 Hz
- **Anomalies**: Column `p_val`: 1734/2500 (69.4%) zero values

---

### J.4: MMN ROI — Summary
**Script:** `analysis_mmn_roi.py`

#### J: stats_comparison_summary.csv
- **Target File**: `derivatives/MMN/stats_comparison_summary.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'Grammar', 'Length', 'ROI', 'Window', 'SeqBase_t', 'SeqBase_p', 'SeqBase_diff', 'ToneBase_t', 'ToneBase_p', 'ToneBase_diff']`
    - Shape: 408 rows × 11 columns
- **Full Data Table / Statistical Summary**:

**Shape: 408 rows × 11 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Length | 408 | 10.6471 | 4.30906 | 4 | 6 | 12 | 16 | 16 |
| SeqBase_t | 408 | -0.0217693 | 1.04101 | -3.53368 | -0.630156 | -0.0536286 | 0.654532 | 2.73787 |
| SeqBase_p | 408 | 0.510195 | 0.297462 | 0.000772536 | 0.261508 | 0.524109 | 0.773027 | 0.998921 |
| SeqBase_diff | 408 | -0.0130654 | 1.41471 | -6.70662 | -0.676969 | -0.0508998 | 0.680653 | 5.17323 |
| ToneBase_t | 408 | 0.0622938 | 1.02722 | -4.01489 | -0.61378 | 0.0406346 | 0.801613 | 3.01323 |
| ToneBase_p | 408 | 0.494424 | 0.291285 | 0.000406317 | 0.249805 | 0.478328 | 0.74463 | 0.998854 |
| ToneBase_diff | 408 | 0.0349066 | 2.1636 | -9.81813 | -0.98224 | 0.0510004 | 1.15161 | 6.73428 |

- **Metadata Check**:
    - FS: 500 Hz
    - Unique Subject: 2 unique → `['Boss', 'Carol']`
    - Unique Grammar: 12 unique → `['Alternation', 'CenterMirror', 'Pairs', 'PairsAndAlternation1', 'PairsAndAlternation2', 'Quadrupletes', 'Quadruplets', 'RandomControl', 'Repetition', 'Shrinking']...`
    - Unique ROI: 3 unique → `['Auditory', 'M1', 'S1']`
    - Unique Window: 2 unique → `['early', 'late']`
- **Anomalies**: None detected.

---

### J.5: MMN ROI — Per-Condition Stats
**Script:** `analysis_mmn_roi.py`

**34 individual condition files detected.**
Showing representative example: `derivatives/MMN/Alternation_Length12/stats_comparison.csv`

- **Data Structure Discovery**:
    - Columns: `['Subject', 'Grammar', 'Length', 'ROI', 'Window', 'SeqBase_t', 'SeqBase_p', 'SeqBase_diff', 'ToneBase_t', 'ToneBase_p', 'ToneBase_diff']`
    - Shape: 12 rows × 11 columns
- **Full Data Table (example)**:

**Shape: 12 rows × 11 columns** (showing statistical summary for numeric columns)

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Length | 12 | 12 | 0 | 12 | 12 | 12 | 12 | 12 |
| SeqBase_t | 12 | 0.446403 | 0.807654 | -0.820496 | -0.0552813 | 0.575098 | 0.759855 | 2.20619 |
| SeqBase_p | 12 | 0.516156 | 0.224944 | 0.030784 | 0.414486 | 0.542793 | 0.629365 | 0.947148 |
| SeqBase_diff | 12 | 0.612641 | 1.05807 | -0.691289 | -0.0693663 | 0.588308 | 0.996668 | 3.11779 |
| ToneBase_t | 12 | -0.253766 | 1.53913 | -2.01849 | -1.75853 | -0.423488 | 1.14907 | 1.8479 |
| ToneBase_p | 12 | 0.229845 | 0.227528 | 0.0493384 | 0.0658146 | 0.15736 | 0.276469 | 0.761892 |
| ToneBase_diff | 12 | -0.894507 | 3.41801 | -7.15112 | -2.27066 | -0.680686 | 1.94991 | 3.06596 |

**All condition files in registry:**

- `derivatives/MMN/Alternation_Length12/stats_comparison.csv`
- `derivatives/MMN/Alternation_Length16/stats_comparison.csv`
- `derivatives/MMN/Alternation_Length4/stats_comparison.csv`
- `derivatives/MMN/Alternation_Length6/stats_comparison.csv`
- `derivatives/MMN/Alternation_Length8/stats_comparison.csv`
- `derivatives/MMN/CenterMirror_Length12/stats_comparison.csv`
- `derivatives/MMN/CenterMirror_Length16/stats_comparison.csv`
- `derivatives/MMN/PairsAndAlternation1_Length12/stats_comparison.csv`
- `derivatives/MMN/PairsAndAlternation1_Length16/stats_comparison.csv`
- `derivatives/MMN/PairsAndAlternation1_Length8/stats_comparison.csv`
- `derivatives/MMN/PairsAndAlternation2_Length12/stats_comparison.csv`
- `derivatives/MMN/PairsAndAlternation2_Length16/stats_comparison.csv`
- `derivatives/MMN/Pairs_Length12/stats_comparison.csv`
- `derivatives/MMN/Pairs_Length16/stats_comparison.csv`
- `derivatives/MMN/Pairs_Length4/stats_comparison.csv`
- `derivatives/MMN/Pairs_Length6/stats_comparison.csv`
- `derivatives/MMN/Pairs_Length8/stats_comparison.csv`
- `derivatives/MMN/Quadrupletes_Length16/stats_comparison.csv`
- `derivatives/MMN/Quadruplets_Length12/stats_comparison.csv`
- `derivatives/MMN/Quadruplets_Length16/stats_comparison.csv`
- `derivatives/MMN/Quadruplets_Length8/stats_comparison.csv`
- `derivatives/MMN/RandomControl_Length12/stats_comparison.csv`
- `derivatives/MMN/RandomControl_Length16/stats_comparison.csv`
- `derivatives/MMN/RandomControl_Length6/stats_comparison.csv`
- `derivatives/MMN/RandomControl_Length8/stats_comparison.csv`
- `derivatives/MMN/Repetition_Length12/stats_comparison.csv`
- `derivatives/MMN/Repetition_Length16/stats_comparison.csv`
- `derivatives/MMN/Repetition_Length4/stats_comparison.csv`
- `derivatives/MMN/Repetition_Length6/stats_comparison.csv`
- `derivatives/MMN/Repetition_Length8/stats_comparison.csv`
- `derivatives/MMN/Shrinking_Length12/stats_comparison.csv`
- `derivatives/MMN/Shrinking_Length16/stats_comparison.csv`
- `derivatives/MMN/Triplets_Length6/stats_comparison.csv`
- `derivatives/MMN/Xxx_Length4/stats_comparison.csv`

- **Anomalies across all files**: Checked 34 files, all share identical column structure.

---

## Step K: Unique Variance Analysis (Collinearity Diagnostics)

**Script:** `analyze_unique_variance.py`  
**Description:** VIF diagnostics for predictor collinearity prior to ΔR² analysis.

### K: collinearity_diagnostics_erp_baseglobal.csv
- **Target File**: `derivatives/analysis/unique_variance/collinearity_diagnostics_erp_baseglobal.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'DataType', 'BaselineMode', 'CondNum_Full', 'CondNum_ReducedMDL', 'CondNum_ReducedSurprisal', 'HighCollinearity_Warning', 'N_Trials']`
    - Shape: 2 rows × 8 columns
- **Full Data Table**:

| Subject | DataType | BaselineMode | CondNum_Full | CondNum_ReducedMDL | CondNum_ReducedSurprisal | HighCollinearity_Warning | N_Trials |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Boss | erp | global | 42.9581 | 14.9083 | 34.8889 | True | 68952 |
| Carol | erp | global | 42.9581 | 14.9083 | 34.8889 | True | 68952 |

- **Anomalies**: None detected.

---

### K: collinearity_diagnostics_erp_baselocal.csv
- **Target File**: `derivatives/analysis/unique_variance/collinearity_diagnostics_erp_baselocal.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'DataType', 'BaselineMode', 'CondNum_Full', 'CondNum_ReducedMDL', 'CondNum_ReducedSurprisal', 'HighCollinearity_Warning', 'N_Trials']`
    - Shape: 2 rows × 8 columns
- **Full Data Table**:

| Subject | DataType | BaselineMode | CondNum_Full | CondNum_ReducedMDL | CondNum_ReducedSurprisal | HighCollinearity_Warning | N_Trials |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Carol | erp | local | 42.9581 | 14.9083 | 34.8889 | True | 68952 |
| Boss | erp | local | 42.9581 | 14.9083 | 34.8889 | True | 68952 |

- **Anomalies**: None detected.

---

### K: collinearity_diagnostics_hfa_baseglobal.csv
- **Target File**: `derivatives/analysis/unique_variance/collinearity_diagnostics_hfa_baseglobal.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'DataType', 'BaselineMode', 'CondNum_Full', 'CondNum_ReducedMDL', 'CondNum_ReducedSurprisal', 'HighCollinearity_Warning', 'N_Trials']`
    - Shape: 2 rows × 8 columns
- **Full Data Table**:

| Subject | DataType | BaselineMode | CondNum_Full | CondNum_ReducedMDL | CondNum_ReducedSurprisal | HighCollinearity_Warning | N_Trials |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Boss | hfa | global | 42.9581 | 14.9083 | 34.8889 | True | 68952 |
| Carol | hfa | global | 42.9581 | 14.9083 | 34.8889 | True | 68952 |

- **Anomalies**: None detected.

---

### K: collinearity_diagnostics_hfa_baselocal.csv
- **Target File**: `derivatives/analysis/unique_variance/collinearity_diagnostics_hfa_baselocal.csv`
- **Data Structure Discovery**:
    - Columns: `['Subject', 'DataType', 'BaselineMode', 'CondNum_Full', 'CondNum_ReducedMDL', 'CondNum_ReducedSurprisal', 'HighCollinearity_Warning', 'N_Trials']`
    - Shape: 2 rows × 8 columns
- **Full Data Table**:

| Subject | DataType | BaselineMode | CondNum_Full | CondNum_ReducedMDL | CondNum_ReducedSurprisal | HighCollinearity_Warning | N_Trials |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Boss | hfa | local | 42.9581 | 14.9083 | 34.8889 | True | 68952 |
| Carol | hfa | local | 42.9581 | 14.9083 | 34.8889 | True | 68952 |

- **Anomalies**: None detected.

---
