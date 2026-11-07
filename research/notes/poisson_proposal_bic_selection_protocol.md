# Poisson proposal-pool and BIC selection experiment

## Research question

When the observation-only Poisson detector misses real sources, is the limiting factor (a) the single highest Pearson-residual matched-filter proposal, or (b) the unchanged Poisson BIC acceptance rule?

The previous deterministic multi-start experiment found that nine local initializations barely changed recovery. This experiment changes proposal selection, not the likelihood or source-count penalty.

## Predeclared comparison

Three methods receive the same count observation in each trial:

1. Existing Gaussian baseline.
2. Existing Poisson detector: one highest-scoring Pearson-residual proposal, one initialization, existing Poisson deviance fit and BIC acceptance.
3. Poisson top-five/BIC proposal selection: obtain the five highest spatially separated local peaks in the same Pearson-residual matched-filter score map; fit each candidate location once using the same complete-scene Poisson deviance optimizer; select the successful fit with lowest BIC; then apply the same unchanged BIC acceptance threshold.

The top-five method is observation-only. It does not inspect truth, source labels, amplitudes, or source count. It is intentionally more computationally expensive; report candidate fits and function evaluations, not just recovery.

## Fixed controls

- Same synthetic seven-source scene family, PSF, background, image size, exposure levels, and scoring rule as PR #35.
- Same Pearson residual and matched-filter template.
- Same Poisson deviance objective, parameterization, bounds, tolerances, and BIC penalty.
- One initialization per proposal; no multi-start.
- Same stopping rule: stop at the first proposal whose BIC does not improve.
- Fresh seed range starts at 20261900, disjoint from PR #35 and PR #36.
- 90 trials: geometry scales 0.8/1.0/1.2, exposures 1.0/0.1/0.03, ten trials per cell.
- Hungarian one-to-one scoring within 1 px is performed only after detection.

## Proposal pool definition

At each greedy step, construct the existing Pearson-residual matched-filter score map and retain its five highest peaks using deterministic non-maximum suppression. After selecting a peak, suppress a radius of 1.0 px around it before extracting the next peak. The default detector path remains the original single global maximum. The experimental path fits all available peaks (up to five) against the same current accepted scene.

For a fixed proposed source count, choose the successful fit with lowest Poisson BIC. Since the parameter count is identical among alternatives at that step, this is equivalent to choosing the lowest Poisson deviance, but the implementation records BIC explicitly. The selected proposal is then accepted only if its BIC is lower than the current scene's BIC. No penalty or threshold is changed.

## Primary outcomes

- Mean matched truth sources, missed sources, unmatched candidates, and exact seven-source recoveries.
- Paired per-trial differences against both controls.
- Outcomes by geometry scale and exposure.
- Number of proposal candidates evaluated and total optimizer function evaluations.
- For each accepted or rejected step: candidate coordinates/scores, fit success, deviance, BIC, selected candidate rank, and BIC margin.
- Whether top-five selection finds a truth-matching candidate when the highest-scoring peak does not (post-fit audit only).
- Whether a candidate near an unmatched truth source is rejected by the unchanged BIC rule.

## Interpretation discipline

A gain would support the claim that choosing among several residual peaks helps this synthetic setup; it would not establish general superiority or real-image performance. No gain would weaken the case that a larger proposal pool alone resolves under-recovery. A source-like proposal rejected by BIC is diagnostic evidence about the model-selection boundary, not proof that BIC is wrong: truth matching is only a post-hoc audit.

This experiment changes both proposal choice and the number of candidate fits per step, so it cannot fully separate proposal ranking from optimizer-selection effects. The recorded candidate-level fits are intended to make that distinction inspectable. If results are promising, a later experiment can isolate proposal generation from BIC acceptance.

## Status

Predeclared protocol. No benchmark results are available until the workflow completes and the full artifact is inspected. The PR remains draft and unmerged.
