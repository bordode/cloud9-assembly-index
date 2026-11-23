# Independent pixel-integrated reference and common scoring region

**Date:** 8 November 2026  
**Status:** analytic reference implemented; 38-test CI validation passed  
**Related PR:** https://github.com/bordode/cloud9-assembly-index/pull/41

## Why this validation is needed

The dither operator's adjoint tests prove that its forward and transpose implementations agree algebraically. They do not establish that bilinear shifts reproduce physical pixel-area integration. This stage adds an independent continuous-source reference that does not call the dither operator.

## Reference scene

The validation scene is a mixture of axis-aligned two-dimensional Gaussian sources. Each source has a total flux, a subpixel centre, and separate row/column Gaussian widths. The reference integrates the Gaussian analytically over rectangular areas using Gaussian cumulative distribution functions.

Two independent integrations are provided:

- gaussian_scene_subpixel_integrals: integrate the continuous scene into high-resolution subpixel cells. The resulting array stores cell-integrated flux, not point samples.
- pixel_integrated_gaussian_frame: integrate the same continuous scene directly over detector-pixel footprints at a specified phase.

The detector phase convention matches the operator: positive phase moves scene content toward increasing row/column indices, so detector pixel (i,j) integrates the unshifted scene over [i-phase_y, i+1-phase_y] × [j-phase_x, j+1-phase_x].

## Common scoring region

The validation arrays include a four-pixel detector border around a fixed 20×22 science region. All error comparisons crop exactly that same science region using crop_common_interior. The crop is independent of phase and binning factor; padding is not scored. This prevents changing field boundaries from changing the evaluation footprint.

This is a controlled synthetic boundary test, not yet a proof that four pixels is sufficient for every PSF or scene. Wider PSFs, longer wings, or larger shifts require a correspondingly larger guard region.

## What the validation tests distinguish

1. At zero phase, block-summing integrated subpixel cells should reproduce exact detector pixel integrals to floating-point precision.
2. At bin factor three, phases of ±1/3 pixel align exactly to one high-resolution cell. The discrete shift should then reproduce the analytic pixel-area integral to floating-point precision.
3. Off-grid phases such as (0.23, -0.17) require interpolation. In this fixed three-source control, relative RMSE was approximately 5.52% at 2×, 0.812% at 4×, 0.259% at 8×, and 0.0790% at 16×. This is a measured convergence example for this scene and phase, not a universal error bound.
4. Extending the padding from four to eight detector pixels leaves the fixed scored interior unchanged to the test tolerance (relative tolerance 1e-11; absolute tolerance 1e-10).

The aligned-phase result is an exactness check for this analytic Gaussian control, not evidence that arbitrary bilinear phases are exact.

## Limits

- The analytic reference uses a separable, axis-aligned Gaussian mixture. It does not yet cover Airy diffraction, asymmetric or spatially varying PSFs, detector intrapixel sensitivity, charge diffusion, optical distortion, or wavelength dependence.
- The scene is continuous and noiseless in this validation. The Poisson acquisition simulator remains a separate stage.
- The padding-extension test covers four versus eight detector pixels for this geometry and phase. Wider PSFs, longer wings, larger shifts, or different scene placements still require their own guard-region checks.
- No reconstruction or blind-lambda comparison is included. No dither benefit is claimed.
