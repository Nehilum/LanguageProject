import numpy as np
import sys
from pathlib import Path

def check_npz(npz_path):
    print(f"Checking {npz_path}...")
    try:
        data = np.load(npz_path, allow_pickle=True)
        keys = list(data.keys())
        print("Keys:", keys)
        
        fs = data['fs']
        print(f"Sampling Rate: {fs}")
        if fs != 500.0:
            print("ERROR: Sampling rate is not 500Hz!")
            
        signals = data['signals_cmr']
        hfa = data['hfa_cmr']
        mask = data['artifact_mask']
        
        print(f"Signals Shape: {signals.shape}")
        print(f"HFA Shape: {hfa.shape}")
        print(f"Mask Shape: {mask.shape}")
        
        if signals.shape != hfa.shape or signals.shape != mask.shape:
            print("ERROR: Shapes do not match!")
            
        chs = data['channel_names']
        print(f"Channel Names ({len(chs)}): {chs}")
        
        bad = data['bad_channels']
        print(f"Bad Channels: {bad}")
        
        seq_ver = data['sequence_version']
        print(f"Sequence Version: '{seq_ver}'")
        
        ref_pool_size = data['ref_pool_size']
        print(f"Reference Pool Size: {ref_pool_size}")
        
        print("Verification Complete.")
        
    except Exception as e:
        print(f"Verification Failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_preproc.py <path_to_npz>")
    else:
        check_npz(sys.argv[1])
