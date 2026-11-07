# Poisson AIC versus BIC acceptance: paired pilot results

**Date:** 7 November 2026  
**Experiment:** `C9-DEBLENDING-POISSON-AIC-BIC-ACCEPTANCE-001`  
**Status:** completed exploratory synthetic benchmark  
**Workflow run:** [42423940784](https://github.com/bordode/cloud9-assembly-index/actions/runs/42423940784)  
**Tested commit:** `08e7650d366958b766ac0ccd7543456c747000ec`  
**Artifact:** `deblending-poisson-aic-bic-acceptance` (ID `13595132084`)  
**Artifact SHA-256 (GitHub digest):** `323fc9fc51fcbb43d246888c4a528ddf66dd0dab80fb53ad957097ffeb926121`

## Executive result

The benchmark completed successfully: six paired methods on the same 27 synthetic Poisson observations. AIC accepted more sources than BIC, but the additional complexity did not produce a reliable increase in recovered truths. It substantially increased unmatched candidates.

The result supports a narrow conclusion: in this scene family and setup, replacing BIC with AIC makes the detector more permissive, not demonstrably more accurate.

## Design

- 27 trials, three trials in each geometry-scale/exposure cell.
- Geometry scales 0.8, 1.0, 1.2; exposures 1.0, 0.1, 0.03.
- Seed range begins at 20262100.
- Six methods: BIC/AIC crossed with fixed top-five, fixed top-ten, and adaptive top-five-to-ten.
- Each method receives the same Poisson count image within a trial.
- Same pixel-integrated PSF, Poisson deviance, parameterisation, bounds, optimizer tolerances and residual proposal map.
- Truth withheld from detection and used only for post-run Hungarian scoring within 1 px.

The model uses (k=3N+1) parameters and (n=441) pixels:
- AIC penalty per added source: (2(3)=6).
- BIC penalty per added source: (3\ln(441)=18.2671).
- BIC therefore charges about 12.267 more criterion units per additional source under this pixel-count convention.

## Aggregate results

| Method | Mean matched truths | Mean missed truths | Mean unmatched candidates | Mean selected candidates | Exact 7-source recoveries | Proposal fits | Optimizer evaluations |
|---|---:|---:|---:|---:|---:|---:|---:|
| BIC top-five | 3.593 | 3.407 | 0.222 | 3.815 | 1/27 | 650 | 18,001 |
| BIC top-ten | 3.556 | 3.444 | 0.259 | 3.815 | 1/27 | 1,300 | 36,422 |
| BIC adaptive | 3.593 | 3.407 | 0.222 | 3.815 | 1/27 | 785 | 21,461 |
| AIC top-five | 3.593 | 3.407 | 1.630 | 5.222 | 1/27 | 840 | 23,666 |
| AIC top-ten | 3.593 | 3.407 | 1.704 | 5.296 | 1/27 | 1,700 | 47,784 |
| AIC adaptive | 3.593 | 3.407 | 1.704 | 5.296 | 1/27 | 995 | 27,761 |

## Paired comparisons

### AIC versus BIC at matched proposal depth

- Top-five: AIC matched more truths in 6 trials, fewer in 7, tied in 14; mean matched-source difference 0.000. AIC added an average 1.407 unmatched candidates per trial.
- Top-ten: AIC matched more in 7, fewer in 8, tied in 12; mean matched-source difference +0.037. AIC added 1.444 unmatched candidates per trial.
- Adaptive: AIC matched more in 7, fewer in 8, tied in 12; mean matched-source difference 0.000. AIC added 1.481 unmatched candidates per trial.

AIC produced more unmatched candidates than BIC in 16–17 of 27 paired trials, depending on proposal policy. The small top-ten mean recovery difference is not a stable win: it is accompanied by more unmatched candidates and does not improve exact seven-source recovery.

### Adaptive versus fixed proposal depth

- BIC adaptive and BIC top-five had identical matched-source and unmatched-candidate scores in all 27 trials. Adaptive performed 135 additional proposal fits and used 3,460 more optimizer function evaluations, with zero rescued expansions.
- AIC adaptive versus AIC top-five: 25 ties, one better and one worse in matched-source count; mean matched-source difference 0.000. Adaptive added only 0.074 unmatched candidates per trial on average, while using 155 additional proposal fits and 4,095 additional optimizer evaluations.

Thus the adaptive expansion rule did not materially improve final recovery in this benchmark. Under BIC it exactly reproduced top-five scoring while incurring extra fitting cost.

## Exposure dependence

Mean matched truths for top-five methods:

| Exposure | BIC top-five | AIC top-five | Mean unmatched: BIC | Mean unmatched: AIC |
|---:|---:|---:|---:|---:|
| 1.0 | 4.556 | 5.000 | 0.333 | 1.333 |
| 0.1 | 3.667 | 3.111 | 0.111 | 1.778 |
| 0.03 | 2.556 | 2.667 | 0.222 | 1.778 |

AIC's effect is not uniformly beneficial across exposure: it improves the mean matched count at exposure 1.0, reduces it at 0.1, and changes it only slightly at 0.03. Its unmatched-candidate rate is higher in every exposure group. Three trials per cell are far too few to establish a reliable exposure interaction.

## Interpretation

The experiment separates two issues:

1. **Candidate ranking within a proposal step:** because candidates within that step have the same parameter count, AIC and BIC rank their fitted likelihoods identically.
2. **Acceptance across model sizes:** AIC's lower penalty makes adding a source easier. In this pilot, that mainly increases model size and false extras rather than consistently recovering more withheld sources.

The BIC penalty is based on all 441 pixels. The validity of that (n) depends on the likelihood and effective-independence assumptions. PSF coupling, model misspecification, or correlated residuals could make nominal BIC calibration imperfect. This benchmark does not establish that BIC is universally correct or AIC universally wrong.

## Limitations

- Exploratory pilot: only 27 trials, three per geometry/exposure cell.
- One seven-source synthetic scene family, one PSF family and one noise setup.
- Repeated trials share a fixed scene family and are not independent astronomical fields.
- Truth matching uses a 1 px post-hoc Hungarian threshold.
- The experiment does not establish performance on real astronomical images.
- No claim is made that either criterion is generally optimal.

## Recommended next experiment

Do not switch the detector to AIC on this evidence. Keep BIC as the current default and preserve AIC as an explicit experimental option.

The next useful study is a larger, independently seeded benchmark that varies source density, flux contrast, PSF width, background level and image size. It should also test sensitivity to the BIC observation-count convention and include model-mismatch controls. Report paired uncertainty intervals and calibration of unmatched detections, not only mean matched-source counts.

## Reproducibility

The uploaded artifact contains all 27 trial records and per-method diagnostics. The GitHub Actions run reports successful criterion tests, successful six-method benchmark execution, and successful artifact upload. This note records the artifact summary; it does not alter the detector implementation.
