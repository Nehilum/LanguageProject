# A Dynamical Regime Shift Limits the Capacity for Abstract Sequence Compression in Primate Auditory Cortex

This repository contains the analysis pipeline and key results for investigating the biological limits of abstract sequence compression in the macaque monkey (*Macaca mulatta*). Using high-density Electrocorticography (ECoG), we track how the primate auditory cortex processes auditory sequences of varying complexity and length.

## 🧠 Project Overview

The core objective of this study is to test the "Language of Thought" hypothesis in non-human primates. We dissociate subject-specific encoding strategies from universal dynamical limits using a "Stress Test" paradigm.

### Key Findings
1.  **Complexity Tracking**: In the low-load regime (Short sequences, 4–8 items), the auditory cortex tracks structural complexity (Minimal Description Length, MDL).
2.  **Diverse Strategies**: Subjects employ distinct strategies—**Subject Boss** uses an "Efficiency/Predictive Coding" mode, while **Subject Carol** uses a "Recruitment/Cognitive Effort" mode.
3.  **Capacity Limit**: A universal breakdown of complexity tracking occurs as sequence length exceeds ~12 items.
4.  **Dynamical Regime Shift**: State-space analysis reveals that cognitive overload is marked by neural trajectories "escaping" the computational manifold into a disjoint, passive attractor state.

## 📂 Repository Structure

This repository is a filtered subset of the full analysis pipeline, focusing on reproducibility and visualization.

- `code/`: Python analysis scripts.
    - `analysis/`: Core statistical and hypothesis testing scripts (Gating, PAC, ITC, etc.).
    - `glm_analysis/`: Time-resolved hierarchical GLM implementation.
    - `visualization/`: Utility scripts for generating figures and sensor-level plots.
- `figures/`: High-resolution PNGs of the primary results (Figures 1-3).
- `docs/`: Supplemental documentation and manifest files.
- `*.md`: Scientific narrative, methods, and results documentation.
- `*.sh`: Shell scripts for running the full analysis pipeline.

### Core Dependencies
- **Data Prep**: `prepare_glm_data.py`
- **Gating**: `analyze_gating_hypothesis.py`
- **Trajectories**: `analyze_neural_trajectory.py`
- **MMN Regression**: `analyze_mmn_regression.py`

### Running the Pipeline
To reproduce the results (assuming access to the derivatives/ dataset):
```bash
bash run_full_analysis.sh
```
---
**Contact:** nehilum.0@gmail.com  
**Year:** 2026
