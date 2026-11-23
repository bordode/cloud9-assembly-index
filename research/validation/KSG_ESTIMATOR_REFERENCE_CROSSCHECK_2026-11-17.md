# Recovered v3 KSG: independent reference implementation cross-check

**Date:** 2026-11-17  
**Workflow:** [43987689799](https://github.com/bordode/cloud9-assembly-index/actions/runs/43987689799)  
**Commit:** `2c5e1ad255bee95206fdcf3bbb57e965155f992e`  
**Artifact:** `v3-full-ensemble-reproduction`, ID `14286416114`  
**Artifact SHA-256:** `9355bc6abf1985ae0c9d62c4c2f67efbabfbeaa53f3d6404812a523a0e5f9090`  
**Reference version:** scikit-learn 1.9.1

## Purpose and design

The unchanged recovered v3 `ksg_mi_2d` implementation was compared against scikit-learn's `mutual_info_regression` on identical deterministic samples. Both outputs are expressed in bits. The comparison uses continuous features, `n_neighbors=3`, sample sizes 1,200 and 3,000, and 20 replicates per condition.

Conditions include bivariate Gaussian samples with correlation 0.5, shuffled versions of those samples, a nonlinear sinusoidal dependence construction, and shuffled versions of that construction.

The scikit-learn method is a separate maintained nearest-neighbour mutual-information implementation related to KSG. It is not assumed to use convention-identical neighbour counting, radius handling, or finite-sample corrections. It is therefore an independent cross-check, not ground truth.

## Results

### Gaussian dependence, analytic reference = 0.207519 bits

| N | Estimator | Mean (bits) | Median (bits) | Empirical 2.5–97.5% range |
|---:|---|---:|---:|---:|
| 1,200 | recovered v3 | 0.1808 | 0.1796 | 0.1194–0.2482 |
| 1,200 | scikit-learn | 0.2154 | 0.2146 | 0.1516–0.2840 |
| 3,000 | recovered v3 | 0.1830 | 0.1766 | 0.1508–0.2230 |
| 3,000 | scikit-learn | 0.2046 | 0.1971 | 0.1724–0.2446 |

The recovered-v3 minus scikit-learn paired difference had a median of -0.0344 bits at N=1,200 and -0.0217 bits at N=3,000. The recovered-v3 medians were also below the analytic Gaussian value by 0.0279 and 0.0309 bits, respectively.

### Shuffled Gaussian controls

| N | Estimator | Mean (bits) | Median (bits) | Empirical 2.5–97.5% range |
|---:|---|---:|---:|---:|
| 1,200 | recovered v3 | 0.0014 | 0.0000 | 0.0000–0.0150 |
| 1,200 | scikit-learn | 0.0104 | 0.0020 | 0.0000–0.0475 |
| 3,000 | recovered v3 | 0.0032 | 0.0000 | 0.0000–0.0179 |
| 3,000 | scikit-learn | 0.0111 | 0.0037 | 0.0000–0.0382 |

The recovered implementation clips negative raw estimates to zero, which contributes to its zero-heavy shuffled distribution. The difference between estimators on shuffled data is not itself evidence of bias because both estimator conventions and clipping behaviour differ.

### Nonlinear sinusoidal stress test

| N | Estimator | Mean (bits) | Median (bits) | Empirical 2.5–97.5% range |
|---:|---|---:|---:|---:|
| 1,200 | recovered v3 | 1.0811 | 1.0795 | 1.0399–1.1324 |
| 1,200 | scikit-learn | 1.1119 | 1.1109 | 1.0572–1.1666 |
| 3,000 | recovered v3 | 1.0789 | 1.0785 | 1.0494–1.1142 |
| 3,000 | scikit-learn | 1.1155 | 1.1185 | 1.0819–1.1473 |

No analytic MI is asserted for this nonlinear construction. The two estimators produce comparable-scale estimates, with the recovered implementation lower in these runs. This is a stress comparison only.

The reported 2.5th and 97.5th percentiles are empirical quantiles across 20 replicate estimates, not confidence intervals for a population parameter.

## Interpretation

1. The reference comparison confirms a systematic numerical difference between the recovered implementation and scikit-learn on the tested paired Gaussian samples.
2. The recovered estimator's Gaussian median is below the analytic value in both sample-size conditions. Increasing N from 1,200 to 3,000 did not remove the observed shortfall in this finite experiment.
3. Scikit-learn's estimates are closer to the analytic value in these runs, but this does not prove that scikit-learn is unbiased or that its convention is the correct match for the historical implementation.
4. The comparison does not isolate the source of the difference. Candidate factors include KSG estimator variant, inclusive versus strict marginal radius counts, epsilon handling, self-count conventions, finite-sample correction, and scikit-learn's continuous-feature noise regularization.
5. The recovered implementation's nonnegative clipping changes the shuffled-null distribution. Raw unclipped values are needed to quantify this effect directly.
6. Neither estimator is certified for spatially structured cosmological density fields, temporally dependent snapshots, or IllustrisTNG data.

## Next diagnostic priorities

1. Reproduce the recovered estimator's raw, unclipped KSG expression in a separate diagnostic helper; do not modify the historical function.
2. Compare marginal-neighbour count conventions (strict radius versus inclusive radius plus epsilon) against explicit small-sample calculations and a documented KSG variant.
3. Run a broader Gaussian grid over N, correlation and k, with more replicates and raw as well as clipped outputs.
4. Add tie-heavy and quantized inputs to test radius-boundary handling.
5. Keep any corrected estimator as a separately versioned method with its own tests; do not rewrite historical outputs.

## Historical reproduction status

The same workflow passed the strict 100-member archived ensemble reproduction: all 100 members matched, including all 15 MI values per member, across all nine comparison fields at tolerance 1e-10. This computational reproducibility result remains distinct from estimator validity.

## Claim boundary

The recovered implementation detects the tested paired dependencies relative to shuffled controls, but it exhibits a persistent quantitative difference from the analytic Gaussian MI and from the independent scikit-learn implementation. The cross-check narrows the question; it does not settle estimator correctness. The KSG estimator remains **not validated or certified** for Cloud-9's cosmological application.
