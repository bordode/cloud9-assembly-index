# Off-grid dither reconstruction benchmark: 30-seed paired results

**Date:** 9 November 2026  
**Related PR:** https://github.com/bordode/cloud9-assembly-index/pull/41  
**Benchmark run:** https://github.com/bordode/cloud9-assembly-index/actions/runs/42539243091  
**Python tests:** https://github.com/bordode/cloud9-assembly-index/actions/runs/42539247636  
**Status:** successful controlled synthetic follow-up; broader validation required

## Question

Does the phase-diversity result survive when dither phases do not align with the 3× reconstruction grid?

## Protocol

- 30 paired seeds: 2026110900–2026110929.
- Same three-source axis-aligned Gaussian scene, fluxes, widths, 20×22 detector-pixel science crop, four-pixel guard, 3× high-resolution reconstruction grid and total exposure 1.0 as the first pilot.
- Photon noise only; no read noise or background.
- Three reconstruction conditions:
  1. Nine stationary frames.
  2. Nine aligned dither frames, row/column phases from -1/3, 0, +1/3 detector pixels.
  3. Nine deliberately off-grid dither frames, row phases -0.29, 0, +0.29 and column phases -0.23, 0, +0.23 detector pixels.
- The off-grid phases correspond to high-resolution cell shifts of ±0.87 rows and ±0.69 columns, so the shifts are not integer cell translations.
- The same seed is used for aligned and off-grid trials. Stationary observations are therefore identical across the paired phase-set comparisons; the phase-specific dither Poisson draws are generated independently.
- Truth data are generated from independent continuous Gaussian detector-pixel area integrals. Reconstruction uses non-negative Poisson Richardson-Lucy with the bilinear shift-and-bin operator and its exact discrete adjoint.
- Five fixed iteration checkpoints: 1, 2, 3, 5 and 10.
- Metrics: fixed-interior relative RMSE; known-centre aperture centroid error and absolute aperture-flux-ratio error. The aperture metrics are not blind source detection.
- Paired per-seed differences with 95% t confidence intervals.

The off-grid test intentionally introduces forward-model mismatch: continuous Gaussian pixel integrals generate observations, while the reconstruction approximates fractional phase shifts through bilinear interpolation of high-resolution cell fluxes. This is a test of that approximation under this scene, not an exact matched-model test.

## Mean relative RMSE by iteration

Lower is better. Means across 30 seeds.

| RL iterations | Nine stationary | Aligned dither | Off-grid dither |
|---:|---:|---:|---:|
| 1 | 0.325237 | 0.170788 | 0.184407 |
| 2 | 0.325237 | 0.155372 | 0.156512 |
| 3 | 0.325237 | 0.195739 | 0.185601 |
| 5 | 0.325237 | 0.270604 | 0.245529 |
| 10 | 0.325237 | 0.414809 | 0.375938 |

At iteration 2, off-grid dither improves RMSE relative to stationary by 0.168725 (paired 95% CI -0.173673 to -0.163778). Aligned dither improves RMSE relative to stationary by 0.169865 (95% CI -0.175755 to -0.163975).

The paired off-grid-minus-aligned RMSE difference at iteration 2 is +0.001140 (95% CI -0.005358 to +0.007638). This interval includes zero: this pilot does not detect a meaningful RMSE difference between the aligned and off-grid phase grids at the second iteration.

The phase-diversity RMSE advantage is therefore not confined to exact cell-aligned shifts in this experiment. However, the advantage is iteration-dependent. At iteration 10, off-grid dither is worse than stationary by +0.050701 (95% CI +0.042692 to +0.058710), although it is less degraded than aligned dither.

## Secondary metrics at iteration 2

Paired differences are off-grid minus stationary unless otherwise stated.

- Mean centroid error: stationary 0.039479 px; off-grid 0.038989 px. Paired difference -0.000490 px (95% CI -0.006234 to +0.005255). The interval includes zero; no clear centroid improvement is established.
- Mean absolute aperture-flux error: stationary 0.052985; off-grid 0.032204. Paired difference -0.020781 (95% CI -0.031400 to -0.010161).
- Off-grid minus aligned centroid-error difference: -0.003029 px (95% CI -0.008270 to +0.002212), includes zero.
- Off-grid minus aligned absolute aperture-flux-error difference: -0.002421 (95% CI -0.009542 to +0.004699), includes zero.

## Interpretation and limits

This 30-seed follow-up supports a narrow conclusion: in this synthetic Gaussian scene, a 3× reconstruction with bilinear fractional shifts retains a strong early-iteration RMSE benefit from a balanced off-grid nine-phase pattern. The observed iteration-2 RMSE is nearly the same as the aligned-phase control.

It does not establish universal dither benefit, blind source localization, or a general stopping rule. The off-grid model mismatch is specific to this bilinear approximation, scene, phase pattern and 3× grid. No read noise, background, asymmetric or spatially varying PSF, Airy structure, intrapixel response, charge diffusion, or extended galaxy-like scenes have been tested. The known-centre aperture metrics must not be described as blind detection.

The iteration curve again shows early stopping matters. At iteration 10, both dithered reconstructions are worse than the stationary control. Iteration 2 is the best of the five sampled checkpoints for off-grid dither, not a validated general optimum.

## Reproducibility

- Benchmark run 42539243091: success; benchmark JSON artifact uploaded.
- Python test run 42539247636: success.
- PR checks run 42539244467: success.
- Artifact ID: 13639958628.
- Artifact SHA-256: 1bba0c1c8cd945d5a8d036c23c0aad1f5d279b0860ecfda5a6584959e11dfec1.
- Artifact expires 7 February 2027.

## Next experiment

Test read noise and background as separate matched sensitivity arms, then vary the PSF away from the axis-aligned Gaussian assumption. Keep the stopping rule fixed or calibrated on a separate validation set before confirmatory testing.

**Decision:** retain as a positive but narrowly scoped off-grid phase-diversity result. PR #41 remains draft and unmerged.
