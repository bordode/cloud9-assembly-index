# Deterministic multi-start test for Poisson PSF deblending

**Experiment ID:** `C9-DEBLENDING-POISSON-MULTISTART-001`  
**Status:** protocol predeclared; implementation and results pending  
**Parent comparison:** [PR #35](https://github.com/bordode/cloud9-assembly-index/pull/35)  
**Branch:** `research/poisson-deterministic-multistart`

## Question

Does the current Poisson detector under-recover sources because its candidate-scene optimizer is sensitive to initialization, rather than because Poisson likelihood/BIC is intrinsically too conservative?

This experiment changes initialization only. It does not tune the BIC penalty, alter the Poisson likelihood, use truth to propose candidates, or change the Gaussian baseline.

## Paired design

For each synthetic observation, run three detectors on the exact same observed count-rate image:

1. **Gaussian baseline:** the existing observation-only Gaussian detector.
2. **Poisson single-start:** the existing Poisson detector, unchanged.
3. **Poisson deterministic multi-start:** same proposal score, proposal order, likelihood, parameterization, bounds, BIC penalty, stopping rule, PSF, and exposure as the single-start detector. At each proposed source count, run a fixed, predeclared set of deterministic position offsets around the observation-derived proposal; jointly refit the complete scene from each start and retain the successful fit with the lowest Poisson deviance.

The multi-start grid is centred on the Pearson-residual matched-filter proposal and uses offsets (in detector pixels):
`(0,0), (+0.35,0), (-0.35,0), (0,+0.35), (0,-0.35), (+0.35,+0.35), (+0.35,-0.35), (-0.35,+0.35), (-0.35,-0.35)`.
All starting positions are clipped to the same physical detector bounds. Existing accepted source coordinates are initialized from the current best scene in every start; only the newly proposed source receives the offset. No random starts are used.

If all multi-start fits fail, the candidate is rejected. Otherwise selection among starts uses only optimizer success and Poisson deviance; BIC is then evaluated exactly as in the single-start detector. Since the parameter count is the same across starts, minimizing deviance and minimizing BIC are equivalent for this comparison.

## Predeclared evaluation grid

- Seven-source synthetic scene, same 21×21 detector and pixel-integrated PSF model as PR #35.
- Geometry scales: 0.8, 1.0, 1.2.
- Exposures: 1.0, 0.1, 0.03.
- Ten trials per cell; 90 paired observations.
- Fresh seed range begins at 20261800 and is disjoint from PR #35's 20261700–20261789 grid.
- The same count realization is passed to all three methods within each trial.
- Truth positions, amplitudes, and source count are withheld from all detectors and used only after detection for common Hungarian assignment scoring within 1 px.

## Primary outcomes

- Mean matched truth sources out of seven.
- Exact seven-source recoveries.
- Missed truth sources and unmatched extra candidates.
- Selected source count.
- Optimizer success/failure and function evaluations.
- Per-proposal deviance and BIC changes.
- Multi-start winner offset and spread of deviance across starts.
- Paired per-trial differences between single-start and multi-start Poisson detectors.

## Interpretation rules

- A multi-start improvement is evidence that initialization/local optimization contributed to the single-start detector's under-recovery on this synthetic design. It does not prove the BIC rule is optimal.
- No improvement suggests that proposal quality, model selection, model mismatch, or other limitations remain plausible bottlenecks; it does not prove initialization never matters.
- More exact recoveries are not sufficient by themselves: misses, false candidates, and localization errors must also be reported.
- No BIC penalty tuning or seed selection based on truth-scored outcomes is permitted.
- The original PR #35 benchmark and results remain unchanged; this is a separate follow-on experiment.

## Limitations

Synthetic point sources only; fixed PSF family/width, detector size, source fluxes, and constant background. This experiment tests one deterministic local-start grid, not all possible optimizers or initializations. Findings will not establish performance on real astronomical images.


## Results — first 90-trial run

**Workflow:** [run 42282527270](https://github.com/bordode/cloud9-assembly-index/actions/runs/42282527270)  
**Code commit tested:** `cb33a78160ef1b215885f4616f0d270bfaa0b710`  
**Artifact:** `deblending-poisson-multistart-comparison`  
**Artifact SHA-256:** `750033671da9b8d4d0f99cc0a7834fa71b6ba6332fe2212ce4180ebf1f981926`

The test suite passed, the full 90-trial three-way comparison completed, and the artifact uploaded successfully.

### Aggregate results

| Metric | Gaussian baseline | Poisson single-start | Poisson nine-start |
|---|---:|---:|---:|
| Mean matched truth sources (of 7) | 3.68 | 3.11 | 3.16 |
| Mean missed truth sources | 3.32 | 3.89 | 3.84 |
| Mean selected candidate count | 4.77 | 3.43 | 3.47 |
| Mean unmatched candidates | 1.09 | 0.32 | 0.31 |
| Exact seven-source recoveries | 5/90 | 1/90 | 1/90 |
| Trials with optimizer success | 90/90 | 90/90 | 90/90 |

### Paired Poisson comparison

- Nine-start matched more truth sources in 3/90 trials.
- Single-start matched more in 0/90.
- The methods tied in 87/90.
- Mean matched-source difference (nine-start minus single-start): **+0.044 sources/trial**.
- Exact seven-source recoveries did not change: **1/90 for each method**.
- The selected source count differed in three trials; those changes did not alter the exact-recovery count.

The multi-start method therefore produced a small positive paired difference, but not a practically meaningful improvement in this grid. It did not close the recovery gap with the Gaussian baseline.

### Initialization diagnostics and cost

There were 402 proposed-source fitting steps in the multi-start records. Each evaluated all nine prescribed initializations: **3,618 initialization attempts**, all reported successful optimizer status.

For most proposed-source steps, the deviance spread across starts was very small (median approximately (1.28\times10^{-7})). The 99th percentile was larger (approximately 73.1), and the maximum was approximately 3,064.7, so a small number of proposals were meaningfully start-sensitive even though the selected-scene recovery metrics barely changed.

The winning offset was not concentrated on one grid point; all nine offsets won at least some proposal fits. This confirms that different starts can win locally, but it does not show that those local differences materially change source recovery.

The artifact counts initialization attempts but does not aggregate function evaluations across every start. The benchmark therefore establishes a ninefold number of optimizer attempts per proposal, not an exact ninefold wall-clock or function-evaluation cost.

### Interpretation

This result weakens the hypothesis that ordinary local initialization sensitivity is the main cause of the Poisson detector's under-recovery in this synthetic design. It does not show that initialization never matters: the deviance spread has a long tail, and three trials changed matched-source count in the multi-start method's favour.

The more important unresolved bottlenecks remain the observation-derived proposal sequence, greedy source addition, the approximate Poisson BIC decision, and the fixed model assumptions. This experiment does not isolate which of those is responsible.

The Gaussian baseline still recovers more truth sources on average (3.68 versus 3.16 for multi-start Poisson), at the cost of more unmatched candidates. This is a tradeoff, not an unqualified Gaussian win.

### Limitations and next experiment

This is one 90-trial synthetic grid, one fixed nine-offset pattern, one detector/PSF/source configuration, and one fresh seed range. The Poisson detector still uses greedy proposals and the same approximate BIC rule. Optimizer success is not evidence of a correct scene.

The next discriminating experiment should preserve the Poisson likelihood and fitting machinery while testing the proposal/model-selection bottleneck separately. In particular, log the complete candidate sequence and BIC decisions, then test a predeclared alternative proposal strategy or a controlled source-count decision diagnostic without tuning against truth. Do not simply expand the start grid: the current result gives little evidence that more local starts are the highest-value next step.
