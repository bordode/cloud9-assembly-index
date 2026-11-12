# Matched-exposure acquisition model

**Date:** 8 November 2026  
**Status:** implementation stage; no reconstruction or blind-lambda results  
**Related PR:** [#41](https://github.com/bordode/cloud9-assembly-index/pull/41)

## Purpose

The dither operator now supports a stack of nine fractional-phase frames and its exact discrete adjoint. This note defines the next controlled layer: generate observations with equal total exposure while keeping the number of detector readouts explicit.

## Three acquisition arms

For a common padded high-resolution scene-rate array, binning factor, total exposure E, and master seed:

1. **Single long:** one stationary detector exposure of E, one readout.
2. **Nine stationary:** nine stationary exposures of E/9, nine readouts.
3. **Nine dithered:** nine exposures of E/9 at nine distinct fractional detector-pixel phases, nine readouts.

The default dither phases form a 3×3 grid with row and column offsets -1/3, 0, +1/3 detector pixels. The stationary arm uses zero phase for every frame. Dither phases are applied to the high-resolution rate scene before detector block integration, not to already-binned images.

## Noise convention

- Each pixel in each frame receives an independent Poisson draw from that frame's expected photo-electron count.
- The photon-noise-only configuration (read_noise_sigma=0) is the primary comparison.
- Optional read noise is an independent Gaussian draw per detector pixel per readout, with the same per-read standard deviation in the two nine-frame arms.
- Consequently, summing nine frames accumulates nine read-noise variances, while the single-long arm has one readout. This is an explicit practical difference, not something to conceal by rescaling.
- Do not create nine frames by splitting or rescaling one noisy long-exposure image.
- A fixed integer seed reproduces the complete three-arm simulation. Use multiple independent master seeds for inference; one seed is only a deterministic test fixture.

## Implementation

research/sandbox/matched_exposure_acquisition.py exposes:

- nine_phase_grid()
- simulate_matched_exposure_arms(...)

The simulator returns the three noisy observations, their expected-count arrays, and metadata describing exposure, phase units, and readout/noise conventions. Stack arrays have shape (frame, detector_row, detector_column) and remain separate; reconstruction code must decide how to combine them.

## Model limitations and safeguards

- The underlying shift is the existing non-periodic bilinear interpolation operator followed by block summation. It is a controlled discrete model, not a continuous optical PSF or exact pixel-response integral.
- The high-resolution input is a padded non-negative rate scene. Use sufficient padding and score a common valid interior region so boundary loss cannot masquerade as a dither effect.
- This simulator does not yet add background, dark current, gain variation, cosmic rays, correlated detector noise, exposure-to-exposure drift, or calibration uncertainty.
- It does not reconstruct images, select lambda, or establish any dither benefit.
- Compare nine-stationary with nine-dithered to isolate phase diversity at matched total exposure and readout count. Compare single-long with nine-stationary to expose the cost/benefit of multiple readouts.

## Decision boundary

No claim about improved reconstruction, blind-lambda selection, or shallower RMSE basins is supported until the acquisition model is independently validated, the common interior is fixed, and paired multi-seed reconstruction trials are completed. The bilinear operator's exact adjoint establishes algebraic consistency only; it does not validate the physical detector model.
