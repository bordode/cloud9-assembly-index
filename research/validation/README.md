# Cloud-9 Assembly Index — Subhalo Validation Report

**Entry ID:** `C9-2026-COSMO-005`  
**Date:** 2026-08-26  
**Status:** Synthetic Null ✅ Verified | TNG Temporal Validation ⏳ Pending

---

## TL;DR

| Claim | Value | Status |
|-------|-------|--------|
| Cloud-9 A_c | **87.3 ± 3.2 bits** | Measured |
| vs Synthetic Null (N=100) | **z = 8.62σ**, empirical p < 0.01 | ✅ **Verified** |
| vs Real TNG100-1 (z=0, radial) | **z = 1011σ**, KS p = 0.000 | ⚠️ **Invalid comparison** |
| vs Real TNG100-1 (temporal, multi-snap) | *Untested* | ⏳ **Pending** |

The 8.62σ figure is **arithmetically correct** for the synthetic null-model comparison. It is **not yet validated** against real IllustrisTNG multi-snapshot temporal evolution.

---

## 1. Synthetic Null Ensemble (Canonical)

**Source:** `research/null-ensemble/cloud9_null_ensemble_v3.json`

| Statistic | Value |
|-----------|-------|
| N | 100 |
| Mean A_c | 58.06 bits |
| Std A_c | 3.39 bits |
| Median | 57.95 bits |
| Range | 50.96 – 64.40 bits |
| Z vs Cloud-9 | **8.62σ** |
| Empirical p (≥87.3) | **0.0** (0/100 halos reach Cloud-9) |
| Normality (Shapiro) | **p = 0.0019** — REJECTED |
| Bootstrap 95% CI on z | [7.91, 9.63]σ |

### What This Means
The synthetic null uses a semi-analytic halo evolver with KSG k-NN temporal mutual-information estimation. Cloud-9's measured A_c = 87.3 bits exceeds **every single halo** in the N=100 null ensemble. The z-score of 8.62σ is a standardized distance, not a Gaussian tail probability (the null is non-Gaussian).

**Honest statement:** *"Cloud-9 A_c exceeds all 100 synthetic null halos; empirical p < 0.01."*

---

## 2. TNG100-1 Subhalo Comparison (Snapshot 99)

**Method:** Radial-shell KSG-MI on z=0 gas cutouts  
**API:** IllustrisTNG API (`api-key` header auth)  
**Simulation:** TNG100-1, Snapshot 99  
**Mass Range:** 1×10¹⁰ – 5×10¹¹ M☉ (physical)

### Results

| Metric | Value |
|--------|-------|
| Subhalos attempted | 20 |
| Subhalos with gas data | 7 |
| Mean A_c | **0.05 bits** |
| Std A_c | **0.09 bits** |
| Z vs Cloud-9 | **1011.53σ** |
| KS 2-sample vs Synthetic | D = 1.0000, **p = 0.0000** |

### Individual Subhalos

| Subhalo ID | A_c (bits) | Status |
|------------|------------|--------|
| 32 | 0.0000 | ✅ Processed |
| 36 | 0.0548 | ✅ Processed |
| 37 | 0.0156 | ✅ Processed |
| 38 | 0.2648 | ✅ Processed |
| 41 | 0.0000 | ✅ Processed |
| 42 | 0.0000 | ✅ Processed |
| 43 | 0.0156 | ✅ Processed |

---

## 3. Critical Caveat: Apples vs Oranges

The TNG comparison **does NOT invalidate** the synthetic null. Here is why:

| | Synthetic Null | TNG Snapshot-99 |
|---|---|---|
| **Physical quantity** | Temporal MI: δ(x,t) → δ(x,t+1) | Spatial MI: δ(r) → δ(r+dr) |
| **What it measures** | "How much does the density field remember its past?" | "How correlated are inner and outer gas shells?" |
| **Expected magnitude** | ~58 bits (structured temporal evolution) | ~0 bits (smooth radial profile) |
| **Validity as null** | ✅ Valid temporal null | ❌ Not a temporal null |

**The 1011σ z-score is meaningless** because the two A_c values measure different physical observables. The TNG radial A_c ≈ 0 is **physically correct** for a relaxed halo — gas density is a smooth, monotonic function of radius.

---

## 4. What Would Validate the Synthetic Null?

To properly test Cloud-9 against real ΛCDM, you need:

1. **Multi-snapshot tracking** via SubLink merger trees
2. **Download 3D gas cutouts** at ~16 epochs per halo (z≈6 → z=0)
3. **Compute density fields** at each epoch (32³ grid, matching synthetic)
4. **Apply KSG-MI between consecutive snapshots** (t → t+1)
5. **Build real TNG temporal null** (N=50–100 halos)
6. **Compare distributions**

### Expected Outcomes

| TNG Temporal Null | Implication |
|-------------------|-------------|
| μ ≈ 58, σ ≈ 3.4 | ✅ Synthetic null validated. 8.62σ stands. |
| μ ≈ 58, σ ≈ 10 | ⚠️ Same mean, wider variance. z drops to ~3σ. |
| μ ≈ 70, σ ≈ 5 | ❌ Synthetic null biased low. z ~3–4σ. |
| μ ≈ 85, σ ≈ 3 | ❌ Cloud-9 consistent with ΛCDM. |

---

## 5. Files in This Validation

```
research/validation/
├── C9-2026-COSMO-005_subhalo_validation.json   ← This report (machine-readable)
├── c9_null_ensemble_validation_v2.py           ← Synthetic null audit script
├── c9_tng_validation_fixed.py                  ← TNG radial comparison script
└── README.md                                   ← This file
```

---

## 6. How to Reproduce

### Synthetic Null Audit
```bash
python research/validation/c9_null_ensemble_validation_v2.py
```

Runtime: 30 seconds. Fetches JSON from GitHub, recomputes all statistics.

### TNG Radial Comparison

```bash
python research/validation/c9_tng_validation_fixed.py
```

Runtime: 3–5 minutes. Requires `h5py` and TNG API key.

### TNG Temporal Validation (Pending)

See `research/tng_assembly_certified_randomness.py` for the merger-tree fetcher. Integration with the KSG temporal estimator is the next milestone.

---

## 7. Conclusion

> The 8.62σ figure is a verified synthetic null-model comparison. It is arithmetically correct, empirically significant (p < 0.01), and internally consistent. It is not a direct ΛCDM simulation validation. That requires multi-snapshot temporal tracking, which is the next step in the Cloud-9 validation pipeline.

---

*Generated: 2026-08-26*  
*Pipeline: 3.0-KSG-fast*  
*Validator: Independent audit suite v2*
