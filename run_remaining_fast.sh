#!/bin/bash

# ==============================================================================
# MonkeyLanguage Analysis Pipeline - Remaining Fast Execution
# ==============================================================================
# 
# Purpose: Skips already completed steps and runs remaining steps with 
#          fast parameters (N_PERM=0) for quick preliminary results.
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
LOG_FILE="derivatives/pipeline_fast_$(date +%Y%m%d_%H%M%S).log"
export PYTHONUNBUFFERED=1

# Initialize Log
echo "Starting Remaining Fast Analysis Run: $(date)" | tee "$LOG_FILE"
echo "------------------------------------------------" | tee -a "$LOG_FILE"

# Function to log and run
run() {
    echo -e "\n[$(date +%H:%M:%S)] RUNNING: $*" | tee -a "$LOG_FILE"
    { "$@" 2>&1; echo "GEMINI_CLI_EXIT_CODE=$?" >&3; } 3> >(read -r; exit "${REPLY##*=}") | tee -a "$LOG_FILE"
}

# --- Phase 2: Core Analysis & GLM Loops (Remaining) ---
# We already finished erp_local. 
# Remaining: erp_global, hfa_local, hfa_global
REMAINING_COMBOS=("erp global" "hfa local" "hfa global")

echo -e "\n>>> Phase 2: Hierarchical GLM & Gating Analysis (REMAINING)" | tee -a "$LOG_FILE"

for combo in "${REMAINING_COMBOS[@]}"; do
    read -r data_type base_mode <<< "$combo"
    echo -e "\n--- Processing: Type=${data_type}, Baseline=${base_mode} (FAST MODE) ---" | tee -a "$LOG_FILE"

    # 1. Prepare GLM Data (H5 Generation)
    run python3 code/glm_analysis/prepare_glm_data.py \
        --data_type "$data_type" \
        --baseline_mode "$base_mode"

    # 2. Fit Hierarchical GLM (Level 1 & 2)
    run python3 code/glm_analysis/run_glm_hierarchical.py \
        --data_type "$data_type" \
        --baseline_mode "$base_mode"

    # 3. Gating Hypothesis Analysis
    run python3 code/analysis/analyze_gating_hypothesis.py \
        --data_type "$data_type" \
        --baseline_mode "$base_mode"

    # 4. Waveform Morphology (Latency & RSI)
    run python3 code/analysis/analyze_gating_latency_rsi.py \
        --data_type "$data_type" \
        --baseline_mode "$base_mode"

    # 5. Unique Variance Analysis (FAST: n_perm=0)
    run python3 code/analysis/analyze_unique_variance.py \
        --data_type "$data_type" \
        --baseline_mode "$base_mode" \
        --n_perm 0
done


# --- Phase 3: Multi-modal / Cross-type Analyses ---
echo -e "\n>>> Phase 3: Coupling & Cross-type Analyses" | tee -a "$LOG_FILE"
BASELINE_MODES=("local" "global")

for base_mode in "${BASELINE_MODES[@]}"; do
    echo -e "\n--- Processing: Baseline=${base_mode} ---" | tee -a "$LOG_FILE"

    run python3 code/analysis/analyze_gating_coupling.py --baseline_mode "$base_mode"
    run python3 code/analysis/analyze_hfa_erp_latency.py --baseline_mode "$base_mode"
    
    # Note: PAC is still heavy. You may want to modify its N_SURR as well later.
    run python3 code/analysis/analyze_pac.py --baseline_mode "$base_mode"
done


# --- Phase 4: Standalone & Specialized Analyses ---
echo -e "\n>>> Phase 4: Standalone & Specialized Analyses" | tee -a "$LOG_FILE"

run python3 code/analysis/analysis_frequency.py
run python3 code/analysis/analysis_frequency_itc.py
run python3 code/analysis/analyze_baseline_state.py
run python3 code/analysis/analyze_neural_trajectory.py
run python3 code/analysis/analysis_mmn_roi.py

# Results_C dependency
RESULTS_C_ERP_LOCAL="derivatives/glm_results/glm_results_erp_baselocal_ModelC.h5"
if [ -f "$RESULTS_C_ERP_LOCAL" ]; then
    run python3 code/glm_analysis/analyze_resource_constraints.py \
        --input_file "$RESULTS_C_ERP_LOCAL" \
        --output_dir "derivatives/glm_results"
fi


# --- Phase 5: Visualization ---
echo -e "\n>>> Phase 5: Visualization" | tee -a "$LOG_FILE"

run python3 code/visualization/viz_sensor_erp.py
run python3 code/visualization/plot_unique_variance.py --data_type erp --baseline_mode local
run python3 code/visualization/plot_unique_variance.py --data_type erp --baseline_mode global

# Final Report
echo -e "\n------------------------------------------------" | tee -a "$LOG_FILE"
echo "Remaining Fast Analysis Completed: $(date)" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
