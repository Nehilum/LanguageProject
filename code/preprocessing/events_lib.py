import pandas as pd
import os
import glob

def find_event_file(mat_path, bids_events_root):
    """
    Tries to find the corresponding event file for a given .mat file.
    Assumes naming convention: <FilenameStem>_events.tsv
    """
    if not os.path.exists(bids_events_root):
        print(f"Warning: Events root not found: {bids_events_root}")
        return None
        
    base_name = os.path.basename(mat_path)
    stem = os.path.splitext(base_name)[0] # e.g. 20250620T112628B01
    
    # Search recursively or in specific folders?
    # The structure is bids_events/Functional/Boss/...
    # Let's search recursively
    search_pattern = os.path.join(bids_events_root, "**", f"{stem}_events.tsv")
    candidates = glob.glob(search_pattern, recursive=True)
    
    if len(candidates) == 0:
        print(f"No event file found for {stem} in {bids_events_root}")
        return None
    elif len(candidates) > 1:
        print(f"Warning: Multiple event files found for {stem}, using first: {candidates[0]}")
        return candidates[0]
    else:
        return candidates[0]

def load_events(tsv_path, target_trial_types=None):
    """
    Loads events.tsv and returns onsets (in seconds) for specific trial types.
    target_trial_types: list of strings (e.g. ['stimulus_on']) or string. 
                        If None, return all onsets.
    """
    if not os.path.exists(tsv_path):
        raise FileNotFoundError(f"Event file not found: {tsv_path}")
        
    df = pd.read_csv(tsv_path, sep='\t')
    
    # Check columns
    if 'onset' not in df.columns:
        raise ValueError(f"Invalid events file (no 'onset' column): {tsv_path}")
        
    if target_trial_types:
        if isinstance(target_trial_types, str):
            target_trial_types = [target_trial_types]
            
        if 'trial_type' in df.columns:
            # Filter
            mask = df['trial_type'].isin(target_trial_types)
            df_subset = df[mask]
        else:
            print("Warning: 'trial_type' column missing, returning all onsets.")
            df_subset = df
    else:
        df_subset = df
        
    return df_subset['onset'].values

