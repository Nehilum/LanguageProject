import sys
import os
import traceback
import json
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, sosfiltfilt, filtfilt, iirnotch

# --- PATH CONFIGURATION ---
# Script Location: NewPipeline/code/functional_roi/run_final_visualization.py
# Project Root: NewPipeline/
curr_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(curr_dir, '..', '..'))
DATA_ROOT = os.path.join(PROJECT_ROOT, "data")
EVENTS_ROOT = os.path.join(DATA_ROOT, "bids_events")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "derivatives", "rois")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures_detailed")

# Ensure internal libs can be imported (NewPipeline/code/preprocessing)
sys.path.append(os.path.join(PROJECT_ROOT, "code"))

try:
    from preprocessing import preproc_lib, events_lib
except ImportError:
    print("Error importing local libs")
    sys.exit(1)

# --- ANALYSIS CONFIGURATION ---
SUBJECTS = ["Boss", "Carol"]
BIPOLAR_JSON = os.path.join(DATA_ROOT, "electrode_bipolar.json")

# Task Specific Params
SEP_HP_FREQ = 25.0
SEP_EPOCH = (-0.05, 0.1)
SEP_BASELINE = (-0.05, 0.0)

AUDITORY_EPOCH = (-0.2, 0.5)
AUDITORY_BASELINE = (-0.2, 0.0)

TFR_FREQS = np.arange(5, 151, 5)

os.makedirs(FIG_DIR, exist_ok=True)

# --- HELPERS ---

def load_bipolar_config():
    """Load pairs and channel mapping from JSON."""
    with open(BIPOLAR_JSON, 'r') as f:
        data = json.load(f)
    
    pairs = []
    if "left_hemisphere" in data["bipolar_pairs"]:
        pairs.extend(data["bipolar_pairs"]["left_hemisphere"])
    if "right_hemisphere" in data["bipolar_pairs"]:
        pairs.extend(data["bipolar_pairs"]["right_hemisphere"])
        
    mapping = data.get("channel_remapping", {})
    return pairs, mapping

def butter_highpass(cutoff, fs, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    if normal_cutoff >= 1.0: normal_cutoff = 0.99
    sos = butter(order, normal_cutoff, btype='high', output='sos')
    return sos

def process_signals(signals, fs, task_type):
    """
    Apply filters based on task type.
    - Auditory: No filters (Raw).
    - SEP: High-pass (>25Hz).
    """
    if task_type == "Auditory":
        return signals # Return Raw
        
    elif "SEP" in task_type:
        # High Pass > 25Hz
        sos = butter_highpass(SEP_HP_FREQ, fs, order=4)
        sig_hp = sosfiltfilt(sos, signals, axis=0)
        
        # Optional: Notch filter? 
        # User requested "High-pass 25Hz above". 
        # Keeping Notch for SEP as standard practice to remove line noise
        for f0 in range(60, 241, 60):
            if f0 < fs/2:
                b, a = iirnotch(w0=f0, Q=30.0, fs=fs)
                sig_hp = filtfilt(b, a, sig_hp, axis=0)
        return sig_hp
        
    return signals

def get_mapped_channel(physical_name, subject_map):
    return subject_map.get(physical_name, physical_name)

def compute_bipolar_signals(raw_sig, ch_names, pairs, subject_map, imp_list):
    n_samples = raw_sig.shape[0]
    n_pairs = len(pairs)
    sig_bip = np.zeros((n_samples, n_pairs))
    pair_labels = []
    bad_pairs = []
    
    ch_idx_map = {name: i for i, name in enumerate(ch_names)}
    
    for i, p in enumerate(pairs):
        phy_an = p['anode']
        phy_ca = p['cathode']
        label = f"{phy_an}-{phy_ca}"
        pair_labels.append(label)
        
        dat_an = get_mapped_channel(phy_an, subject_map)
        dat_ca = get_mapped_channel(phy_ca, subject_map)
        
        if dat_an in ch_idx_map and dat_ca in ch_idx_map:
            sig_bip[:, i] = raw_sig[:, ch_idx_map[dat_an]] - raw_sig[:, ch_idx_map[dat_ca]]
        else:
            sig_bip[:, i] = np.nan
            
        if (dat_an in imp_list) or (dat_ca in imp_list):
            bad_pairs.append(label)
            
    return sig_bip, pair_labels, bad_pairs

def epoch_data(data, fs, onsets, tmin, tmax):
    n_samples, n_ch = data.shape
    s_min = int(round(tmin * fs))
    s_max = int(round(tmax * fs))
    n_pts = s_max - s_min
    onset_samps = np.round(onsets * fs).astype(int)
    epochs = []
    for t0 in onset_samps:
        start = t0 + s_min
        end = t0 + s_max
        if start < 0 or end > n_samples: continue
        epoch = data[start:end, :]
        epochs.append(epoch)
    times = np.linspace(tmin, tmax, n_pts, endpoint=False)
    if not epochs:
        return np.empty((0, n_pts, n_ch)), times
    return np.array(epochs), times

def apply_baseline(epochs, times, b_min, b_max):
    idx_0 = np.searchsorted(times, b_min)
    idx_1 = np.searchsorted(times, b_max)
    if idx_1 > idx_0:
        base = np.mean(epochs[:, idx_0:idx_1, :], axis=1, keepdims=True)
        return epochs - base
    return epochs

def morlet_transform(epochs, fs, freqs):
    n_trials, n_times, n_ch = epochs.shape
    n_freqs = len(freqs)
    power_sum = np.zeros((n_ch, n_freqs, n_times))
    
    for f_idx, f in enumerate(freqs):
        sigma = 5.0 / (2 * np.pi * f)
        n_wavelet = int(fs * 5 * sigma) * 2 + 1
        t_w = np.arange(-n_wavelet//2, n_wavelet//2 + 1) / fs
        wavelet = np.exp(2j * np.pi * f * t_w) * np.exp(-t_w**2 / (2 * sigma**2))
        wavelet /= np.linalg.norm(wavelet)
        wavelet_center_idx = (n_wavelet - 1) // 2
        
        for ch in range(n_ch):
            for tr in range(n_trials):
                conv_full = np.convolve(epochs[tr, :, ch], wavelet, mode='full')
                conv = conv_full[wavelet_center_idx : wavelet_center_idx + n_times]
                power_sum[ch, f_idx, :] += np.abs(conv)**2
                
    return power_sum / n_trials

def find_impedance_file(subject, date_str):
    imp_dir = os.path.join(DATA_ROOT, "impedance", subject)
    if not os.path.exists(imp_dir): return None
    files = glob.glob(os.path.join(imp_dir, "*.csv"))
    if not files: return None
    files.sort()
    for f in files:
        if date_str in os.path.basename(f):
            return f
    return files[-1]

def parse_csv_map(subject):
    csv_path = os.path.join(DATA_ROOT, "csv", f"{subject}_Functional.csv")
    if not os.path.exists(csv_path): return [], {}
    df = pd.read_csv(csv_path)
    piano = []
    sep = {}
    for i, row in df.iterrows():
        ds = str(row.iloc[0]).strip()
        cond = str(row.iloc[1]).strip()
        date = str(row.iloc[2]).strip()
        fname = str(row.iloc[4]).strip()
        final = f"{date}{fname}"
        if not final.endswith(".mat"): final += ".mat"
        path = os.path.join(DATA_ROOT, "matfiles", subject, final)
        if "piano" in ds.lower(): piano.append((path, date))
        elif "sep" in ds.lower():
            if cond not in sep: sep[cond] = []
            sep[cond].append((path, date))
    return piano, sep

# --- PLOTTING ---

def plot_erp_grid(subject, epochs, times, labels, bad_labels, title, filename):
    evoked = np.mean(epochs, axis=0)
    n_ch = len(labels)
    n_cols = 8
    n_rows = int(np.ceil(n_ch / n_cols))
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(24, n_rows*3), sharex=True, sharey=True)
    axes = axes.flatten()
    
    for i in range(len(axes)):
        ax = axes[i]
        if i >= n_ch:
            ax.axis('off'); continue
        
        lbl = labels[i]
        is_bad = lbl in bad_labels
        color = 'r' if is_bad else 'k'
        
        ax.plot(times, evoked[:, i], color=color)
        ax.axvline(0, color='gray', linestyle='--')
        ax.set_title(lbl, fontsize=9, color=color)
        
    plt.suptitle(f"{subject} {title} (N={epochs.shape[0]})", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(os.path.join(FIG_DIR, filename))
    plt.close()

def plot_tfr_grid(subject, epochs, times, labels, bad_labels, fs, title, filename):
    print(f"  Calculating TFR for {title}...")
    power = morlet_transform(epochs, fs, TFR_FREQS)
    
    idx_b0 = np.searchsorted(times, AUDITORY_BASELINE[0])
    idx_b1 = np.searchsorted(times, AUDITORY_BASELINE[1])
    
    if idx_b1 > idx_b0:
        base = np.mean(power[:, :, idx_b0:idx_b1], axis=2, keepdims=True)
        power_db = 10 * np.log10(power / (base + 1e-9))
    else:
        power_db = 10 * np.log10(power)
        
    n_ch = len(labels)
    n_cols = 8
    n_rows = int(np.ceil(n_ch / n_cols))
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(24, n_rows*3), sharex=True, sharey=True)
    axes = axes.flatten()
    
    for i in range(len(axes)):
        ax = axes[i]
        if i >= n_ch:
            ax.axis('off'); continue
        lbl = labels[i]
        ax.imshow(power_db[i], aspect='auto', origin='lower', 
                  extent=[times[0], times[-1], TFR_FREQS[0], TFR_FREQS[-1]],
                  cmap='RdBu_r', vmin=-3, vmax=3)
        ax.axvline(0, color='k', linestyle='--')
        ax.set_title(lbl, color='r' if lbl in bad_labels else 'k', fontsize=9)
        
    plt.suptitle(f"{subject} {title} (N={epochs.shape[0]})", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(os.path.join(FIG_DIR, filename))
    plt.close()

# --- MAIN ---

def run_subject_analysis(subject):
    print(f"\nProcessing {subject} (Refined)...")
    piano, sep = parse_csv_map(subject)
    pairs_conf, full_mapping = load_bipolar_config()
    subject_map = full_mapping.get(subject, {})
    
    conditions = []
    if piano: 
        conditions.append(("Auditory", piano, "Auditory", 
                           AUDITORY_EPOCH[0], AUDITORY_EPOCH[1], 
                           AUDITORY_BASELINE[0], AUDITORY_BASELINE[1]))
    if '1' in sep: 
        conditions.append(("SEP_Left_Stim", sep['1'], "SEP",
                           SEP_EPOCH[0], SEP_EPOCH[1], 
                           SEP_BASELINE[0], SEP_BASELINE[1]))
    if '2' in sep: 
        conditions.append(("SEP_Right_Stim", sep['2'], "SEP",
                           SEP_EPOCH[0], SEP_EPOCH[1], 
                           SEP_BASELINE[0], SEP_BASELINE[1]))
    
    for cond_name, files, task_type, tmin, tmax, bl_min, bl_max in conditions:
        print(f"  Condition: {cond_name} (Task: {task_type})")
        
        all_mono_eps = []
        all_bip_eps = []
        times = None
        fs_final = 250.0
        
        mono_labels = []
        mono_bads = set()
        bip_labels = []
        bip_bads = set()
        
        for fpath, date in files:
            if not os.path.exists(fpath): continue
            
            sig, fs_val, ch_names = preproc_lib.load_cortec_data(fpath)
            if sig is None: continue
            fs_final = fs_val
            
            # --- FILTERING ---
            sig_proc = process_signals(sig, fs_val, task_type)
            
            imp_file = find_impedance_file(subject, date)
            bads_data = []
            if imp_file:
                bads_data = preproc_lib.check_impedance(imp_file, ch_names)
            
            # Mono
            ch_idxs = [i for i, n in enumerate(ch_names) if n.startswith("CH")]
            mono_labels = [ch_names[i] for i in ch_idxs]
            for b in bads_data: mono_bads.add(b)
            
            # Bipolar
            sig_bip, labels_bip, bads_bip_batch = compute_bipolar_signals(
                sig_proc, ch_names, pairs_conf, subject_map, bads_data
            )
            bip_labels = labels_bip
            for b in bads_bip_batch: bip_bads.add(b)
            
            # Epoch
            evt_key = 'stimulus_on' if task_type == "Auditory" else 'ssep_stim'
            evt = events_lib.find_event_file(fpath, EVENTS_ROOT)
            onsets = events_lib.load_events(evt, [evt_key])
            
            sig_mono = sig_proc[:, ch_idxs]
            eps_m, ts = epoch_data(sig_mono, fs_val, onsets, tmin, tmax)
            eps_m = apply_baseline(eps_m, ts, bl_min, bl_max)
            if len(eps_m) > 0: all_mono_eps.append(eps_m)
            
            eps_b, _ = epoch_data(sig_bip, fs_val, onsets, tmin, tmax)
            eps_b = apply_baseline(eps_b, ts, bl_min, bl_max)
            if len(eps_b) > 0: all_bip_eps.append(eps_b)
            
            times = ts
            
        if all_mono_eps:
            concat_m = np.concatenate(all_mono_eps, axis=0)
            plot_erp_grid(subject, concat_m, times, mono_labels, mono_bads, 
                          f"{cond_name} Monopolar", f"Final_{subject}_{cond_name}_Monopolar_ERP.png")
            if task_type == "Auditory":
                 plot_tfr_grid(subject, concat_m, times, mono_labels, mono_bads, fs_final,
                               f"{cond_name} Monopolar TFR", f"Final_{subject}_{cond_name}_Monopolar_TFR.png")
        if all_bip_eps:
            concat_b = np.concatenate(all_bip_eps, axis=0)
            plot_erp_grid(subject, concat_b, times, bip_labels, bip_bads,
                          f"{cond_name} Bipolar", f"Final_{subject}_{cond_name}_Bipolar_ERP.png")

def main():
    for sub in SUBJECTS:
        try:
            run_subject_analysis(sub)
        except Exception:
            traceback.print_exc()

if __name__ == "__main__":
    main()
