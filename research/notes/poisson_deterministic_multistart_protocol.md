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
