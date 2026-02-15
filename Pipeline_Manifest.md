# Pipeline Manifest and Execution Standards

**Version:** 2026-02-13 (Updated — 500 Hz, Script-Verified)  
**Purpose:** Definitive registry of scripts, dependencies, and result file locations for the Analysis Pipeline.  
**Sampling Rate:** 500 Hz (2 ms temporal resolution, downsampled from 1000 Hz raw).

---

## 1. Pipeline Architecture

## 1. Pipeline Architecture

### Step 0: Functional Mapping (ROI Definition)
*   **Script:** `code/functional_roi/run_functional_mapping.py`
    *   **Library:** `code/preprocessing/preproc_lib.py`
*   **Input:** Raw Cortec `.mat` files (Routine functional localizer & SEP task).
*   **Output:** `derivatives/rois/master_channel_map.json`
*   **Key Logic:** Auditory HFA responsiveness (p < 0.001) and Somatosensory LFP N20 phase reversal.

### Step 1: Preprocessing
*   **Script:** `code/preprocessing/run_daily_preproc.py`
*   **Input:** Raw Cortec `.mat` files.
*   **Output:** `derivatives/preproc/*/[Subject]/*.npz` (Contains `signals_cmr`, `hfa_cmr`, `fs`, `ch_names`)
*   **Key Parameter:** `TARGET_FS = 500.0`

### Step 2: Predictor Generation
*   **Script:** `code/glm_analysis/generate_predictors.py`
*   **Output:** `derivatives/predictors/{Condition}/{Subject}/{Session}.parquet`
*   **Contains:** `ToneID`, `Position`, `Length`, `Surprisal`, `MDL`, `IsHab`, `IsDeviant`, `Repetition`, `Interaction`

### Step 3: Epoching
*   **Script:** `code/epoching/cut_epoch_unified.py`
*   **Output:** `derivatives/epochs/{Condition}/{Subject}/*.npz`
*   **Contains:** `erp_epochs`, `hfa_epochs`, `meta`, `channel_names`, `fs`
*   **Epoch shape:** `(N_trials, 500, N_channels)` at 500 Hz (1.0 s epoch: −0.2 to +0.8 s)

### Step 4: GLM Data Preparation
*   **Script:** `code/glm_analysis/prepare_glm_data.py`
    *   **Arguments:** `--data_type [erp|hfa] --baseline_mode [local|global]`
*   **Input:** `derivatives/epochs/**/*.npz`, `derivatives/predictors/**/*.parquet`
*   **Output:**
    *   `derivatives/glm_data/glm_dataset_erp_baselocal.h5`
    *   `derivatives/glm_data/glm_dataset_erp_baseglobal.h5`
    *   `derivatives/glm_data/glm_dataset_hfa_baselocal.h5`
    *   `derivatives/glm_data/glm_dataset_hfa_baseglobal.h5`
*   **HDF5 Structure:** `/{Condition}/{Subject}/Y` (trial × channel × time), `/{Condition}/{Subject}/X/{predictor}`, Root attribute `fs=500.0`

---

## 2. Statistical Analyses

### A. Hierarchical GLM (Time-Resolved)
*   **Script:** `code/glm_analysis/run_glm_hierarchical.py`
    *   **Arguments:** `--data_type [erp|hfa] --baseline_mode [local|global]`
*   **Output:**
    *   `derivatives/glm_results/glm_results_{erp|hfa}_{baselocal|baseglobal}_Model{A-D}.h5`
*   **HDF5 Structure:** `/{Subject}/ROIBetas`, `/{Subject}/ROITstats`

### B. Quick Screening (Uncorrected)
*   **Script:** `code/glm_analysis/run_glm_stats.py`
    *   **Arguments:** `--data_type [erp|hfa] --baseline_mode [local|global] --model [A|B|C|D]`
*   **Script:** `code/glm_analysis/plot_glm_results.py`
    *   **Arguments:** `--data_type [erp|hfa] --baseline_mode [local|global] --model [A|B|C|D]`
*   **Output:**
    *   `derivatives/glm_results/stats_{erp|hfa}_{baselocal|baseglobal}_Model{A-D}.csv`
    *   `derivatives/glm_results/figures_{erp|hfa}_{baselocal|baseglobal}_Model{A-D}/`

### C. Permutation Testing (Cluster-Based Correction)
*   **Script:** `code/glm_analysis/run_glm_permutation.py`
    *   **Arguments:** `--data_type [erp|hfa] --baseline_mode [local|global] --model [A|B|C|D] --predictor [name]`
*   **Output:**
    *   `derivatives/glm_results/permutation_clusters_{erp|hfa}_{baselocal|baseglobal}_Model{A-D}.csv`

### D. Gating Hypothesis (Complexity × Length)
*   **Script:** `code/analysis/analyze_gating_hypothesis.py`
    *   **Arguments:** `--data_type [erp|hfa] --baseline_mode [local|global]`
*   **Output:**
    *   `derivatives/analysis/gating/gating_sliding_stats_{erp|hfa}_{baselocal|baseglobal}.csv`
    *   `derivatives/analysis/gating/gating_stats_{erp|hfa}_{baselocal|baseglobal}.csv`
    *   `derivatives/analysis/gating/gating_waveforms_{erp|hfa}_{baselocal|baseglobal}.csv`

### E. HFA–ERP Amplitude Coupling
*   **Script:** `code/analysis/analyze_gating_coupling.py`
    *   **Arguments:** `--baseline_mode [local|global]`
*   **Output:**
    *   `derivatives/analysis/gating/coupling_stats_{baselocal|baseglobal}.csv`
*   **Visualization:**
    *   `derivatives/visualization/gating_coupling_{baselocal|baseglobal}/`

### F. HFA–ERP Latency Analysis
*   **Script:** `code/analysis/analyze_hfa_erp_latency.py`
    *   **Arguments:** `--baseline_mode [local|global]`
*   **Output:**
    *   `derivatives/analysis/gating/latency_hfa_erp_stats_{baselocal|baseglobal}.csv`
*   **Visualization:**
    *   `derivatives/visualization/latency_hfa_erp_{baselocal|baseglobal}/Latency_Dist_{Subject}.png`

### G. Phase–Amplitude Coupling (PAC)
*   **Script:** `code/analysis/analyze_pac.py`
    *   **Arguments:** `--baseline_mode [local|global] --freq_low [Hz] --freq_high [Hz]`
*   **Output:**
    *   `derivatives/analysis/gating/pac_stats_{baselocal|baseglobal}.csv`
*   **Visualization:**
    *   `derivatives/visualization/pac_{baselocal|baseglobal}/PAC_Polar_{Subject}.png`
*   **Key Parameters:** 18 phase bins, 200 surrogates, 100 bootstrap iterations (N-equalised subsampling), Mirror Padding (0.5s)

### H. Waveform Morphology (Latency, RSI & Shape)
*   **Script:** `code/analysis/analyze_gating_latency_rsi.py`
    *   **Arguments:** `--data_type [erp|hfa] --baseline_mode [local|global]`
*   **Output:**
    *   `derivatives/analysis/gating/morphology_stats_{erp|hfa}_{baselocal|baseglobal}.csv`
*   **Visualization:**
    *   `derivatives/visualization/gating_latency_{erp|hfa}_{baselocal|baseglobal}/Gating_DiffWave.png`

### I. Frequency Tagging
*   **Script:** `code/analysis/analysis_frequency.py`
    *   **Method:** PSD via Welch, per-length `nperseg` (full sequence duration). Resolution: L4→1.0Hz, L8→0.5Hz, L16→0.25Hz.
    *   **Output:** `derivatives/frequency/frequency_stats.csv`
*   **Script:** `code/analysis/analysis_frequency_itc.py` (Refined)
    *   **Method:** Inter-Trial Coherence (ITC) on full sequence-duration FFT (per-length resolution). Subsampling equalization (N=50) and permutation testing (N=1000).
    *   **Output:** `derivatives/frequency/itc_stats_refined.csv`
    *   **Visualization:** `derivatives/frequency/ITC_plots_refined/`

### J. Additional Analyses
*   **Baseline State:** `code/analysis/analyze_baseline_state.py` — `baseline_raw_data.csv`, `baseline_regression_stats.csv`
*   **MMN ROI:** `code/analysis/analysis_mmn_roi.py` — Extracts trial-level indices (Peak, AUC) for Deviant-Standard difference using dual baselines (Global/Local).
*   **Neural Trajectory:** `code/analysis/analyze_neural_trajectory.py` — PCA-based state maintenance analysis

---

### L. MMN-proxy Regression Analysis
*   **Script:** `code/analysis/analyze_mmn_regression.py`
    *   **Logic:** Correlates MMN metrics (Peak/AUC) with sequence complexity (MDL). Splits analysis by subject to account for individual strategies and uses **Local Baseline** to isolate transient prediction error from sequence-level drift.
*   **Output:**
    - `derivatives/analysis/mmn_regression/regression_stats_refined.csv`
    - `derivatives/analysis/mmn_regression/regression_plots_[Subject].png` (Boxplot + Jittered Stripplot)

---

### K. Unique Variance Analysis ($\Delta R^2$)
*   **Analysis Script:** `code/analysis/analyze_unique_variance.py`
    *   **Arguments:** `--data_type [erp|hfa] --baseline_mode [local|global]`
*   **Visualization Script:** `code/visualization/plot_unique_variance.py`
*   **Output:**
    *   `derivatives/analysis/unique_variance/unique_variance_{erp|hfa}_{baselocal|baseglobal}.h5`
        *   HDF5 contains: `ROI_DeltaR2_MDL`, `ROI_DeltaR2_Surp`, `ROI_PValue_MDL`, `ROI_PValue_Surp` (200 permutations)
    *   `derivatives/visualization/unique_variance/{ROI}_UniqueVariance_{type}_{base}.png`

### K.5 Collinearity Diagnostics (VIF)
*   **Script:** `check_vif.py`
    *   **Arguments:** `--file [path_to_h5]`
*   **Purpose:** Formally evaluate Variance Inflation Factors (VIF) and Condition Numbers for the GLM design matrix.
*   **Key Insight:** Ensures that MDL and Sequence Length are sufficiently decorrelated for independent estimation.

---

## 3. Visualization
*   **Script:** `code/visualization/viz_sensor_erp.py` — Sensor-level ERP plots
*   **Outputs:** `derivatives/visualization/*/` (organised by analysis and baseline)

---

## 4. Reader Instructions (for LLMs)
1.  **GLM Results:** Read `derivatives/glm_results/glm_results_*.h5`. Look for `ROITstats` dataset under each Subject group.
2.  **Gating Slopes:** Read `derivatives/analysis/gating/gating_sliding_stats_{erp|hfa}_{base}.csv` for the timecourse of the regime shift.
3.  **Morphology:** Read `derivatives/analysis/gating/morphology_stats_{type}_{base}.csv` for Peak Latency, AUC, FWHM, and Rise Slope.
4.  **Coupling:** Read `derivatives/analysis/gating/coupling_stats_{base}.csv` for HFA–ERP amplitude correlation.
5.  **Latency:** Read `derivatives/analysis/gating/latency_hfa_erp_stats_{base}.csv` for HFA–ERP peak timing analysis.
6.  **PAC:** Read `derivatives/analysis/gating/pac_stats_{base}.csv` for Phase–Amplitude Coupling results.
7.  **Neural Trajectory:** Read `derivatives/analysis/trajectory/Trajectory_Stats_{Subject}.csv` for PCA-based context-dependent configuration.
8.  **All output files use baseline suffix:** `_baselocal` or `_baseglobal`.
9.  **Sampling rate** is stored as `fs` attribute in HDF5 files and `fs` key in `.npz` files.
10. **Latest File Priority:** If multiple files match the naming pattern (e.g., gating_stats_*.csv) in the target directory, the system must select and read only the file with the Last Modified Date closest to the current analysis time.