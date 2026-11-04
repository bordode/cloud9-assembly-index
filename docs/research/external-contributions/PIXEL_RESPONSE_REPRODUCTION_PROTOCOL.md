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

**Current status:** the full protocol is not yet complete. A limited isolated-source pilot and its null result are recorded in Section 9; the seven-source comparison and robustness tests remain outstanding.


## 9. Initial limited pilot (4 November 2026)

A first, deliberately narrow Cloud-9 pilot is now implemented in
[`research/sandbox/pixel_response_reproduction.py`](../../../research/sandbox/pixel_response_reproduction.py)
with regression checks in
[`tests/test_pixel_response_reproduction.py`](../../../tests/test_pixel_response_reproduction.py).

It uses one isolated circular-Gaussian source on a 21×21 detector, a fixed
`sigma = 1.3` pixels, noiseless area-integrated synthetic data, and a 5×5
sub-pixel phase grid (25 positions). The integrated and centre-sampled models
fit the same data using the same least-squares optimizer, bounds, and stopping
tolerances. Amplitude and background are fitted nuisance parameters.

**Observed pilot result:** both models recover the source centre to numerical
precision in this isolated, symmetric, noise-free control. The centre-sampled
model's mean radial position error is approximately
`4.02 × 10⁻⁷` pixels (maximum approximately `5.68 × 10⁻⁷`); the
area-integrated model's maximum is approximately `3.24 × 10⁻¹⁶` pixels.
There is no meaningful centroid-accuracy advantage for either model in this
specific control.

This is a useful null result, not a failed test: it shows that the reported
position difference does not follow automatically from replacing a pixel
integral with a centre sample for an isolated symmetric source under these
conditions. Blending, asymmetry, multiple-source fitting, noise, PSF mismatch,
and the exact seven-star geometry remain untested. In particular, this pilot
does **not** reproduce or refute Aimy's seven-star result.

The full staged protocol remains incomplete. The next discriminating experiment
is a controlled multi-source scene with known positions and separations, first
noise-free and then with specified noise, while retaining identical fitting
conditions.


## 10. Seven-source crowded-scene pilot (4 November 2026)

The sandbox script now includes
[`run_seven_source_experiment()`](../../../research/sandbox/pixel_response_reproduction.py).
It generates seven circular-Gaussian sources on a 25×25 detector using the
same pixel-area-integrated forward model as the isolated-source pilot. The
PSF width is `sigma = 1.3` pixels. Source positions and fluxes are fixed and
published in the script; separations are deliberately close enough for the
profiles to overlap. The data are noiseless in this first run.

Both fitting methods estimate the same 22 parameters: fourteen source
coordinates, seven positive source amplitudes, and one shared background.
They receive the same initial positions, bounds, optimizer, and tolerances.
Source-specific ±0.5-pixel coordinate bounds preserve source identity and
prevent label swaps from being counted as localization error.

**Observed result for this specified geometry:**

| Fit model | Mean radial position error | RMSE radial error | Maximum radial error |
|---|---:|---:|---:|
| Area-integrated | approximately 1.8 × 10⁻¹⁵ px | approximately 2.1 × 10⁻¹⁵ px | approximately 2.8 × 10⁻¹⁵ px |
| Pixel-centre sampled | approximately 0.06015 px | approximately 0.06260 px | approximately 0.07266 px |

The integrated fit recovers the known parameters to numerical precision.
The centre-sampled fit has a systematic position error in this crowded,
overlapping-source configuration. The mean error is of the same order as
Aimy's reported 0.06 px, but this is **not** a reproduction of Aimy's
experiment: our source geometry, fluxes, detector size, fitting setup, and
other details are independently specified and may differ from hers.

This comparison is a controlled synthetic result under a correctly specified
integrated-data generator. It demonstrates that source overlap can make the
choice of detector forward model consequential in this particular setup.
It does not establish a universal 0.06-pixel error, nor does it establish
that the integrated method will retain this advantage under noise, incorrect
PSFs, different source separations, or different initializations.

**Next controls:** repeat over multiple geometries and sub-pixel phases; add
Gaussian read noise and Poisson counting noise as separately identified
conditions; test PSF-width mismatch; and report convergence and source-wise
bias distributions. Only after these controls should this be compared more
closely with the reported seven-star case.


## 11. Staged robustness implementation (4 November 2026)

A separate sensitivity runner is now present at
[`research/sandbox/pixel_response_robustness.py`](../../../research/sandbox/pixel_response_robustness.py),
with smoke/regression checks in
[`tests/test_pixel_response_robustness.py`](../../../tests/test_pixel_response_robustness.py).
It varies one factor at a time around the seven-source synthetic scene:

- source-spacing scale factors of 0.8, 1.0, and 1.25;
- common sub-pixel phase offsets;
- Gaussian read-noise standard deviations of 1 and 3 counts;
- Poisson counting noise;
- fitting PSF widths of 1.2 and 1.4 pixels against a 1.3-pixel truth.

For each case, both detector models receive the same observed image, initial
parameters, source-specific bounds, and optimizer settings. The runner records
signed x/y errors and per-source radial errors as well as aggregate position
metrics and least-squares cost.

**Noise treatment:** Gaussian read-noise residuals are divided by the stated
read-noise standard deviation. Poisson cases use signed square-root Poisson
deviance residuals, with a non-negative fitted background. These are
noise-appropriate objectives for the two separate noise assumptions; the
Gaussian and Poisson cases are not claimed to have matched signal-to-noise.

**Important status:** the sensitivity runner and tests have been added, but
the full sweep has not yet been independently executed and its numerical
outcomes are not reported here. The current suite uses one fixed realization
per noisy condition, one base source arrangement, and source-specific
±0.5-pixel coordinate bounds centred on the known truth. These bounds supply
source-neighbourhood information and may constrain the localization problem.
The present work therefore remains a controlled sensitivity study, not a
general benchmark. Further work should include multiple noise realizations,
broader or independently initialized fits, additional geometries, and
uncertainty-coverage analysis before making population-level claims.
