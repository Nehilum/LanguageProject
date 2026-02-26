#!/bin/bash

# ==============================================================================
# MonkeyLanguage Analysis Pipeline - Master Execution Script
# ==============================================================================
#
# Purpose: Automates the entire analysis flow from preprocessing to visualization.
# Author: Antigravity AI
# Version: 2026-02-15
#
# Usage:
#   chmod +x run_full_analysis.sh
#   ./run_full_analysis.sh
#
# Note: Functional Mapping (Phase 0) is excluded as it requires manual selection.
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
LOG_FILE="derivatives/pipeline_run_$(date +%Y%m%d_%H%M%S).log"
export PYTHONUNBUFFERED=1

# Initialize Log
echo "Starting Analysis Pipeline Run: $(date)" | tee "$LOG_FILE"
echo "------------------------------------------------" | tee -a "$LOG_FILE"

# Function to log and run
run() {
    echo -e "\n[$(date +%H:%M:%S)] RUNNING: $*" | tee -a "$LOG_FILE"
    # Ensure the command result is captured correctly with tee
    { "$@" 2>&1; echo "GEMINI_CLI_EXIT_CODE=$?" >&3; } 3> >(read -r; exit "${REPLY##*=}") | tee -a "$LOG_FILE"
}

# --- Phase 1: Preprocessing & Basic Data Prep ---
echo -e "\n>>> Phase 1: Preprocessing & Basic Data Prep" | tee -a "$LOG_FILE"

run python3 code/preprocessing/run_daily_preproc.py
run python3 code/glm_analysis/generate_predictors.py
run python3 code/epoching/cut_epoch_unified.py


# --- Phase 2: Core Analysis & GLM Loops ---
DATA_TYPES=("erp" "hfa")
BASELINE_MODES=("local" "global")

echo -e "\n>>> Phase 2: Hierarchical GLM & Gating Analysis" | tee -a "$LOG_FILE"

for data_type in "${DATA_TYPES[@]}"; do
    for base_mode in "${BASELINE_MODES[@]}"; do
        echo -e "\n--- Processing: Type=${data_type}, Baseline=${base_mode} ---" | tee -a "$LOG_FILE"

        # 1. Prepare GLM Data (H5 Generation)
        run python3 code/glm_analysis/prepare_glm_data.py \
            --data_type "$data_type" \
            --baseline_mode "$base_mode"

        # 2. Fit Hierarchical GLM (Level 1 & 2)
        run python3 code/glm_analysis/run_glm_hierarchical.py \
            --data_type "$data_type" \
            --baseline_mode "$base_mode"

        # 3. GLM Stats and Plotting (Screening)
        for model in "ModelA" "ModelB" "ModelC" "ModelD"; do
            run python3 code/glm_analysis/run_glm_stats.py \
                --data_type "$data_type" \
                --baseline_mode "$base_mode" \
                --model "$model"
            run python3 code/glm_analysis/plot_glm_results.py \
                --data_type "$data_type" \
                --baseline_mode "$base_mode" \
                --model "$model"
        done

        # 4. Cluster-based Permutation Testing (Scientific Significance)
        # Model B: Test Length and Surprisal
        for pred in "Length_c" "Surprisal"; do
            run python3 code/glm_analysis/run_glm_permutation.py \
                --data_type "$data_type" \
                --baseline_mode "$base_mode" \
                --model "ModelB" \
                --predictor "$pred"
        done

        # Model C: Test MDL
        run python3 code/glm_analysis/run_glm_permutation.py \
            --data_type "$data_type" \
            --baseline_mode "$base_mode" \
            --model "ModelC" \
            --predictor "MDL"

        # Model D: Competition (Test MDL, Length, and Surprisal)
        for pred in "MDL" "Length_c" "Surprisal"; do
            run python3 code/glm_analysis/run_glm_permutation.py \
                --data_type "$data_type" \
                --baseline_mode "$base_mode" \
                --model "ModelD" \
                --predictor "$pred"
        done

        # 5. Gating Hypothesis Analysis
        run python3 code/analysis/analyze_gating_hypothesis.py \
            --data_type "$data_type" \
            --baseline_mode "$base_mode"

        # 6. Waveform Morphology (Latency & RSI)
        run python3 code/analysis/analyze_gating_latency_rsi.py \
            --data_type "$data_type" \
            --baseline_mode "$base_mode"

        # 7. Unique Variance Analysis (Delta R^2)
        run python3 code/analysis/analyze_unique_variance.py \
            --data_type "$data_type" \
            --baseline_mode "$base_mode"
    done
done


# --- Phase 3: Multi-modal / Cross-type Analyses ---
echo -e "\n>>> Phase 3: Coupling & Cross-type Analyses" | tee -a "$LOG_FILE"

for base_mode in "${BASELINE_MODES[@]}"; do
    echo -e "\n--- Processing: Baseline=${base_mode} ---" | tee -a "$LOG_FILE"

    # HFA-ERP Amplitude Coupling
    run python3 code/analysis/analyze_gating_coupling.py \
        --baseline_mode "$base_mode"

    # HFA-ERP Latency Alignment
    run python3 code/analysis/analyze_hfa_erp_latency.py \
        --baseline_mode "$base_mode"

    # Phase-Amplitude Coupling (PAC)
    run python3 code/analysis/analyze_pac.py \
        --baseline_mode "$base_mode"
done


# --- Phase 4: Standalone & Specialized Analyses ---
echo -e "\n>>> Phase 4: Standalone & Specialized Analyses" | tee -a "$LOG_FILE"

run python3 code/analysis/analysis_frequency.py
run python3 code/analysis/analysis_frequency_itc.py
run python3 code/analysis/analyze_baseline_state.py
run python3 code/analysis/analyze_neural_trajectory.py
run python3 code/analysis/analyze_mmn_regression.py

# Special: Resource Constraints depends on specifically Model C results.
# This now calls the script with arguments, removing the need for `cp`.
RESULTS_C_ERP_LOCAL="derivatives/glm_results/glm_results_erp_baselocal_ModelC.h5"
if [ -f "$RESULTS_C_ERP_LOCAL" ]; then
    run python3 code/glm_analysis/analyze_resource_constraints.py \
        --input_file "$RESULTS_C_ERP_LOCAL" \
        --output_dir "derivatives/glm_results"
else
    echo "Warning: $RESULTS_C_ERP_LOCAL not found. Skipping Resource Constraints analysis." | tee -a "$LOG_FILE"
fi


# --- Phase 5: Visualization ---
echo -e "\n>>> Phase 5: Visualization" | tee -a "$LOG_FILE"

run python3 code/visualization/viz_sensor_erp.py
run python3 code/visualization/plot_unique_variance.py --data_type erp --baseline_mode local
run python3 code/visualization/plot_unique_variance.py --data_type erp --baseline_mode global

# Final Report
echo -e "\n------------------------------------------------" | tee -a "$LOG_FILE"
echo "Analysis Pipeline Completed Successfully: $(date)" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
