# Calibration-border contamination stress-test protocol

**Frozen:** 2026-11-12  
**Repository:** `bordode/cloud9-assembly-index`  
**Branch:** `research/dithered-stack-control-protocol`

## Question

How sensitive is the estimated-background reconstruction result to contamination of the detector-border pixels used for calibration?

## Locked design

- 30 fresh paired seeds: `2026111500–2026111529`, disjoint from all earlier development and validation ranges.
- True horizontal gradient amplitude fixed at 0.25; true background map remains `0.5 + 0.25*x`, with x spanning -1 to +1 across detector columns.
- Three calibration contamination fractions: 0%, 5%, and 15% of the outer three-pixel border pixels.
- Contaminated calibration pixels receive an additional Poisson background rate of 1.0 per detector pixel per total-exposure unit. The same deterministic contamination mask is applied to all three acquisition arms within a seed.
- The contamination is present in the observed frames. The estimator is not told which pixels are contaminated and continues fitting its original non-negative horizontal linear model to all border pixels.
- 9 stationary, 9 aligned-dither, and 9 off-grid-dither frames; total exposure 1.0 per arm.
- Richardson–Lucy reconstruction fixed at two iterations.
- Primary outcome: fixed-interior relative RMSE. Secondary outcomes: aperture-flux error, centroid error, background-map RMSE, and mean-background error.
- 30 paired seeds per contamination level; paired per-seed differences with 95% t confidence intervals.
- The clean 0% condition is included as the within-experiment reference.

## Interpretation boundary

This is a deliberately controlled calibration-contamination stress test, not a model of every detector defect. The contaminant mask is restricted to the calibration border and is shared across acquisition conditions. The estimator remains a simple horizontal-linear Poisson maximum-likelihood fit. Results do not establish robustness to arbitrary background-model mismatch, temporal drift, read noise, PSF mismatch, or real instrument systematics.

The seed range, contamination fractions, contamination strength, estimator, and two-iteration reconstruction are frozen before execution. Do not tune them against the validation results.
