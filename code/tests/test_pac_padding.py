import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, hilbert

def bandpass_filter(signal, lo, hi, fs, order=3):
    nyq = fs / 2.0
    low = lo / nyq
    high = hi / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal, axis=-1)

def extract_phase_nopad(signal, lo, hi, fs):
    filtered = bandpass_filter(signal, lo, hi, fs)
    analytic = hilbert(filtered, axis=-1)
    return np.angle(analytic)

def extract_phase_padded(signal, lo, hi, fs, pad_sec=0.5):
    pad_samples = int(pad_sec * fs)
    pad_samples = min(pad_samples, signal.shape[-1] - 1)
    padded_signal = np.pad(signal, (pad_samples, pad_samples), mode='reflect')
    filtered = bandpass_filter(padded_signal, lo, hi, fs)
    analytic = hilbert(filtered, axis=-1)
    analytic_cropped = analytic[pad_samples:-pad_samples]
    return np.angle(analytic_cropped)

def run_test():
    fs = 500
    t = np.arange(0, 0.8, 1/fs)
    freq = 4.0
    # Ground truth phase
    gt_phase = np.mod(2 * np.pi * freq * t + np.pi, 2 * np.pi) - np.pi
    
    # Signal: 4Hz sine wave
    signal = np.sin(2 * np.pi * freq * t)
    
    phase_nopad = extract_phase_nopad(signal, 4.0, 8.0, fs)
    phase_pad = extract_phase_padded(signal, 4.0, 8.0, fs)
    
    # Calculate error
    err_nopad = np.abs(np.unwrap(phase_nopad) - np.unwrap(gt_phase))
    err_pad = np.abs(np.unwrap(phase_pad) - np.unwrap(gt_phase))
    
    print(f"Mean error (no pad): {np.mean(err_nopad):.6f}")
    print(f"Mean error (pad):    {np.mean(err_pad):.6f}")
    
    # Check edge error (first and last 50ms)
    edge_idx = int(0.05 * fs)
    edge_err_nopad = np.mean(err_nopad[:edge_idx]) + np.mean(err_nopad[-edge_idx:])
    edge_err_pad = np.mean(err_pad[:edge_idx]) + np.mean(err_pad[-edge_idx:])
    
    print(f"Edge error (no pad): {edge_err_nopad:.6f}")
    print(f"Edge error (pad):    {edge_err_pad:.6f}")
    
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(t, gt_phase, 'k', label='Ground Truth', alpha=0.5)
    plt.plot(t, phase_nopad, 'r--', label='No Padding')
    plt.plot(t, phase_pad, 'b', label='Mirror Padding', alpha=0.7)
    plt.title("Phase Estimation Comparison")
    plt.legend()
    
    plt.subplot(2, 1, 2)
    plt.plot(t, err_nopad, 'r', label='Error (No Padding)')
    plt.plot(t, err_pad, 'b', label='Error (Mirror Padding)')
    plt.title("Phase Error")
    plt.legend()
    plt.tight_layout()
    plt.savefig("code/tests/pac_fix_verification.png")
    print("Verification plot saved to code/tests/pac_fix_verification.png")

if __name__ == "__main__":
    run_test()
