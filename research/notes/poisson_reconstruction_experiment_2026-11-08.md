# Photon-limited reconstruction experiment: first controlled implementation

**Date:** 8 November 2026  
**Related PR:** https://github.com/bordode/cloud9-assembly-index/pull/41  
**Status:** implementation added; CI and repeated-seed benchmark pending

## Question

Does a nine-frame subpixel-dithered observation improve high-resolution reconstruction over one long exposure when total exposure is held fixed? A stationary nine-frame arm separates phase diversity from merely splitting the exposure.

## Reconstruction

The solver is non-negative Poisson Richardson-Lucy maximum likelihood using the existing shift-and-bin forward operator and its exact discrete adjoint. It estimates a high-resolution cell-flux image rather than fitting the known Gaussian source parameters. Iteration count is recorded as an early-stopping regularizer; the experiment reports an iteration curve rather than declaring a truth-selected optimum.

## Independent acquisition and exact stationary control

- The data generator uses direct continuous Gaussian pixel-area integrals from the independent analytic reference.
- Nine stationary frames each receive one ninth of the total exposure and independent Poisson photon counts.
- The single-long image is formed by summing those same nine stationary Poisson frames. By Poisson additivity, this is a valid one-long-exposure photon-count realization and gives the stationary and long controls exactly the same sufficient statistic.
- Nine dithered frames receive the same per-frame exposure, with distinct subpixel phases; expected pixel counts are computed directly from the continuous analytic reference.
- No read noise, background, or detector effects are included in this first reconstruction experiment.

The reconstruction path is separate from data generation: continuous Gaussian integrals generate detector observations, while a non-parametric high-resolution image is reconstructed with the discrete shift-and-bin operator. At bin factor three, the default ±1/3-pixel phase grid aligns to high-resolution cells. Off-grid phase reconstruction is not yet part of this benchmark.

## Metrics

- Relative RMSE on the same fixed science interior for every arm.
- Source-centroid error and aperture-flux ratio in radius-two-pixel apertures centred on known source positions. These are conditional localization/photometry metrics, not blind source detection.
- Single-long versus stationary-stack maximum absolute reconstruction difference, which should be numerical zero when the same summed counts and exposure are used.

## Required analysis before conclusions

Run paired seeds and report the full iteration curve for all three arms. The stationary and long arms should agree to numerical precision. Any dither advantage must be evaluated across seeds and across the iteration curve, not selected from one favorable iteration. Report source-position and flux metrics alongside image RMSE. Do not claim a general dither benefit from this Gaussian, photon-only, known-source control.

## Limitations

This is a controlled synthetic experiment with axis-aligned Gaussian sources, Poisson noise only, known phase offsets, and a simplified detector. It omits read noise, background, PSF mismatch, intrapixel response, asymmetric or spatially varying PSFs, Airy diffraction, optical distortion, and blind source discovery. Early stopping is a regularization choice and needs a predeclared or validation-based selection rule before any final comparative claim.
