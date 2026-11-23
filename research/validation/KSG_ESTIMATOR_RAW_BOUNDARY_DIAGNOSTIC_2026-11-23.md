# Recovered v3 KSG: raw output and radius-boundary sensitivity

**Date:** 2026-11-23  
**Workflow:** [45095297552](https://github.com/bordode/cloud9-assembly-index/actions/runs/45095297552)  
**Commit:** `809be9b7fc51c99602a9bd0265977efa55657d71`  
**Artifact:** `v3-full-ensemble-reproduction`, ID `14782972673`  
**Artifact SHA-256:** `489a8554309cefd03d569a1dbae25568f12cab87f9bfbfe2f0262d122e2b6c47`  
**SciPy:** 1.18.1

## Purpose and method

This diagnostic reconstructs the recovered v3 KSG digamma expression in a separate helper, without the historical function's `max(0, MI)` clipping. The recovered source file and historical estimator were not modified.

Two marginal-radius conventions were compared on identical deterministic samples:

1. **Current recovered convention:** joint kth-neighbour radius plus (10^{-12}), then inclusive `query_ball_point` counts.
2. **Strict-boundary sensitivity variant:** `nextafter(kth_radius, -infinity)`, so marginal points exactly on the kth-radius boundary are excluded.

The study used 20 replicates, k=3, N=1,200 and 3,000, and the same Gaussian and sinusoidal sample constructions used in the reference cross-check. The strict variant is a sensitivity test, not yet declared the corrected or canonical implementation.

## Main result: the boundary convention changes every replicate

For all four sample conditions at both sample sizes, the strict and current estimates differed in all 20 replicates. Every sample point had at least one marginal neighbour count changed by the boundary rule. On average, the current inclusive convention counted approximately 0.5 additional neighbours in each marginal dimension per point.

### Gaussian rho=0.5 paired samples

Analytic Gaussian MI: **0.207519 bits**.

| N | Convention | Mean (bits) | Median (bits) | Empirical 2.5–97.5% range |
|---:|---|---:|---:|---:|
| 1,200 | Current inclusive + epsilon | 0.1808 | 0.1796 | 0.1194–0.2482 |
| 1,200 | Strict below kth radius | 0.2151 | 0.2145 | 0.1519–0.2833 |
| 3,000 | Current inclusive + epsilon | 0.1830 | 0.1766 | 0.1508–0.2230 |
| 3,000 | Strict below kth radius | 0.2047 | 0.1979 | 0.1723–0.2450 |

The strict-boundary variant moves the estimates substantially closer to the analytic Gaussian value in this experiment. At N=1,200 its mean is 0.0076 bits above the analytic value; at N=3,000 its mean is 0.0028 bits below it. The current inclusive convention is lower by about 0.027–0.031 bits at the median.

Mean marginal count differences (current minus strict) were approximately 0.498 in X and 0.502 in Y at N=1,200, and 0.498 in X and 0.502 in Y at N=3,000.

### Shuffled Gaussian controls: raw unclipped values

| N | Convention | Mean (bits) | Median (bits) | Fraction negative |
|---:|---|---:|---:|---:|
| 1,200 | Current inclusive + epsilon | -0.0283 | -0.0227 | 75% |
| 1,200 | Strict below kth radius | 0.0038 | 0.0092 | 35% |
| 3,000 | Current inclusive + epsilon | -0.0222 | -0.0225 | 95% |
| 3,000 | Strict below kth radius | -0.0020 | -0.0021 | 60% |

This shows why clipping matters: the historical estimator converts negative estimates to zero. The raw current-convention shuffled estimates are predominantly negative, whereas the strict-boundary variant is centred much closer to zero in these tests. Negative finite-sample estimates are not themselves an error; mutual information is nonnegative in population, while an estimator can fluctuate below zero.

### Nonlinear sinusoidal stress test

| N | Convention | Paired mean (bits) | Paired median (bits) |
|---:|---|---:|---:|
| 1,200 | Current inclusive + epsilon | 1.0803 | 1.0887 |
| 1,200 | Strict below kth radius | 1.1265 | 1.1356 |
| 3,000 | Current inclusive + epsilon | 1.0927 | 1.0978 |
| 3,000 | Strict below kth radius | 1.1220 | 1.1270 |

No analytic MI is asserted for this nonlinear construction. The strict-boundary sensitivity variant is consistently higher in this stress test as well. Shuffled raw estimates remain distributed around zero under both conventions, with finite-sample variation.

The 2.5th and 97.5th percentiles in the artifact are empirical quantiles across 20 replicate estimates, not confidence intervals for a population parameter.

## Interpretation

1. **Boundary handling is a leading explanation for the Gaussian shortfall.** The radius convention alone shifts the paired Gaussian estimate by approximately 0.03–0.035 bits, close to the shortfall previously observed against analytic Gaussian MI and scikit-learn.
2. **This does not yet certify the strict variant.** Its closeness to the analytic Gaussian value in this small grid is evidence for further investigation, not proof of correctness or unbiasedness.
3. **The source of the shift is explicit.** With a max-norm joint distance, at least one coordinate of the kth neighbour lies on the kth-radius boundary. Inclusive marginal counts plus epsilon include boundary points; the strict variant excludes them. The observed average count change is about half a neighbour in each marginal dimension.
4. **Clipping masks negative raw estimates.** The current shuffled raw means are negative, but the historical function clips each estimate to zero before returning it. This materially alters the null distribution.
5. **The nonlinear case is only a sensitivity stress test.** No analytic truth is asserted for it.
6. **Domain validity remains untested.** These are iid synthetic samples, not spatially structured cosmological fields, temporally dependent snapshots, or TNG data.

## Required next steps

1. Check the exact inequality and count definitions against the original KSG Algorithm 1 and relevant maintained implementations; document the estimator variant precisely.
2. Add small hand-constructed samples that make boundary inclusion/exclusion and self-count handling directly inspectable.
3. Add quantized and tie-heavy samples, where multiple points can lie exactly on the kth-radius boundary.
4. Expand the Gaussian grid over N, rho and k, and report raw and clipped estimates separately.
5. If a correction is justified, implement it as a separately versioned estimator and rerun the synthetic ensemble under the new method. Do not alter the historical v3 function or archived JSON.

## Claim boundary

This diagnostic identifies radius-boundary handling as a plausible and quantitatively important source of the recovered estimator's Gaussian calibration discrepancy. It does not by itself establish which convention should be used, certify the KSG implementation, or validate Cloud-9's cosmological interpretation. The historical estimator remains unchanged.
