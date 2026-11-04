# Proposed Reproducibility Protocol: Pixel-Integrated Detector Models

**Status:** Proposed Cloud-9 follow-up protocol; not an experiment result.  
**Motivation:** Aimy's reported seven-star synthetic comparison, recorded in [the attributed research note](AIMY_LAPLACIAN_PRIOR_NOISE_STUDY_2026-11-04.md), contrasts integrating a blurred source over each detector pixel with evaluating the blur only at the pixel centre. The reported position errors are 0.004 px and 0.06 px, respectively. Cloud-9 has not independently reproduced these figures.

This protocol is designed to test the scope and robustness of that reported effect without assuming the result will replicate.

## 1. Questions

1. Does pixel-area integration reduce systematic position bias relative to pixel-centre sampling when the simulated detector measures finite pixel areas?
2. How does the difference depend on source position within a pixel, blur width, sampling ratio, source brightness, and noise?
3. Does the advantage persist when the assumed point-spread function (PSF) or detector response is slightly misspecified?
4. Does better sub-pixel parameter estimation remain distinct from recovering image detail that the detector did not measure?

## 2. Synthetic ground truth

Begin with a fully specified synthetic scene rather than a compressed astronomical image.

- Define source positions, fluxes, and a stated PSF (initially a circular Gaussian; add a second, non-Gaussian PSF only as a separate experiment).
- Define detector pixel boundaries and generate each noiseless pixel value by numerical integration of the continuous blurred scene over that pixel's area.
- Record the numerical integration method, oversampling factor or quadrature tolerance, coordinate convention, and convergence check.
- Use fixed, published random seeds for every noisy realization.
- Preserve the exact continuous source parameters as ground truth.

The synthetic generator must be independent of the fitting implementation wherever practical, to reduce the risk that the same coding error is shared by both.

## 3. Matched comparison

Fit identical simulated measurements with at least two forward models:

- **Area-integrated model:** predicts each detector value by integrating the model signal over the pixel area.
- **Centre-sampled model:** predicts each detector value from the model signal at the pixel centre.

Keep the following identical between methods: data, fitted parameters, optimizer, stopping criteria, initialization policy, parameter bounds, noise likelihood, and evaluation code. Report any unavoidable differences.

Include a third diagnostic where useful: a centre-sampled model with a calibrated effective response or other explicitly stated correction. Do not silently tune one method against the hidden truth while leaving the other untuned.

## 4. Experimental factors

Vary one factor at a time in an initial factorial design, then test selected interactions:

- **Sub-pixel phase:** source centres at pixel centre, edge, corner, and a uniform grid of phases within one pixel.
- **Sampling:** several PSF widths relative to pixel pitch, including the reported 1.3-pixel case if its definition can be recovered.
- **Signal-to-noise:** noiseless data plus multiple noise levels, with the noise model stated (for example, Poisson, Gaussian read noise, or both).
- **Source configuration:** isolated stars first; then controlled close pairs and the seven-source arrangement.
- **Background and detector response:** constant background initially; later test gradients, pixel-response nonuniformity, and mild PSF mismatch as separate factors.

Do not combine all complications in the first reproduction. A staged design makes failure modes identifiable.

## 5. Metrics

Report parameter-estimation and image-prediction performance separately.

**Position estimation**
- Per-source signed x/y bias and radial error.
- RMSE and median absolute position error across sources and realizations.
- Error distributions by sub-pixel phase, not only a single pooled average.
- Confidence-interval coverage, where uncertainty estimates are available.

**Forward prediction**
- Residual maps and residual summaries.
- Flux and background bias.
- Sensitivity to initialization and optimizer convergence.

Do not use a single image RMSE as a substitute for source-centre accuracy. Do not describe parameter localization as recovery of arbitrary above-Nyquist image structure.

## 6. Essential controls and failure checks

- Verify that the area-integration routine converges as numerical integration is refined.
- Verify coordinate axes, pixel boundaries, row/column ordering, and units with small hand-checkable cases.
- Confirm zero-noise behaviour independently; exact recovery is expected only if the model is identifiable, correctly specified, and the optimizer reaches the correct solution.
- Test whether the centre-sampling bias changes sign or magnitude with sub-pixel phase.
- Check whether any advantage disappears or reverses under PSF mismatch.
- Run an independent implementation or small analytic benchmark before treating a numerical difference as robust.
- Publish failed runs, non-convergence, and all baseline corrections alongside successful results.

## 7. Reporting and provenance

Every reported result should identify:
- code revision and environment;
- scene parameters and random seeds;
- detector and PSF definitions;
- numerical integration accuracy;
- noise model and realization count;
- optimizer, initialization, and stopping criteria;
- exact metric definitions and aggregation method.

Label outcomes as **reproduced**, **partially reproduced**, **not reproduced**, or **not yet tested**. A successful synthetic reproduction would support the stated measurement-model lesson under the tested conditions; it would not establish that undersampling is generally harmless or that lost image detail can be reconstructed without additional assumptions.

## 8. Interpretation boundary

The central hypothesis is narrow: when a detector integrates signal over finite pixel areas, a forward model that represents that integration may avoid systematic parameter-estimation error introduced by a point-sampling approximation.

This is not a claim that pixel integration creates information absent from the measurements. Sub-pixel estimation can be possible when the source model and measurement process jointly constrain the parameters; arbitrary structure removed by sampling, blur, or noise is not thereby restored.

**Current status:** protocol only. No Cloud-9 experiment has been run under this specification, and no new numerical result is asserted.
