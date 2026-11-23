# Blind-background-estimation validation protocol

**Frozen:** 2026-11-11  
**Repository:** `bordode/cloud9-assembly-index`  
**Branch:** `research/dithered-stack-control-protocol`

## Question

Does the dither-associated reconstruction advantage persist when the true detector background is hidden and must be estimated from the observations?

## Locked design

- 30 fresh paired seeds: `2026111400–2026111429`, disjoint from all prior development and validation seed ranges.
- Richardson–Lucy iterations fixed at **2**.
- True mean background rate: 0.5 counts per detector pixel per total-exposure unit.
- Horizontal linear gradient amplitudes: 0.0, 0.25 and 0.45; true map is `0.5 + amplitude*x`, where x spans −1 to +1 across detector columns.
- The true map is used only to generate Poisson observations and score estimation error. It is never supplied to reconstruction.
- Background estimator: fit non-negative left/right endpoint rates by Poisson maximum likelihood, using only the outer three detector-pixel border. The fitted horizontal linear map is supplied to reconstruction.
- Nine stationary, nine aligned-dither and nine off-grid-dither frames; total exposure 1.0 in each arm.
- Same three-source continuous Gaussian scene, detector geometry and reconstruction operator as prior validations.
- Primary outcome: fixed-interior relative RMSE. Secondary outcomes: known-centre centroid error, absolute aperture-flux error, background-map RMSE and mean-background error.
- Paired per-seed differences with 95% t confidence intervals.

## Calibration assumption and interpretation boundary

The method assumes the outer three-pixel detector border is source-free and representative of the same detector-fixed horizontal background field across the image. This is an explicit calibration-region assumption, not fully blind estimation without any spatial prior or calibration region. The true map is hidden from the estimator and reconstruction. The model remains restricted to horizontal linear gradients; curved/vertical/time-varying/source-correlated backgrounds, read noise, PSF mismatch and realistic calibration systematics remain untested. Off-grid shifts retain bilinear high-resolution cell interpolation.

The iteration count and estimator are frozen before fresh-seed execution. Do not tune them on validation outcomes.
