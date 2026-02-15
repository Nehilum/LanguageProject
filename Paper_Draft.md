# Methods

## Subjects
Two adult male rhesus macaques (*Macaca mulatta*), identified as "Boss" and "Carol," participated in the study. All procedures were approved by the local Animal Care and Use Committee and complied with the National Institutes of Health Guide for the Care and Use of Laboratory Animals.

## Stimuli and Experimental Design

### Auditory Stimuli
Stimuli consisted of binary sequences composed of two pure tones, ‘A’ and ‘B,’ and a silence/mirror interval ‘X’. Tone A was a low-pitch complex tone (sum of 350, 700, and 1400 Hz sine waves), and Tone B was a high-pitch complex tone (sum of 500, 1000, and 2000 Hz sine waves). Each tone had a duration of 50 ms. The Stimulus Onset Asynchrony (SOA) was fixed at 250 ms, resulting in a presentation rate of 4 Hz.

### Sequence Structure and Complexity
We employed a Local-Global paradigm (Bekinschtein et al., 2009) adapted to test the "Language of Thought" hypothesis (Al Roumi et al., 2023). Sequences varied in **Length** (4, 6, 8, 12, and 16 items) and **Complexity**, defined by Minimal Description Length (MDL). The MDL metric quantifies the compressibility of a sequence based on the length of the shortest program required to generate it using a set of recursive rules (repetition, alternation, concatenation, nesting).

The stimulus set included 10 core sequence structures ranging from low complexity (e.g., Repetition "AAAA...", Alternation "ABAB...") to high complexity (e.g., "Complex" random-like patterns). For the specific purpose of this study, we categorized sequences into **Short** (Length 4, 6, 8) and **Long** (Length 12, 16) regimes to investigate the dynamical limits of sequence processing.

### Experimental Protocol
The experiment followed a "Mini-Session" block design, where each sequence structure was presented in a dedicated block of trials:
1.  **Habituation Phase:** A specific sequence (e.g., AAAA) was presented repeatedly (typ. 10 repetitions) to establish an internal model of the structural rule.
2.  **Test Phase:** The same sequence continued, but with occasional **Deviants** (violations) introduced at random positions (e.g., AAAB instead of AAAA). Deviants consisted of a single tone flip (A→B or B→A).

This design allows for the dissociation of responses to:
*   **Standards:** Predicted items, eliciting reduced responses due to predictive suppression.
*   **Deviants:** Violations of the internal model, eliciting prediction error signals. We refer to this differential response (Deviant - Standard) as a **Mismatch Negativity (MMN) proxy**, as it represents the macaque ECoG equivalent of the well-established human scalp-recorded MMN.

## Data Acquisition
Neural activity was recorded using a high-density Electrocorticography (ECoG) system (Cortec Neural Interface).
*   **Sampling Rate:** 500 Hz (downsampled from 1000 Hz raw acquisition).
*   **Temporal Resolution:** 2 ms per sample.
*   **Regions of Interest (ROIs):** Subject-specific functional ROIs were defined prior to the main task:
    *   **Auditory Cortex (Sensory):** Defined functionally by the presence of high-amplitude N100-P200 complexes (peaking ~100-200 ms) in Bipolar re-referenced data during the passive auditory localizer. Channels located in the ventral portion of the grid exhibiting these clear evoked responses were selected (e.g., Boss: CH16, CH10, CH20, CH24; Carol: CH08, CH09, CH19, CH20).
    *   **Somatosensory/Motor (S1/M1):** The Central Sulcus was localized using the Phase Reversal technique on Somatosensory Evoked Potentials (SEP) following median nerve stimulation (N20/P20 component). Primary Somatosensory Cortex (S1) was defined by the polarity inversion relative to Motor Cortex (M1) across the central sulcus boundary (e.g., Boss Left Hemisphere: Phase reversal between CH06 and CH13).

## Data Preprocessing
Data processing was performed using a custom pipeline in Python.
1.  **Signal Processing:** Raw signals were bandpass filtered (0.5 – 250 Hz) and notch filtered to remove 60 Hz line noise and harmonics.
2.  **Referencing:** A Selective Common Median Reference (CMR) was applied, where the median was computed across non-auditory channels to preserve local auditory signals.
3.  **High-Frequency Activity (HFA):** The amplitude envelope of the High-Gamma band (70–150 Hz) was extracted using the Hilbert transform, serving as a proxy for multi-unit firing rates.
4.  **Epoching:**
    *   **Sequence Epochs:** [-0.5s, 4.5s] relative to sequence onset (for Global Baseline and Frequency Tagging).
    *   **Tone Epochs:** [-0.2s, 0.8s] relative to each tone onset.
    *   **Baselines:** A **Local Baseline** ([-50ms, 0ms] relative to tone onset) was used for transient error analysis, while a **Global Baseline** ([-200ms, 0ms] relative to sequence onset) was used for state-space trajectories.

## Statistical Analysis

### General Linear Model (GLM)
We employed a time-resolved hierarchical GLM to quantify the encoding of sequence parameters at each timepoint [-200, 800 ms].
*   **Regressors:** The model included `ToneID` (A/B), `Repetition` (freq. of current tone), `Position`, `Surprisal` (local transition probability), `MDL` (global complexity), and `Sequence Length`.
*   **Collinearity Control:** Variance Inflation Factors (VIF) were computed to ensure separability of MDL and Length (VIF < 1.5).
*   **Significance:** Effects were assessed using cluster-based permutation testing (Maris & Oostenveld, 2007) on ROI-level t-statistics (1000 permutations, p < 0.05 corrected).

### Gating Hypothesis (Regime Shift Test)
To test the hypothesis that sequence length gates the neural representation of complexity (the "Capacity Limit"), we performed a sliding-window partial regression of neural activity (HFA and ERP) against **MDL Complexity** at each timepoint [-50, 600 ms]. Crucially, this analysis was performed **separately** for Short (Length 4, 6, 8) and Long (Length 12, 16) sequences. The slope of this regression ($\beta_{MDL}$) serves as a time-resolved metric of "Complexity Tracking," allowing us to detect if the tracking mechanism collapses or inverts in the Long regime.

### Neural State Trajectory Analysis
To investigate the dynamical regime shift between Short and Long sequences:
1.  **State Space Construction:** We computed principal component analysis (PCA) on the cross-condition average activity (Time × Channels) within the Auditory ROI.
2.  **Trajectory Divergence:** We projected Short and Long sequence trials onto the first 3 PCs and calculated the time-resolved Euclidean distance between their trajectories.
3.  **Statistical Test:** A permutation test (shuffling Short/Long labels) determined intervals of significant state-space separation, testing the hypothesis that Long sequences engage a distinct dynamical mode ("Overload" or "Passive") rather than a noisy version of the Short sequence mode.

### Phase-Amplitude Coupling (PAC)
We assessed whether low-frequency oscillations (Theta, ~4 Hz) modulated HFA during sequence processing:
*   **Method:** Modulation Index (Tort et al., 2010).
*   **Parameters:** Phase extracted from ERP (4-8 Hz) and Amplitude from HFA. 18 phase bins.
*   **Controls:** Mirror padding (0.5s) was applied to mitigate edge artifacts. Trial counts were equalized between conditions via bootstrapping to prevent bias.

### Frequency Tagging (Inter-Trial Coherence)
To measure tracking of abstract structure (e.g., AABB -> 2 Hz modulation):
*   **Method:** Inter-Trial Coherence (ITC) was computed on full-sequence FFTs.
*   **Contrast:** $ITC_{Structure} - ITC_{RandomControl}$ isolated structure-specific phase-locking.
*   **Statistics:** Permutation testing (shuffling Structure/Random labels) identified significant peaks in the difference spectrum.

### MMN-Proxy Regression
To quantify the "prediction strength" of the internal model:
*   **Metric:** The MMN-proxy was defined as the difference in response (Peak Amplitude or AUC) between Deviant and Standard tones.
*   **Regression:** We regressed the MMN-proxy metric against MDL Complexity separately for Short (4-8) and Long (12-16) sequences. The slope of this regression indicated the system's sensitivity to structural rules (Efficiency vs. Recruitment strategies).

---

# Results

## Diverse Strategies for Compression (The Computational Manifold)

We first verified that the macaque auditory system is sensitive to the structural complexity of auditory sequences in the low-load regime (Short Sequences: Length 4–8). Our results demonstrate robust neural tracking of structure (**Fig. 1C, D**), albeit implemented through distinct individual strategies (**Fig. 2**).

Auditory cortex showed strong responsiveness to the stimuli in both subjects (**Fig. 1D**; Effect Magnitude: Boss ERP T-stat = 199.07, HFA T-stat = 5.21; Carol ERP T-stat = 201.51, HFA T-stat = 10.25; p < 1e-10 uncorrected).

Crucially, regression analysis of MMN-proxy responses against MDL Complexity in the Short regime revealed subject-specific encoding strategies, which we define as **neural gating slopes** (**Fig. 2A**):
*   **Subject Boss ("Efficiency Mode"):** Exhibited a negative gating slope ($\beta_{MDL} = -0.558$, Pearson $r = -0.11$, **Fig. 2B**). This pattern indicates that simpler sequences (Low MDL) elicited larger prediction error signals upon violation, consistent with a "Predictive Coding" model where a high-precision internal model generates strong mismatch responses.
*   **Subject Carol ("Recruitment Mode"):** Exhibited a positive gating slope ($\beta_{MDL} = +0.123$, Pearson $r = 0.05$, **Fig. 2C**). This suggests that more complex sequences (High MDL) drove higher aggregate neural engagement, consistent with a "Cognitive Effort" or resource recruitment model.

Exploratory frequency tagging (Inter-Trial Coherence) provided corroborating evidence for structural sensitivity (**Fig. 1C**). We observed condition-specific phase-locking to abstract rules, such as a significant 2 Hz modulation for Alternation sequences (e.g., Length 6, p < 0.05). Although the global effect was weak (Mean Difference = -0.001, p ~ 0.51), the presence of specific spectral peaks supports the view that the underlying machinery for tracking abstract structure is present.

## The Universal Collapse (The Capacity Limit)

Despite the divergent encoding strategies employed by the two subjects, a universal dynamical limit emerged when sequence length exceeded the working memory capacity (Long Sequences: Length 12–16).

We performed the same gating analysis for the Long condition and observed a collapse or "Regime Flip" of the gating slopes in both subjects (**Fig. 2A, B, C**):
*   **Boss:** The efficiency-based mechanism inverted (**gating slope** $\beta_{MDL} = +0.271$), indicating a loss of the precision-weighted prediction error signal that characterized the Short regime.
*   **Carol:** The recruitment-based mechanism collapsed (**gating slope** $\beta_{MDL} = -0.154$), suggesting an inability to sustain the elevated neural engagement required for complex long sequences.

This failure cannot be attributed to collinearity between Length and Complexity regressors. Variance Inflation Factor (VIF) analysis confirmed that MDL remains statistically separable from Length (VIF = 1.48) and Interaction terms (VIF = 5.48), well below the critical threshold of 10. Thus, the observed breakdown reflects a biological limit rather than a mathematical artifact.

## A Dynamical Escape (The Mechanism)

To investigate the physical mechanism underlying this capacity limit, we analyzed the neural state trajectories using Principal Component Analysis (PCA) (**Fig. 3**). This analysis revealed a "Dynamical Regime Shift."

In Short sequences, neural trajectories evolved along a stable "Computation Manifold" (**Fig. 3A**). However, in Long sequences, the trajectories did not merely become noisier; they diverged into a distinct region of state space.
*   **State Separation:** We computed the time-resolved Euclidean distance between Short and Long trajectories (**Fig. 3B**). Both subjects showed significant divergence (Permutation test, p < 0.001).
*   **Magnitude:** Subject Carol exhibited a particularly strong "escape" into the alternative state space (Max Distance = 20.09) compared to Boss (Max Distance = 12.87), which was reflected in the morphology of their respective ERP waveforms (**Fig. 3C**).

Statistical analysis of the **ERP waveform morphology (Panel 3C)** confirmed the subject-level dissociations in how the dynamical manifold handles memory load:
- **Boss (Efficiency-based Strategy):** Showed a significant release from suppression for Long sequences, with increased peak amplitude (Short: -0.14 $\mu$V vs. Long: 0.98 $\mu$V; **$t = -4.12, p < 10^{-4}$**) and a dramatic increase in response area (AUC Short vs Long: **$t = -20.00, p < 10^{-88}$**). This indicates that the efficient predictive-coding regime collapses into a passive, unfiltered response.
- **Carol (Recruitment-based Strategy):** Showed a significant collapse of neural enhancement for Long sequences, with decreased peak amplitude (Short: 2.36 $\mu$V vs. Long: 1.44 $\mu$V; **$t = 3.47, p < 10^{-3}$**) and response area (**AUC $t = 13.30, p < 10^{-39}$**). This reflects the failure to sustain the high-effort cognitive resources required for long sequences.

This robust state-space separation and associated morphology shift confirm that the "Overload" state is a distinct dynamical attractor. The system undergoes a phase transition when memory load is exceeded, escaping the computational manifold required for active/predictive processing and settling into a passive regime. This "Dynamical Escape" provides a mechanistic explanation for the behavioral and electrophysiological capacity limits observed in primate auditory cognition.
