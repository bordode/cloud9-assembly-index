# Photon-limited dither reconstruction: 30-seed pilot results

**Date:** 8 November 2026  
**Related PR:** https://github.com/bordode/cloud9-assembly-index/pull/41  
**Benchmark workflow:** https://github.com/bordode/cloud9-assembly-index/actions/runs/42524571798  
**Python test workflow:** https://github.com/bordode/cloud9-assembly-index/actions/runs/42524574297  
**Status:** first controlled pilot completed; broader validation still required

## Protocol actually run

- 30 independent Poisson master seeds.
- Three axis-aligned Gaussian sources with fixed fluxes and widths.
- Fixed 20×22 detector-pixel science region, four-pixel guard, 3× high-resolution reconstruction grid.
- Total exposure 1.0 in every arm.
- One long exposure, nine stationary exposures of 1/9 each, and nine dithered exposures of 1/9 each.
- Dither phases: 3×3 grid at row/column offsets -1/3, 0, +1/3 detector pixels. At bin factor three, these phases align exactly to high-resolution cell shifts.
- Photon noise only: independent Poisson counts; no read noise or background.
- Non-negative Poisson Richardson-Lucy reconstruction, reporting iterations 1, 2, 3, 5, and 10.
- Relative RMSE scored on the same fixed interior. Centroid and aperture-flux metrics use radius-two-pixel apertures around known source centres; these are conditional localization/photometry metrics, not blind source detection.
- Paired dither-minus-stationary differences use 95% t confidence intervals across the 30 seeds.

The data generator uses direct continuous Gaussian pixel-area integrals. Reconstruction estimates a non-parametric high-resolution cell-flux image using the separate shift-and-bin operator. The two implementations are independent code paths, and the aligned phase grid makes the discrete reconstruction operator exact for this idealized cell-integrated Gaussian setup. This is a matched-model control, not a PSF-mismatch test.

## Main results

Values are means across 30 seeds.

| RL iterations | Nine stationary RMSE | Nine dithered RMSE | Paired difference (dither − stationary), 95% CI |
|---:|---:|---:|---:|
| 1 | 0.324772 | 0.164999 | -0.159773 [-0.166148, -0.153397] |
| 2 | 0.324772 | 0.149591 | -0.175181 [-0.180777, -0.169584] |
| 3 | 0.324772 | 0.191490 | -0.133282 [-0.139667, -0.126897] |
| 5 | 0.324772 | 0.268636 | -0.056136 [-0.063749, -0.048524] |
| 10 | 0.324772 | 0.416863 | +0.092091 [+0.082187, +0.101996] |

The nine-stationary and single-long reconstructions are numerically identical in every trial and iteration: the maximum absolute image difference across the benchmark was 1.43e-14. This is the expected Poisson-additivity control: the single-long image is formed by summing the same nine stationary Poisson frames.

At the second sampled iteration, mean relative RMSE is about 54% lower in the dithered arm than in the stationary arm. The paired centroid-error difference is -0.007642 detector pixels (95% CI -0.014865 to -0.000418). Mean absolute aperture-flux-ratio error improves from 0.045470 to 0.030417 (paired difference -0.015053; 95% CI -0.022483 to -0.007622).

The result is iteration-sensitive. Dithered RMSE is lowest at iteration two among the five sampled points, then worsens; by iteration ten it is worse than the stationary control. This is evidence that early stopping matters, not a calibrated universal stopping rule. Iteration two is not declared an optimum beyond this sampled curve.

## Interpretation

Within this single idealized Gaussian scene, matched total exposure, photon-only noise, and grid-aligned phases, the nine dither phases add spatial sampling information that the stationary binned frames do not contain. The stationary arm does not improve over the long exposure merely by splitting it into nine Poisson frames. The control therefore isolates phase diversity in this specific model.

The large RMSE gain should not be generalized. The phase grid is deliberately aligned to the 3× reconstruction grid, and the forward model is otherwise perfectly matched. The experiment does not test off-grid phases, read noise, background, PSF mismatch, Airy structure, asymmetric or spatially varying PSFs, intrapixel response, charge diffusion, blind source discovery, or blind lambda selection. It also uses known source centres for aperture metrics.

## Reproducibility

- Benchmark workflow run: 42524365879 (success).
- Python tests workflow run: 42524369756 (success; 41 tests passed).
- Artifact: dither-reconstruction-benchmark, 30 seeds × 5 iteration counts × 3 arms.
- Artifact SHA-256 (ZIP): f3bfbbca9424b72de1bd5b437b99d40a220eaa69a8cb8f607453f7adc34a5659.
- Extracted JSON SHA-256: edb947a0b5fd85cf0977bb17ebc09110d1fb7c41c8c2fa06b75a192bd36dc972.
- Artifact expires 6 February 2027.

## Next tests

1. Repeat with off-grid phases and a finer reconstruction grid, quantifying model mismatch against the analytic reference.
2. Add read noise and background as separate, explicitly matched sensitivity arms.
3. Test broader PSFs and scene classes, including crowded sources and extended structure.
4. Add PSF mismatch and detector-response perturbations.
5. Establish an iteration/stopping rule using a validation set or data-only criterion, then freeze it before a confirmatory seed batch.
6. Only after these tests consider blind-lambda selection. This pilot does not test or establish a blind-lambda benefit.

**Decision:** retain as a positive but narrowly scoped synthetic phase-diversity result. PR remains draft and unmerged.
