import h5py
import numpy as np
import os
from pathlib import Path

def verify_fs(file_path):
    print(f"Verifying {file_path}...")
    if not os.path.exists(file_path):
        print(f"MISSING: {file_path}")
        return
        
    try:
        if file_path.endswith('.h5'):
            with h5py.File(file_path, 'r') as hf:
                if 'fs' in hf.attrs:
                    print(f"  FS Attribute: {hf.attrs['fs']} Hz")
                    if hf.attrs['fs'] != 500.0:
                        print(f"  WARNING: FS is {hf.attrs['fs']}, expected 500.0")
                else:
                    print(f"  ERROR: Missing 'fs' attribute!")
                    
                # Check data shapes
                for grp in hf.keys():
                    if isinstance(hf[grp], h5py.Group):
                        for sub in hf[grp].keys():
                            if 'Y' in hf[f"{grp}/{sub}"]:
                                shape = hf[f"{grp}/{sub}/Y"].shape
                                print(f"  Data Shape ({grp}/{sub}): {shape}")
                                # Expected time points for 1s epoch at 500Hz is 500
                                # Tone epochs might be different (e.g. 0.8s -> 400)
                                if shape[-1] == 250:
                                    print(f"  WARNING: Found 250 time points (likely 250Hz)!")
        elif file_path.endswith('.npz'):
            data = np.load(file_path, allow_pickle=True)
            if 'fs' in data:
                print(f"  FS: {data['fs']} Hz")
            else:
                print(f"  ERROR: Missing 'fs'!")
            
            # Check shape
            for k in ['signal', 'signals_cmr', 'erp_epochs', 'seq_epochs']:
                if k in data:
                    print(f"  Data '{k}' Shape: {data[k].shape}")
                    if data[k].shape[1] == 250:
                        print(f"  WARNING: Found 250 time points in '{k}'!")
                        
    except Exception as e:
        print(f"  FAILED: {e}")

if __name__ == "__main__":
    # Check key files
    files = [
        "derivatives/preproc/Boss/daily/sess-01_preproc.npz",
        "derivatives/epochs/ToneDeviant_6/Boss/seqver-A_epochs.npz",
        "derivatives/glm_data/glm_dataset_erp_baselocal.h5",
        "derivatives/glm_stats/glm_stats_erp_baselocal.h5"
    ]
    
    for f in files:
        verify_fs(f)
