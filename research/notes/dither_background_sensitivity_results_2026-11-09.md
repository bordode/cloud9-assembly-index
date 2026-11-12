# Known-background dither sensitivity benchmark

**Date:** 9 November 2026  
**Related PR:** https://github.com/bordode/cloud9-assembly-index/pull/41  
**Benchmark run:** https://github.com/bordode/cloud9-assembly-index/actions/runs/42540030321  
**Python tests:** https://github.com/bordode/cloud9-assembly-index/actions/runs/42540034854  
**CodeQL / PR checks:** https://github.com/bordode/cloud9-assembly-index/actions/runs/42540031048  
**Status:** successful controlled synthetic sensitivity test; broader detector realism remains outstanding

## Question

Does the early-iteration phase-diversity result persist when source photons are accompanied by a known uniform Poisson background?

## Forward and likelihood model

For detector pixel p in frame k, the expected count is:

    mu[k,p] = t[k] * (A[k] x[p] + b)

where t[k] is frame exposure, A[k] is the discrete bilinear shift-and-bin source operator, x is the non-negative high-resolution scene, and b is a spatially uniform background count rate per detector pixel per exposure unit.

The reconstruction likelihood is supplied the exact value of b. Each Richardson–Lucy update includes the additive background in the predicted mean, while the sensitivity denominator remains the adjoint response to the source component only. This is the known-background Poisson likelihood update for the implemented linear source operator.

This does not test blind background estimation, a background gradient, time-variable sky, dark-current uncertainty, or read noise.

## Protocol

- 30 paired seeds: 2026111000–2026111029.
- Five background rates: 0, 0.1, 0.5, 1.0 and 2.0 expected background counts per detector pixel per unit total exposure.
- Total exposure 1.0, nine frames per arm, each frame exposure 1/9.
- Detector shape 28×30 including a four-pixel guard; fixed science crop 20×22.
- 3× high-resolution reconstruction grid.
- Same three-source continuous axis-aligned Gaussian scene used in the off-grid pilot.
- Three arms: nine stationary frames, nine aligned dither frames, nine deliberately off-grid dither frames.
- Aligned phases: row/column offsets -1/3, 0, +1/3 detector pixels.
- Off-grid phases: row offsets -0.29, 0, +0.29; column offsets -0.23, 0, +0.23 detector pixels.
- Source and background counts are Poisson. No read noise.
- Truth data are generated from continuous Gaussian detector-pixel area integrals. Reconstruction uses the bilinear shift-and-bin source model and exact discrete adjoint.
- Five fixed Richardson–Lucy checkpoints: 1, 2, 3, 5 and 10 iterations.
- Same seed at each background level for aligned and off-grid conditions; stationary control is identical across those two phase-set comparisons.
- Metrics are fixed-interior relative RMSE and known-centre aperture centroid/flux errors. Aperture scores are not blind source detection.
- Paired per-seed differences with 95% t confidence intervals.

## Iteration-2 relative RMSE

Lower is better. Means across 30 seeds.

| Background rate | Nine stationary | Aligned dither | Off-grid dither |
|---:|---:|---:|---:|
| 0.0 | 0.325411 | 0.155820 | 0.163007 |
| 0.1 | 0.324944 | 0.154981 | 0.155830 |
| 0.5 | 0.325501 | 0.157031 | 0.158243 |
| 1.0 | 0.325673 | 0.152251 | 0.159029 |
| 2.0 | 0.329112 | 0.165736 | 0.164619 |

### Paired RMSE differences at iteration 2

Off-grid minus stationary:

| Background rate | Mean paired difference | 95% CI |
|---:|---:|---:|
| 0.0 | -0.162404 | [-0.167010, -0.157799] |
| 0.1 | -0.169114 | [-0.173927, -0.164302] |
| 0.5 | -0.167258 | [-0.172068, -0.162447] |
| 1.0 | -0.166645 | [-0.170225, -0.163064] |
| 2.0 | -0.164493 | [-0.168758, -0.160228] |

All five intervals exclude zero: under the tested known-background conditions, off-grid dither retains a strong RMSE advantage over the stationary arm.

Off-grid minus aligned:

| Background rate | Mean paired difference | 95% CI |
|---:|---:|---:|
| 0.0 | +0.007186 | [+0.000986, +0.013387] |
| 0.1 | +0.000849 | [-0.006133, +0.007831] |
| 0.5 | +0.001212 | [-0.004459, +0.006883] |
| 1.0 | +0.006778 | [+0.002562, +0.010994] |
| 2.0 | -0.001118 | [-0.006734, +0.004499] |

The off-grid and aligned patterns are close at this checkpoint. At background 0.1, 0.5 and 2.0, their paired intervals include zero. At 0.0 and 1.0, the aligned pattern has a small RMSE advantage. This is not evidence that off-grid is universally equivalent or superior.

### Iteration dependence

At iteration 10, off-grid-minus-stationary RMSE differences remain positive at every tested background level:
- b=0.0: +0.064386 (95% CI [+0.055761, +0.073011])
- b=0.1: +0.056164 (95% CI [+0.045998, +0.066331])
- b=0.5: +0.051667 (95% CI [+0.041609, +0.061725])
- b=1.0: +0.049650 (95% CI [+0.040956, +0.058344])
- b=2.0: +0.052380 (95% CI [+0.044007, +0.060752])

Thus, the dither advantage is still iteration-sensitive. Early stopping remains essential, and iteration 2 is only the best of the sampled checkpoints in this pilot, not a validated universal stopping rule.

## Interpretation

Within this synthetic scene and with the background level known exactly, a uniform additive Poisson background does not erase the early-iteration phase-diversity RMSE advantage. At iteration 2, off-grid dither outperforms the stationary control at every tested background rate, including the strongest tested background of two expected counts per detector pixel over the total exposure.

This is a robustness result for a known, uniform Poisson background model, not a general real-detector validation. The source forward-model mismatch remains: continuous pixel-integrated Gaussian data are reconstructed with bilinear fractional cell shifts.

## Limits

Not tested:
- unknown or estimated background;
- spatially varying or time-varying background;
- read noise or Poisson-Gaussian likelihood;
- dark-current uncertainty;
- asymmetric, Airy, spatially varying or chromatic PSFs;
- intrapixel sensitivity or charge diffusion;
- extended galaxy-like scenes;
- blind source discovery or blind stopping-rule calibration.

No universal dither gain is claimed. The known-centre aperture metrics must not be described as blind source localization.

## Reproducibility

- Benchmark run 42540030321: success.
- Python tests run 42540034854: success.
- PR / CodeQL checks run 42540031048: success for Python and Actions analysis.
- Artifact ID: 13641151342.
- Artifact SHA-256: 9cb3239f30aaf1e08328e770d0c079b48cc5d992458bb74b3dbdd0321e9eaf6c.
- Artifact expires 7 February 2027.

## Next experiment

Introduce detector read noise separately. Do not pass negative Poisson-plus-Gaussian observations to ordinary Richardson–Lucy. Implement and test a Poisson-Gaussian likelihood (or a clearly labelled approximation), then compare with the known-background Poisson baseline. Keep background known for that first read-noise experiment; only afterward test background estimation.

**Decision:** retain as a positive, bounded known-background robustness result. PR #41 remains draft and unmerged.
