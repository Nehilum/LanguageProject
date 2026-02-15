# Figure- [x] Update documentation to match findings
- [x] Verify the fixprovides a detailed overview of the generation scripts and figure legends for the three main figures of the paper.

---

## Figure 1: Paradigm & Neural Encoding of Structure

### 1. Script Information
- **Script Path**: `code/figures/generate_figure1.py`
- **Output Path**: `figures/Figure1.png`
- **Dependencies**: `numpy`, `pandas`, `matplotlib`, `seaborn`, `scipy`, `pathlib`

### 2. Inputs & Data Sources
| Input Path Pattern | Description | Used For |
| :--- | :--- | :--- |
| `derivatives/epochs/{condition}_{L}/{subject}/*_epochs.npz` | Preprocessed Epochs (Signals & Metadata) | **Panel C**: Phase coherence calculation (ITC) |
| `derivatives/epochs/{grammar}_{L}/{subject}/*_epochs.npz` | Preprocessed Epochs (Standard & Violation) | **Panel D**: ERP averaging |
| `derivatives/rois/functional_rois.json` | ROI Definitions | Channel selection (Auditory ROI) |

### 3. Figure Legend
**Figure 1: Experimental Paradigm and Neural Encoding of Abstract Structure.**
**(A & B)** Schematics of the experimental design and auditory sequence structures (Placeholders).
**(C) Frequency Tagging Analysis.**
Inter-Trial Coherence (ITC) spectrum showing the difference between Structured (Alternation) and Random sequences. A significant peak at **2 Hz** (arrow) confirms that the neural system tracks the abstract structural rule (A-B-A-B pattern, period = 2 items). The spectrum is averaged across subjects (Boss & Carol) and electrodes within the auditory ROI.
**(D) Mismatch Negativity (MMN) Response.**
Grand Average Event-Related Potentials (ERPs) for Standard (Gray) and Deviant/Violation (Red) tones.
- **Data Selection**: This Grand Average pools trials from **Repetition** and **Triplets** grammars across both subjects. These conditions yield a consistent and robust Mismatch Response, whereas other grammars (e.g., Alternation, Pairs) exhibit subject-level dissociations (Efficiency vs. Recruitment modes) that cancel out in a grand average (see Figure 2 for individual strategy analysis).
- **Standard**: The specific tone is predicted by the global sequence structure.
- **Deviant**: A structural violation (e.g., A-A in an A-B rule) elicits a robust Mismatch Response ($p < 0.001$).
- **Shaded Regions**: Indicate standard error of the mean (SEM).
- **Gray Vertical Shading**: Highlights the time window(s) of significant difference ($p < 0.05$), automatically calculated via point-wise t-tests.
- **Statistical Annotation**: The pooled p-value for the predefined window (150-350ms) is displayed on the plot.

---

## Figure 2: Individual Strategy

### 1. Script Information
- **Script Path**: `code/figures/Figure2_IndividualStrategy.py`
- **Output Path**: `figures/Figure2_IndividualStrategy.png`
- **Dependencies**: `numpy`, `pandas`, `matplotlib`, `seaborn`, `pathlib`

### 2. Inputs & Data Sources
| Input File | Description | Used For |
| :--- | :--- | :--- |
| `derivatives/analysis/mmn_regression/regression_stats_refined.csv` | Regression Slopes | **Panel A**: Grouped Bar Plot |
| `derivatives/MMN/stats_comparison_summary.csv` | Single-Trial MMN Amplitude | **Panel B**: Boxplot & Regression |
| `derivatives/predictors/**/*.csv` | Sequence Metadata | MDL Mapping |

### 3. Figure Legend
**Figure 2: Individual Strategies for Handling Complexity.**
This figure illustrates the divergence in neural strategies between subjects when facing increasing sequence complexity, organized in a **2x3 grid**.
**(A) Neural Gating Slopes (Column 1).**
Bar plot displaying the encoding strength (slope of MMN vs. MDL) for Short (Blue) vs. Long (Red) sequences.
- **Boss (Efficiency Mode)**: Shows a "Regime Flip"—predictive encoding (negative slope) for short sequences reverses for long sequences.
- **Carol (Recruitment Mode)**: Shows a "Capacity Limit"—attentional enhancement (positive slope) for short sequences collapses for long sequences.
**(B & C) Trial-level Prediction Failure (Columns 2 & 3).**
Boxplots with overlaid regression lines showing single-trial MMN amplitude as a function of MDL complexity, with **shared Y-axes** for cross-subject comparison.
- **Top Row (Boss)**: Illustrates the transition from predictive coding to mechanism breakdown.
- **Bottom Row (Carol)**: Illustrates the collapse of the recruitment-based enhancement strategy.
- **Zero Lines**: Horizontal dashed lines at $y=0$ visualize the decay of the neural tracking signal.

---

## Figure 3: The Dynamical Mechanism

### 1. Script Information
- **Script Path**: `code/figures/generate_figure_3.py`
- **Output Path**: `figures/Figure3_DynamicalMechanism.png`
- **Dependencies**: `numpy`, `pandas`, `matplotlib`, `sklearn`, `scipy`, `pathlib`

### 2. Inputs & Data Sources
| Input File | Description | Used For |
| :--- | :--- | :--- |
| `derivatives/epochs/**/*.npz` | Raw Epochs (All Conditions) | **Panel A**: PCA Trajectory Calculation |
| `derivatives/analysis/trajectory/Trajectory_Stats_{subject}.csv` | Euclidean Distance Stats | **Panel B**: Distance Time Course |
| `derivatives/analysis/gating/gating_waveforms_erp_baseglobal.csv` | Aggregated ERPs | **Panel C**: ERP Morphology Comparison |

### 3. Figure Legend
**Figure 3: Dynamical Mechanism of Regime Shifts.**
**(A) Neural State Trajectories (Manifolds).**
PCA-based visualization of the neural state space trajectory for Short (Blue) vs. Long (Red) sequences.
- **Manifolds**: The trajectories are rendered as 2D manifolds (tubes/bubbles) where the volume indicates the **Standard Error of the Mean (SEM)** across trials.
- **Divergence**: The volumetric representation highlights that the brain shifts into a distinct neural subspace for Long sequences, rather than simply exhibiting a noisier version of the Short-sequence state.
- **Key Events**: **X** marks Tone Onset; **Gray dot** marks Epoch Start.
**(B) State Separation.**
Time course of the Euclidean distance between Short and Long neural states in the high-dimensional space.
- **Red Shading**: Indicates time windows of significant divergence (p < 0.05).
- The sustained separation confirms that the brain treats "Overload" as a distinct dynamical state, not just a noisy version of the "Competent" state.
**(C) ERP Morphology.**
Comparison of the temporal response profile for Short vs. Long sequences.
- **Boss (Efficiency Mode)**: Shows suppressed amplitude for Long sequences, consistent with neuronal efficiency or gating.
- **Carol (Enhancement Mode)**: Shows enhanced amplitude for Short sequences that cannot be sustained for Long ones.
- **Shaded Regions**: SEM.
