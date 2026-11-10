# Research Protocol: Estimator Calibration and Temporal-Null Falsification

**Date:** 2026-11-09  
**Status:** Proposed preregistered computational protocol; initial Gaussian calibration and paired KSG convention audit executed; further validation pending  
**Purpose:** Determine what the Cloud-9 v3 temporal mutual-information statistic measures under controlled conditions before applying it to physical simulation histories.

## 1. Research question

Can the current KSG-style estimator and the proposed time-integrated statistic distinguish a specified assembly-like temporal process from ordinary persistence, shared initial conditions, and spatially correlated stochastic evolution?

The null hypothesis is not “the universe is random.” The operational null is narrower:

> Given matched spatial statistics, shared initial conditions where appropriate, temporal autocorrelation, and the same observation/sampling pipeline, the proposed statistic does not reliably distinguish the assembly-like process from ordinary correlated evolution.

A positive result would establish discrimination only for the tested generative families. It would not establish a cosmological detection or consciousness.

## 2. Freeze the analysis before simulation

Before generating the calibration data, record:
- immutable commit SHA and environment lock;
- exact estimator implementation and k;
- spatial grid, sample locations and boundary handling;
- normalization and clipping choices;
- time points and integration rule;
- primary endpoint and secondary diagnostics;
- number of independent realizations and random seed list;
- all exclusion, failure and convergence rules.

Do not tune the estimator or choose thresholds on the final held-out seeds.

## 3. Estimator calibration independent of halo simulation

### 3.1 Known-information controls

Generate paired scalar samples with known population mutual information:
- independent Gaussian variables (MI = 0);
- bivariate Gaussian variables with predeclared correlations, using (I=-\frac12\log_2(1-r^2));
- nonlinear dependent pairs with known or independently numerically evaluated MI.

For each condition, vary sample size (e.g. 64, 128, 256, 512, 1,200), k (2, 3, 5, 10), marginal distributions and noise. Report bias, variance, median absolute error, interval coverage and fraction of estimates clipped to zero.

The primary estimator should be evaluated both with the current nonnegative clipping and with an unclipped diagnostic. Do not silently treat clipped estimates as unbiased.

### 3.2 Spatial dependence controls

Create 2-D/3-D random fields with controlled correlation lengths and matched power spectra. Sample the same fixed spatial locations used by the v3 design. Compare:
- independent spatial samples;
- spatially correlated samples;
- block subsampling at several separations;
- spatial block bootstrap uncertainty.

The effective sample size must not be assumed to equal the raw count of 1,200 locations. Quantify how bias and uncertainty change with spatial correlation length and sampling separation.

## 4. Temporal process controls

Use matched spatial fields and predeclared temporal processes:

| Control | Construction | What it tests |
|---|---|---|
| T0 Independent | Independent spatial field each time | Estimator baseline near zero temporal dependence |
| T1 Shared field | Same base field with known deterministic scaling | Dependence caused by shared initial structure |
| T2 AR process | Spatially correlated innovations with known temporal coefficient | Ordinary stochastic temporal persistence |
| T3 Smooth deterministic evolution | Known smooth deformation/growth without a special assembly event | Dependence due to smooth evolution |
| T4 Assembly-like intervention | Predefined localized structure-growth event added to matched baseline | Whether statistic detects the specified intervention |
| T5 V3 reproduction | Reproduce current generator exactly | Benchmark against existing synthetic design |

For T0–T4, match spatial power spectrum, marginal distributions, sample geometry, time grid and signal-to-noise as closely as possible. State where exact matching is impossible.

The T4 intervention must be defined before simulation and must not be tuned to maximize the MI statistic. Include negative controls in which the intervention is absent or its timing is randomized.

## 5. Ablation plan for the existing v3 generator

Run the existing v3 construction with one feature removed at a time:
1. shared `delta_unit` component;
2. correlated `delta_ss_corr` component;
3. collapse trigger and NFW-like profile blending;
4. merger perturbations;
5. substructure;
6. gas contribution;
7. fixed spatial sample locations (replace with independent locations only as a diagnostic, not as the primary paired design).

Ablation results identify which design features drive temporal MI. They do not establish that any component is physically realistic.

## 6. Time integration and units

The source currently computes an unweighted sum of adjacent-step MI values. This is not the stated time integral when intervals are unequal.

Define the intended statistic explicitly. If (I_i) is the MI estimate at interval midpoint (t_i^*=(t_i+t_{i+1})/2), a first-order interval sum is:

[
A_c^{(1)}=\sum_i I_i\,(t_{i+1}-t_i)
]

This has units of bits·Gyr when time is measured in Gyr. If a dimensionless or bits-only index is desired, specify the normalization timescale in advance.

Compare this with:
- the legacy unweighted sum (reported only as a distinct statistic);
- trapezoidal integration if MI is defined at time nodes rather than intervals;
- alternative snapshot grids with matched endpoints.

Require convergence under time-grid refinement. Do not retrofit a corrected value to the historical target without reconstructing its original density history and applying the same definition to target and null.

## 7. Statistical analysis plan

Primary outcomes:
- estimator bias and variance under known-MI controls;
- false-positive rate for T0–T3 under a predeclared threshold;
- sensitivity and specificity for the predeclared T4 intervention;
- calibration of uncertainty intervals under spatial dependence;
- difference in A_c between T4 and each matched null, with paired intervals where seeds/design permit.

Report raw distributions, effect sizes, confidence intervals, exceedance counts and all failed runs. Do not convert a small finite-ensemble exceedance count into an extreme Gaussian sigma value. If a tail model is used, justify it and show sensitivity to alternatives.

Use independent training/calibration seeds and a held-out evaluation set. Predeclare sample size based on precision/power simulations, not on an expected significance outcome.

## 8. Pass/fail criteria

The estimator is not ready for physical interpretation if any of the following hold:
- material positive bias under known-zero MI after the intended correction;
- confidence intervals materially under-cover under spatial dependence;
- false-positive rates exceed the predeclared tolerance for T0–T3;
- results change qualitatively with reasonable k, sample size or block separation;
- temporal-grid refinement does not converge;
- T4 cannot be distinguished from matched T1–T3 controls under held-out seeds.

A pass means only that the method discriminates the specified synthetic processes under tested conditions. Physical interpretation still requires traceable multi-snapshot simulations and external review.

## 9. Reproducibility outputs

Each run should produce:
- machine-readable configuration and seed manifest;
- raw per-realization MI time series and integrated statistics;
- estimator calibration tables;
- temporal-process labels and intervention parameters;
- paired comparison summaries and confidence intervals;
- software/environment metadata;
- plots of calibration, residuals, distributions and convergence;
- a concise limitations record.

## 10. Explicit non-claims

This protocol does not assume that:
- high mutual information means non-stochastic assembly;
- temporal persistence is anomalous;
- an assembly-like synthetic intervention represents real cosmological physics;
- information integration is a measure of consciousness;
- any (A_c) threshold establishes subjective experience, agency or moral standing.

The protocol is designed to falsify overinterpretation as readily as it is designed to identify a useful statistic. A null or negative result is a valid and informative outcome.


## Implementation status — first calibration harness

A standalone known-MI calibration harness has been added at
`scripts/run_mi_estimator_calibration.py`, with focused tests in
`tests/test_mi_estimator_calibration.py`.

The first implementation covers independent and correlated bivariate Gaussian
controls, using the exact reference
(I(X;Y)=-\frac{1}{2}\log_2(1-\rho^2)). It reports the raw estimate and
the zero-clipped estimate side by side, including bias, RMSE, dispersion,
negative-estimate fraction, clipping fraction, and a replicate-level
bootstrap interval for mean bias. The neighbourhood-count radius follows the
existing v3 implementation (`epsilon = kth_distance + 1e-12)); the historical
v3 source itself remains unchanged.

Default run:

```bash
python scripts/run_mi_estimator_calibration.py
```

This produces `mi_estimator_calibration.json`. The default grid is 100
independent replicates for each combination of sample size 64, 128, 256, 512,
and 1200; k=2, 3, 5, and 10; and correlation 0, 0.2, 0.5, and 0.8. This is
the independent-observation stage only. Spatially correlated fields, nonlinear
controls, and temporal nulls remain unimplemented and must not be inferred
from this first harness.

A dedicated workflow, `.github/workflows/mi-estimator-calibration.yml`, now
runs the focused calibration tests and the full 100-replicate Gaussian grid
on relevant review-branch pushes and pull-request updates. It uploads the
machine-readable JSON result as a 90-day workflow artifact. The workflow uses
the repository's pinned Python dependency constraints and a fixed seed.

**Status:** harness, tests, and automated calibration workflow added.
Execution results and estimator-adequacy assessment remain pending. No
calibration result or claim of estimator adequacy is made here.


## First calibration results — 2026-11-10

The first 100-replicate Gaussian known-MI grid has completed successfully:
80 conditions and 8,000 replicate estimates. The full artifact is attached
to GitHub Actions workflow run #6. A descriptive analysis is recorded in
`docs/research/KNOWN_MI_GAUSSIAN_KSG_CALIBRATION_RESULTS_2026-11-10.md`.

The first result is a caution, not a pass: the raw estimator showed negative
finite-sample bias across the tested Gaussian conditions. Zero-clipping
substantially changed the null distribution by setting roughly 85–90% of
independent-control estimates to exactly zero. At N=1,200, residual mean raw
bias across k was approximately -0.028 bits for rho=0 and remained negative
for all tested nonzero correlations. These findings are limited to the
independent-observation bivariate Gaussian grid.

**Status:** initial Gaussian calibration executed; estimator adequacy not
established. Before spatial/temporal controls, audit the strict/inclusive
marginal-neighbour counting convention and radius offset, add nonlinear and
non-Gaussian known-MI controls, and implement interval-coverage evaluation.


## Paired KSG convention audit — execution status (2026-11-10)

The paired Gaussian audit has now completed: 80 conditions, 100 paired
replicates per condition (8,000 paired comparisons). It compares the
historical kth-radius-plus-`1e-12`/inclusive-count convention against an
uninflated-radius/strict-count convention. These are two combined
implementation choices; the experiment does not isolate the radius-offset
effect from the marginal-boundary inclusion effect.

On this tested grid, the strict convention had lower RMSE in 79 of 80
condition cells and lower absolute bias in 79 of 80. Mean strict bias was
close to zero across most sample sizes, but a notable exception occurred at
N=1,200, k=10, rho=0.8, where the historical convention was already more
accurate. This result supports further evaluation of the strict convention
as a candidate; it does not establish universal superiority or justify
changing the historical v3 estimator or correcting archived outputs.

The two workflow runs on commit
`b8b68b57164166ff5b87068a57ce0b2c3c1af3cd` produced byte-identical
calibration and audit JSON artifacts. This confirms deterministic output
under the same seed and environment, not independent statistical
replication.

**Remaining gates:** nonlinear and non-Gaussian known-MI controls; interval
coverage; an experiment separating radius-offset and strict/inclusive
counting effects; explicit tie/duplicate handling beyond the current
zero-radius guard; then spatial-dependence and temporal-null controls.


## Nonlinear and non-Gaussian known-MI controls — completed (2026-11-10)

The expanded workflow #21 completed successfully on commit
`9de5ec07dc975a3a00be3a26558f8c2715905c31`. In addition to rerunning the
Gaussian grid and paired boundary audit, it ran 16,000 estimates over two
known-MI transformed-Gaussian families (80 conditions × 100 replicates per
family): nonlinear sinh/exp marginals and uniform marginals with a Gaussian
copula. Coordinate-wise strictly monotone invertible transformations
preserve the analytic population MI.

Mean raw RMSE declined with sample size in both families. At N=1,200, the
mean RMSE across k and rho was approximately 0.0334 bits for the nonlinear
family and 0.0357 bits for the copula family. Bias differed between families:
the nonlinear family approached zero aggregate bias, while the copula family
showed a small positive aggregate bias at larger N. Larger k reduced average
RMSE in these grids but increased negative bias in the nonlinear family,
illustrating a bias/variance trade-off rather than a universal k optimum.

Zero-clipping produced positive mean bias under known-zero MI (approximately
+0.023 to +0.025 bits averaged over N and k at rho=0), with about half of
null estimates clipped to zero. A clipped mean near zero is therefore not a
valid calibration argument.

**Status:** the strict KSG candidate has now passed software execution and
finite-output checks on these two transformed-Gaussian families. This is
limited synthetic calibration evidence, not proof of universal unbiasedness
or validity for arbitrary non-Gaussian data. No spatial or temporal
dependence is included. No individual-estimate interval-coverage study has
been completed. Historical v3 and archived outputs remain unchanged.

**Next gates remain:** (1) empirically evaluate interval coverage using
independent datasets and predeclared intervals; (2) isolate radius offset
from strict/inclusive marginal counting; (3) specify and test tie/duplicate
handling; (4) assess spatially correlated fields and effective sample size;
(5) test temporal null processes T0–T5, with held-out seeds and ablations.
Only after those stages should physical-data validation be considered.
