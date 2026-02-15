# Atomic Fact Sheet (HDF5)

**Audit Timestamp**: 2026-02-15 10:37:59.930346

### [Audit]: unique_variance_hfa_baseglobal.h5
- **Target File**: `derivatives/analysis/unique_variance/unique_variance_hfa_baseglobal.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/Channel_DeltaR2_MDL, Boss/Channel_DeltaR2_Surp, Boss/ROI_DeltaR2_MDL, Boss/ROI_DeltaR2_Surp, Carol, Carol/Channel_DeltaR2_MDL, Carol/Channel_DeltaR2_Surp, Carol/ROI_DeltaR2_MDL, Carol/ROI_DeltaR2_Surp`
    - Target Dataset Shape: `(28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/Channel_DeltaR2_MDL` | **0.0006** | 0.0000 | 0.0001 | 0.0000 | (28, 500) |
| `Boss/Channel_DeltaR2_Surp` | **0.0004** | 0.0000 | 0.0000 | 0.0000 | (28, 500) |
| `Boss/ROI_DeltaR2_MDL` | **0.0002** | 0.0000 | 0.0000 | 0.0000 | (3, 500) |
| `Boss/ROI_DeltaR2_Surp` | **0.0001** | 0.0000 | 0.0000 | 0.0000 | (3, 500) |
| `Carol/Channel_DeltaR2_MDL` | **0.0006** | 0.0000 | 0.0000 | 0.0000 | (29, 500) |
| `Carol/Channel_DeltaR2_Surp` | **0.0006** | 0.0000 | 0.0000 | 0.0000 | (29, 500) |
| `Carol/ROI_DeltaR2_MDL` | **0.0001** | 0.0000 | 0.0000 | 0.0000 | (3, 500) |
| `Carol/ROI_DeltaR2_Surp` | **0.0001** | 0.0000 | 0.0000 | 0.0000 | (3, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `HFA magnitude`
- **Anomalies**: `Missing 'fs' attribute`

---

### [Audit]: glm_results_hfa_baseglobal_ModelD.h5
- **Target File**: `derivatives/glm_results/glm_results_hfa_baseglobal_ModelD.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/ChannelBetas, Boss/ChannelTstats, Boss/ROIBetas, Boss/ROITstats, Carol, Carol/ChannelBetas, Carol/ChannelTstats, Carol/ROIBetas, Carol/ROITstats`
    - Target Dataset Shape: `(8, 28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/ChannelBetas` | **0.1881** | -0.1672 | -0.0006 | 0.0009 | (8, 28, 500) |
| `Boss/ChannelTstats` | **6.4699** | -6.1851 | -0.0104 | 2.4091 | (8, 28, 500) |
| `Boss/ROIBetas` | **0.0970** | -0.0733 | -0.0006 | 0.0002 | (3, 8, 500) |
| `Boss/ROITstats` | **5.2120** | -5.1706 | 0.0073 | 2.0933 | (3, 8, 500) |
| `Carol/ChannelBetas` | **0.4029** | -0.2853 | 0.0026 | 0.0015 | (8, 29, 500) |
| `Carol/ChannelTstats` | **16.5298** | -11.1525 | 0.0120 | 3.9548 | (8, 29, 500) |
| `Carol/ROIBetas` | **0.1884** | -0.1283 | 0.0023 | 0.0006 | (3, 8, 500) |
| `Carol/ROITstats` | **10.2467** | -7.7661 | -0.0338 | 3.8463 | (3, 8, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `HFA magnitude`
- **Anomalies**: `Missing 'fs' attribute`

---

### [Audit]: glm_results_hfa_baseglobal_ModelC.h5
- **Target File**: `derivatives/glm_results/glm_results_hfa_baseglobal_ModelC.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/ChannelBetas, Boss/ChannelTstats, Boss/ROIBetas, Boss/ROITstats, Carol, Carol/ChannelBetas, Carol/ChannelTstats, Carol/ROIBetas, Carol/ROITstats`
    - Target Dataset Shape: `(7, 28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/ChannelBetas` | **0.2375** | -0.1744 | 0.0005 | 0.0011 | (7, 28, 500) |
| `Boss/ChannelTstats` | **6.5142** | -6.0194 | 0.0447 | 2.2505 | (7, 28, 500) |
| `Boss/ROIBetas` | **0.0874** | -0.0700 | 0.0004 | 0.0003 | (3, 7, 500) |
| `Boss/ROITstats` | **4.6510** | -4.7621 | 0.1065 | 2.0870 | (3, 7, 500) |
| `Carol/ChannelBetas` | **0.3865** | -0.2378 | 0.0040 | 0.0017 | (7, 29, 500) |
| `Carol/ChannelTstats` | **16.5226** | -12.2458 | 0.0234 | 3.9649 | (7, 29, 500) |
| `Carol/ROIBetas` | **0.1983** | -0.0841 | 0.0034 | 0.0007 | (3, 7, 500) |
| `Carol/ROITstats` | **10.2379** | -9.2267 | -0.0455 | 4.2852 | (3, 7, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `HFA magnitude`
- **Anomalies**: `Missing 'fs' attribute`

---

### [Audit]: glm_results_hfa_baseglobal_ModelB.h5
- **Target File**: `derivatives/glm_results/glm_results_hfa_baseglobal_ModelB.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/ChannelBetas, Boss/ChannelTstats, Boss/ROIBetas, Boss/ROITstats, Carol, Carol/ChannelBetas, Carol/ChannelTstats, Carol/ROIBetas, Carol/ROITstats`
    - Target Dataset Shape: `(8, 28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/ChannelBetas` | **0.2087** | -0.1416 | 0.0008 | 0.0008 | (8, 28, 500) |
| `Boss/ChannelTstats` | **7.4229** | -5.5035 | 0.0069 | 2.0902 | (8, 28, 500) |
| `Boss/ROIBetas` | **0.1104** | -0.0544 | 0.0008 | 0.0002 | (3, 8, 500) |
| `Boss/ROITstats` | **6.0562** | -4.2997 | 0.0388 | 1.8156 | (3, 8, 500) |
| `Carol/ChannelBetas` | **0.4212** | -0.2923 | 0.0031 | 0.0014 | (8, 29, 500) |
| `Carol/ChannelTstats` | **16.5298** | -11.5439 | 0.0522 | 3.6486 | (8, 29, 500) |
| `Carol/ROIBetas` | **0.2049** | -0.1319 | 0.0025 | 0.0006 | (3, 8, 500) |
| `Carol/ROITstats` | **10.2475** | -7.6879 | 0.0206 | 3.9811 | (3, 8, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `HFA magnitude`
- **Anomalies**: `Missing 'fs' attribute`

---

### [Audit]: glm_results_hfa_baseglobal_ModelA.h5
- **Target File**: `derivatives/glm_results/glm_results_hfa_baseglobal_ModelA.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/ChannelBetas, Boss/ChannelTstats, Boss/ROIBetas, Boss/ROITstats, Carol, Carol/ChannelBetas, Carol/ChannelTstats, Carol/ROIBetas, Carol/ROITstats`
    - Target Dataset Shape: `(4, 28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/ChannelBetas` | **0.1390** | -0.1362 | 0.0019 | 0.0011 | (4, 28, 500) |
| `Boss/ChannelTstats` | **6.8030** | -6.1509 | 0.0933 | 2.6755 | (4, 28, 500) |
| `Boss/ROIBetas` | **0.0855** | -0.0434 | 0.0019 | 0.0003 | (3, 4, 500) |
| `Boss/ROITstats` | **7.6278** | -5.1366 | 0.1685 | 2.5740 | (3, 4, 500) |
| `Carol/ChannelBetas` | **0.3837** | -0.2585 | 0.0071 | 0.0024 | (4, 29, 500) |
| `Carol/ChannelTstats` | **20.4223** | -16.6197 | 0.3562 | 6.4996 | (4, 29, 500) |
| `Carol/ROIBetas` | **0.1855** | -0.0946 | 0.0058 | 0.0010 | (3, 4, 500) |
| `Carol/ROITstats` | **13.6987** | -9.0203 | 0.4274 | 7.6182 | (3, 4, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `HFA magnitude`
- **Anomalies**: `Missing 'fs' attribute`

---

### [Audit]: unique_variance_hfa_baselocal.h5
- **Target File**: `derivatives/analysis/unique_variance/unique_variance_hfa_baselocal.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/Channel_DeltaR2_MDL, Boss/Channel_DeltaR2_Surp, Boss/ROI_DeltaR2_MDL, Boss/ROI_DeltaR2_Surp, Carol, Carol/Channel_DeltaR2_MDL, Carol/Channel_DeltaR2_Surp, Carol/ROI_DeltaR2_MDL, Carol/ROI_DeltaR2_Surp`
    - Target Dataset Shape: `(28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/Channel_DeltaR2_MDL` | **0.0004** | 0.0000 | 0.0000 | 0.0000 | (28, 500) |
| `Boss/Channel_DeltaR2_Surp` | **0.0003** | 0.0000 | 0.0000 | 0.0000 | (28, 500) |
| `Boss/ROI_DeltaR2_MDL` | **0.0001** | 0.0000 | 0.0000 | 0.0000 | (3, 500) |
| `Boss/ROI_DeltaR2_Surp` | **0.0001** | 0.0000 | 0.0000 | 0.0000 | (3, 500) |
| `Carol/Channel_DeltaR2_MDL` | **0.0004** | 0.0000 | 0.0000 | 0.0000 | (29, 500) |
| `Carol/Channel_DeltaR2_Surp` | **0.0004** | 0.0000 | 0.0000 | 0.0000 | (29, 500) |
| `Carol/ROI_DeltaR2_MDL` | **0.0002** | 0.0000 | 0.0000 | 0.0000 | (3, 500) |
| `Carol/ROI_DeltaR2_Surp` | **0.0001** | 0.0000 | 0.0000 | 0.0000 | (3, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `HFA magnitude`
- **Anomalies**: `Missing 'fs' attribute`

---

### [Audit]: glm_results_hfa_baselocal_ModelD.h5
- **Target File**: `derivatives/glm_results/glm_results_hfa_baselocal_ModelD.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/ChannelBetas, Boss/ChannelTstats, Boss/ROIBetas, Boss/ROITstats, Carol, Carol/ChannelBetas, Carol/ChannelTstats, Carol/ROIBetas, Carol/ROITstats`
    - Target Dataset Shape: `(8, 28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/ChannelBetas` | **0.2292** | -0.1562 | 0.0006 | 0.0008 | (8, 28, 500) |
| `Boss/ChannelTstats` | **5.6189** | -5.6375 | 0.0186 | 1.8030 | (8, 28, 500) |
| `Boss/ROIBetas` | **0.1004** | -0.0523 | 0.0007 | 0.0002 | (3, 8, 500) |
| `Boss/ROITstats` | **4.5707** | -4.4160 | 0.0578 | 1.7383 | (3, 8, 500) |
| `Carol/ChannelBetas` | **0.4239** | -0.2282 | 0.0005 | 0.0013 | (8, 29, 500) |
| `Carol/ChannelTstats` | **16.2463** | -10.8721 | 0.0265 | 2.8976 | (8, 29, 500) |
| `Carol/ROIBetas` | **0.2278** | -0.0922 | 0.0004 | 0.0007 | (3, 8, 500) |
| `Carol/ROITstats` | **9.9992** | -6.0418 | 0.0587 | 3.6271 | (3, 8, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `HFA magnitude`
- **Anomalies**: `Missing 'fs' attribute`

---

### [Audit]: glm_results_hfa_baselocal_ModelC.h5
- **Target File**: `derivatives/glm_results/glm_results_hfa_baselocal_ModelC.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/ChannelBetas, Boss/ChannelTstats, Boss/ROIBetas, Boss/ROITstats, Carol, Carol/ChannelBetas, Carol/ChannelTstats, Carol/ROIBetas, Carol/ROITstats`
    - Target Dataset Shape: `(7, 28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/ChannelBetas` | **0.2204** | -0.2215 | -0.0005 | 0.0011 | (7, 28, 500) |
| `Boss/ChannelTstats` | **5.3316** | -5.6327 | 0.0156 | 1.7471 | (7, 28, 500) |
| `Boss/ROIBetas` | **0.0828** | -0.0944 | -0.0000 | 0.0003 | (3, 7, 500) |
| `Boss/ROITstats` | **4.8490** | -4.1377 | 0.0660 | 1.7855 | (3, 7, 500) |
| `Carol/ChannelBetas` | **0.3774** | -0.2239 | 0.0022 | 0.0015 | (7, 29, 500) |
| `Carol/ChannelTstats` | **16.2397** | -10.9132 | 0.1436 | 2.7873 | (7, 29, 500) |
| `Carol/ROIBetas` | **0.2022** | -0.0908 | 0.0023 | 0.0007 | (3, 7, 500) |
| `Carol/ROITstats` | **10.0004** | -6.9890 | 0.2431 | 3.5542 | (3, 7, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `HFA magnitude`
- **Anomalies**: `Missing 'fs' attribute`

---

### [Audit]: glm_results_hfa_baselocal_ModelB.h5
- **Target File**: `derivatives/glm_results/glm_results_hfa_baselocal_ModelB.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/ChannelBetas, Boss/ChannelTstats, Boss/ROIBetas, Boss/ROITstats, Carol, Carol/ChannelBetas, Carol/ChannelTstats, Carol/ROIBetas, Carol/ROITstats`
    - Target Dataset Shape: `(8, 28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/ChannelBetas` | **0.2121** | -0.1791 | 0.0007 | 0.0007 | (8, 28, 500) |
| `Boss/ChannelTstats` | **6.1593** | -5.6407 | 0.0074 | 1.7462 | (8, 28, 500) |
| `Boss/ROIBetas` | **0.0989** | -0.0575 | 0.0009 | 0.0002 | (3, 8, 500) |
| `Boss/ROITstats` | **5.0291** | -4.4104 | 0.0419 | 1.7547 | (3, 8, 500) |
| `Carol/ChannelBetas` | **0.4703** | -0.2252 | 0.0025 | 0.0014 | (8, 29, 500) |
| `Carol/ChannelTstats` | **16.2478** | -10.7215 | 0.0595 | 2.8615 | (8, 29, 500) |
| `Carol/ROIBetas` | **0.2491** | -0.0950 | 0.0023 | 0.0008 | (3, 8, 500) |
| `Carol/ROITstats` | **10.7664** | -5.9634 | 0.1016 | 3.8245 | (3, 8, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `HFA magnitude`
- **Anomalies**: `Missing 'fs' attribute`

---

### [Audit]: glm_results_hfa_baselocal_ModelA.h5
- **Target File**: `derivatives/glm_results/glm_results_hfa_baselocal_ModelA.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/ChannelBetas, Boss/ChannelTstats, Boss/ROIBetas, Boss/ROITstats, Carol, Carol/ChannelBetas, Carol/ChannelTstats, Carol/ROIBetas, Carol/ROITstats`
    - Target Dataset Shape: `(4, 28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/ChannelBetas` | **0.1424** | -0.1449 | 0.0014 | 0.0009 | (4, 28, 500) |
| `Boss/ChannelTstats` | **6.5944** | -5.6341 | 0.0924 | 2.0386 | (4, 28, 500) |
| `Boss/ROIBetas` | **0.0836** | -0.0486 | 0.0019 | 0.0003 | (3, 4, 500) |
| `Boss/ROITstats` | **7.0014** | -4.1093 | 0.2096 | 2.2976 | (3, 4, 500) |
| `Carol/ChannelBetas` | **0.4098** | -0.2344 | 0.0055 | 0.0020 | (4, 29, 500) |
| `Carol/ChannelTstats` | **19.4921** | -11.5357 | 0.3028 | 4.9842 | (4, 29, 500) |
| `Carol/ROIBetas` | **0.2070** | -0.0957 | 0.0052 | 0.0012 | (3, 4, 500) |
| `Carol/ROITstats` | **14.4958** | -5.9424 | 0.4821 | 7.7674 | (3, 4, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `HFA magnitude`
- **Anomalies**: `Missing 'fs' attribute`

---

### [Audit]: unique_variance_erp_baseglobal.h5
- **Target File**: `derivatives/analysis/unique_variance/unique_variance_erp_baseglobal.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/Channel_DeltaR2_MDL, Boss/Channel_DeltaR2_Surp, Boss/ROI_DeltaR2_MDL, Boss/ROI_DeltaR2_Surp, Carol, Carol/Channel_DeltaR2_MDL, Carol/Channel_DeltaR2_Surp, Carol/ROI_DeltaR2_MDL, Carol/ROI_DeltaR2_Surp`
    - Target Dataset Shape: `(28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/Channel_DeltaR2_MDL` | **0.0012** | 0.0000 | 0.0001 | 0.0000 | (28, 500) |
| `Boss/Channel_DeltaR2_Surp` | **0.0009** | 0.0000 | 0.0000 | 0.0000 | (28, 500) |
| `Boss/ROI_DeltaR2_MDL` | **0.0004** | 0.0000 | 0.0001 | 0.0000 | (3, 500) |
| `Boss/ROI_DeltaR2_Surp` | **0.0002** | 0.0000 | 0.0000 | 0.0000 | (3, 500) |
| `Carol/Channel_DeltaR2_MDL` | **0.0036** | 0.0000 | 0.0001 | 0.0000 | (29, 500) |
| `Carol/Channel_DeltaR2_Surp` | **0.0008** | 0.0000 | 0.0000 | 0.0000 | (29, 500) |
| `Carol/ROI_DeltaR2_MDL` | **0.0012** | 0.0000 | 0.0001 | 0.0000 | (3, 500) |
| `Carol/ROI_DeltaR2_Surp` | **0.0003** | 0.0000 | 0.0000 | 0.0000 | (3, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `ERP (likely V or z-score)`
- **Anomalies**: `Missing 'fs' attribute`

---

### [Audit]: glm_results_erp_baseglobal_ModelD.h5
- **Target File**: `derivatives/glm_results/glm_results_erp_baseglobal_ModelD.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/ChannelBetas, Boss/ChannelTstats, Boss/ROIBetas, Boss/ROITstats, Carol, Carol/ChannelBetas, Carol/ChannelTstats, Carol/ROIBetas, Carol/ROITstats`
    - Target Dataset Shape: `(8, 28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/ChannelBetas` | **11.2478** | -9.2649 | 0.0116 | 0.4766 | (8, 28, 500) |
| `Boss/ChannelTstats` | **30.6981** | -27.3264 | 0.0600 | 9.2348 | (8, 28, 500) |
| `Boss/ROIBetas` | **29.4439** | -3.3906 | 2.7522 | 66.7753 | (3, 8, 500) |
| `Boss/ROITstats` | **199.0668** | -34.1251 | 16.8934 | 2726.1909 | (3, 8, 500) |
| `Carol/ChannelBetas` | **10.1378** | -15.5275 | 0.0025 | 1.2696 | (8, 29, 500) |
| `Carol/ChannelTstats` | **42.3936** | -43.8769 | 0.0486 | 24.8623 | (8, 29, 500) |
| `Carol/ROIBetas` | **26.1642** | -2.3938 | 2.7583 | 61.0906 | (3, 8, 500) |
| `Carol/ROITstats` | **201.5059** | -25.1276 | 18.5237 | 3160.0032 | (3, 8, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `ERP (likely V or z-score)`
- **Anomalies**: `Missing 'fs' attribute`

---

### [Audit]: glm_results_erp_baseglobal_ModelC.h5
- **Target File**: `derivatives/glm_results/glm_results_erp_baseglobal_ModelC.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/ChannelBetas, Boss/ChannelTstats, Boss/ROIBetas, Boss/ROITstats, Carol, Carol/ChannelBetas, Carol/ChannelTstats, Carol/ROIBetas, Carol/ROITstats`
    - Target Dataset Shape: `(7, 28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/ChannelBetas` | **11.1400** | -10.2181 | 0.0085 | 0.5712 | (7, 28, 500) |
| `Boss/ChannelTstats` | **37.6172** | -35.6058 | 0.0321 | 11.1794 | (7, 28, 500) |
| `Boss/ROIBetas` | **28.8017** | -3.4262 | 2.9699 | 73.2143 | (3, 7, 500) |
| `Boss/ROITstats` | **240.7981** | -34.1554 | 23.2025 | 4460.3957 | (3, 7, 500) |
| `Carol/ChannelBetas` | **9.7634** | -15.5306 | 0.0058 | 1.4691 | (7, 29, 500) |
| `Carol/ChannelTstats` | **42.4003** | -53.8587 | 0.0482 | 32.0856 | (7, 29, 500) |
| `Carol/ROIBetas` | **26.1950** | -2.4132 | 3.1481 | 68.2556 | (3, 7, 500) |
| `Carol/ROITstats` | **249.4347** | -25.1291 | 26.7806 | 5378.1894 | (3, 7, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `ERP (likely V or z-score)`
- **Anomalies**: `Missing 'fs' attribute`

---

### [Audit]: glm_results_erp_baseglobal_ModelB.h5
- **Target File**: `derivatives/glm_results/glm_results_erp_baseglobal_ModelB.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/ChannelBetas, Boss/ChannelTstats, Boss/ROIBetas, Boss/ROITstats, Carol, Carol/ChannelBetas, Carol/ChannelTstats, Carol/ROIBetas, Carol/ROITstats`
    - Target Dataset Shape: `(8, 28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/ChannelBetas` | **10.8560** | -9.2567 | 0.0026 | 0.4640 | (8, 28, 500) |
| `Boss/ChannelTstats` | **33.5944** | -30.9532 | 0.0428 | 8.8499 | (8, 28, 500) |
| `Boss/ROIBetas` | **28.9739** | -3.4037 | 2.7298 | 65.7654 | (3, 8, 500) |
| `Boss/ROITstats` | **220.9764** | -34.2357 | 18.6093 | 3379.8013 | (3, 8, 500) |
| `Carol/ChannelBetas` | **9.7689** | -15.4460 | 0.0058 | 1.2564 | (8, 29, 500) |
| `Carol/ChannelTstats` | **42.3888** | -49.3993 | 0.0577 | 25.1808 | (8, 29, 500) |
| `Carol/ROIBetas` | **26.1860** | -2.3938 | 2.7535 | 60.8312 | (3, 8, 500) |
| `Carol/ROITstats` | **228.5720** | -25.1175 | 21.3209 | 4024.5906 | (3, 8, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `ERP (likely V or z-score)`
- **Anomalies**: `Missing 'fs' attribute`

---

### [Audit]: glm_results_erp_baseglobal_ModelA.h5
- **Target File**: `derivatives/glm_results/glm_results_erp_baseglobal_ModelA.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/ChannelBetas, Boss/ChannelTstats, Boss/ROIBetas, Boss/ROITstats, Carol, Carol/ChannelBetas, Carol/ChannelTstats, Carol/ROIBetas, Carol/ROITstats`
    - Target Dataset Shape: `(4, 28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/ChannelBetas` | **10.4203** | -9.8749 | 0.0064 | 0.9177 | (4, 28, 500) |
| `Boss/ChannelTstats` | **52.2771** | -53.6991 | -0.0051 | 22.9013 | (4, 28, 500) |
| `Boss/ROIBetas` | **28.6399** | -3.4024 | 5.4154 | 117.7658 | (3, 4, 500) |
| `Boss/ROITstats` | **355.0326** | -34.2605 | 61.8762 | 15488.5174 | (3, 4, 500) |
| `Carol/ChannelBetas` | **9.7489** | -15.4925 | 0.0118 | 2.4675 | (4, 29, 500) |
| `Carol/ChannelTstats` | **59.6206** | -80.8853 | 0.0423 | 76.9574 | (4, 29, 500) |
| `Carol/ROIBetas` | **26.0635** | -2.3899 | 5.5193 | 105.5090 | (3, 4, 500) |
| `Carol/ROITstats` | **369.1749** | -25.1375 | 72.8133 | 18079.4304 | (3, 4, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `ERP (likely V or z-score)`
- **Anomalies**: `Missing 'fs' attribute`

---

### [Audit]: unique_variance_erp_baselocal.h5
- **Target File**: `derivatives/analysis/unique_variance/unique_variance_erp_baselocal.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/Channel_DeltaR2_MDL, Boss/Channel_DeltaR2_Surp, Boss/ROI_DeltaR2_MDL, Boss/ROI_DeltaR2_Surp, Boss/ROI_PValue_MDL, Boss/ROI_PValue_Surp, Carol, Carol/Channel_DeltaR2_MDL, Carol/Channel_DeltaR2_Surp, Carol/ROI_DeltaR2_MDL, Carol/ROI_DeltaR2_Surp, Carol/ROI_PValue_MDL, Carol/ROI_PValue_Surp`
    - Target Dataset Shape: `(28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/Channel_DeltaR2_MDL` | **0.0013** | 0.0000 | 0.0001 | 0.0000 | (28, 500) |
| `Boss/Channel_DeltaR2_Surp` | **0.0006** | 0.0000 | 0.0000 | 0.0000 | (28, 500) |
| `Boss/ROI_DeltaR2_MDL` | **0.0004** | 0.0000 | 0.0001 | 0.0000 | (3, 500) |
| `Boss/ROI_DeltaR2_Surp` | **0.0001** | 0.0000 | 0.0000 | 0.0000 | (3, 500) |
| `Boss/ROI_PValue_MDL` | **0.9850** | 0.0000 | 0.1323 | 0.0379 | (3, 500) |
| `Boss/ROI_PValue_Surp` | **1.0000** | 0.0000 | 0.2514 | 0.0607 | (3, 500) |
| `Carol/Channel_DeltaR2_MDL` | **0.0036** | 0.0000 | 0.0002 | 0.0000 | (29, 500) |
| `Carol/Channel_DeltaR2_Surp` | **0.0007** | -0.0000 | 0.0000 | 0.0000 | (29, 500) |
| `Carol/ROI_DeltaR2_MDL` | **0.0014** | 0.0000 | 0.0001 | 0.0000 | (3, 500) |
| `Carol/ROI_DeltaR2_Surp` | **0.0003** | 0.0000 | 0.0000 | 0.0000 | (3, 500) |
| `Carol/ROI_PValue_MDL` | **0.8050** | 0.0000 | 0.0510 | 0.0126 | (3, 500) |
| `Carol/ROI_PValue_Surp` | **1.0000** | 0.0000 | 0.2548 | 0.0681 | (3, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `ERP (likely V or z-score)`
- **Anomalies**: `Missing 'fs' attribute`

---

### [Audit]: glm_results_erp_baselocal_ModelD.h5
- **Target File**: `derivatives/glm_results/glm_results_erp_baselocal_ModelD.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/ChannelBetas, Boss/ChannelTstats, Boss/ROIBetas, Boss/ROITstats, Carol, Carol/ChannelBetas, Carol/ChannelTstats, Carol/ROIBetas, Carol/ROITstats`
    - Target Dataset Shape: `(8, 28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/ChannelBetas` | **11.0972** | -9.4156 | -0.0399 | 0.5546 | (8, 28, 500) |
| `Boss/ChannelTstats` | **26.2389** | -22.8581 | -0.0406 | 9.1305 | (8, 28, 500) |
| `Boss/ROIBetas` | **32.8046** | -3.9634 | 2.9298 | 78.0432 | (3, 8, 500) |
| `Boss/ROITstats` | **199.8311** | -36.1453 | 17.0623 | 2833.5940 | (3, 8, 500) |
| `Carol/ChannelBetas` | **11.3516** | -14.8532 | -0.0086 | 1.5776 | (8, 29, 500) |
| `Carol/ChannelTstats` | **36.9973** | -39.2824 | -0.2828 | 26.7509 | (8, 29, 500) |
| `Carol/ROIBetas` | **28.4649** | -2.5945 | 2.9754 | 70.7583 | (3, 8, 500) |
| `Carol/ROITstats` | **200.0020** | -25.5902 | 18.8803 | 3295.8217 | (3, 8, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `ERP (likely V or z-score)`
- **Anomalies**: `Missing 'fs' attribute`

---

### [Audit]: glm_results_erp_baselocal_ModelC.h5
- **Target File**: `derivatives/glm_results/glm_results_erp_baselocal_ModelC.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/ChannelBetas, Boss/ChannelTstats, Boss/ROIBetas, Boss/ROITstats, Carol, Carol/ChannelBetas, Carol/ChannelTstats, Carol/ROIBetas, Carol/ROITstats`
    - Target Dataset Shape: `(7, 28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/ChannelBetas` | **10.3118** | -11.0463 | -0.1071 | 0.7580 | (7, 28, 500) |
| `Boss/ChannelTstats` | **30.1655** | -32.1301 | -0.2004 | 11.0283 | (7, 28, 500) |
| `Boss/ROIBetas` | **32.2791** | -4.0167 | 3.1762 | 85.1837 | (3, 7, 500) |
| `Boss/ROITstats` | **242.0812** | -36.2980 | 23.5874 | 4617.4713 | (3, 7, 500) |
| `Carol/ChannelBetas` | **11.4163** | -14.2165 | 0.0043 | 1.9452 | (7, 29, 500) |
| `Carol/ChannelTstats` | **37.0112** | -48.8605 | -0.2741 | 36.0613 | (7, 29, 500) |
| `Carol/ROIBetas` | **28.5654** | -2.5996 | 3.4112 | 79.6530 | (3, 7, 500) |
| `Carol/ROITstats` | **248.4441** | -25.3613 | 27.3952 | 5647.2682 | (3, 7, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `ERP (likely V or z-score)`
- **Anomalies**: `Missing 'fs' attribute`

---

### [Audit]: glm_results_erp_baselocal_ModelB.h5
- **Target File**: `derivatives/glm_results/glm_results_erp_baselocal_ModelB.h5`
- **H5 Structure Discovery**:
    - Groups/Datasets: `Boss, Boss/ChannelBetas, Boss/ChannelTstats, Boss/ROIBetas, Boss/ROITstats, Carol, Carol/ChannelBetas, Carol/ChannelTstats, Carol/ROIBetas, Carol/ROITstats`
    - Target Dataset Shape: `(8, 28, 500)` (Showing primary)
- **Raw Numerical Summary**:
| Dataset Path | Max Value | Min Value | Mean | Variance | Shape |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Boss/ChannelBetas` | **10.8193** | -9.2934 | -0.0514 | 0.5685 | (8, 28, 500) |
| `Boss/ChannelTstats` | **29.0066** | -24.7144 | -0.1327 | 8.6915 | (8, 28, 500) |
| `Boss/ROIBetas` | **32.5626** | -3.9767 | 2.9173 | 77.3049 | (3, 8, 500) |
| `Boss/ROITstats` | **222.6327** | -36.2744 | 18.8436 | 3537.6750 | (3, 8, 500) |
| `Carol/ChannelBetas` | **11.0912** | -14.1237 | -0.0081 | 1.5638 | (8, 29, 500) |
| `Carol/ChannelTstats` | **36.9956** | -39.8558 | -0.2143 | 26.1013 | (8, 29, 500) |
| `Carol/ROIBetas` | **28.4499** | -2.5924 | 2.9750 | 70.6095 | (3, 8, 500) |
| `Carol/ROITstats` | **226.7647** | -25.5399 | 21.8249 | 4201.9938 | (3, 8, 500) |
- **Metadata Check**:
    - FS Attribute: `NOT DETECTED`
    - Scale Check: `ERP (likely V or z-score)`
- **Anomalies**: `Missing 'fs' attribute`

---
