# Three-estimator KSG calibration protocol

**Status:** draft protocol; implementation manifest and preregistration pending  
**Date opened:** 2026-11-25  
**Scope:** synthetic statistical calibration of the recovered historical v3 KSG-style estimator against complete KSG Type I and Type II implementations  
**Non-goal:** changing the historical v3 estimator, archived ensemble, or archived (A_c) values

## 1. Research question

How do the recovered historical estimator, complete KSG Type I, and complete KSG Type II behave under controlled distributions with known mutual information, especially as sample size, neighbourhood parameter, ties, and quantization change?

The study separates:

1. implementation agreement (whether independent implementations compute the same defined algorithm);
2. statistical calibration (bias, variance, and error relative to known mutual information);
3. robustness under ties/quantization (where continuous-data estimator assumptions may no longer apply);
4. consequences of the historical non-negative clipping operation.

A passing implementation cross-check is not statistical validation. A good Gaussian result is not validation on spatially structured cosmological fields.

## 2. Methods under comparison

All three methods receive exactly the same paired ((X,Y)) observations for each replicate. The complete KSG Type-I and Type-II equations (8) and (9) use natural logarithms and return nats; convert their raw values to bits by dividing by ln(2) for comparison with population MI in bits. The recovered historical function, by contrast, converts its internally computed nat value to bits after applying non-negative clipping, and its public return value is already clipped bits. Do not divide that returned value by ln(2) again. For H, expose the pre-clipping, pre-conversion nat value through a separate diagnostic reproduction, verify that its clipped bit output matches the untouched historical function, and report raw nats, clipped nats, and returned bits distinctly.

### H — historical v3 implementation

Use the recovered historical function unchanged. The audited source is `research/null-ensemble/cloud9_null_ensemble_v3.py`, function `ksg_mi_2d`; its current Git blob SHA on `audit/null-ensemble-v3-provenance` is `32e4b0c97659367470e82512c1571d2a67b478d2`. It builds a joint cKDTree with the L-infinity norm, requests `k+1` neighbours, and takes `dists[:, k]` as the kth radius. It then adds `1e-12` to that radius and performs inclusive `query_ball_point` marginal counts at the same joint radius in X and Y, subtracting one to exclude the anchor. The digamma expression adds one back through `ψ(n_x+1)` and `ψ(n_y+1)`, and uses `ψ(k) - mean[ψ(n_x+1)+ψ(n_y+1)] + ψ(N)`: a historical hybrid with Type-I-style digamma terms and inclusive, epsilon-expanded marginal counts, not complete Type I or Type II. It has no Type-II `-1/k` correction and does not use separate Type-II projected radii. It clips `max(0, mi)` and then divides by `ln(2)`, so the function returns non-negative bits. For `N < k+2`, it returns `0.0` bits. Preserve the source and record its commit and SHA-256. Do not repair, reinterpret, or silently normalize its behaviour inside this arm. cKDTree's exact kth-neighbour tie selection must be characterized by fixtures rather than assumed to be uniquely defined.

For diagnosis, a separate function may reproduce the exact historical calculation while returning the unmodified nat value before clipping/conversion, the clipped nat value, and the final bit value. It must not alter neighbour selection or counts. Verify that its final bit value matches the untouched original function on a frozen test set, including the `N < k+2` early-return case.

### I — complete KSG Type I

Implement the complete Type-I algorithm from Kraskov, Stögbauer & Grassberger (2004), not a hybrid. Use the joint-space maximum-norm kth-neighbour radius ε(i)/2. For each anchor i, count other observations (exclude the anchor itself) with |x_j−x_i| < ε(i)/2 and |y_j−y_i| < ε(i)/2. Denote these counts n_x(i), n_y(i). The paper equation (8) is: I^(1) = ψ(k) + ψ(N) − mean_i[ψ(n_x(i)+1) + ψ(n_y(i)+1)]. The strict marginal boundary is part of this estimator. Exact kth-distance ties have probability zero under the continuous model assumed in the derivation; do not silently resolve them by random jitter. Record raw MI before any optional clipping.

### II — complete KSG Type II

Implement the complete Type-II algorithm from Kraskov et al. (2004). For each anchor, determine ε_x(i)/2 and ε_y(i)/2 as the maximum absolute X and Y projections, respectively, among the k selected joint-space neighbours. These radii can be set by different neighbours. Count observations including the anchor itself satisfying |x_j−x_i| ≤ ε_x(i)/2 and |y_j−y_i| ≤ ε_y(i)/2, respectively. Denote these counts n_x(i), n_y(i). This inclusion is required by the ψ(n_x) and ψ(n_y) terms in Eq. (9); the anchor has zero marginal distance and is therefore counted. The paper equation (9) is: I^(2) = ψ(k) − 1/k + ψ(N) − mean_i[ψ(n_x(i)) + ψ(n_y(i))]. The marginal boundary is inclusive for Type II. The paper notes that additional exact boundary coincidences have zero probability under its continuous-data assumptions; constructed ties must therefore be treated as a separately specified stress/fixture policy, not as ordinary continuous observations. Do not substitute the joint radius for both marginal radii or use only the single kth-neighbour point projections. The production implementation and independent reference must use the same declared anchor-inclusion/exclusion, boundary and tie conventions.

Primary reference: Kraskov, Stögbauer & Grassberger (2004), “Estimating mutual information,” Physical Review E 69, 066138, DOI: 10.1103/PhysRevE.69.066138. Also record the published erratum, Physical Review E 83, 019903 (2011). The paper defines both estimators using natural logarithms, so their native output is in nats.

## 3. Relationship to earlier known-MI calibration work

A related calibration harness exists on the separate evidence-boundary review branch, `review/cloud9-evidence-boundary-audit-2026-11-09`, at `scripts/run_mi_estimator_calibration.py`. Its function `ksg_mi_2d_raw` is explicitly unclipped, but its estimator geometry and equation use the same historical convention described for H: joint L-infinity kth-neighbour radius, addition of `1e-12`, inclusive marginal ball queries, anchor subtraction followed by ψ(n_x+1) and ψ(n_y+1), and conversion from nats to bits. It is therefore **not a complete strict-boundary KSG Type-I implementation** as specified in this protocol. It is an unclipped diagnostic implementation of the historical H convention.

Consequently, results produced by that harness must be attributed to the historical-radius/inclusive-count convention unless a separate source-level audit establishes otherwise. They must not be relabelled as Type-I calibration results merely because the file or result metadata uses the label “KSG-1”. The harness is useful prior known-MI evidence for H's unclipped form, but it does not replace the paired H/I/II comparison defined here. Do not duplicate its Gaussian calibration grid; reuse its established generation and summary design where compatible, while implementing and independently checking the missing complete Type-I and Type-II arms.

## 4. Distribution families

### A. Independent continuous Gaussian (null)

Generate independent standard normal X and Y. The population mutual information is zero. This arm measures finite-sample offset and spread under independence; report negative raw estimates rather than hiding them.

### B. Correlated bivariate Gaussian (known positive MI)

Generate standard normal pairs with Pearson correlation ρ in {0.25, 0.50, 0.75}. The population MI in bits is:

`I(X;Y) = -0.5 log2(1-ρ^2)`.

This is the primary quantitative calibration family.

### C. Invertibly transformed Gaussian copula controls

Apply fixed, strictly monotone transformations independently to X and Y from the correlated Gaussian family (for example, exponential to one margin and a monotone logistic map to the other, with numerically stable generation). Mutual information is invariant under one-to-one transformations. This tests sensitivity to marginal shape without changing the population MI. Transform definitions and numerical clipping, if any, must be frozen.

### D. Quantized/tie-heavy stress controls

Quantize the continuous Gaussian observations using predeclared bin widths and/or finite-level rounding. These data are discrete or mixed, so the continuous KSG estimators do not automatically retain the same target or assumptions. Treat this arm as a robustness/stress diagnostic, not as a direct ranking against the continuous-data truth unless the exact discrete joint distribution and its discrete MI are computed and the estimand is explicitly defined.

Include exact duplicate pairs and constructed kth-boundary ties as implementation unit tests, separately from random quantized samples.

## 5. Sample sizes and neighbourhood values

Proposed primary sample sizes: N in {1,200, 3,000}.  
Proposed k values: {3, 10, 25, 50}; omit any k that violates the minimum sample-size requirements of a method.

The k grid deliberately includes the historical k=3 and larger neighbourhoods because earlier diagnostics showed substantial finite-sample dependence on k. Do not select a best k after seeing confirmatory results.

## 6. Replication and randomization

- Pilot: 20 independent replicates per continuous distribution/sample-size cell.
- Confirmatory: at least 100 fresh replicates per continuous distribution/sample-size cell, using seed values disjoint from all pilot seeds.
- Use a single frozen seed manifest shared by all three estimators.
- Generate each observation array once and pass the identical arrays to H, I, II and their independent references.
- Keep the random-number generator family and version in the manifest.
- Do not discard difficult, negative, tied, or high-error replicates. Any numerical failure is logged and counted; report failure rates by method.

## 7. Independent implementation checks

Before statistical calibration, validate each complete algorithm against an independently written reference on small deterministic arrays.

Required fixtures:
1. continuous sample with no ties;
2. exact duplicate observations;
3. kth-neighbour distance tied across multiple observations;
4. different joint neighbours setting the maximum X and maximum Y projections for Type II;
5. points exactly on each marginal boundary;
6. anchor-point inclusion/exclusion fixture;
7. permutation of row order, which must not change the estimate except where the declared tie-breaking convention explicitly makes a result non-unique.

For small N, use an O(N²) pairwise-distance implementation as the reference. It must not call cKDTree or share helper functions with the production implementation. For each observation, compare selected joint-neighbour distances/sets, marginal radii, integer marginal counts, and final raw MI. Exact agreement is expected for integer counts and defined radii; floating-point tolerances must be declared for distances and final arithmetic.

Do not use one implementation as its own oracle. Keep production and reference code paths separate.

## 8. Outcomes

For each estimator, distribution, N and k, report:

- mean raw MI and standard deviation;
- median, interquartile range and selected quantiles;
- signed bias against population MI;
- RMSE and mean absolute error;
- fraction of negative raw estimates;
- mean after non-negative clipping, reported separately;
- clipping-induced change in bias and RMSE;
- numerical failure rate;
- sensitivity to row permutation and tie handling;
- for quantized controls, tie frequency and the explicitly defined discrete target where available.

For continuous null controls, do not describe the mean estimate as a calibrated false-positive rate: an MI estimator is not itself a hypothesis test. If a separate permutation-based test is later added, preregister its statistic, exchangeability assumptions, permutation count, and type-I error analysis separately.

## 9. Analysis plan

Primary comparisons are paired within each generated dataset. Report paired differences in absolute error and squared error between estimators, with uncertainty intervals obtained by resampling replicate-level paired differences. Use a fixed bootstrap procedure and replicate count in the frozen manifest.

Do not compare raw BIC-style quantities or unrelated datasets here; the estimand is mutual information in bits.

Present estimator-by-N-by-k results, not only a pooled average. Distinguish implementation agreement from estimator accuracy. A method may agree exactly with its independent reference and still be statistically biased.

Do not declare a universal winner based on one Gaussian family or one k value. Treat quantized/tie-heavy cases as a separate stress domain.

## 10. Historical archive protection

- The archived v3 JSON and historical recovered source remain immutable.
- No new estimator may overwrite historical (A_c) or the archived 100-member results.
- Any future cosmological estimator must receive a new name/version and its own outputs.
- Do not recompute or reinterpret the historical significance claim using a replacement estimator without a separately documented analysis.
- The study is synthetic calibration only; it does not establish validity on IllustrisTNG, JWST observations, or temporally dependent spatial fields.

## 11. Preregistration gate

Before confirmatory runs, freeze and commit a machine-readable manifest containing:

- exact distribution parameter rows and transformations;
- exact sample sizes and k values;
- exact pilot and confirmatory seed lists;
- generator family/version and data-generation code hash;
- exact Type-I and Type-II equations, neighbour and count conventions, tie policy, self-count convention, native nats and conversion to bits;
- exact historical source hash and raw/clipped diagnostic procedure;
- deterministic fixture arrays and expected outputs;
- bootstrap method, interval level, resample count and primary paired estimands;
- failure and missing-run handling;
- software versions, numerical tolerances and execution command.

The status may be changed from “draft protocol” to “preregistered” only after this manifest exists and is frozen before confirmatory results are inspected.

## 12. Current status

Draft protocol only. No estimator implementation, calibration run, new statistical result, or change to the historical v3 estimator has been made in this branch. The prior Type-II cKDTree-versus-pairwise cross-check remains a computational agreement result on its tested continuous Gaussian inputs; it is not a replacement for this three-estimator calibration study.
