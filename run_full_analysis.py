import os
import sys
import subprocess
from datetime import datetime

# ==============================================================================
# MonkeyLanguage Analysis Pipeline - Master Execution Script (Python Wrapper)
# ==============================================================================
#
# Purpose: Automates the entire analysis flow from preprocessing to visualization.
# Author: Antigravity AI
# Version: 2026-02-26
#
# Usage:
#   python run_full_analysis.py
#
# Note: Functional Mapping (Phase 0) is excluded as it requires manual selection.
# ==============================================================================

# Exit immediately if a command exits with a non-zero status
# In python we achieve this by checking returncode in our run() function.

# --- Configuration ---
os.makedirs("derivatives", exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = f"derivatives/pipeline_run_{timestamp}.log"
os.environ["PYTHONUNBUFFERED"] = "1"

def log_print(msg, end="\n"):
    print(msg, end=end, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + end)

# Initialize Log
log_print(f"Starting Analysis Pipeline Run: {datetime.now()}")
log_print("------------------------------------------------")

def run(cmd_args):
    """
    Function to log and run a command.
    """
    current_time = datetime.now().strftime("%H:%M:%S")
    cmd_str = " ".join(cmd_args)
    log_print(f"\n[{current_time}] RUNNING: {cmd_str}")

    process = subprocess.Popen(
        cmd_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=False, # Read as bytes to avoid cp1252/cp932 decoding errors
        bufsize=1
    )

    for line_bytes in iter(process.stdout.readline, b''):
        # Decode ignoring errors, then encode to console safe, or just let python handle it cleanly 
        line_str = line_bytes.decode('utf-8', errors='replace')
        sys.stdout.buffer.write(line_str.encode(sys.stdout.encoding or 'utf-8', errors='replace'))
        sys.stdout.flush()
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line_str)

    process.wait()
    if process.returncode != 0:
        log_print(f"Error: Command exited with status {process.returncode}: {cmd_str}")
        sys.exit(process.returncode)

PYTHON_EXE = sys.executable

# --- Phase 1: Preprocessing & Basic Data Prep ---
log_print("\n>>> Phase 1: Preprocessing & Basic Data Prep")

run([PYTHON_EXE, "code/preprocessing/run_daily_preproc.py"])
run([PYTHON_EXE, "code/glm_analysis/generate_predictors.py"])
run([PYTHON_EXE, "code/epoching/cut_epoch_unified.py"])

# --- Phase 2: Core Analysis & GLM Loops ---
DATA_TYPES = ["erp", "hfa"]
BASELINE_MODES = ["local", "global"]

log_print("\n>>> Phase 2: Hierarchical GLM & Gating Analysis")

for data_type in DATA_TYPES:
    for base_mode in BASELINE_MODES:
        log_print(f"\n--- Processing: Type={data_type}, Baseline={base_mode} ---")

        # 1. Prepare GLM Data (H5 Generation)
        run([PYTHON_EXE, "code/glm_analysis/prepare_glm_data.py", 
             "--data_type", data_type, 
             "--baseline_mode", base_mode])

        # 2. Fit Hierarchical GLM (Level 1 & 2)
        run([PYTHON_EXE, "code/glm_analysis/run_glm_hierarchical.py", 
             "--data_type", data_type, 
             "--baseline_mode", base_mode])

        # 3. GLM Stats and Plotting (Screening)
        for model in ["ModelA", "ModelB", "ModelC", "ModelD"]:
            run([PYTHON_EXE, "code/glm_analysis/run_glm_stats.py", 
                 "--data_type", data_type, 
                 "--baseline_mode", base_mode, 
                 "--model", model])
            run([PYTHON_EXE, "code/glm_analysis/plot_glm_results.py", 
                 "--data_type", data_type, 
                 "--baseline_mode", base_mode, 
                 "--model", model])

        # 4. Cluster-based Permutation Testing (Scientific Significance)
        # Model B: Test Length and Surprisal
        for pred in ["Length_c", "Surprisal"]:
            run([PYTHON_EXE, "code/glm_analysis/run_glm_permutation.py", 
                 "--data_type", data_type, 
                 "--baseline_mode", base_mode, 
                 "--model", "ModelB", 
                 "--predictor", pred])

        # Model C: Test MDL
        run([PYTHON_EXE, "code/glm_analysis/run_glm_permutation.py", 
             "--data_type", data_type, 
             "--baseline_mode", base_mode, 
             "--model", "ModelC", 
             "--predictor", "MDL"])

        # Model D: Competition (Test MDL, Length, and Surprisal)
        for pred in ["MDL", "Length_c", "Surprisal"]:
            run([PYTHON_EXE, "code/glm_analysis/run_glm_permutation.py", 
                 "--data_type", data_type, 
                 "--baseline_mode", base_mode, 
                 "--model", "ModelD", 
                 "--predictor", pred])

        # 5. Gating Hypothesis Analysis
        run([PYTHON_EXE, "code/analysis/analyze_gating_hypothesis.py", 
             "--data_type", data_type, 
             "--baseline_mode", base_mode])

        # 6. Waveform Morphology (Latency & RSI)
        run([PYTHON_EXE, "code/analysis/analyze_gating_latency_rsi.py", 
             "--data_type", data_type, 
             "--baseline_mode", base_mode])

        # 7. Unique Variance Analysis (Delta R^2)
        run([PYTHON_EXE, "code/analysis/analyze_unique_variance.py", 
             "--data_type", data_type, 
             "--baseline_mode", base_mode])


# --- Phase 3: Multi-modal / Cross-type Analyses ---
log_print("\n>>> Phase 3: Coupling & Cross-type Analyses")

for base_mode in BASELINE_MODES:
    log_print(f"\n--- Processing: Baseline={base_mode} ---")

    # HFA-ERP Amplitude Coupling
    run([PYTHON_EXE, "code/analysis/analyze_gating_coupling.py", 
         "--baseline_mode", base_mode])

    # HFA-ERP Latency Alignment
    run([PYTHON_EXE, "code/analysis/analyze_hfa_erp_latency.py", 
         "--baseline_mode", base_mode])

    # Phase-Amplitude Coupling (PAC)
    run([PYTHON_EXE, "code/analysis/analyze_pac.py", 
         "--baseline_mode", base_mode])


# --- Phase 4: Standalone & Specialized Analyses ---
log_print("\n>>> Phase 4: Standalone & Specialized Analyses")

run([PYTHON_EXE, "code/analysis/analysis_frequency.py"])
run([PYTHON_EXE, "code/analysis/analysis_frequency_itc.py"])
run([PYTHON_EXE, "code/analysis/analyze_baseline_state.py"])
run([PYTHON_EXE, "code/analysis/analyze_neural_trajectory.py"])
run([PYTHON_EXE, "code/analysis/analyze_mmn_regression.py"])

# Special: Resource Constraints depends on specifically Model C results.
RESULTS_C_ERP_LOCAL = "derivatives/glm_results/glm_results_erp_baselocal_ModelC.h5"
if os.path.exists(RESULTS_C_ERP_LOCAL):
    run([PYTHON_EXE, "code/glm_analysis/analyze_resource_constraints.py", 
         "--input_file", RESULTS_C_ERP_LOCAL, 
         "--output_dir", "derivatives/glm_results"])
else:
    log_print(f"Warning: {RESULTS_C_ERP_LOCAL} not found. Skipping Resource Constraints analysis.")


# --- Phase 5: Visualization ---
log_print("\n>>> Phase 5: Visualization")

run([PYTHON_EXE, "code/visualization/viz_sensor_erp.py"])
run([PYTHON_EXE, "code/visualization/plot_unique_variance.py", 
     "--data_type", "erp", 
     "--baseline_mode", "local"])
run([PYTHON_EXE, "code/visualization/plot_unique_variance.py", 
     "--data_type", "erp", 
     "--baseline_mode", "global"])

# Final Report
log_print("\n------------------------------------------------")
log_print(f"Analysis Pipeline Completed Successfully: {datetime.now()}")
log_print(f"Log file: {LOG_FILE}")
