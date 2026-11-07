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


## First benchmark results — run 42352555123

**Workflow:** [run 42352555123](https://github.com/bordode/cloud9-assembly-index/actions/runs/42352555123)  
**Code commit:** `4a4d746dec08f7020a489f450e60f56c6a421f86`  
**Artifact:** `deblending-poisson-proposal-bic-comparison`  
**GitHub artifact digest:** `sha256:0e5ba020a82d93a29bb21ede5d464f548b94ab0247f3f4af7b54958170659fd3`  
**Extracted JSON SHA-256:** `07cf0519b3e011079a2a71a3464e20df11a3bd3bb7069d204aecd292f5df7bc6`

Tests passed, all 90 trials completed, and the full artifact uploaded.

### Aggregate results

| Metric | Gaussian | Poisson single proposal | Poisson top-five/BIC |
|---|---:|---:|---:|
| Mean matched truths (of 7) | 3.78 | 3.29 | 3.42 |
| Mean missed truths | 3.22 | 3.71 | 3.58 |
| Mean selected candidates | 4.78 | 3.59 | 3.70 |
| Mean unmatched extra candidates | 1.00 | 0.30 | 0.28 |
| Exact seven-source recoveries | 3/90 | 0/90 | 0/90 |
| Optimizer-success trials | 90/90 | 90/90 | 90/90 |

Paired top-five/BIC versus single-proposal Poisson:
- Top-five matched more truths in 9/90 trials.
- Single-proposal matched more in 0/90.
- Tie in 81/90.
- Mean difference: +0.133 matched truths per trial.
- Exact recovery remained zero for both.

By exposure and geometry, the top-five method's gains were modest and not universal. Its largest mean differences appeared at geometry 1.0/exposure 0.1 (+0.4 sources) and geometry 1.2/exposure 0.1 (+0.2); most cells differed by 0.0–0.2. The Gaussian baseline still had higher mean recovery overall and achieved all three exact recoveries, all at geometry 1.2/exposure 1.0.

### Cost and proposal diagnostics

Across 423 greedy proposal steps, top-five evaluated 2,115 complete-scene candidate fits and used 63,244 optimizer function evaluations. There were 333 accepted steps and 90 rejected steps. This is a substantial computational premium over one proposal fit per step.

Across the 2,115 proposed coordinates, 286 (13.5%) fell within 1 px of any truth source in the post-detection audit. At least one proposal was within 1 px of some truth source in 112/423 steps (26.5%). This audit does not distinguish already-recovered sources from still-missed sources, so it cannot by itself show that a missing source was available to be recovered.

The chosen proposal rank was spread across the pool: rank 1 was selected 97 times, rank 2 94, rank 3 79, rank 4 79, and rank 5 74. This indicates that the highest residual peak was not always the lowest-BIC fitted proposal.

### Important numerical caution

For each step, compare the maximum and minimum BIC among successful candidate fits. Across 423 steps, the median spread was approximately (1.70\times10^{-7}); 64.8% of steps had a spread below (10^{-6}), and 68.8% below 1. A small number had much larger spreads (99th percentile about 82.9; maximum about 103.3).

Because all alternatives at a given step have the same parameter count, BIC ranking is driven by deviance. The very small spreads in most steps suggest many candidate initializations converge to effectively the same solution, with the nominal winner potentially determined by tiny numerical differences. The observed +0.133-source average is promising but small and requires a repeat run before stronger interpretation. It must not be presented as a robust improvement yet.

A strengthened test now asserts that the selected proposal rank corresponds to the minimum BIC among successful candidate fits. A repeat 90-trial workflow is being triggered to assess whether the aggregate advantage persists. This experiment remains synthetic and does not establish real-image performance.


## Independent repeat benchmark — run 42353164442

**Workflow:** [run 42353164442](https://github.com/bordode/cloud9-assembly-index/actions/runs/42353164442)  
**Code commit tested:** `4152ff308ca2d717f2cd8b281b1cc3ac272270e9`  
**GitHub artifact digest:** `sha256:387a907f707d5fce462f8fce3e975409fab76c3448ebdf520e781686f62e93e6`  
**Extracted JSON SHA-256:** `c729f64960893e4e1cc06a3e9bf3865531583f1bd62be401c231fd00d375e73a`

The repeat passed the strengthened tests, completed all 90 trials, and uploaded the full artifact.

| Metric | First run | Repeat |
|---|---:|---:|
| Gaussian mean matched truths | 3.78 | 3.78 |
| Poisson single mean matched | 3.29 | 3.28 |
| Poisson top-five/BIC mean matched | 3.42 | 3.42 |
| Top-five paired wins | 9 | 9 |
| Single-proposal paired wins | 0 | 0 |
| Ties | 81 | 81 |
| Mean paired advantage | +0.133 | +0.144 |
| Gaussian exact recoveries | 3/90 | 3/90 |
| Poisson single exact recoveries | 0/90 | 0/90 |
| Poisson top-five exact recoveries | 0/90 | 0/90 |

The qualitative result is repeatable on this fresh-seed grid: top-five/BIC yields a small average increase in matched sources, but no exact seven-source recoveries and no improvement in any exact-recovery count. The Gaussian baseline remains ahead by mean matched sources (3.78 versus 3.42).

### Repeat cost and numerical diagnostics

The repeat evaluated 2,115 proposal fits across 423 steps, with 63,428 optimizer function evaluations; 333 steps were accepted and 90 rejected. This is close to the first run's 63,244 function evaluations.

Accepted proposal ranks in the repeat were: rank 1 = 77, rank 2 = 68, rank 3 = 61, rank 4 = 57, rank 5 = 70. The selected fit is often not rank 1 by residual score, but this alone does not mean it recovers more true sources.

The median successful-fit BIC spread per step was (1.77\times10^{-7}); 65.5% of steps had spread below (10^{-6}), and 69.3% below 1. The 99th percentile was about 69.4, with a maximum about 100.7. This closely resembles the first run and confirms that many proposal alternatives converge to numerically near-identical fits, with a smaller tail of genuinely different outcomes.

### Revised conclusion

The top-five proposal pool has a small, repeatable benefit in mean matched-source count in this controlled synthetic experiment. However:
- It does not improve exact seven-source recovery.
- It remains below the Gaussian baseline in mean matched sources.
- It adds roughly five full-scene fits per proposal step.
- Most candidate fits have almost indistinguishable BIC values, so selection among them is often a numerical tie-break rather than evidence that a different proposal has found a better scene.

This is a modest algorithmic signal, not yet a persuasive practical improvement. Do not merge on this result alone. The next useful work should inspect the candidate fits that materially differ, distinguish numerical near-ties from genuinely different fitted scenes, and test whether a more informative proposal mechanism can identify missed sources without multiplying optimizer cost. Keep the PR draft and unmerged.
