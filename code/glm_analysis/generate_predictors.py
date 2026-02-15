#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Predictors for GLM Analysis
====================================

This script generates predictor files (parquet) for the GLM analysis by combining:
1. BIDS Events (metadata: grammar, length, sequence_version).
2. Sequences Excel (abstract A/B patterns and MDL values).

It calculates:
- Surprisal (Bayesian Ideal Observer with decay)
- Repetition (Low-level sensory adaptation)
- Tone Identity (Physical frequency based on version)

Output:
- derivatives/predictors/<Condition>/<Subject>/predictors_seqver-<ver>_tau<TAU>_session.parquet
"""

import os
import glob
import json
import math
import argparse
import pandas as pd
import numpy as np
from pathlib import Path

# Configuration
DATA_ROOT = "data"
BIDS_ROOT = os.path.join(DATA_ROOT, "bids_events")
SEQS_XLSX = os.path.join(DATA_ROOT, "csv", "sequences.xlsx")
OUT_ROOT = "derivatives/predictors"

# Parameters for Ideal Observer
TAU = 100.0
GAP_RESET_SEC = 200.0  # Reset history if gap > 200s (effectively per session)

# ------------------------------------------------------------------------------
# 1. Load Abstract Sequences (A/B)
# ------------------------------------------------------------------------------

def load_abstract_sequences(xlsx_path):
    """
    Load sequences.xlsx and return a lookup dictionary:
    (Grammar, Length) -> {'Standard': 'AAB...', 'Violations': ['AAA...', ...], 'MDL': 4.0}
    """
    df = pd.read_excel(xlsx_path)
    # Normalize columns
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Map 'category' -> 'grammar' if needed
    if 'category' in df.columns:
        df.rename(columns={'category': 'grammar'}, inplace=True)
    
    lookup = {}
    for _, row in df.iterrows():
        grammar = row['grammar']
        length = int(row['length'])
        standard = row['standard'].strip()
        mdl = pd.to_numeric(row['mdl value'], errors='coerce')
        
        # Collect violations (Violation type 1, 2, 3, 4)
        viols = []
        for i in range(1, 5):
            col = f'violation type {i}'
            if col in df.columns and pd.notna(row[col]):
                viols.append(row[col].strip())
        
        lookup[(grammar, length)] = {
            'standard': standard,
            'violations': viols,
            'mdl': mdl
        }
    return lookup

# ------------------------------------------------------------------------------
# 2. Sequence Reconstruction Logic
# ------------------------------------------------------------------------------

def get_sequence_pattern(grammar, length, trial_type, violation_pos, lookup):
    """
    Reconstruct the specific A/B string for a trial.
    """
    key = (grammar, length)
    if key not in lookup:
        # Fallback or error?
        print(f"Warning: Unknown grammar/length {key}")
        return None, None

    info = lookup[key]
    std_seq = info['standard']
    mdl = info['mdl']
    
    # Simple cases
    if trial_type in ['habituation', 'standard'] or violation_pos == 0:
        return std_seq, mdl
    
    # Violation Logic
    # We need to find the violation string that deviates at `violation_pos`.
    # A violation at Pos X means the character at X is different from Standard.
    target_char = 'B' if std_seq[violation_pos-1] == 'A' else 'A'
    
    found_viol = None
    for v_str in info['violations']:
        if len(v_str) >= violation_pos and v_str[violation_pos-1] == target_char:
            found_viol = v_str
            break
            
    # Fallback: if explicit string not found, manually flip the bit (safest)
    if found_viol is None:
        # Construct synthetic violation
        found_viol = list(std_seq)
        found_viol[violation_pos-1] = target_char
        found_viol = "".join(found_viol)
        
    return found_viol, mdl

# ------------------------------------------------------------------------------
# 3. Predictor Calculation (Surprisal & Repetition)
# ------------------------------------------------------------------------------

def calculate_surprisal(sequence_stream, tau=100.0):
    """
    Calculate surprisal for a stream of symbols ['A', 'B', 'A', ...]
    Using Bayesian Ideal Observer with exponential decay.
    """
    # Counts for A and B, initialized with prior (Laplace smoothing + decay)
    # Using a simple implementation: 
    # Global counts P(A) vs P(B) ? Or Transition counts P(A|A), P(B|A)?
    # The prompt implies "Surprisal values derived from the computational model in the legacy script".
    # Legacy script uses TRANSITION counts with decay.
    
    # Initialize counts: [A, B] given previous char
    # We track 2 contexts: Prev=A, Prev=B
    counts = {
        'A': {'A': 1.0, 'B': 1.0}, # Context A: count(A->A), count(A->B)
        'B': {'A': 1.0, 'B': 1.0}  # Context B: count(B->A), count(B->B)
    }
    
    surprisals = []
    decay = math.exp(-1.0 / tau)
    
    # For the very first item, we assume uniform prior or undefined? 
    # Usually undefined or based on global prob. Let's assume P(A)=0.5
    surprisals.append(-math.log2(0.5)) 
    
    for i in range(1, len(sequence_stream)):
        curr = sequence_stream[i]
        prev = sequence_stream[i-1]
        
        # 1. Decay all counts
        for ctx in counts:
            for dest in counts[ctx]:
                counts[ctx][dest] *= decay
                
        # 2. Update count for the OBSERVED transition (prev -> curr) *before* prediction?
        # NO. "Surprisal" is the negative log probability of the current event GIVEN history.
        # So we predict first, THEN update.
        
        # Prediction
        total_ctx = counts[prev]['A'] + counts[prev]['B']
        p_curr = counts[prev][curr] / total_ctx
        s_val = -math.log2(p_curr)
        surprisals.append(s_val)
        
        # Update
        counts[prev][curr] += 1.0
        
    return surprisals

# ------------------------------------------------------------------------------
# 4. Main Processing
# ------------------------------------------------------------------------------

def process_file(events_path, seq_lookup):
    """
    Process a single events.tsv file.
    """
    df = pd.read_csv(events_path, sep='\t')
    
    # Filter valid columns
    req_cols = ['trial_type', 'grammar', 'length', 'violation_position', 'sequence_version']
    for c in req_cols:
        if c not in df.columns:
            # Try to infer or fill defaults?
            if c == 'violation_position': df[c] = 0
            else: return None # Cannot process
            
    item_rows = []
    
    for idx, row in df.iterrows():
        grammar = row['grammar']
        length = int(row['length'])
        ttype = row['trial_type']
        vpos = int(row['violation_position']) if pd.notna(row['violation_position']) else 0
        seqver = row['sequence_version']
        
        ab_seq, mdl = get_sequence_pattern(grammar, length, ttype, vpos, seq_lookup)
        
        if ab_seq is None:
            continue
            
        # Calculate Surprisal per sequence (Reset model state)
        # This ensures counts restart from uniform prior for each trial,
        # correctly handling sequences of length 4, 6, 8, 12, or 16.
        trial_surprisals = calculate_surprisal(list(ab_seq), tau=TAU)
        
        # Physical tone mapping
        # low-high: A=350, B=500
        # high-low: A=500, B=350
        is_low_high = (seqver == 'low-high')
        
        for pos, char in enumerate(ab_seq):
            # 1-based position
            p_idx = pos + 1
            s_val = trial_surprisals[pos]
            
            # Tone Identity
            if is_low_high:
                tone_id = 0 if char == 'A' else 1
            else:
                tone_id = 1 if char == 'A' else 0
                
            # Repetition (Local)
            if pos == 0:
                rep = 0 # No previous in sequence
            else:
                rep = 1 if ab_seq[pos] == ab_seq[pos-1] else 0
                
            item_rows.append({
                'session_id': idx, # Using trial index as session proxy
                'trial_index': idx,
                'pos': p_idx,
                'tone_char': char,
                'tone_id': tone_id,
                'repetition': rep,
                'surprisal': s_val,
                'mdl': mdl,
                'grammar': grammar,
                'length': length,
                'trial_type': ttype, 
                'violation_position': vpos,
                'seqver': seqver
            })
            
    if not item_rows:
        return None
        
    out_df = pd.DataFrame(item_rows)
    return out_df

def main():
    # Load sequences
    print(f"Loading sequences from {SEQS_XLSX}...")
    seq_lookup = load_abstract_sequences(SEQS_XLSX)
    
    # Find all event files
    search_pat = os.path.join(BIDS_ROOT, "*", "*", "*_events.tsv")
    files = glob.glob(search_pat)
    print(f"Found {len(files)} event files.")
    
    for fpath in files:
        try:
            # Extract metadata from path: .../Condition/Subject/filename.tsv
            parts = fpath.split(os.sep)
            subject = parts[-2]
            condition = parts[-3]
            fname = os.path.basename(fpath).replace('_events.tsv', '')
            
            # Process
            df = process_file(fpath, seq_lookup)
            if df is None or df.empty:
                print(f"Skipping {fname} (empty or error)")
                continue
                
            # Save
            # Output structure: derivatives/predictors/Condition/Subject
            save_dir = os.path.join(OUT_ROOT, condition, subject)
            os.makedirs(save_dir, exist_ok=True)
            
            # We need to discern "seqver" to naming? 
            # The files might contain mixed seqvers? Usually 1 session = 1 seqver.
            # Let's check unique seqver.
            seqvers = df['seqver'].unique()
            for sv in seqvers:
                sub_df = df[df['seqver'] == sv]
                # Naming convention: predictors_seqver-<ver>_<session>.parquet
                out_name = f"predictors_seqver-{sv}_{fname}.parquet"
                out_path = os.path.join(save_dir, out_name)
                
                try:
                    sub_df.to_parquet(out_path, index=False)
                    print(f"Saved {out_path}")
                except ImportError:
                    # Fallback to CSV
                    out_path_csv = out_path.replace('.parquet', '.csv')
                    sub_df.to_csv(out_path_csv, index=False)
                    print(f"Saved {out_path_csv} (fallback)")
                
        except Exception as e:
            print(f"Error processing {fpath}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
