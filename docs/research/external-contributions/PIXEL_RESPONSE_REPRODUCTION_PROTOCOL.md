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


## 12. Repeated-noise trial control (4 November 2026)

The sensitivity runner now includes
`run_repeated_noise_trials`. It supports repeated Gaussian read-noise and
Poisson-counting-noise trials. Each trial receives a distinct noise seed, while
the initialization seed is held fixed across the series. Within each trial,
the integrated and centre-sampled models fit the same observed image. The
runner reports across-trial means, sample standard deviations, minima, and
maxima for mean radial error, radial RMSE, maximum radial error, and signed
mean x/y error.

This separates variation due to the generated noise from variation due to
changing optimizer starts. It does **not** test initialization sensitivity;
that remains a separate control. The function requires at least two trials,
but a scientifically useful report should use a substantially larger number
and include uncertainty intervals or paired trial-level comparisons.

The repeated-trial function and a small three-trial regression smoke test have
been added. The smoke test verifies seed handling and finite aggregate output;
it is not a reported scientific result. No repeated-trial numerical outcomes
are claimed until the full trial series is executed, inspected, and recorded.

The same limitations from Section 11 remain: one synthetic scene, known
source-neighbourhood bounds of ±0.5 pixels, and no claim of reproducing Aimy's
original experiment. A later initialization study should vary starting
positions independently, retain source identity without silently using the
true positions as tight bounds, and report convergence failures as well as
successful fits.


### 12.1 Fixed-observation initialization sensitivity

A complementary function, `run_initialization_trials`, now holds the generated
observation fixed while varying the initialization seed. This is paired with
the repeated-noise design above:

- repeated-noise trials: vary the observation/noise seed, hold initialization
  fixed;
- initialization trials: hold the observation seed fixed, vary the starting
  positions.

A three-start regression smoke test checks that the observation seed remains
constant and the initialization seeds vary as intended. This test verifies
experimental bookkeeping and finite output, not optimizer globality or
scientific performance.

**Remaining limitation:** both controls still use source-specific ±0.5-pixel
bounds centred on the known truth. Varying starting positions within those
bounds is not a test of blind source association or unconstrained localization.
A later experiment should widen or remove these bounds, introduce explicit
source-association handling, and report failures, source swaps, and convergence
diagnostics rather than silently excluding difficult fits.


## 13. Wider and unbounded source-position diagnostics (4 November 2026)

The robustness runner now accepts an explicit source-position bound half-width
or `None` for unbounded coordinates. The default remains the existing
truth-centred ±0.5-pixel diagnostic bound so earlier experiments remain
reproducible. The new option is a control mechanism, not evidence that a
blind-localization experiment has already succeeded.

For evaluation, fitted positions are matched to the known truth positions by
minimum-total-distance assignment (Hungarian assignment). This separates
physical source localization from arbitrary parameter-array ordering and
makes source-label permutations countable. The runner records the assignment
permutation, number of non-identity assignments, total assignment distance,
optimizer status/evaluation count, and position-bound hits where bounds are
active. Both competing forward models still receive the same observation,
initialization, bound policy, optimizer budget, and fitting parameterization.

Regression tests now cover unbounded fitting diagnostics and validation of
invalid bound widths. These are bookkeeping and execution checks only. The
unbounded and progressively widened fits have **not yet been run as a
scientific sweep**, so no claim is made about source swaps, convergence rates,
or localization accuracy outside the previous ±0.5-pixel neighbourhoods.

The next execution should compare at least ±0.5, ±1, ±2 pixels, and unbounded
coordinates over multiple independent starts. It must retain every run,
including non-convergence and poor fits; report source-association permutations,
bound hits, and residual diagnostics; and avoid using truth-centred starts as
a substitute for blind source detection. A separate initialization design
should generate starts independently of the true source coordinates. Even
with assignment matching, a fit with missing, duplicated, or spurious sources
requires an explicit detection/association policy rather than forcing a
one-to-one seven-source match.


## 14. Position-bound sweep implementation (4 November 2026)

The robustness runner now includes `run_position_bound_sweep`, which executes
paired integrated-versus-centre fits at ±0.5, ±1, ±2 pixels, and unbounded
coordinates. It holds the generated observation fixed and varies the
initialization seed across starts. It records per-model optimizer success or
failure, radial localization error, source-assignment permutations, source
swaps, bound hits, and evaluation counts. Non-successful optimizer terminations
are retained as records rather than causing the entire sweep to abort.

An additional `detector_uniform` initialization policy starts the seven model
components independently across the detector field, without using the true
source coordinates to seed their positions. This is a stronger initialization
stress test, but it is not yet a complete blind-detection experiment: the
model is still told to fit exactly seven components, and the one-to-one
Hungarian assignment still assumes seven true sources.

The new regression test executes a small one-start-per-bound smoke sweep. It
checks that all four bound conditions and both models are represented. This
CI test is not a substitute for the multi-start scientific run. The full
sweep's quantitative results must be generated and reviewed separately before
any conclusion about localization stability or the advantage of either model.


## 15. Initial three-start position-bound sweep results (4 November 2026)

A three-start, fixed-observation, noise-free synthetic sweep was executed in
GitHub Actions run 41920555994 (commit `42edd5e`). The initialization policy
was `truth_jitter`: each start was perturbed around the known seven-source
truth positions. This tests optimizer-start repeatability within an informed
initialization regime, not blind detection.

| Position bounds | Integrated model radial RMSE (px) | Centre model radial RMSE (px) | Optimizer failures (both models) | Source swaps (maximum) | Bound hits (both models) |
|---|---:|---:|---:|---:|---:|
| ±0.5 px | 3.94e-15 | 0.062135 | 0 | 0 | 0 |
| ±1.0 px | 2.28e-15 | 0.062135 | 0 | 0 | 0 |
| ±2.0 px | 4.13e-15 | 0.062135 | 0 | 0 | 0 |
| Unbounded | 3.50e-15 | 0.062135 | 0 | 0 | 0 |

Each condition contains three starts per model. The integrated-model errors
are at numerical precision for this correctly specified, noiseless synthetic
scene. The centre-sampled model remains near 0.0621 px across all four bound
widths. No bound hits or source swaps occurred in these informed-start runs.
The result therefore suggests that the observed difference in this particular
scene is not an artefact of the ±0.5-pixel bound width. It does **not** establish
robust blind localization, noisy performance, or generalization to other scenes.

A separate detector-uniform, unbounded initialization diagnostic has now been
added to the regression suite. Its result is pending the latest workflow run;
no conclusion about convergence from detector-wide starts is made here.


## 16. Detector-wide unbounded initialization diagnostic (4 November 2026)

Three additional noiseless fits per forward model were started from independently
uniformly distributed source coordinates across the detector, with no
truth-centred coordinate bounds. The same observed image and each identical
initial parameter vector were supplied to the two models in each paired run.
GitHub Actions run 41920828422 (commit `b591e88`) passed all 34 regression
tests and emitted the following diagnostics:

| Start | Integrated-model radial RMSE (px) | Centre-model radial RMSE (px) | Integrated swaps | Centre swaps |
|---|---:|---:|---:|---:|
| 1 | 1,363,901.13 | 254,900.98 | 7 | 7 |
| 2 | 509.29 | 6,176,639.56 | 7 | 6 |
| 3 | 4.25e-15 | 11,011.20 | 6 | 5 |

All six optimizer calls reported numerical termination success, but these
position errors and assignment permutations show that **optimizer success is
not localization success**. Only one of the six fits recovered the seven
positions to numerical precision; the other fits were catastrophically wrong.
The one-to-one assignment reports the best permutation among the seven fitted
components, but cannot repair a fit that has moved components far from the
true scene or become degenerate.

This is a negative but useful result: simply removing truth-centred bounds and
randomizing starts does not create a reliable blind source-localization method.
The next method-development step is to constrain candidate source coordinates
to the physical detector field (rather than to known truth neighbourhoods),
use a defensible initialization/detection stage, monitor amplitude/background
parameter degeneracy, and report residual norms and parameter-bound hits.
A true blind-detection evaluation must also allow missed and spurious sources;
a forced seven-to-seven assignment is not enough. The controlled ±0.5 to
unbounded truth-jitter sweep remains a separate, informed-start sensitivity
result and must not be conflated with this detector-wide diagnostic.


## 17. Physical detector-field initialization control (4 November 2026)

The detector-wide initialization diagnostic has been refined. The earlier
unbounded experiment allowed fitted source coordinates to move arbitrarily far
outside the detector, producing enormous coordinate errors despite successful
optimizer termination. That result remains documented in Section 16 as a
failure mode of unconstrained optimization, not as a valid detector-localization
benchmark.

The runner now supports a separate **physical detector-field bound**. Candidate
source coordinates are constrained to the detector's actual coordinate extent
(±12 pixels for the current 25×25 detector), without using the known true source
positions. This is distinct from truth-centred ±0.5, ±1, or ±2 pixel bounds.
The detector-uniform initialization remains independent of the true source
coordinates. Both forward models receive the same physical bounds and paired
starting positions.

The runner also records the maximum absolute fitted coordinate, and regression
tests check that detector-bounded fits remain inside the physical field. The
detector-wide three-start diagnostic is now rerun under these physical bounds;
its numerical outcomes must be reviewed before drawing conclusions. CI success
will establish only that the implementation and checks execute correctly.

**Remaining limitations:** the model is still told to fit exactly seven
components; Hungarian assignment still forces a seven-to-seven match; the
initialization is random rather than detection-informed; and the experiment
does not yet allow missed or spurious sources. This is a constrained
localization stress test, not a complete blind source-detection pipeline.


### 17.1 Three detector-bounded random-start outcomes (4 November 2026)

The detector-field-bounded, detector-uniform diagnostic completed in Python
workflow run 41925771611 (commit `a005306`; 35 tests passed). The same three
observation/start-seed pairs were fitted by both forward models. All six
optimizer calls reported numerical termination success, and all fitted
coordinates remained within the detector field. However, optimizer termination
did not imply successful recovery:

| Start | Integrated radial RMSE (px) | Centre radial RMSE (px) | Integrated swaps | Centre swaps |
|---|---:|---:|---:|---:|
| 1 | 8.515 | 8.515 | 6 | 6 |
| 2 | 4.959 | 4.958 | 6 | 7 |
| 3 | approximately 0 | 4.958 | 6 | 5 |

Only one of six fits (the integrated model on start 3) recovered the seven
source positions to numerical precision. The other five fits had large
localization errors despite remaining inside the physical detector field.
The two models behaved similarly on starts 1 and 2; the integrated model
recovered the truth on start 3 while the centre-sampled model did not.

This small three-start diagnostic is **not enough to estimate a reliable
success rate or claim a general advantage**. It does establish that merely
adding physical field-of-view bounds does not solve the initialization
problem. The repeated source-assignment swaps also show why the forced
seven-to-seven matching must be interpreted alongside the actual spatial
errors, not as a detection score.

The result motivates a detection-informed initialization stage and a more
complete evaluation that permits missed and spurious sources. The next
experiment should use more independent starts and compare a principled
candidate-detection initializer against detector-uniform random starts,
while keeping the paired forward-model comparison fair. No noisy-scene
conclusion is drawn from this noise-free diagnostic.


## 18. Exploratory cross-scene noise-boundary check reported by Kimi (4 November 2026)

A separate exploratory sandbox run was reported by Kimi after the detector-initialization discussion. It tested whether the empirical noise/binning relationship reported for Aimy's Andromeda crop, approximately sigma * b = 0.075, transfers to other image content. Kimi reported using a pixel-area-integrated block-mean forward model, three additional 180×180 scenes (a Hubble deep-field crop, a Moon image, and a synthetic star field), a four-value regularization-parameter grid, and a conjugate-gradient solver.

**These are externally reported exploratory results, not yet an independently reproduced Cloud-9 result.** The sandbox run completed its initial sweep in approximately 25.6 seconds. A finer lambda-grid/tighter-convergence refinement timed out and was not completed. The full executable code, exact image provenance/preprocessing, noise seeds, lambda values, convergence diagnostics, and machine-readable result table have not yet been captured in this repository. The figures below should therefore be treated as provisional and attributed to Kimi.

### 18.1 Reported observations

Kimi reported the following approximate zero-crossing noise levels:

| Scene | b=2 | b=3 | b=4 | b=5/6 | Reported sigma* × b behaviour |
|---|---:|---:|---:|---:|---|
| Synthetic stars | 0.016 | 0.015 | 0.022 | 0.017 | approximately 0.03 to 0.09; not constant |
| Hubble deep-field crop | 0.075 | >0.08 | >0.08 | >0.08 | approximately 0.15 at b=2, then at least 0.24 |
| Aimy's Andromeda crop (previously reported by Aimy) | 0.035 | 0.025 | 0.020 | 0.015 | approximately 0.075 |

Kimi also reported high-noise upturns in the Moon and synthetic-star curves. For the Moon at b=2, reported gain changed from +10.9% at sigma=0.01 to +0.6% at sigma=0.03 and +22.7% at sigma=0.08. For the synthetic stars at b=2, gain reportedly became negative around sigma=0.02–0.03 and rose to +18.7% at sigma=0.08. For the Hubble crop, Kimi reported an approximately flat 7% gain for b≥3 across the tested noise range.

Kimi's interpretation is that the zero-crossing is a local transition in the relative advantage of the reconstruction methods, not necessarily a point beyond which regularization has no utility. At higher noise, denoising may again improve the regularized estimator's score. This is a hypothesis suggested by the reported curves, not yet a general conclusion.

### 18.2 Critical comparability and verification limits

Several controls are required before comparing these values quantitatively with Aimy's reported sigma * b ≈ 0.075:

- Kimi reports adding independent noise at native sensor-pixel resolution before block averaging. Under an ideal independent-noise block mean, the binned standard deviation scales as sigma/b. The meaning and normalization of sigma must be matched to Aimy's experiment before comparing thresholds; the numerical sigma values may not represent the same noise convention.
- The regularization parameter was selected by an oracle over a coarse four-point grid. This is useful for exploring achievable performance under the tested setup, but it is not a blind parameter-selection method and may move the apparent crossing.
- The reported conjugate-gradient tolerance was rtol=1e-3. Kimi noted that individual percentages may carry roughly 1–2% numerical uncertainty; the refinement run did not complete.
- Zero-crossings were interpolated from a sparse noise sweep. Their precision is therefore limited by the grid and interpolation procedure.
- The three scenes differ in content, but the reported intra-block contrast values alone do not establish that contrast causes the threshold differences. Scene structure, preprocessing, normalization, noise placement, binning, metric, and regularization selection may all contribute.
- The high-noise upturn should be checked against a wider noise sweep, finer lambda search, tighter solver tolerances, repeated noise realizations, and paired per-trial results.
- Exact source images, licenses/provenance, crop coordinates, preprocessing, random seeds, full parameter grid, baseline definition, gain formula, and complete output should be recorded before attempting an independent reproduction.

The strongest provisional conclusion is therefore narrow: **the reported cross-scene results do not support treating sigma * b ≈ 0.075 as a universal law.** They motivate a controlled study of scene dependence and noise convention. They do not yet establish a universal exponent, a contrast-only mechanism, or a general high-noise recovery branch.

This section records Kimi's reported sandbox observations separately from Aimy's original results and Cloud-9's own independently executed experiments. It does not claim that Cloud-9 has rerun or verified Kimi's sweep.


## 19. Observation-derived peak-candidate pilot (4 November 2026)

The next Cloud-9 implementation step adds an observation-only local-maximum
candidate detector to `research/sandbox/pixel_response_robustness.py`,
exposed as `run_image_peak_detection()`.

The detector:
- generates the same controlled seven-source synthetic observation used by
  the pixel-response pilot, with optional Gaussian-read or Poisson noise;
- applies a declared Gaussian smoothing width and a small local-maximum
  neighbourhood;
- ranks peaks by filtered observed intensity and applies a declared
  minimum-separation rule;
- repeats detection over explicit fractions of the observed filtered dynamic
  range;
- does not use true source coordinates, true amplitudes, or a forced
  seven-candidate list to generate candidates;
- uses the known truth coordinates only after detection to score candidate
  coverage, missed truth sources, and unmatched candidates within a declared
  1 px diagnostic matching radius.

The function deliberately does **not** launch the seven-component optimizer
yet. If the detected candidate count differs from seven, it reports that the
case is not ready for the fixed-seven-component fit rather than silently
adding, deleting, or moving candidates using hidden truth. Even exactly seven
candidates are marked as fit-not-yet-run: candidate count alone does not prove
correct source identity or reliable initialization.

This is an implementation and regression-test milestone, not an experimental
finding. The threshold sweep's actual candidate counts and coverage must be
read from the test/workflow output before drawing conclusions. A later stage
can add fitting only after the detection policy is shown to behave sensibly
across thresholds and noise realizations, with false positives, missed
sources, duplicate candidates, and assignment swaps retained in the record.

The pilot remains synthetic and does not reproduce Aimy's original seven-star
experiment or establish astronomical detection performance.
