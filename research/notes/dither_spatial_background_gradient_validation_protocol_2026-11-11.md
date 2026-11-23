# Spatial-background-gradient validation protocol

**Frozen:** 2026-11-11  
**Repository:** `bordode/cloud9-assembly-index`  
**Branch:** `research/dithered-stack-control-protocol`

## Question

Does the relative-RMSE advantage previously observed for aligned and off-grid dithering persist when the detector background is spatially varying rather than uniform?

## Locked design

- Richardson–Lucy iterations: **2 only**, fixed from the prior development and independent validation; no tuning on these data.
- Fresh seeds: `2026111300–2026111329` (30 seeds), disjoint from development seeds `2026111000–2026111029` and uniform-background validation seeds `2026111200–2026111229`.
- Mean background rate: 0.5 expected counts per detector pixel per total-exposure unit.
- Horizontal linear gradient amplitudes: 0.0, 0.25, 0.45 counts per detector pixel per total-exposure unit.
- The background map is `0.5 + amplitude * x`, where x spans -1 to +1 across detector columns. Thus the three maps have ranges 0.50–0.50, 0.25–0.75, and 0.05–0.95, respectively; all have mean 0.5.
- The same detector-fixed map is applied to every frame and supplied exactly to the reconstruction likelihood.
- Nine stationary, nine aligned-dither and nine off-grid-dither frames; same seed and map across paired conditions.
- Same three-source continuous Gaussian scene, detector geometry, total exposure, phases and reconstruction operator as the prior validation.
- Primary metric: fixed-interior relative RMSE. Secondary metrics: known-centre aperture centroid and absolute flux errors.
- Paired per-seed differences with 95% t confidence intervals.

## Interpretation boundary

This tests a **known** detector-fixed horizontal gradient. It does not test blind background estimation, vertical or curved gradients, temporal drift, source-correlated backgrounds, read noise, PSF mismatch, or blind source detection. Off-grid shifts remain approximated by bilinear high-resolution cell interpolation.

The validation is independent by seed, but deliberately changes only the background spatial model relative to the prior fixed-iteration validation.
