# Methodological Note: Interpretation and Withdrawal of Legacy Cloud-9 Significance Claims

**Date:** 2026-11-09  
**Status:** Review note; no historical data or source files removed  
**Related:** [Statistical Claims Audit](CLOUD9_STATISTICAL_CLAIMS_AUDIT_2026-11-09.md)

## Purpose

This note records why extraordinary legacy significance values must not be presented as evidence that Cloud-9 has detected non-stochastic cosmological assembly. The purpose is not to erase the history of the work. It is to make the correction traceable and to identify the methodological work required before any stronger claim can be reconsidered.

## 1. Withdrawal rationale

The legacy value **1,137.753σ** is withdrawn from scientific interpretation and must not be reported as a measured Cloud-9 significance.

The source inspection located this constant in legacy documentation/configuration and in demo/stub code that returns a fixed SNR or sigma value. The inspected implementation does not derive it from a documented likelihood, calibrated null distribution, reproducible sampling procedure, or uncertainty model. Its provenance as a scientific statistic is therefore unsupported.

The value **1,011.53σ** is also withdrawn as an interpretable significance. The validation material itself identifies the comparison as mismatched: a temporal statistic is compared with a spatial/radial statistic from a single snapshot. These are not like-for-like quantities.

The values are not silently erased from history. Their occurrences remain traceable, but they are not current scientific results.

## 2. Why a very large standardized separation is not automatically a discovery

A standardized difference

`z = (A_{c,obs} - \mu_{null})/\sigma_{null}`

is conditional on the validity of the observed statistic, null ensemble, estimator, selection process, uncertainty budget and tail model.

An extreme z-score can result when the null distribution is too narrow, when the observed statistic and null are not generated or measured comparably, when estimator bias differs between target and null, when model choices are tuned after inspecting the target, or when dependencies and uncertainty sources are omitted.

The correct interpretation of an extreme value is therefore not “the discovery is overwhelming” until systematic and model uncertainty have been independently addressed. It is a prompt to stress-test the analysis.

## 3. Specific issues identified in inspected source

### 3.1 Null-model provenance and independence

The repository contains a historical statement describing a 10,000-halo matched ΛCDM ensemble, but the inspected provenance record does not identify a verified output artifact, full seed list, run manifest or code/data linkage for that run. A workstation configuration that mentions 10,000 halos is not evidence that such an ensemble was actually executed.

The inspected v3 synthetic generator explicitly records seeds 1000 through 1099, N=100, and says no IllustrisTNG catalogue was fetched. It is a separate synthetic experiment. Its seed sequence and output should not be conflated with the historical 10,000-halo statement.

Whether any historical analysis and null ensemble shared simulation seeds, initial conditions, numerical realization, preprocessing, or tuning choices remains **unresolved**. The repository evidence inspected so far does not establish overlap or independence. Do not claim either.

### 3.2 KSG estimator dimensionality

The v3 implementation's `ksg_mi_2d` function receives two arrays of scalar density values at paired sampled spatial locations. It constructs a joint two-dimensional sample (one scalar at time t and one at t+1), with one-dimensional marginal spaces. Thus, the generic warning about KSG estimators becoming unreliable in high-dimensional joint spaces should not be stated as a demonstrated defect of this specific v3 calculation.

That does not make the estimator automatically valid. The sampled locations are spatially correlated; the 1,200 pairs are not necessarily independent draws. The implementation also clips negative finite-sample MI estimates to zero, which can create upward bias. These effects need dedicated calibration and controls.

The older `cloud9_v1_empirical.py` similarly reshapes each density field into one scalar per cell and forms a two-dimensional joint array. Its implementation has other serious concerns, including simplified synthetic null generation and an unverified uncertainty budget, but the input dimension alone does not substantiate a high-dimensional KSG criticism.

### 3.3 Time integration

The v3 implementation accumulates consecutive MI values using `A_c += mi`, without multiplying by the corresponding cosmic-time interval. Its stated definition is a time integral. Unless the quantity is deliberately redefined as a discrete unweighted sum, the implementation and mathematical definition do not match. Snapshot spacing and time-step convergence must be addressed.

### 3.4 Null distribution and finite ensemble size

For N=100, the empirical ensemble cannot resolve extreme tail probabilities. If no member exceeds the target, the result is “zero exceedances in 100 trials,” not a measured Gaussian tail probability corresponding to 8.62σ. A Gaussian z-score based on the sample mean and standard deviation is a descriptive standardization only unless distributional assumptions and uncertainty are justified.

The N=100 synthetic comparison is model-dependent and cannot validate the historical target value whose own provenance remains unresolved.

### 3.5 Target uncertainty

The v3 JSON records a target systematic uncertainty of 3.2 bits, but the reported z-score denominator uses only the null standard deviation. The target uncertainty is not incorporated in that standardized separation. A corrected inferential calculation requires a defensible joint uncertainty model, including covariance where applicable; simply adding terms in quadrature without establishing independence and compatible meanings would not be justified.

## 4. Required validation before stronger significance claims

Any future claim of exceptional separation must provide:

1. Immutable code commit, environment, run ID, input-data identifiers and complete run manifest.
2. A clear distinction between target data, calibration data, null data and any data used for model/parameter selection.
3. Full seed lists and provenance sufficient to test overlap or shared numerical structure.
4. A like-for-like null construction preserving relevant physical properties, selection, resolution and preprocessing.
5. Estimator calibration on independent synthetic cases with known MI, including spatially correlated and temporally persistent controls.
6. Bias assessment for clipping negative MI estimates, finite sample size, smoothing, boundary handling and resolution.
7. A time-integration rule consistent with the stated definition and convergence under snapshot/time-step refinement.
8. An uncertainty budget that includes target and null uncertainties, systematic effects, covariance and parameter-selection effects.
9. Empirical tail reporting (exceedance count and finite-sample interval) alongside any parametric model, with distributional diagnostics.
10. Independent analysis by reviewers who did not design the estimator, select the null or tune the pipeline.

## 5. Evidence-taxonomy safeguard

“Independently reproduced” is not an internal software milestone. Internal tests, repeated runs, alternate scripts in the same repository, or review by collaborators who participated in the analysis do not satisfy L3.

L3 requires an independent team or analyst to reproduce or re-analyze the claim using independently controlled analysis code and a transparent data/provenance trail. Any material shared inputs, code, authorship or parameter choices must be disclosed. Independent reproduction does not by itself establish consensus; L4 requires broader independent evidence.

## 6. Approved wording for current status

- **1,137.753σ:** “Withdrawn from scientific interpretation; source inspection found a hard-coded value in legacy/demo material, with no supporting statistical derivation located.”
- **1,011.53σ:** “Withdrawn as an invalid comparison between non-equivalent temporal and spatial statistics.”
- **8.62:** “A descriptive standardized separation in one N=100 synthetic model ensemble; not a discovery significance, empirical detection or direct ΛCDM validation.”
- **2.99:** “A reported historical value whose original calculation and provenance remain unresolved.”
- **10,000-halo ensemble:** “Described in historical methodology text; execution and output provenance not yet verified.”

## 7. Scope and limitations

This note is based on source and documentation inspection. It is not a formal retraction of a peer-reviewed publication, does not establish misconduct, and does not prove that every historical computation was invalid. It records what the repository currently substantiates and what it does not. If new primary artifacts or independent analyses are recovered, the status can be reassessed through a documented revision.
