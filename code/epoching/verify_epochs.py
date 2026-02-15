import numpy as np
import sys
from pathlib import Path

def check_epochs(npz_path):
    print(f"Checking Epochs {npz_path}...")
    try:
        data = np.load(npz_path, allow_pickle=True)
        keys = list(data.keys())
        print("Keys:", keys)
        
        # New Keys: signal, hfa
        if 'signal' in data:
            sig = data['signal']
            print(f"Signal Shape: {sig.shape} (N_seq, Time, Ch)")
        elif 'erp_epochs' in data:
            sig = data['erp_epochs']
            print(f"ERP Shape (Legacy): {sig.shape}")
        else:
            print("ERROR: No signal/erp_epochs found!")
            return

        if 'hfa' in data:
            hfa = data['hfa']
            print(f"HFA Shape: {hfa.shape}")
        elif 'hfa_epochs' in data:
            hfa = data['hfa_epochs']
            print(f"HFA Shape (Legacy): {hfa.shape}")
            
        meta = data['meta']
        chs = data['channel_names']
        fs = data['fs']
        
        print(f"Meta Length: {len(meta)}")
        print(f"Channel Names ({len(chs)}): {chs}")
        print(f"Fs: {fs}")
        
        if 'epoch_window' in data:
            print(f"Epoch Window: {data['epoch_window']}")
        
        # Check NaNs
        if np.isnan(sig).any():
            print("WARNING: Signal contains NaNs!")
        if np.isnan(hfa).any():
            print("WARNING: HFA contains NaNs!")
            
        # Check first meta
        if len(meta) > 0:
            print("Sample Meta[0]:", meta[0])
            
        print("Verification Complete.")
        
    except Exception as e:
        print(f"Verification Failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_epochs.py <path_to_npz>")
    else:
        check_epochs(sys.argv[1])
