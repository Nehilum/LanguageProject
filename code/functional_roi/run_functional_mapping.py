import sys
import os
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd

# Add code folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from preprocessing import preproc_lib, events_lib

# --- CONFIG ---
DATA_ROOT = "/Users/nehilum/GitCode/MonkeyLanguage/NewPipeline/data" 

OUTPUT_DIR = "/Users/nehilum/GitCode/MonkeyLanguage/NewPipeline/derivatives/rois"
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")
EVENTS_ROOT = os.path.join(DATA_ROOT, "bids_events")

os.makedirs(FIG_DIR, exist_ok=True)

# Subject-specific file mappings
SUBJECT_FILES = {
    "Boss": {
        "routine_mat": "matfiles/Boss/20250620T112628B01.mat",
        "sep_mat": "matfiles/Boss/20250807T104429B01.mat",
        "routine_imp": "impedance/Boss/20250620T111241.csv",
        "sep_imp": "impedance/Boss/20250801T112941.csv"
    },
    "Carol": {
        "routine_mat": "matfiles/Carol/20250620T112628C01.mat",  # Update with actual Carol files
        "sep_mat": "matfiles/Carol/20250807T104429C01.mat",
        "routine_imp": "impedance/Carol/20250620T111241.csv",
        "sep_imp": "impedance/Carol/20250801T112941.csv"
    }
}

def epoch_data(data, fs, onsets, tmin, tmax, baseline=None):
    n_samples, n_ch = data.shape
    s_min = int(round(tmin * fs))
    s_max = int(round(tmax * fs))
    n_pts = s_max - s_min
    
    onset_samps = np.round(onsets * fs).astype(int)
    
    epochs = []
    
    for i, t0 in enumerate(onset_samps):
        start = t0 + s_min
        end = t0 + s_max
        if start < 0 or end > n_samples: continue
            
        epoch = data[start:end, :]
        if baseline:
            b_s_min = int(round(baseline[0] * fs)) - s_min
            b_s_max = int(round(baseline[1] * fs)) - s_min
            b_s_min = max(0, b_s_min)
            b_s_max = min(n_pts, b_s_max)
            if b_s_max > b_s_min:
                base_mean = np.mean(epoch[b_s_min:b_s_max, :], axis=0)
                epoch = epoch - base_mean
        epochs.append(epoch)
        
    times = np.linspace(tmin, tmax, n_pts, endpoint=False)
    return np.array(epochs), times

def run_auditory_scout(signals_hfa, fs, ch_names, onsets, bad_channels):
    print(f"Running Auditory Scout on {len(onsets)} trials...")
    tmin, tmax = -0.2, 0.8
    win_base = (-0.2, 0.0)
    win_resp = (0.0, 0.4)
    
    epochs, times = epoch_data(signals_hfa, fs, onsets, tmin, tmax, baseline=None)
    
    def get_indices(win):
        idx_start = np.searchsorted(times, win[0])
        idx_end = np.searchsorted(times, win[1])
        return idx_start, idx_end
        
    b_idx = get_indices(win_base)
    r_idx = get_indices(win_resp)
    
    val_base = np.mean(epochs[:, b_idx[0]:b_idx[1], :], axis=1)
    val_resp = np.mean(epochs[:, r_idx[0]:r_idx[1], :], axis=1)
    
    auditory_channels = []
    
    t_vals, p_vals = stats.ttest_rel(val_resp, val_base, axis=0)
    
    diff = val_resp - val_base
    sd_diff = np.std(diff, axis=0) + 1e-9
    cohens_d = np.mean(diff, axis=0) / sd_diff
    
    # LOGGING
    log_path = os.path.join(OUTPUT_DIR, "auditory_stats.txt")
    with open(log_path, "w") as f:
        f.write("Channel\tCohensD\tPFactor\tStatus\n")
        
        # Sort by D
        indices = np.argsort(cohens_d)[::-1]
        
        for i in indices:
            ch = ch_names[i]
            is_good = (ch.startswith("CH") and ch not in bad_channels)
            status = "GOOD" if is_good else "BAD/AUX"
            
            f.write(f"{ch}\t{cohens_d[i]:.4f}\t{p_vals[i]:.4e}\t{status}\n")
            
            if is_good:
                if p_vals[i] < 0.001 and cohens_d[i] > 0.5:
                    auditory_channels.append(ch)

    print(f"Auditory Channels selected: {auditory_channels}")
    plot_auditory(times, epochs, auditory_channels, ch_names)
    return auditory_channels

def plot_auditory(times, epochs, active_chs, all_chs):
    plt.figure(figsize=(10, 6))
    evoked = np.mean(epochs, axis=0)
    
    # Plot active red
    idx_active = [i for i, ch in enumerate(all_chs) if ch in active_chs]
    if idx_active:
        plt.plot(times, evoked[:, idx_active], 'r', alpha=0.5, label='Auditory ROI')
        
    # Plot others black
    idx_inactive = [i for i, ch in enumerate(all_chs) 
                    if ch not in active_chs and ch.startswith("CH")]
    if idx_inactive:
        plt.plot(times, evoked[:, idx_inactive], 'k', alpha=0.1, label='Others')
        
    plt.axvline(0, color='k', linestyle='--')
    plt.title(f"Auditory HFA Response (n={len(active_chs)})")
    plt.xlabel("Time (s)")
    plt.ylabel("HFA Amplitude")
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    plt.savefig(os.path.join(FIG_DIR, "auditory_scout_map.png"))
    plt.close()

def run_somato_scout(signals_lfp, signals_hfa, fs, ch_names, onsets, bad_channels):
    print(f"Running Somatosensory Scout on {len(onsets)} trials...")
    tmin, tmax = -0.05, 0.1
    baseline = (-0.05, 0.0)
    
    epochs_lfp, times = epoch_data(signals_lfp, fs, onsets, tmin, tmax, baseline=baseline)
    epochs_hfa, _ = epoch_data(signals_hfa, fs, onsets, tmin, tmax, baseline=None)
    
    evoked_lfp = np.mean(epochs_lfp, axis=0)
    evoked_hfa = np.mean(epochs_hfa, axis=0)
    
    somato_channels = []
    
    # Analysis 1: N20 Reversal
    # Only consider GOOD CH channels
    ch_indices = [i for i, name in enumerate(ch_names) 
                  if name.startswith("CH") and name not in bad_channels]
    
    idx_start = np.searchsorted(times, 0.015)
    idx_end = np.searchsorted(times, 0.025)
    
    peaks = np.max(evoked_lfp[idx_start:idx_end, :], axis=0)
    troughs = np.min(evoked_lfp[idx_start:idx_end, :], axis=0)
    
    polarities = np.zeros(len(ch_names))
    for i in ch_indices:
        if abs(troughs[i]) > abs(peaks[i]):
            polarities[i] = -1
        else:
            polarities[i] = 1
            
    # Check neighbors in CH list
    reversal_pairs = []
    # indices are subsets, but let's assume physical adjacency follows index order for CHxx
    # We should iterate through contiguous blocks of indices in ch_indices
    for k in range(len(ch_indices)-1):
        i = ch_indices[k]
        j = ch_indices[k+1]
        
        # Check if names are sequential (CH01, CH02)
        # Parse int
        try:
            id_i = int(ch_names[i].replace("CH", ""))
            id_j = int(ch_names[j].replace("CH", ""))
            is_adj = (abs(id_j - id_i) == 1)
        except:
            is_adj = False
            
        if is_adj and (polarities[i] * polarities[j] == -1):
            print(f"Reversal detected between {ch_names[i]}({polarities[i]}) and {ch_names[j]}({polarities[j]})")
            reversal_pairs.append((ch_names[i], ch_names[j]))
            if ch_names[i] not in somato_channels: somato_channels.append(ch_names[i])
            if ch_names[j] not in somato_channels: somato_channels.append(ch_names[j])
            
    # Analysis 2: HFA Responsiveness
    idx_hfa_start = np.searchsorted(times, 0.0)
    idx_hfa_end = np.searchsorted(times, 0.050)
    idx_base = np.searchsorted(times, -0.05)
    idx_zero = np.searchsorted(times, 0.0)
    
    base_mean = np.mean(evoked_hfa[idx_base:idx_zero, :], axis=0)
    base_std = np.std(evoked_hfa[idx_base:idx_zero, :], axis=0) + 1e-9
    resp_max = np.max(evoked_hfa[idx_hfa_start:idx_hfa_end, :], axis=0)
    z_scores = (resp_max - base_mean) / base_std
    
    for i in ch_indices:
        if z_scores[i] > 3.0:
            if ch_names[i] not in somato_channels:
                somato_channels.append(ch_names[i])
                
    somato_channels = sorted(list(set(somato_channels)))
    plot_somato(times, evoked_lfp, somato_channels, ch_names)
    return somato_channels

def plot_somato(times, evoked_lfp, active_chs, all_chs):
    if not active_chs: return
    plt.figure(figsize=(8, 10))
    offset = 0
    step = np.percentile(np.abs(evoked_lfp), 99) * 1.5 + 1e-6
    
    indices = [i for i, ch in enumerate(all_chs) if ch in active_chs]
    
    for i in indices:
        plt.plot(times * 1000, evoked_lfp[:, i] + offset, 'k')
        plt.text(times[0]*1000, offset, all_chs[i], fontsize=8)
        offset -= step
        
    plt.axvline(20, color='r', linestyle='--', alpha=0.5, label='20ms')
    plt.title(f"Somato LFP (N={len(active_chs)})")
    plt.xlabel("Time (ms)")
    plt.yticks([])
    plt.savefig(os.path.join(FIG_DIR, "sep_reversal.png"))
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Run Functional ROI Mapping")
    parser.add_argument("--subject", type=str, default="Boss", choices=["Boss", "Carol"],
                        help="Subject ID to process (Boss or Carol)")
    args = parser.parse_args()
    
    SUBJECT = args.subject
    
    # Get subject-specific file paths
    if SUBJECT not in SUBJECT_FILES:
        print(f"Error: Unknown subject '{SUBJECT}'. Available: {list(SUBJECT_FILES.keys())}")
        return
    
    files = SUBJECT_FILES[SUBJECT]
    ROUTINE_MAT = os.path.join(DATA_ROOT, files["routine_mat"])
    SEP_MAT = os.path.join(DATA_ROOT, files["sep_mat"])
    ROUTINE_IMP = os.path.join(DATA_ROOT, files["routine_imp"])
    SEP_IMP = os.path.join(DATA_ROOT, files["sep_imp"])
    
    print(f"Processing Subject: {SUBJECT}")
    
    # 1. Routine
    print(f"Loading Routine: {ROUTINE_MAT}")
    sig_rout, fs_rout, ch_rout = preproc_lib.load_cortec_data(ROUTINE_MAT)
    if sig_rout is None: return

    bad_imp_rout = preproc_lib.check_impedance(ROUTINE_IMP, ch_rout)
    bad_imp_rout += preproc_lib.REF_CHANNELS
    
    print(f"Routine Preproc (Fs={fs_rout})...")
    res_rout = preproc_lib.apply_preprocessing_step(sig_rout, fs_rout, ch_rout, bad_imp_rout)
    bad_channels_rout = res_rout['bad_channels_final']
    print(f"Bad Channels Routine: {bad_channels_rout}")

    events_file = events_lib.find_event_file(ROUTINE_MAT, EVENTS_ROOT)
    auditory_ch = []
    if events_file:
        onsets = events_lib.load_events(events_file, target_trial_types=['stimulus_on'])
        if len(onsets) > 0:
            auditory_ch = run_auditory_scout(
                res_rout['hfa'], fs_rout, ch_rout, 
                onsets, bad_channels_rout
            )
        else:
            print("Events found but zero 'stimulus_on' trials.")
    
    # 2. SEP
    print(f"Loading SEP: {SEP_MAT}")
    sig_sep, fs_sep, ch_sep = preproc_lib.load_cortec_data(SEP_MAT)
    bad_imp_sep = preproc_lib.check_impedance(SEP_IMP, ch_sep)
    bad_imp_sep += preproc_lib.REF_CHANNELS
    
    print("SEP Preproc...")
    res_sep = preproc_lib.apply_preprocessing_step(sig_sep, fs_sep, ch_sep, bad_imp_sep)
    bad_channels_sep = res_sep['bad_channels_final']
    print(f"Bad Channels SEP: {bad_channels_sep}")
    
    events_file_sep = events_lib.find_event_file(SEP_MAT, EVENTS_ROOT)
    somato_ch = []
    if events_file_sep:
        onsets_sep = events_lib.load_events(events_file_sep, target_trial_types=['ssep_stim'])
        if len(onsets_sep) > 0:
            somato_ch = run_somato_scout(
                res_sep['signals_cmr'], res_sep['hfa'], 
                fs_sep, ch_sep, onsets_sep, bad_channels_sep
            )
            
    # 3. Save
    master_map = {
        SUBJECT: {
            "Auditory": auditory_ch,
            "Somatosensory": somato_ch,
            "Reference": preproc_lib.REF_CHANNELS,
            "Bad_Routine_Stat": bad_channels_rout,
            "Bad_SEP_Stat": bad_channels_sep
        }
    }
    
    out_path = os.path.join(OUTPUT_DIR, "master_channel_map.json")
    with open(out_path, "w") as f:
        json.dump(master_map, f, indent=2)
    print(f"Saved Master Map to {out_path}")

if __name__ == "__main__":
    main()
