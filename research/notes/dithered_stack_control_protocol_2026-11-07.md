# Controlled dithered-stacking test: protocol and decision criteria

**Date:** 7 November 2026  
**Status:** preregistered follow-up protocol; no results yet  
**Scope:** synthetic blind-regularisation study; not an astronomical-data validation

## Motivation

A nine-phase sub-pixel-dithered pilot reported much smaller blind-lambda RMSE penalties than a single-frame baseline. The pilot is encouraging, but it does not yet isolate the cause: the improvement could come from phase diversity, simply having nine independent noise realizations, a larger total photon budget, or implementation details of the shift/forward operator.

The next experiment must compare acquisition strategies at matched total information and exposure, not merely compare one frame with nine frames.

## Primary comparison: three acquisition arms

For each scene, binning factor, noise regime, and master seed, generate one underlying continuous/high-resolution scene and construct three observations:

1. **Single long exposure:** one frame with total exposure budget (E).
2. **Nine stationary exposures:** nine frames at the same detector phase, each with exposure (E/9).
3. **Nine phase-dithered exposures:** nine frames at nine genuinely sub-pixel phases, each with exposure (E/9).

The nine-frame arms must have the same total exposure (E), same number of detector readouts, and matched noise assumptions. The dithered and stationary arms differ only in the known phase offsets.

### Noise accounting

- For photon-counting noise, generate Poisson counts using each frame's expected signal at exposure (E/9), then sum or jointly fit the nine frames. Do not rescale a single noisy frame and call it nine exposures.
- If read noise is included, apply the same per-read noise model to both nine-frame arms. The single-long-exposure arm has one readout and is therefore a separate practical comparator; report this difference explicitly.
- Include a photon-noise-only primary analysis and a separate read-noise sensitivity analysis. Do not mix their conclusions.
- Use paired master seeds so all three arms share the same scene and controlled noise-generation seed family.

## Forward model and numerical controls

- Model each frame's phase shift in the forward operator; do not shift already-binned images as a substitute for detector-phase diversity.
- Use genuinely fractional-pixel phases. Include a diagnostic confirming that the chosen phases do not share a common alias null for the tested binning factor.
- Avoid circular wraparound as the primary boundary condition. Simulate on a padded field and score a common valid interior region, or use a validated non-periodic operator with its exact adjoint.
- Verify the forward/adjoint inner-product identity numerically for every acquisition arm:
  `<A x, y> = <x, A* y>`
  with a stated relative-error tolerance.
- Test phase-shift operators against an independent spatial-domain implementation on impulses and random arrays. Explicitly document any Nyquist/band-limit convention.
- Require objective and residual convergence checks. A solver's success flag alone is insufficient.

## Regularisation selection and oracle definition

Use the same reconstruction objective, regulariser, parameterisation, stopping tolerances, and lambda grid for the three arms.

For each individual simulated dataset:
- The **oracle lambda** is the grid value minimising reconstruction RMSE against withheld truth on the common valid region.
- The **blind criteria** (whiteness, L-curve, GCV, discrepancy) receive observations and the declared noise model only; they must not access truth.
- Report blind-minus-oracle RMSE as both absolute error and percentage of oracle RMSE.
- Report selected lambda, oracle lambda, grid-boundary hits, and the full RMSE(lambda) curve. A selected lambda matching the oracle on a coarse grid is not sufficient evidence of a reliable selector.

Refine the lambda grid around each coarse-grid optimum. Repeat the GCV calculation with multiple independent Hutchinson probes and report the estimate's variability. A single probe is exploratory only.

## Basin-shape hypothesis

Test the hypothesis that the RMSE basin becomes shallower at higher noise.

For every cell, define the near-optimal basin as the contiguous lambda interval around the global grid minimum satisfying:

`RMSE(lambda) <= 1.02 * RMSE_min`

Report:
- basin width in log10(lambda) decades;
- left and right widths separately (to preserve asymmetry);
- curvature of log-RMSE versus log-lambda near the minimum, using a documented local fit;
- the location of the oracle minimum and any boundary truncation.

Compare basin width and curvature between noise regimes within each scene and binning factor. Do not infer a general high-noise flattening effect from pooled means alone. The hypothesis is supported only if the paired within-cell changes are consistent across independently generated noise realizations and scenes.

## Replication and analysis plan

- Use at least three scene classes: a smooth extended field, a structured extended field, and a crowded point-source field.
- Include binning factors 2, 3, and 4, and at least two noise levels corresponding to the existing low/high pilot regimes.
- Use at least 10 independent master seeds per cell for the first confirmatory pass; increase this if confidence intervals remain broad.
- Freeze scene arrays, phase offsets, seeds, lambda grid, solver tolerances, and scoring region before evaluating blind criteria.
- Report paired differences with confidence intervals, not only cell means.
- Keep exploratory grid tuning separate from the confirmatory run.

## Primary decision rules

A phase-diversity benefit is supported only if the nine-dither arm improves blind-selection cost or reconstruction error over the nine-stationary arm at matched total exposure and readout count, with paired uncertainty excluding a negligible effect.

A pure multi-frame/noise-averaging benefit is indicated if the stationary and dithered nine-frame arms improve similarly over the single-frame arm.

The shallow-basin hypothesis is supported only if the 2%-basin width increases and local curvature decreases at higher noise in a reproducible, within-scene paired analysis. A broad basin alone does not establish a noise-dependent mechanism.

A claim that dithering “solves” blind-lambda selection is not justified by a small pilot or by GCV matching a coarse-grid oracle. The defensible claim, if replicated, is narrower: phase-diverse multi-frame observations reduce blind-selection regret under the tested forward model and noise assumptions.

## Required outputs

1. Machine-readable per-trial results, including full RMSE(lambda) curves and blind criterion diagnostics.
2. Operator/adjoint and shift-validation test logs.
3. A figure comparing all three acquisition arms at matched total exposure.
4. A basin-width/curvature figure by scene, binning factor, and noise level.
5. A provenance note recording code commit, dependencies, seeds, solver tolerances, and artifact checksums.

## Current evidence boundary

The previously supplied pilot summary reports four dithered cells, one noise realization per cell, a six-point lambda grid, periodic shift boundaries, and one Hutchinson probe. Its reported penalties (whiteness 0–3.4%, L-curve 1.8–6.0%, GCV 0.0%) are provisional and do not establish the matched-exposure phase-diversity effect or the basin-shallowness mechanism. This protocol is a proposal for a new test; it contains no new measured results.
