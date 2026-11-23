# MI estimator calibration follow-up — workflow run #56 (2026-11-20)

## Status and scope

This note records the completed follow-up calibration artifact from GitHub Actions workflow run **#56** in `bordode/cloud9-assembly-index`. The run completed successfully and its six JSON result files were inspected: each parsed successfully and all numeric outputs checked were finite.

Run #56 is a computationally successful calibration and diagnostic run. It does **not** validate the estimator for general spatial data, establish nominal interval coverage, or provide evidence of cosmological detection, non-stochastic assembly, consciousness, agency, or subjective experience.

## Run configuration and artifact checks

The artifact contains:

- `mi_estimator_calibration.json`
- `mi_nongaussian_calibration.json`
- `ksg_boundary_convention_audit.json`
- `ksg_boundary_factorial_audit.json`
- `ksg_boundary_distance_sensitivity.json`
- `mi_subsampling_coverage_screening.json`

All six files parsed as JSON. Numeric values inspected were finite. The coverage harness recorded per-outer-dataset seeds, interval endpoints, coverage flags, and failure status. Four coverage conditions each had 10 valid independent outer datasets and zero interval-construction failures.

## Known-MI calibration findings

### Gaussian controls

The raw KSG estimates retained negative finite-sample bias throughout the tested Gaussian grid. Bias and RMSE generally decreased as sample size increased, but bias remained negative at N=1,200:

| N | Independent bias | Correlated bias | Independent RMSE | Correlated RMSE |
|---:|---:|---:|---:|---:|
| 64 | -0.1215 | -0.1532 | 0.1510 | 0.1975 |
| 128 | -0.0815 | -0.0958 | 0.1077 | 0.1370 |
| 256 | -0.0611 | -0.0637 | 0.0801 | 0.0983 |
| 512 | -0.0448 | -0.0407 | 0.0600 | 0.0663 |
| 1,200 | -0.0277 | -0.0257 | 0.0393 | 0.0449 |

These values support a finite-sample-bias characterization for the tested Gaussian controls, not a universal bias correction.

### Nonlinear and non-Gaussian controls

Two coordinate-wise invertible transformed-Gaussian families were tested. Their population MI is preserved by the transformations. Raw RMSE declined with N in both families:

| N | Nonlinear bias | Nonlinear RMSE | Gaussian-copula uniform bias | Gaussian-copula uniform RMSE |
|---:|---:|---:|---:|---:|
| 64 | -0.0464 | 0.1341 | -0.0066 | 0.1328 |
| 128 | -0.0201 | 0.0984 | +0.0058 | 0.0967 |
| 256 | -0.0117 | 0.0719 | +0.0070 | 0.0720 |
| 512 | -0.0022 | 0.0494 | +0.0059 | 0.0522 |
| 1,200 | -0.0001 | 0.0334 | +0.0051 | 0.0357 |

This is evidence limited to these two synthetic families. It does not establish performance on general spatial, astrophysical, or temporally dependent data.

## Subsampling interval-coverage screen: not validated

The screening configuration was deliberately small:

- n=256, k=3, subsample size b=84 (floor of n^0.8);
- 20 without-replacement subsamples per outer dataset;
- 10 independent outer datasets per condition;
- two transformed-Gaussian families and correlations 0 and 0.5;
- raw strict KSG intervals designated primary; zero-clipped intervals diagnostic only.

Raw strict interval coverage across the 10 independent outer datasets was:

| Control family | Correlation | 90% nominal coverage | 95% nominal coverage |
|---|---:|---:|---:|
| Monotone nonlinear | 0.0 | 60% (6/10) | 60% (6/10) |
| Monotone nonlinear | 0.5 | 70% (7/10) | 70% (7/10) |
| Uniform Gaussian copula | 0.0 | 80% (8/10) | 80% (8/10) |
| Uniform Gaussian copula | 0.5 | 70% (7/10) | 80% (8/10) |

The Wilson 95% intervals are necessarily wide with only 10 independent outer datasets: 6/10 gives approximately [0.313, 0.832], 7/10 gives [0.397, 0.892], and 8/10 gives [0.490, 0.943]. Similar 90% and 95% coverage counts in several cells are not evidence that the intervals are calibrated.

The 20-subset quantile resolution is especially coarse: the expected number of subset draws in each tail is 1 at nominal 90% and 0.5 at nominal 95%. There were zero interval-construction failures, but successful construction is not evidence of correct coverage. Zero-clipped intervals sometimes produced higher coverage, but clipping changes the estimator/interval behavior and remains diagnostic only.

**Conclusion:** this is a runtime and method screen, not a coverage validation. The preregistered larger study (100 independent outer datasets × 200 subsamples, across the specified conditions) remains the next coverage-validation gate. Do not silently substitute this screening run for that design.

## KSG boundary-convention diagnostics

- The paired convention comparison found lower RMSE and lower absolute bias for the uninflated-radius/strict-count candidate in 79 of 80 tested Gaussian condition cells; one exception occurred at N=1,200, k=10, rho=0.8.
- This paired comparison changed radius inflation and strict/inclusive counting together, so it cannot isolate the contribution of either change.
- In the nominal 2×2 factorial audit, three variants had identical summary values across the tested grid. The offset and inclusion effects were therefore aliased in that design; equal effects must not be interpreted as independently identified causal contributions.
- The deterministic boundary-distance sensitivity test separated the four counting conventions for radius 1.0 and offset 1e-12: uninflated strict=1, uninflated inclusive=2, inflated strict=4, inflated inclusive=5. This is a floating-point geometry diagnostic, not estimator-bias or interval-coverage evidence.

## Interpretation and next gates

1. Keep historical v3 code and archived outputs unchanged; this run authorizes no retroactive correction.
2. Retain strict KSG as a candidate estimator, not a validated replacement.
3. Run the preregistered coverage design with substantially more independent outer datasets and subsamples; report failures and uncertainty, not only point coverage.
4. Investigate whether the subsampling interval assumptions are appropriate for a non-smooth KSG estimator before treating nominal coverage as expected.
5. After coverage work, continue with spatial dependence and temporal-null falsification only under the protocol's predeclared controls and failure criteria.
6. Keep any future scientific claims bounded by the tested synthetic families and actual data provenance.

## Provenance

- Repository: `bordode/cloud9-assembly-index`
- Workflow: calibration run #56
- Artifact files: six JSON outputs listed above
- Interpretation status: computational run complete; synthetic calibration evidence; coverage screen inconclusive; no external independent reproduction.

