# Cloud-9 Statistical Claims Audit

**Date:** 2026-11-09  
**Scope:** Read-only review of the repository's current `master` branch and the named source files below.  
**Purpose:** Establish a conservative, traceable status for prominent numerical and interpretive claims before any public-facing README or manuscript revision.

> **This is a documentation audit, not a fresh independent reproduction.** No full pipeline was rerun for this note. Findings are based on source inspection and consistency checks across the repository.

## Executive finding

The repository contains several distinct numerical claims that must not be combined:

1. **1,137.753** — appears in legacy materials as a Bayesian sigma value, while the inspected stellar-broadening code returns the same number as a hard-coded SNR/sigma in stub/demo methods. No statistical derivation supporting a cosmological or Bayesian detection was located. Do not report it as a measured significance.
2. **8.62** — a standardized separation calculated from a reported historical target value (87.3 bits) and an ensemble of 100 synthetic, semi-analytic model realizations. It is a model-dependent computational comparison, not a discovery significance or a direct validation against a full ΛCDM simulation.
3. **2.99** — a historical result associated with a 1,000-member null ensemble in older documentation. The original inputs and run provenance remain unresolved. It must remain a reported historical value, not an independently reproduced result.
4. **1,011.53** — a reported comparison between a temporal synthetic statistic and a radial/spatial statistic from a single TNG snapshot. The validation report correctly identifies this as an invalid apples-to-oranges comparison. It is not an interpretable significance result.
5. **3.04** — an exploratory result in `sigma_boost.py` that uses a hard-coded simulated standard error. It is not independent statistical confirmation.

The current top-level README has improved evidence caveats, but legacy files still contain stronger or contradictory statements. A researcher following links into the repository can encounter those statements without seeing the newer qualifications.

## 1. Claim-by-claim findings

### 1.1 Legacy 1,137.753 value — unsupported as a statistical significance

**Locations inspected**
- `docs/README.md`: presents “v1.4.0 Bayesian σ = 1137.753” alongside cosmological assembly results.
- `data/cloud9.config.json`: contains `v140_bayesian_sigma: 1137.753`.
- `cloud9_assembly/ssbm/stellar_broadening.py`: `WidthAwareSETIPipeline.detect()` returns a fixed `snr: 1137.753`; `Cloud9SSBMIntegration.simulate_and_detect()` returns a fixed `sigma: 1137.753`. The surrounding classes include explicit demo/mock behavior.

**Finding**

The same constant is exposed in different contexts and is embedded in stub/demo code. The inspected code does not calculate a likelihood ratio, calibrated null tail, posterior odds, or sampling distribution from which a 1,137.753σ cosmological result could be inferred. The older documentation's label “Bayesian σ” is not supported by the inspected implementation.

**Disposition:** Mark as **unsupported legacy value / not a measured significance**. Remove it from current results tables and active marketing/publication language after preserving the historical occurrence in the audit trail. Do not silently delete historical files.

### 1.2 Synthetic Null Ensemble v3 — z = 8.62

**Locations inspected**
- `research/null-ensemble/cloud9_null_ensemble_v3.py`
- `research/null-ensemble/cloud9_null_ensemble_v3.json`
- `research/null-ensemble/README.md`
- `research/validation/README.md`
- `docs/EVIDENCE_STATUS.md`

The JSON records N=100, null mean 58.0622, sample standard deviation 3.3906, target A_c=87.3, and z=8.6233. The arithmetic is consistent with:

`(87.3 - 58.0622) / 3.3906 ≈ 8.6233`

The source generator labels itself a synthetic/prototype model and says no IllustrisTNG catalogue was fetched. It uses a semi-analytic halo-evolution construction, a 32³ grid, 16 time steps, and 1,200 sampled locations per step. It is not a full N-body/hydrodynamical ΛCDM run and is not the pending real-TNG temporal validation.

**Important methodological observations**

- The 8.62 value standardizes the difference using the null ensemble standard deviation. The JSON separately records a 3.2-bit uncertainty on the 87.3 target, but that target uncertainty is not included in the displayed z denominator. Simply adding 3.2 and 3.3906 in quadrature would give an illustrative separation of about 6.27, but that calculation assumes independent, commensurate uncertainties and is **not** offered as a corrected z-score. The proper uncertainty model needs to be specified.
- The ensemble contains only 100 null realizations. Zero exceedances means the empirical tail is unresolved below the finite-sample resolution; under the common plus-one convention, (0+1)/(100+1) is about 0.0099. A Gaussian tail probability must not be inferred from z=8.62, particularly because the validation report records a Shapiro test rejecting normality.
- In the inspected v3 generator, each temporal MI is added directly to A_c (`A_c += mi`). The stated mathematical definition is an integral over cosmic time, but the implementation does not multiply each MI by its corresponding time interval. Since the time steps are logarithmically spaced in scale factor, this is a material definition/implementation mismatch. A time-weighted integration rule and unit convention must be fixed before interpreting A_c as the stated integral.
- The KSG-like estimator samples spatial locations from evolving fields. Those locations are not automatically independent observations: spatial autocorrelation, shared evolution, smoothing, and the generator's construction can influence the estimated MI.
- Negative MI estimates are clipped to zero in the v3 estimator. The resulting upward truncation bias and its effects on the null distribution should be measured using independent calibration experiments.
- The target value 87.3 is itself a historical reported value whose provenance remains unresolved. The synthetic comparison therefore does not independently validate the observed target.

**Disposition:** Retain as **L1 / experimental synthetic model comparison**. The defensible wording is: “The reported historical A_c value exceeds all 100 members of this particular synthetic ensemble; the standardized separation is approximately 8.62 null standard deviations. This is model-dependent and is not a discovery significance or direct ΛCDM validation.” Do not use “8.62σ detection,” “non-stochastic assembly proven,” or equivalent wording.

### 1.3 Historical A_c = 87.3 ± 3.2 bits; reported z = 2.99

**Locations inspected**
- `docs/RESULTS_PROVENANCE.md`
- `docs/EVIDENCE_STATUS.md`
- `cloud9_v1_empirical.py`
- `cloud9/assembly.py`

The provenance document reports an N=1,000 synthetic null, mean 62.1, standard deviation 8.4, target 87.3 ± 3.2 and z=2.99, while explicitly stating that original inputs and the calculation have not been reconstructed. It separately notes a 10,000-member description in older methodology material without verified output provenance.

The arithmetic (87.3−62.1)/8.4 = 3.0. The reported p≈0.0014 corresponds approximately to a **one-sided** normal tail at z=3; the inspected `calculate_z_score()` in `cloud9_v1_empirical.py` calculates a **two-sided** p-value. That convention mismatch needs reconciliation.

The legacy `cloud9/assembly.py` also hard-codes 62.1 and 8.4 as calibration constants. Its current `compute_assembly_index()` sums consecutive-snapshot MI values and does not itself build or query a matched empirical null ensemble. Its status labels therefore should not be treated as a sample-specific statistical test.

**Disposition:** **Reported historical / provenance pending.** Do not call this independently verified. Reconstruct the original dataset, estimator, snapshot times, null ensemble, error budget and tail convention, or retain it only as an explicitly unverified historical report.

### 1.4 TNG radial comparison — z = 1,011.53

**Location inspected:** `research/validation/README.md`

The report gives a temporal MI statistic for the synthetic ensemble and a spatial/radial-shell statistic from gas cutouts at TNG snapshot 99. It explicitly labels the comparison invalid because the quantities differ. A radial profile at one epoch is not a temporal null for a time-integrated statistic.

**Disposition:** Keep only as a documented failed/invalid comparison. Do not quote 1,011.53σ as evidence, a result, or a lower bound. The correct next test is a like-for-like multi-snapshot TNG temporal analysis with matched measurement definitions and controls.

### 1.5 Exploratory z ≈ 3.04 calculation

**Location inspected:** `sigma_boost.py`

The script sets observed A_c=21.65, null mean=21.41 and `refined_std=0.079` with the comment “Simulated”. It writes a “High (Evidence confirmed)” confidence label. This is not an independently estimated sampling distribution or empirical uncertainty calculation.

**Disposition:** Treat as **L1 exploratory arithmetic only**. Replace “Evidence confirmed” language wherever this artifact is surfaced.

## 2. Measurement and interpretation limits

### 2.1 Mutual information is dependence, not a direct detector of non-stochastic assembly

Temporal mutual information measures statistical dependence between states. Persistence can arise from ordinary gravitational evolution, conservation laws, common causes, smooth dynamics, numerical smoothing, and correlated initial conditions. A large value alone does not distinguish these explanations.

To claim sensitivity to non-stochastic assembly, the metric must outperform appropriately matched controls, including temporally correlated stochastic fields and physically constrained ΛCDM simulations. The null should preserve relevant mass, formation history, environment, resolution, baryonic treatment, sampling, and selection procedures.

### 2.2 Integral definition and numerical implementation must agree

The published definition uses an integral over cosmic time. Implementations that merely sum MI values across snapshots are dependent on snapshot count and spacing unless the integration rule is explicitly defined. The code, units, snapshot-time mapping and convergence study must implement the same quantity.

### 2.3 Spatial samples are not automatically independent

A density grid contains spatial dependence. KSG estimators applied to grid-cell samples need controls for spatial autocorrelation, finite-sample bias, boundary effects, estimator choice, smoothing and resolution. Tests on independent random variables alone are insufficient.

### 2.4 No current A_c threshold establishes consciousness or moral status

An Assembly Index score is not a validated consciousness detector. Even a future, robust physical result concerning organization or information processing would support only the specific empirical proposition it measures. A separate argument would be required to connect that result to experience, interests, moral status, or legal rights.

This boundary does not dismiss the possibility that future physics, neuroscience or other empirical sciences may provide evidence relevant to the emergence of consciousness. It means the evidence must be assessed on its own merits and must not be assumed in advance from an A_c value.

## 3. Recommended reporting rules

1. Remove unsupported 1,137.753 and invalid 1,011.53 values from current result summaries. Preserve their historical source files with explicit archival warnings.
2. Report 8.62 only as a standardized separation within the specified N=100 synthetic ensemble, accompanied by the finite-sample and model limitations.
3. Keep 87.3 ± 3.2 and z=2.99 historical/provisional until original provenance is reconstructed.
4. Treat z≈3.04 as exploratory and disclose its simulated standard error.
5. Make the A_c implementation time-weighted and unit-consistent before using the integral definition.
6. Validate estimator bias, spatial dependence, clipping effects, sample-size sensitivity, resolution and time-step convergence.
7. Compare against multiple nulls, including physically constrained multi-snapshot simulation data, not only a single synthetic generator.
8. Keep physical findings, computational tests, hypotheses and normative proposals in distinct evidence categories.
9. Do not infer consciousness, agency, personhood or rights from A_c alone.
10. Require independent review before any future high-significance result is described as a detection.

## 4. Source inventory reviewed

- `README.md`
- `docs/README.md`
- `docs/RESULTS_PROVENANCE.md`
- `docs/EVIDENCE_STATUS.md`
- `research/null-ensemble/README.md`
- `research/null-ensemble/cloud9_null_ensemble_v3.py`
- `research/null-ensemble/cloud9_null_ensemble_v3.json`
- `research/validation/README.md`
- `research/null_ensemble_n100.py`
- `cloud9/assembly.py`
- `cloud9_v1_empirical.py`
- `sigma_boost.py`
- `cloud9_assembly/ssbm/stellar_broadening.py`
- `temporal_geometric_assembly.py`
- `ETHICS.md`
- `CAUSAL_SECURITY.md`
- `TOPOLOGY.md`

**Review limitation:** This is a source/documentation inspection. It does not establish that every branch, release, notebook, external Colab, or historical artifact has been audited. No historical result was rerun or independently reproduced as part of this note.
