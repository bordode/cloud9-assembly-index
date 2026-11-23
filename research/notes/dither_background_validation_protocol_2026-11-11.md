# Independent validation protocol: known Poisson-background dither experiment

**Protocol frozen:** 2026-11-11  
**Repository:** `bordode/cloud9-assembly-index`  
**Branch:** `research/dithered-stack-control-protocol`

## Purpose

Test whether the dither-associated reconstruction improvement observed in the development benchmark generalises to an independent set of Poisson realisations under the same controlled scene and known-background assumptions.

## Frozen design

- Development seeds remain unchanged: `2026111000–2026111029`.
- Independent validation seeds: `2026111200–2026111229` (30 seeds; disjoint from development).
- Richardson–Lucy iteration count: **2 only**, fixed before validation. No iteration tuning or selection is permitted using validation outcomes.
- Background rates: 0, 0.1, 0.5, 1.0, and 2.0 counts per detector pixel per total-exposure unit.
- Conditions: nine stationary frames, nine aligned-dither frames, and nine off-grid-dither frames.
- Total exposure, scene, detector geometry, phase grids, reconstruction operator, and metrics remain matched to the development experiment.
- Same validation seed is paired across the dither conditions and stationary controls.
- Report condition means and paired per-seed differences with 95% t confidence intervals for relative RMSE, centroid error, and absolute aperture-flux-ratio error.

## Interpretation boundary

The background is known exactly, spatially uniform, and temporally constant. This is not a test of blind background estimation. Read noise, gradients, dark-current drift, PSF mismatch, and blind source detection remain outside scope. The off-grid reconstruction continues to use bilinear fractional-cell shifts, so the validation retains that known model approximation.

A validation result that does not reproduce the development direction must be reported as such; do not revise the fixed iteration count or silently change the protocol after inspecting results.
