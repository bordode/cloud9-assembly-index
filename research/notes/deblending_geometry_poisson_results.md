# Geometry and Poisson stress test: verified 90-trial results

**Experiment:** `C9-DEBLENDING-GEOMETRY-POISSON-001`  
**Workflow run:** [42189022104](https://github.com/bordode/cloud9-assembly-index/actions/runs/42189022104)  
**Code commit tested:** `f591c63459f5e943c08c89198eacd2b1e3880794`  
**Artifact:** `deblending-geometry-poisson-results` (90 JSON trial records; GitHub Actions artifact, 30-day retention; created 2026-11-06)  
**Artifact SHA-256:** `4ea8598b838238bec57e07944d616e627ec9d8fcd1e2ffcfb2f02d14f161d9b6`

## Design

The synthetic experiment varies seven-source geometry scale (0.8, 1.0, 1.2) and Poisson exposure (1.0, 0.1, 0.03), with ten independent seeds per cell: nine conditions and 90 trials total.

The true PSF width and assumed PSF width are both 1.3 px. Source positions are uniformly scaled about the detector centre; source identities and fluxes remain fixed. Expected pixel rates are rendered with the pixel-integrated Gaussian model. Counts are generated as:

`observed = Poisson(expected_rate * exposure) / exposure`

The detector receives only the noisy observation and declared PSF width. It is not given truth positions or source count. Truth is used only for post-fit scoring. Greedy and conditional joint-refined candidate lists are scored separately by Hungarian one-to-one assignment within 1 px. Exact seven-source recovery requires all seven truth sources matched and zero unmatched candidates.

## Results

### Joint-refined candidates by exposure

| Exposure | Trials | Mean matched truth sources (of 7) | Mean missed | Mean unmatched candidates | Exact seven-source recoveries |
|---:|---:|---:|---:|---:|---:|
| 1.00 | 30 | 5.53 | 1.47 | 0.33 | 9/30 |
| 0.10 | 30 | 3.37 | 3.63 | 1.40 | 0/30 |
| 0.03 | 30 | 2.90 | 4.10 | 1.10 | 0/30 |
| **All** | **90** | **3.93** | **3.07** | **0.94** | **9/90** |

All 90 joint optimizers reported numerical success. This is not a recovery metric: 81/90 trials did not achieve exact seven-source recovery despite optimizer success.

### Joint-refined candidates by geometry scale

| Geometry scale | Trials | Mean matched truth sources (of 7) | Mean unmatched candidates | Exact seven-source recoveries |
|---:|---:|---:|---:|---:|
| 0.8 | 30 | 3.43 | 0.63 | 0/30 |
| 1.0 | 30 | 4.07 | 0.97 | 2/30 |
| 1.2 | 30 | 4.30 | 1.23 | 7/30 |

### Exact recoveries by condition

| Geometry scale | Exposure 1.00 | Exposure 0.10 | Exposure 0.03 |
|---:|---:|---:|---:|
| 0.8 | 0/10 | 0/10 | 0/10 |
| 1.0 | 2/10 | 0/10 | 0/10 |
| 1.2 | 7/10 | 0/10 | 0/10 |

The greedy stage alone had no exact seven-source recoveries in any of the 90 trials. Joint refinement increased mean matched-source count from 2.11 to 3.93 overall, but it did not reliably repair candidate-count errors or missed detections.

## Interpretation

1. **Exposure was the clearest factor in this grid.** Exact recovery occurred only at exposure 1.0. At exposures 0.1 and 0.03, the detector did not recover all seven sources in any of the 60 trials.
2. **Geometry mattered at the highest exposure.** The expanded geometry (scale 1.2) achieved 7/10 exact recoveries, the nominal geometry 2/10, and the compressed geometry 0/10. This is consistent with stronger overlap making the fixed-source scene harder in this particular setup, but the small number of seeds does not establish a general geometry law.
3. **Joint refinement helped localization/count matching on average, but did not make the pipeline robust.** It improved the average number of matched truths relative to greedy candidates, while exact recovery remained 10% overall.
4. **Optimizer success is not scientific correctness.** All joint optimizers reported success, yet only nine trials met the exact-recovery criterion.

## Limitations and caveats

- This is a synthetic point-source experiment with one detector size and one fixed PSF width (1.3 px); only uniform geometry scaling and exposure vary.
- The current detector uses a profiled Gaussian BIC stopping rule on Poisson-counted observations. This is intentionally a **likelihood-mismatch stress test**, not Poisson-optimal inference. The Gaussian BIC may mis-rank candidate counts under Poisson noise.
- Fluxes and source identities remain fixed across geometry scales. This is not a broad morphology or flux-contrast study.
- Ten seeds per condition provide an exploratory comparison, not precise estimates of recovery probabilities.
- Results do not establish performance on Hubble images or real astronomical data.
- The conditional joint refinement fits the component count selected earlier; it does not independently add or remove sources.

## Conclusion

The runner is now verified end-to-end and its full output is archived. In this deliberately mismatched Poisson setting, the observation-only deblender's exact recovery was limited to 9/90 trials, all at the highest exposure; the other 81 trials failed the exact seven-source criterion despite successful optimizer termination. This is a useful negative/limiting result: it identifies exposure and crowding as important stress dimensions and reinforces the need to report detection/recovery accuracy separately from numerical convergence.

This result is an independent Cloud-9 synthetic stress test of the current pipeline. It is not a reproduction of Aimy's experiments and does not validate or refute Aimy's reported pixel-response findings.
