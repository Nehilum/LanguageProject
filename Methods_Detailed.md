# Analysis Methods Report: Macaque Auditory Sequence Learning

**Date:** 2026-02-13 (Updated)  
**Study:** Auditory Sequence Learning (Length vs Complexity)  
**Species:** Macaca Mulatta (N=2: Boss, Carol)

## 1. Experimental Design

### 1.1 Stimuli
The study employs a Local-Global auditory sequence paradigm.
*   **Tones:** Two pure tones (A, B) and a Silence/Mirror tone (X).
*   **Sequences:** Binary sequences of varying **Lengths** (4, 6, 8, 12, 16 tones).
*   **Grammars:**
    *   **Repetition:** AAAA...
    *   **Alternation:** ABAB...
    *   **Pairs:** AABBAABB...
    *   **Pairs+Alt:** AABBABAB...
    *   **Quadruplets:** AAAABBBB...
    *   **CenterMirror:** Symmetry around the center.
*   **Complexity:** Defined by Minimal Description Length (MDL) theory (AlRoumi et al., 2023).

### 1.2 Data Acquisition
*   **Modality:** Electrocorticography (ECoG).
*   **System:** Cortec Neural Interface.
*   **Sampling:** 500 Hz (Downsampled from 1000 Hz raw acquisition).
*   **Temporal Resolution:** 2 ms per sample.
*   **ROIs:**
    *   **Auditory:** Primary sensory (A1, Belt).
    *   **S1_Sensory:** High-level structural processing.
    *   **M1_Motor:** Prediction/Action.

## 2. Phase 0: Functional ROI Mapping

Prior to the main analysis, subject-specific Regions of Interest (ROIs) were defined using functional localizer tasks.

### 2.1 Auditory Scout (Primary & Belt)
*   **Stimuli:** "Routine" functional localizer (piano tones).
*   **Method:**
    1.  Preprocessing using `code/preprocessing/preproc_lib.py` with **Selective CMR** (Iterative Bad Channel rejection).
    2.  HFA Extraction (70–150 Hz).
    3.  Channel-wise t-test: Mean Response [0, 400 ms] vs. Baseline [−200, 0 ms].
    4.  **Selection Criteria:** Channels with $p < 0.001$ and Cohen's $d > 0.5$ were assigned to the Auditory ROI.

### 2.2 Somatosensory Scout (S1/M1)
*   **Stimuli:** Somatosensory Evoked Potential (SEP) task (median nerve stimulation).
*   **Method:**
    1.  LFP-based phase reversal analysis.
    2.  HFA responsiveness (Z-score > 3.0) in the [0, 50 ms] window.
    3.  **Selection Criteria:** Identification of the N20/P20 reversal across the central sulcus and adjacent HFA-responsive clusters.

### 2.3 ROI Definition Output
Results are stored in `derivatives/rois/master_channel_map.json` and used to define the "Reference Pool" for Phase 1 preprocessing and for ROI-level statistical pooling in downstream analyses.

## 3. Preprocessing Pipeline

### 3.1 Signal Processing
*   **Script:** `code/preprocessing/run_daily_preproc.py`
*   **Filter:** Bandpass 0.5 – 250 Hz.
*   **Notch:** 60Hz harmonics.
*   **Reference:** Selective Common Median Reference (CMR). Auditory channels excluded from median.
*   **HFA Extraction:** Hilbert Transform (70–150 Hz) → Amplitude Envelope.
*   **Downsampling:** 1000 Hz → 500 Hz (anti-alias filtered).

### 3.2 Epoching
**Script:** `code/epoching/cut_epoch_unified.py`
1.  **Sequence Epochs:** [−0.5s, 4.5s] relative to sequence onset (for Global Baseline & Frequency Tagging).
2.  **Tone Epochs:** [−0.2s, 0.8s] relative to tone onset (500 timepoints at 500 Hz).
    *   **Local Baseline:** [−50ms, 0ms] relative to tone onset.
    *   **Global Baseline:** [−200ms, 0ms] relative to sequence onset.

## 4. Analysis Frameworks (Script-Verified)

### 4.1 Time-Resolved GLM
**Script:** `code/glm_analysis/run_glm_hierarchical.py`
*   **Input:** Concatenated Design Matrix `glm_dataset_{erp|hfa}_{baselocal|baseglobal}.h5`.
*   **Preparation:** `code/glm_analysis/prepare_glm_data.py`
*   **Models:**
    *   **Model A:** `ToneID`, `Repetition`, `IsHab`.
    *   **Model B:** Model A + `Length_c`, `Surprisal`, `Interaction`, `Position_c`.
    *   **Model C:** Model A + `MDL`, `IsDeviant`, `Position_c`.
    *   **Model D (Competition):** Model A + `Length_c`, `Surprisal`, `MDL`, `Position_c`.
*   **Inference:** Hierarchical (Channel Level → ROI Level).
*   **Resolution:** 2 ms timepoints (500 Hz), −200 to +800 ms.

### 4.2 Quick Screening (Uncorrected)
**Scripts:** `code/glm_analysis/run_glm_stats.py`, `code/glm_analysis/plot_glm_results.py`
*   **Purpose:** Rapid identification of potential effects across all predictors before running computationally intensive permutation tests.
*   **Method:** Applies a fixed threshold of $T > 1.96$ ($p < 0.05$ uncorrected) to the ROI-level T-statistics from Step 4.1.
*   **Output:** Summary CSV of temporal clusters and visualization of beta time-courses.

### 4.3 Permutation Testing (Cluster-Based)
**Script:** `code/glm_analysis/run_glm_permutation.py`
*   **Method:** Cluster-based permutation test (Maris & Oostenveld, 2007) on ROI-level T-statistics.
*   **Significance:** Cluster-level corrected $p < 0.05$ (two-tailed) based on a null distribution of maximum cluster masses (1000 permutations).
*   **Arguments:** `--data_type [erp|hfa] --baseline_mode [local|global] --model [A|B|C|D] --predictor [name]`

### 4.4 Gating Hypothesis (Regime Shift)
**Script:** `code/analysis/analyze_gating_hypothesis.py`
*   **Logic:** Tests if Sequence Length gates the processing of Complexity (MDL).
*   **Sliding Window:** Partial regression of Neural Response ~ MDL at each timepoint [−0.05s, 0.6s], controlling for Position, ToneID, Repetition, and Surprisal confounds.
*   **Grouping:** Separately for Short (4, 6, 8) and Long (12, 16) sequences.
*   **Metric:** `Slope_MDL` (partial regression slope after residualizing confounds).

### 4.5 HFA–ERP Amplitude Coupling
**Script:** `code/analysis/analyze_gating_coupling.py`
*   **Hypothesis:** HFA activity at ~250 ms drives ERP modulation at ~280 ms.
*   **Method:** Trial-by-trial Pearson correlation of single-trial HFA amplitude (240–260 ms window) vs. ERP amplitude (270–290 ms window), within Auditory ROI.
*   **Grouping:** Separate correlations for Short and Long conditions.
*   **Arguments:** `--baseline_mode [local|global]`

### 4.6 HFA–ERP Latency Analysis
**Script:** `code/analysis/analyze_hfa_erp_latency.py`
*   **Hypothesis:** Short sequences produce faster neural processing, measurable as a shift in the temporal lag between HFA and ERP peaks.
*   **Method:**
    1. Per trial, apply Gaussian smoothing (σ=10ms) to reduce noise-driven peak jitter.
    2. Find t_HFA = time of peak smoothed HFA envelope amplitude (100–300 ms window).
    3. Find t_ERP = fractional area latency (50% AUC of smoothed |ERP|) in the 100–300 ms window.
    4. Compute Δt = t_ERP − t_HFA per trial (positive = ERP lags).
    5. Compare Δt between Short and Long trials (Mann-Whitney U).
    6. Compare Δt variance (Levene's test) for Precision hypothesis.
*   **Resolution:** 2 ms (at 500 Hz sampling), enabling sub-4 ms latency differences.
*   **Arguments:** `--baseline_mode [local|global]`

### 4.7 Phase–Amplitude Coupling (PAC)
**Script:** `code/analysis/analyze_pac.py`
*   **Hypothesis:** The phase of slow oscillations (theta, ~4 Hz tone rate) modulates HFA amplitude, and this coupling may differ between Short and Long sequences.
*   **Method (Tort et al., 2010 — Modulation Index):**
    1. Extract phase φ(t) from ERP via bandpass filtering (default 4–8 Hz) + Hilbert transform.
       - **Edge Artifact Mitigation:** Due to the short 0.8s analysis window (only 3.2 cycles at 4 Hz), **Mirror Padding** (0.5s) is applied at both ends of the segment before filtering and Hilbert transformation to ensure stable phase estimation.
    2. Use HFA amplitude A(t) directly.
    3. Divide phase into 18 bins (20° each); compute mean A per bin.
    4. MI = KL-divergence(observed distribution, uniform) / log(N_bins).
    5. **Significance:** 200 circular-shift surrogates per condition, computed on N-equalized subsamples (consistent with observed MI statistic).
    6. **Bootstrap subsampling:** Long group subsampled to match Short trial count (N = 9,384) over 100 iterations to correct for 5.3:1 trial imbalance.
*   **Analysis window:** 0–800 ms post-onset.
*   **Arguments:** `--baseline_mode [local|global] --freq_low [Hz] --freq_high [Hz]`

### 4.8 Feature Morphology (Latency, RSI & Waveform Shape)
**Script:** `code/analysis/analyze_gating_latency_rsi.py`
*   **Metrics:** AUC (Energy), FWHM (Precision/Sharpness), Rise Slope (Efficiency), Peak Latency.
*   **Windows:**
    *   Tone 0: [−200, −50] ms (History/Pre-target).
    *   Tone 1: [50, 200] ms (Sensory).
    *   Tone 2: [250, 450] ms (Cognitive/Late).
*   **Statistics:** Mann-Whitney U (Short vs. Long) per tone and metric.
*   **Arguments:** `--data_type [erp|hfa] --baseline_mode [local|global]`

### 4.9.1 Frequency Tagging (PSD)
**Script:** `code/analysis/analysis_frequency.py`
*   **Method:** PSD computed on sequence-level epochs during Habituation using Welch's method with **per-length `nperseg`** (= full sequence duration). Frequency resolution scales with sequence length: 1.0 Hz (L4), 0.5 Hz (L8), 0.33 Hz (L12), 0.25 Hz (L16). Structure-specific power isolated by subtracting RandomControl PSD.
### 4.9.2 Phase-Based Tracking (ITC) - Statistical Protocol
To rescue structural analysis where PSD matches were weak, we implemented **Inter-Trial Coherence (ITC)** with robust statistical controls:
- **Method:**
  - **FFT Spectrum:** Complex spectral coefficients were computed on the **full sequence duration** per trial (per-length resolution, matching PSD).
  - **Trial Count Equalization (Subsampling):** ITC is biased by trial count ($Bias \approx 1/\sqrt{N}$). To remove this, for each (Condition, Control) pair, we identified $N_{min} = \min(N_{cond}, N_{ctrl})$. We randomly subsampled $N_{min}$ trials from each group 50 times and averaged the results.
  - **ITC Calculation:** $ITC(f) = | \frac{1}{N} \sum_{n=1}^N \frac{Z_n(f)}{|Z_n(f)|} |$.
  - **Difference Spectrum:** $ITC_{Structure} - ITC_{RandomControl}$ isolates phase-locked organizational tracking.
- **Statistical Inference (Permutation Test):**
  - **Null Distribution:** Labels (Structural vs. Random) were shuffled 1000 times within each subject and condition to build a null distribution of the difference score.
  - **Significance:** A peak was considered significant if the observed difference fell in the top 5% of the null distribution (p < 0.05).
- **Expected Peaks:** 1Hz (Pairs), 2Hz (Alternation), 0.5Hz (Quadruplets — resolvable at Length ≥ 8).

---

### 4.10 Time-Resolved Unique Variance Analysis ($\Delta R^2$)
**Script:** `code/analysis/analyze_unique_variance.py`
*   **Hypothesis:** Isolates the unique contribution of local prediction error (Surprisal) vs. global complexity (MDL) over time.
*   **Method:** Fits nested GLM models at each timepoint:
    1.  Full Model: $Y \sim Pos + Surp + MDL + Controls$
    2.  Reduced MDL: $Y \sim Pos + Surp + Controls$
    3.  Reduced Surp: $Y \sim Pos + MDL + Controls$
*   **Metric:** $\Delta R^2_{MDL} = R^2_{Full} - R^2_{Red\_MDL}$ (likewise for Surprisal).
*   **Significance:** Permutation test (200 iterations) shuffling the target predictor column (MDL or Surprisal) and recomputing ROI-averaged ΔR² to build a null distribution.
*   **Axiology:** X-axis shows time relative to deviant tone [-250, 500 ms], allowing observation of contextual peaks (Tone 0, Deviant, Tone +1).
*   **Baseline:** Global Baseline ([-200ms, 0ms] relative to sequence onset).
*   **Surprisal Reset:** Note that Surprisal is calculated with a model reset at the beginning of each sequence, supporting variable lengths (4–16 tones) as per AlRoumi et al. (2023).

---

### 4.11 Neural State Trajectory Analysis
**Script:** `code/analysis/analyze_neural_trajectory.py`
*   **Purpose:** To visualize population-level dynamics and identify the **Context-dependent Configuration** (or **State Maintenance**) that distinguishes Short from Long sequence processing.
*   **Method:**
    1.  **Data Selection:** Use sequence-level epochs [−0.5s, 4.5s] to capture activity before and during the sequence.
    2.  **ROI Filtering:** Restrict analysis to channels within the Auditory Core/Peripheral ROIs.
    3.  **Preprocessing:**
        *   Global Baseline [−200ms, 0ms] subtraction.
        *   Gaussian smoothing (σ = 20ms).
    4.  **Averaging:** Average all trials for Short (Length 4, 6) and Long (Length 12, 16) conditions.
    5.  **PCA Projection:** Perform PCA on the merged condition-averaged matrices (Time × Channels) and project both trajectories onto the first 2–3 principal components.
    6.  **Statistical Validation:**
        *   Compute Euclidean distance between Short and Long trajectories at each timepoint.
        *   **Permutation Test:** Shuffle Short/Long labels at the trial level (500 iterations) to establish a null distribution of distances and identify significant separation intervals.

---

### 4.12 MMN-proxy Regression (Prediction Strength Index)
**Script:** `code/analysis/analyze_mmn_regression.py`
*   **Logic:** Tests if MMN (Deviant - Standard) amplitude/energy serves as a proxy for prediction strength indexed by Complexity (MDL).
*   **Method:**
    1.  **Metric Extraction:** Peak amplitude and AUC (trapezoidal integration) of the difference wave.
    2.  **Subject Dissociation:** Independent analysis for Boss and Carol to avoid cancellation of opposing cognitive strategies.
    3.  **Local Baseline Force:** Analysis restricted to **Tone-based baseline** ([-50, 0]ms) to eliminate artifactual "Global State Drift" during long sequences.
    4.  **Regression:** Linear regression ($\text{MMN Metric} \sim \text{MDL}$) performed separately for Short (4-8) and Long (12-16) sequences.
*   **Visualization:** Boxplots with jittered stripplots to accommodate discrete MDL levels.

---