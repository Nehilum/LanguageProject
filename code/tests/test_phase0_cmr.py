import numpy as np
import sys
import os

# Add code/preprocessing to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'preprocessing')))
import preproc_lib

def test_cmr():
    print("Testing CMR implementation...")
    # Create fake data: 1000 samples, 4 channels
    # CH01: Random
    # CH02: Random + Offset
    # CH03: Random + same Offset (will be median)
    # CH04: Random + Different Offset
    fs = 500.0
    ch_names = ["CH01", "CH02", "CH03", "CH04"]
    t = np.linspace(0, 1, 1000)
    sig = np.random.randn(1000, 4)
    
    # Inject a "common" signal (median)
    common = np.sin(2 * np.pi * 10 * t)[:, None]
    sig += common
    
    # Test apply_preprocessing_step
    # We bypass the actual filtering for this test by mocking parts if possible, 
    # but we can just run it on this raw data.
    
    res = preproc_lib.apply_preprocessing_step(sig, fs, ch_names)
    
    if "signals_cmr" in res:
        print("Success: Found 'signals_cmr' key.")
    else:
        print("Failure: 'signals_cmr' key missing.")
        return

    sig_cmr = res["signals_cmr"]
    print(f"CMR output shape: {sig_cmr.shape}")
    
    # Selective test
    # Exclude CH04
    res_sel = preproc_lib.apply_preprocessing_step(sig, fs, ch_names, ref_exclude_names=["CH04"])
    print("Success: Ran selective CMR.")

if __name__ == "__main__":
    test_cmr()
