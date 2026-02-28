import os
import sys
import subprocess
from datetime import datetime

# ==============================================================================
# MonkeyLanguage Analysis Pipeline - Remaining Analysis Execution Script
# ==============================================================================
#
# Purpose: Resumes the analysis pipeline from Phase 3, specifically
#          restarting from analyze_hfa_erp_latency.py (local mode).
# Author: Antigravity AI
# Version: 2026-02-28
#
# Usage:
#   python run_remaining_analysis.py
# ==============================================================================

os.makedirs("derivatives", exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = f"derivatives/pipeline_run_resume_{timestamp}.log"
os.environ["PYTHONUNBUFFERED"] = "1"
os.environ["PYTHONUTF8"] = "1"

def log_print(msg, end="\n"):
    print(msg, end=end, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + end)

log_print(f"Resuming Analysis Pipeline: {datetime.now()}")
log_print("------------------------------------------------")

def run(cmd_args):
    current_time = datetime.now().strftime("%H:%M:%S")
    cmd_str = " ".join(cmd_args)
    log_print(f"\n[{current_time}] RUNNING: {cmd_str}")

    process = subprocess.Popen(
        cmd_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=False,
        bufsize=1
    )

    for line_bytes in iter(process.stdout.readline, b''):
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

BASELINE_MODES = ["local", "global"]

# --- Phase 3: Multi-modal / Cross-type Analyses ---
log_print("\n>>> Phase 3 (Resumed): Coupling & Cross-type Analyses")

# The user's log shows failure occurred at:
# analyze_hfa_erp_latency.py --baseline_mode local
# Gating coupling local already finished right before latency crashed.

log_print("\n--- Processing: Baseline=local ---")
run([PYTHON_EXE, "code/analysis/analyze_hfa_erp_latency.py", 
     "--baseline_mode", "local"])

run([PYTHON_EXE, "code/analysis/analyze_pac.py", 
     "--baseline_mode", "local"])

# Then global baseline for Phase 3
log_print("\n--- Processing: Baseline=global ---")
run([PYTHON_EXE, "code/analysis/analyze_gating_coupling.py", 
     "--baseline_mode", "global"])

run([PYTHON_EXE, "code/analysis/analyze_hfa_erp_latency.py", 
     "--baseline_mode", "global"])

run([PYTHON_EXE, "code/analysis/analyze_pac.py", 
     "--baseline_mode", "global"])

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
log_print(f"Remaining Analysis Pipeline Completed Successfully: {datetime.now()}")
log_print(f"Log file: {LOG_FILE}")
