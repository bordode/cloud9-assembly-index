# Adaptive Poisson proposal expansion: 27-trial pilot results

**Date:** 7 November 2026  
**Experiment:** `C9-DEBLENDING-POISSON-ADAPTIVE-EXPANSION-001`  
**Workflow run:** [42422796923](https://github.com/bordode/cloud9-assembly-index/actions/runs/42422796923)  
**Artifact:** `deblending-poisson-adaptive-expansion` (artifact ID `13594840143`)  
**Workflow commit:** `ca1546e2fdd8b7283070480940ff549d5a951572`  
**Artifact ZIP SHA-256:** `a75ecb667cdb25798bc5975eef10ad8f36edeb4d12bb98a302e14eac24621ea2`  
**Extracted JSON SHA-256:** `9dbf465bc8713fd1ec06a6152eb3ac1e9c03ac4ab3e4f11f523851d4f337d4ea`

## Design

A paired 27-trial synthetic pilot compared:

1. Top-five: fit the five highest-ranked residual proposals.
2. Fixed top-ten: fit the ten highest-ranked residual proposals.
3. Adaptive top-five-to-ten: fit ranks 1–5, and evaluate ranks 6–10 only if no successful top-five fit lowers the current scene BIC.

Each method received the same Poisson count image for each trial. Geometry scales were 0.8, 1.0 and 1.2; exposures were 1.0, 0.1 and 0.03; three trials per cell. The truth was withheld from detection and selection and used only for post-run Hungarian matching within 1 px.

## Results

| Measure | Top-five | Fixed top-ten | Adaptive |
|---|---:|---:|---:|
| Mean matched truths | 3.370 | 3.370 | 3.370 |
| Mean missed truths | 3.630 | 3.630 | 3.630 |
| Mean unmatched candidates | 0.296 | 0.296 | 0.296 |
| Exact seven-source recoveries | 0/27 | 0/27 | 0/27 |
| Proposal fits | 630 | 1,260 | 765 |
| Optimizer function evaluations | 19,952 | 39,767 | 24,058 |

All paired comparisons tied on matched-truth count in all 27 trials. No method was better or worse in any trial.

### What the adaptive trigger actually did

- Expansion occurred 27 times, exactly once per trial.
- Each expansion was the final, rejected step in that trial.
- All 27 expansions evaluated ranks 1–10.
- In 12/27 expanded steps, a rank 6–10 candidate had a lower BIC than every successful top-five candidate.
- However, in every one of those 12 cases, the best candidate still had a BIC higher than the current accepted scene BIC. Across all expanded steps, the BIC increase after selecting the best candidate ranged from 0.386 to 14.099.
- Therefore, no expansion rescued a rejected step and no additional source was accepted.

This separates two issues: deeper proposals sometimes produced a better candidate fit than the top-five pool, but they did not cross the unchanged BIC acceptance threshold.

### Computational cost

- Adaptive used 765 proposal fits, 39.3% fewer than fixed top-ten (1,260).
- Adaptive used 24,058 optimizer evaluations, 39.5% fewer than fixed top-ten (39,767).
- Relative to top-five, adaptive added 135 proposal fits (+21.4%) and 4,106 optimizer evaluations (+20.6%).
- Adaptive used 60.5% of fixed top-ten's optimizer evaluations.

## Interpretation

This pilot provides **no evidence that expanding the proposal pool from five to ten improves recovery** under this scene family, noise setup and unchanged BIC acceptance rule.

It does show that conditional expansion avoids much of the cost of always fitting ten candidates. But in this pilot the expansion only happened after the top-five method had already reached its terminal rejected step. In 12 cases it changed which candidate was considered best, but not whether that candidate was accepted.

The result suggests that, for these terminal steps, the unchanged BIC acceptance criterion—not simply proposal rank—remained decisive. It does not prove that the acceptance rule is generally too conservative or that deeper ranks cannot help in other scenes.

## Limitations

- Only 27 synthetic trials, with three per geometry/exposure cell.
- One seven-source synthetic scene family and one PSF/noise setup.
- Repeated observations within a fixed scene are not independent samples.
- No exact seven-source recovery occurred under any method.
- This is not a real-astronomy validation or evidence of general detector performance.

## Decision

Keep the adaptive policy as an optional, tested research branch, but do not promote it as a recovery improvement. The evidence supports a modest computational-efficiency claim relative to fixed top-ten, not a scientific-performance gain. A broader scene-family benchmark would be needed before making a general recommendation.
