# A Dynamical Regime Shift Limits the Capacity for Abstract Sequence Compression in Primate Auditory Cortex

This repository contains the analysis pipeline and key results for investigating the biological limits of abstract sequence compression in the macaque. Using high-density Electrocorticography (ECoG), we track how the primate auditory cortex processes auditory sequences of varying complexity and length.

## 🧠 Project Overview

The core objective of this study is to test the "Language of Thought" hypothesis in non-human primates. We dissociate subject-specific encoding strategies from universal dynamical limits using a "Stress Test" paradigm.

## 📂 Repository Structure

This repository is a filtered subset of the full analysis pipeline, focusing on reproducibility and visualization.

- `code/`: Python analysis scripts.
    - `analysis/`: Core statistical and hypothesis testing scripts (Gating, PAC, ITC, etc.).
    - `glm_analysis/`: Time-resolved hierarchical GLM implementation.
    - `visualization/`: Utility scripts for generating figures and sensor-level plots.
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
