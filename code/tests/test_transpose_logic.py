
import numpy as np

def identify_and_transpose_logic(raw_data, expected_samples):
    """
    Mock implementation of the logic added to prepare_glm_data.py
    """
    if raw_data.shape[0] == expected_samples:
        # (Time, Ch) -> transpose to (Ch, Time) for legacy GLM logic
        data_ch_time = raw_data.T
        fmt = "(Time, Ch)"
    elif raw_data.shape[1] == expected_samples:
        # Already (Ch, Time)
        data_ch_time = raw_data
        fmt = "(Ch, Time)"
    else:
        # Fallback for ambiguous or malformed data
        if raw_data.shape[0] > raw_data.shape[1]:
            data_ch_time = raw_data.T
        else:
            data_ch_time = raw_data
        fmt = "Fallback"
    
    return data_ch_time, fmt

def test_logic():
    fs = 500
    expected_samples = 500 # 1.0s
    n_ch = 64
    
    print(f"Testing with FS={fs}, expected_samples={expected_samples}, n_channels={n_ch}")
    
    # Case 1: Standard (Time, Ch) -> should be transposed to (Ch, Time)
    data1 = np.random.rand(expected_samples, n_ch)
    res1, fmt1 = identify_and_transpose_logic(data1, expected_samples)
    assert res1.shape == (n_ch, expected_samples), f"Case 1 failed: {res1.shape}"
    print(f"  [PASS] Case 1: Identifed {fmt1} -> Shape {res1.shape}")
    
    # Case 2: Already (Ch, Time) -> should remain (Ch, Time)
    data2 = np.random.rand(n_ch, expected_samples)
    res2, fmt2 = identify_and_transpose_logic(data2, expected_samples)
    assert res2.shape == (n_ch, expected_samples), f"Case 2 failed: {res2.shape}"
    print(f"  [PASS] Case 2: Identifed {fmt2} -> Shape {res2.shape}")
    
    # Case 3: Tricky Case (Ch == Samples, e.g. 500 channels at 1s epoch)
    n_ch_tricky = expected_samples
    data3 = np.random.rand(expected_samples, n_ch_tricky)
    res3, fmt3 = identify_and_transpose_logic(data3, expected_samples)
    # In this case, both match. Code says:
    # if shape[0] == expected_samples: data_ch_time = raw_data.T
    # This favors (Time, Ch) as input, which is the storage standard.
    assert res3.shape == (n_ch_tricky, expected_samples), f"Case 3 failed: {res3.shape}"
    print(f"  [PASS] Case 3: Identified {fmt3} -> Shape {res3.shape}")
    
    # Case 4: Fragmented or short epoch (Failure case of previous logic if ch > samples)
    expected_short = 50 # 100ms at 500Hz
    n_ch_large = 128
    data4 = np.random.rand(n_ch_large, expected_short)
    # Old logic: shape[0] > shape[1] (128 > 50) -> Transpose to (50, 128) -> WRONG
    # New logic: shape[1] == expected_short -> (Ch, Time) -> CORRECT
    res4, fmt4 = identify_and_transpose_logic(data4, expected_short)
    assert res4.shape == (n_ch_large, expected_short), f"Case 4 failed: {res4.shape}"
    print(f"  [PASS] Case 4: Identified {fmt4} -> Shape {res4.shape}")

if __name__ == "__main__":
    test_logic()
