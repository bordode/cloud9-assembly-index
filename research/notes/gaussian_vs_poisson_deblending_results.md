# Paired Gaussian-versus-Poisson deblending comparison

**Experiment:** `C9-DEBLENDING-GAUSSIAN-VS-POISSON-001`  
**Canonical workflow run:** [42279315393](https://github.com/bordode/cloud9-assembly-index/actions/runs/42279315393)  
**Code commit tested:** `c2d752dbe61bd37769550822ac43b4bc6652e15b`  
**Artifact:** `deblending-gaussian-poisson-comparison` (90 complete paired trial records; 30-day retention)  
**Artifact SHA-256:** `84db6128cdeab80b93206e4212c39777b96184fcc4d6e8dd5aadf493a2aee95f`

## Question

Does the poor exact recovery in the earlier Poisson stress test arise partly because the detector uses a Gaussian residual/BIC rule on Poisson-counted data?

This comparison adds a separate observation-only Poisson detector and tests both methods on exactly the same observations, seeds, PSF assumptions, and post-fit scoring.

## Methods

### Legacy Gaussian detector

- Normalized matched-filter proposals from the observation residual.
- Pixel-integrated Gaussian single-source least-squares fits.
- Profiled Gaussian BIC stopping rule.
- Conditional joint refinement of the selected component count.

### New Poisson detector

- Pearson-residual matched-filter proposals.
- Joint maximum-likelihood fitting of all retained source positions, amplitudes, and a shared non-negative background by minimizing signed square-root Poisson deviance residuals.
- Poisson BIC source-count selection after each proposed source.
- Uses the known exposure to convert the observed count-rate image back to Poisson counts.

### Shared controls

- Seven-source synthetic scene on a 21×21 detector.
- Truth PSF width 1.3 px; both methods assume 1.3 px.
- Three geometry scales (0.8, 1.0, 1.2), three exposures (1.0, 0.1, 0.03), ten independent seeds per cell: 90 paired observations.
- Both methods receive the same noisy count image. Neither receives true source positions, amplitudes, or source count.
- Both methods are scored after detection using Hungarian one-to-one assignment within 1 px. Exact recovery requires seven matched truths and exactly seven candidates.

## Canonical 90-trial results

| Metric | Gaussian detector | Poisson detector |
|---|---:|---:|
| Mean matched truth sources (of 7) | 3.93 | 3.37 |
| Mean missed truth sources | 3.07 | 3.63 |
| Mean selected candidate count | 4.88 | 3.57 |
| Mean unmatched candidates | 0.94 | 0.20 |
| Exact seven-source recoveries | 9/90 | 2/90 |
| Optimizer successes | 90/90 | 90/90 |

Paired trial comparison:
- Poisson detector matched more truth sources in 10/90 trials.
- Gaussian detector matched more in 46/90.
- They tied in 34/90.
- Mean paired difference (Poisson minus Gaussian): −0.57 matched sources per trial.

### Results by exposure

| Exposure | Gaussian mean matched | Gaussian exact | Poisson mean matched | Poisson exact |
|---:|---:|---:|---:|---:|
| 1.00 | 5.53 | 9/30 | 4.60 | 2/30 |
| 0.10 | 3.37 | 0/30 | 3.27 | 0/30 |
| 0.03 | 2.90 | 0/30 | 2.23 | 0/30 |

At exposure 1.0, the Gaussian method had higher mean localization/recovery and more exact seven-source recoveries. At exposure 0.1, mean matched counts were close, with a slight Gaussian advantage. At exposure 0.03, the Gaussian method matched more truth sources on average. Neither method achieved exact recovery at the two lower exposures.

The Poisson method selected fewer candidates and had fewer unmatched candidates at every exposure. That is a conservative-selection tradeoff, not evidence of superior recovery: it reduced extra candidates but also missed more real sources overall.

## Geometry observations

At exposure 1.0:
- Geometry scale 0.8: Gaussian mean 4.6 matched; Poisson mean 4.0.
- Geometry scale 1.0: Gaussian mean 5.5; Poisson mean 4.2.
- Geometry scale 1.2: Gaussian mean 6.5 with 7/10 exact recoveries; Poisson mean 5.6 with 2/10 exact recoveries.

This particular grid suggests that greater separation helps both methods, but the Gaussian detector performed better on this scene. Ten seeds per cell are exploratory, not enough to establish a general ranking.

## Numerical stability and repeatability

A preliminary full benchmark run using the same seed grid produced 3/90 Poisson exact recoveries; the canonical test-plus-benchmark run produced 2/90. Inspection showed one borderline trial (seed 20261764, geometry scale 1.2, exposure 1.0) where the seventh proposed source was accepted in the preliminary run and rejected in the canonical run. The other 89 trials retained the same source-count decisions. This is a numerical/local-optimization sensitivity at a BIC decision boundary and should be retained as a caveat, not averaged away.

A further independent repeat was completed on workflow run [42279936553](https://github.com/bordode/cloud9-assembly-index/actions/runs/42279936553), at branch head `a062067be9c93c990c00acd876164bbbb8533bd8`. This commit changed the results note only; the benchmark implementation was unchanged from the canonical code commit. The repeat's full 90-record JSON artifact was compared record-by-record with the canonical artifact: all 90 trial keys and every Gaussian and Poisson record matched exactly, including candidate decisions, source counts, fit scores, and post-fit recovery scores. Aggregate results were also identical (Gaussian 9/90 exact; Poisson 2/90). The repeat artifact SHA-256 is `d393bdcdcfff3272b6bf6302da2f3ad61be880439a0e8b5ed5388cc1a4eef98b`.

This establishes exact repeatability for this second run in the same workflow environment, but does not erase the earlier one-trial discrepancy. The preliminary discrepancy remains evidence that at least one borderline decision can be sensitive to numerical execution conditions. The present result should therefore be described as repeatable in the latest rerun, not universally numerically invariant.

## Interpretation

1. **The likelihood mismatch is not the only explanation for the earlier failures.** A Poisson-likelihood detector did not improve exact recovery in this first paired implementation. It performed worse than the Gaussian baseline on the selected recovery metrics.
2. **The Poisson detector is more conservative.** Its lower unmatched-candidate count suggests fewer extra detections, but it pays for this with more missed sources.
3. **Optimizer success is not correctness.** Both methods reported 90/90 optimizer successes, while exact recovery was only 9/90 and 2/90 respectively.
4. **A likelihood-matched objective is not sufficient by itself.** Candidate proposal quality, initialization, greedy ordering, model-selection penalty, and local minima still matter.
5. **The comparison does not prove Gaussian BIC is generally preferable.** It covers one synthetic geometry family, one detector size, one PSF width, three exposures, and a finite seed set. The Poisson detector may need better proposals and multi-start or more stable optimization before it is a fair contender.

## Limitations

- Synthetic point sources only; no real astronomical image was used.
- One detector size (21×21), one PSF width, and fixed source fluxes.
- Independent Poisson pixel counts and constant non-negative background are assumed by the Poisson detector.
- Both detectors use greedy proposal order; either can miss sources before model selection.
- BIC is an approximate criterion; finite samples and local minima can change borderline decisions.
- The Poisson model uses known exposure. This is appropriate for the controlled comparison but not a blind exposure-estimation test.
- Ten seeds per condition do not provide precise recovery-probability estimates.

## Conclusion and next experiment

In this paired test, simply replacing Gaussian fitting/stopping with a Poisson-deviance MLE and Poisson BIC did **not** improve source recovery. It reduced unmatched detections but under-selected sources and recovered fewer truths overall. The next useful experiment is not to tune the BIC penalty on these same truth-scored results. Instead, test whether Poisson candidate proposals and local optimization are the bottleneck: compare deterministic multi-start refits and proposal diagnostics on a newly predeclared seed set, keeping truth hidden until scoring.

This is a Cloud-9 synthetic experiment. It is not a reproduction of Aimy's results and does not validate or refute Aimy's pixel-response claims.
