# Cloud-9 Assembly Index — Subhalo Validation Report

**Entry ID:** `C9-2026-COSMO-005`  
**Date:** 2026-08-26  
**Status:** Synthetic Null 🧪 Experimental / reproducible comparison | TNG Temporal Validation ⏳ Pending

---

## TL;DR

| Claim | Value | Status |
|-------|-------|--------|
| Cloud-9 A_c | **87.3 ± 3.2 bits** | Reported historical measurement |
| vs Synthetic Null (N=100) | **z = 8.62σ** | 🧪 Experimental synthetic comparison |
| Empirical tail test | **0/100 synthetic halos ≥ 87.3** | ⚠️ Limited by N=100 |
| vs Real TNG100-1 (z=0, radial) | **z = 1011σ**, KS p = 0.000 | ⚠️ Invalid comparison |
| vs Real TNG100-1 (temporal, multi-snap) | *Untested* | ⏳ Pending |

The 8.62σ figure is **arithmetically correct for this synthetic null-model comparison**. It is **not a discovery claim and is not yet validated against real IllustrisTNG multi-snapshot temporal evolution**.

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
| Empirical exceedances (≥87.3) | **0/100** |
| Empirical tail resolution | **1/100-scale**; exact p convention must be stated |
| Normality (Shapiro) | **p = 0.0019** — REJECTED |
| Bootstrap 95% CI on z | [7.91, 9.63]σ |

### What This Means

The synthetic null uses a semi-analytic halo evolver with KSG k-NN temporal mutual-information estimation. Cloud-9's reported A_c = 87.3 bits exceeds **every single halo** in the N=100 synthetic null ensemble. The z-score of 8.62σ is a standardized distance within this model comparison; because the null is non-Gaussian, it should not be converted automatically into a Gaussian discovery p-value.

**Preferred statement:** *"Cloud-9's reported A_c exceeds all 100 synthetic null halos; the resulting standardized separation is z = 8.62σ in this synthetic comparison."*

The empirical tail probability is limited by the ensemble size. If a finite-sample convention such as `(k+1)/(N+1)` is used, 0 exceedances would correspond to approximately 0.0099; the exact convention should be reported with any p-value.

---

### Reproduction provenance note (2026-11-14)

The 100-member synthetic ensemble (seeds 1000–1099) has now been independently regenerated from the recovered historical `3.0-KSG-fast` implementation using a separate copy with the documented constructor-keyword mapping correction. All 100 members matched the archived JSON across all nine compared fields, including the complete per-member mutual-information vectors, at tolerance 1e-10. The reproduced mean and population SD match the archived aggregate values; the population-SD standardized separation is 8.6232720812.

This result establishes reproducibility from the corrected recovered implementation, **not** successful execution of the unmodified historical script as committed, nor identification of the exact source revision originally used to produce the JSON. The correction and comparison are documented in the [full source-recovery and reproducibility audit](NULL_ENSEMBLE_V3_REPRODUCIBILITY_AUDIT.md) and [GitHub Actions run](https://github.com/bordode/cloud9-assembly-index/actions/runs/43584743288). The scientific caveat below is unchanged: real TNG multi-snapshot temporal validation remains pending.

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

**The 1011σ z-score is not scientifically interpretable as a comparison between the two experiments** because they measure different observables. The TNG radial A_c ≈ 0 may be physically reasonable for a smooth radial profile, but it does not test the temporal-null hypothesis.

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
| μ ≈ 58, σ ≈ 3.4 | Synthetic null model broadly supported; 8.62σ remains the model-comparison separation. |
| μ ≈ 58, σ ≈ 10 | Same mean, wider variance; standardized separation drops to ~3σ. |
| μ ≈ 70, σ ≈ 5 | Synthetic null biased low; standardized separation falls to ~3–4σ. |
| μ ≈ 85, σ ≈ 3 | Cloud-9 reported value becomes much less anomalous under ΛCDM. |

These are scenario illustrations, not predictions of the real TNG result.

---

## 5. Files in This Validation

```
research/validation/
├── C9-2026-COSMO-005_subhalo_validation.json   ← Machine-readable validation record
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

> The 8.62σ figure is a reproducible standardized separation within an N=100 synthetic null-model experiment. It is not a Gaussian discovery significance and is not direct ΛCDM validation. The real test is a like-for-like multi-snapshot temporal comparison using real TNG data, which remains pending.

---

*Generated: 2026-08-26*  
*Pipeline: 3.0-KSG-fast*  
*Validator: Independent audit suite v2*


## 8. Methods review and TNG protocol draft (2026-11-14)

A static code-level methods review has identified issues that must be addressed before the synthetic score is interpreted as a physically validated time-integrated cosmological statistic. In particular, the current implementation sums adjacent-snapshot MI values without time weighting on a non-uniform cosmic-time grid; its cosmic-time helper uses a fixed approximate Hubble conversion rather than the supplied H0; the synthetic density evolution is phenomenological rather than a TNG simulation; and the KSG estimator requires independent calibration. The reproduction comparator also needs stronger archive/schema integrity assertions.

- [Cloud-9 v3 methods review](CLOUD9_V3_METHODS_REVIEW_2026-11-14.md)
- [IllustrisTNG temporal validation protocol draft](ILLUSTRISTNG_TEMPORAL_VALIDATION_PROTOCOL_DRAFT.md)

These are review findings and a proposed protocol, not completed corrections or TNG results. The archived v3 implementation and JSON remain unchanged. The protocol requires the Cloud-9 observable and the mathematical estimand to be defined before any like-for-like TNG comparison is attempted.


### Strict comparator integrity rerun (2026-11-14)

The reproduction comparator now performs strict archive/schema/seed/value checks and writes source, archive and comparator SHA-256 hashes plus runtime versions into its output artifact. The strict rerun succeeded: 100/100 members matched, including all 15 MI estimates per member. See the [strict reproduction manifest](V3_STRICT_REPRODUCTION_MANIFEST_2026-11-14.json), [methods review](CLOUD9_V3_METHODS_REVIEW_2026-11-14.md), and [workflow run 43653944821](https://github.com/bordode/cloud9-assembly-index/actions/runs/43653944821).


### KSG estimator Gaussian diagnostic (2026-11-14)

The recovered v3 KSG estimator was compared with analytic bivariate-Gaussian mutual information at correlations 0.0, 0.5 and 0.8, with N=1,200 and 3,000 and three deterministic replicates per condition. Estimates were close in this small diagnostic; the largest absolute median error was approximately 0.0393 bits. This is preliminary only: more replicates, permutation controls, nonlinear and tie-heavy cases, and reference-implementation comparisons remain necessary.

See [KSG Gaussian diagnostic report](KSG_ESTIMATOR_GAUSSIAN_DIAGNOSTIC_2026-11-14.md) and [workflow run 43654133609](https://github.com/bordode/cloud9-assembly-index/actions/runs/43654133609). The same workflow reran and passed the strict 100-member ensemble reproduction.


## 9. KSG permutation and nonlinear diagnostic (2026-11-17)

The expanded KSG diagnostic completed successfully in [GitHub Actions run 43986162321](https://github.com/bordode/cloud9-assembly-index/actions/runs/43986162321). It tested 20 deterministic replicates at N=1,200 and 3,000, using shuffled-pair controls that preserve each marginal sample.

- Gaussian rho=0.5 paired estimates separated from shuffled controls, but median estimates (0.1796 and 0.1772 bits) were below analytic MI (0.2075 bits) by approximately 0.028–0.030 bits. This persistent discrepancy requires investigation.
- A nonlinear sinusoidal paired-sample stress test also separated strongly from its shuffled controls. No analytic MI is claimed for that construction.
- Between 65% and 90% of shuffled estimates were exactly zero after the recovered estimator's nonnegative clipping. Clipping therefore materially shapes the null distributions and must be examined using raw, unclipped estimates in a separate diagnostic.
- The strict 100-member historical ensemble reproduction passed again in the same workflow.

See [KSG permutation and nonlinear diagnostic report](KSG_ESTIMATOR_PERMUTATION_NONLINEAR_DIAGNOSTIC_2026-11-17.md). These tests are preliminary diagnostics, not estimator certification, cosmological validation, or TNG validation. Next priorities are a convention-matched independent reference implementation, raw unclipped estimates, broader N/rho/k calibration, and tie-heavy inputs.

### KSG permutation, nonlinear and reference-estimator diagnostics (2026-11-17)

The 20-replicate permutation study found clear separation between paired and shuffled Gaussian samples and between paired and shuffled sinusoidal samples. However, the rho=0.5 Gaussian median estimates (0.1796 bits at N=1,200; 0.1772 bits at N=3,000) remained below the analytic value of 0.2075 bits. Between 65% and 90% of shuffled estimates were exactly zero after the recovered estimator's nonnegative clipping. This is preliminary evidence of dependence discrimination alongside an unresolved quantitative calibration concern.

- [KSG permutation and nonlinear diagnostic report](KSG_ESTIMATOR_PERMUTATION_NONLINEAR_DIAGNOSTIC_2026-11-17.md)
- [Workflow 43986162321](https://github.com/bordode/cloud9-assembly-index/actions/runs/43986162321)

A separate implementation cross-check against scikit-learn 1.9.1 completed in [workflow 43987689799](https://github.com/bordode/cloud9-assembly-index/actions/runs/43987689799). Across 20 paired Gaussian replicates, recovered-v3 medians were 0.1796 bits (N=1,200) and 0.1766 bits (N=3,000), below the analytic 0.2075 bits. The recovered-v3 minus scikit-learn paired median difference was -0.0344 and -0.0217 bits, respectively. This is a convention-aware cross-check, not proof that either implementation is ground truth. The persistent numerical difference makes raw unclipped output and neighbour-count convention tests the next priority.

See [KSG independent reference cross-check report](KSG_ESTIMATOR_REFERENCE_CROSSCHECK_2026-11-17.md). The diagnostic artifact is attached to workflow 43987689799.


### KSG raw output and radius-boundary sensitivity (2026-11-23)

A separate diagnostic reconstructed the recovered v3 KSG expression without clipping and compared the existing inclusive `kth_radius + 1e-12` marginal counts with a strict-below-kth-radius sensitivity variant. The strict variant shifted Gaussian rho=0.5 means from 0.1808 to 0.2151 bits at N=1,200 and from 0.1830 to 0.2047 bits at N=3,000, against analytic MI 0.2075 bits. The current and strict conventions differed in all 20 replicates; approximately 0.5 marginal neighbours per dimension were included on average by the current boundary convention. Shuffled raw estimates also show how nonnegative clipping masks negative finite-sample estimates.

This makes boundary handling a leading explanation for the prior Gaussian calibration shortfall, but the strict variant is not yet certified or adopted. The historical source remains unchanged. See [raw KSG and radius-boundary diagnostic report](KSG_ESTIMATOR_RAW_BOUNDARY_DIAGNOSTIC_2026-11-23.md) and [workflow 45095297552](https://github.com/bordode/cloud9-assembly-index/actions/runs/45095297552). Next: verify the exact KSG Algorithm 1 count convention, add hand-checkable boundary and tie-heavy tests, then expand the Gaussian N/rho/k grid.


**KSG convention clarification:** the recovered function appears to mix KSG Type-I and Type-II conventions: it uses inclusive marginal counts but the Type-I digamma expression, omitting the Type-II `-1/k` correction. The strict-boundary sensitivity variant corresponds to Type I. A complete Type-I / Type-II / recovered-hybrid comparison is running in [workflow 45095685382](https://github.com/bordode/cloud9-assembly-index/actions/runs/45095685382); its numerical results are not yet available. See the [raw boundary report and convention mapping](KSG_ESTIMATOR_RAW_BOUNDARY_DIAGNOSTIC_2026-11-23.md), [original KSG paper](https://doi.org/10.1103/PhysRevE.69.066138), and [independent Type-I/Type-II documentation](https://infomeasure.readthedocs.io/en/0.6.0/guide/mutual_information/kraskov_stoegbauer_grassberger/).
