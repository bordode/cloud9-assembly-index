# Observation-only deblending protocol (C9-PIXEL-RESPONSE-DEBLENDING-001)

**Status:** initial noiseless pilot plus a 180-trial Gaussian-noise / PSF-width grid completed. Joint refinement recovered all seven sources in every trial at assumed PSF widths 1.1 and 1.3 px for noise σ=0 and 1; performance declined at σ=3. A 1.5 px assumed width failed to recover all seven in every condition. Geometry and Poisson-noise robustness remain untested.

## Question

Can an observation-derived detector separate overlapping point sources when a local-maximum detector returns one blended peak, without using the true source count, positions, or amplitudes to generate candidates?

This experiment follows the failed 30-configuration / 150-condition local-maximum sensitivity grid. It changes the detection method rather than extending that grid.

## Evidence boundary

- Synthetic truth positions and amplitudes are used only to render the observation and, after candidate generation, to score detections.
- Candidate generation must not read truth positions, truth amplitudes, or the known source count.
- The algorithm may use the declared detector dimensions and an explicitly stated PSF family and width. The PSF width is a model assumption, not a hidden truth lookup; a mismatch sweep is required.
- The source-count stopping rule must be fixed before inspecting truth-scored results.
- No fit may be described as blind merely because its starting coordinates were generated from the image. Any source-count, PSF, or threshold tuning against truth must be labelled oracle/tuning data and excluded from held-out evaluation.

## Proposed detector

Use iterative pixel-integrated PSF matched filtering and residual subtraction:

1. Estimate a constant background from the observation using a declared robust statistic. Record the estimate.
2. Correlate the background-subtracted residual with a normalized pixel-integrated PSF template. Search the detector field only; do not restrict the search around truth coordinates.
3. Refine the strongest observation-derived candidate's subpixel position and non-negative amplitude by fitting a single-source pixel-integrated PSF to the current residual. Keep the PSF width fixed to the declared assumed value in the primary experiment.
4. Subtract that fitted source model from the residual and repeat. Retain the full sequence, including candidates later rejected by the stopping rule.
5. Select the number of sources using a predeclared information criterion (primary: BIC computed from the residual sum of squares and the number of added parameters). Stop when adding a component no longer improves the criterion. Do not force seven components.
6. As a separate secondary stage, jointly refit the retained candidates with the same pixel-integrated forward model. Use physical detector-field bounds only, not source-specific truth-centred bounds. Report optimizer convergence, parameter-bound hits, and assignment swaps.

The first implementation is deliberately simple and auditable. The pilot in `research/sandbox/iterative_psf_deblending.py` uses a normalized matched-filter proposal, a single-source pixel-integrated Gaussian fit, sequential residual subtraction, and a profiled Gaussian BIC stopping rule. On the first deterministic noiseless scene, BIC accepted seven components and rejected the eighth. The greedy candidate coordinates alone matched only three truth sources within 1 px; four candidates were unmatched. A subsequent joint refit of those seven components, using only the observation and greedy initial candidates, recovered all seven truth sources within 1 px with no unmatched candidates. Joint-refit radial errors ranged from approximately 1.7e-10 to 7.95e-5 px. This is a promising single-scene synthetic result, not evidence of robustness: the generator and fit used the same pixel-integrated Gaussian family and the same 1.3 px PSF width, with no added noise. If residual subtraction or joint refinement fails under blends, preserve that failure rather than adding unreported heuristics.

The first robustness grid expanded this to 180 trials: 20 independent seeds for each of three Gaussian read-noise levels (σ=0, 1, 3) and three assumed PSF widths (1.1, 1.3, 1.5 px), with the generated scene fixed at σ=1.3 px. All 42 Python tests passed. Results (mean matched truth sources within 1 px; count of trials recovering all seven) were:

| Gaussian noise σ | Assumed PSF σ | Mean matched after joint refit | All-seven trials |
|---:|---:|---:|---:|
| 0 | 1.1 | 7.00 | 20/20 |
| 0 | 1.3 | 7.00 | 20/20 |
| 0 | 1.5 | 3.00 | 0/20 |
| 1 | 1.1 | 7.00 | 20/20 |
| 1 | 1.3 | 7.00 | 20/20 |
| 1 | 1.5 | 3.00 | 0/20 |
| 3 | 1.1 | 6.75 | 18/20 |
| 3 | 1.3 | 6.50 | 12/20 |
| 3 | 1.5 | 3.00 | 0/20 |

The greedy candidate positions alone matched only 2–3 sources on average in each condition; the joint fit supplied most of the localization improvement. All 180 joint optimizers reported successful numerical termination, including many trials with incorrect source recovery. Thus optimizer success is not a correctness metric. This grid indicates strong sensitivity to PSF-width mismatch and increasing Gaussian noise, but only for one fixed synthetic geometry and detector. The 1.1 px case performed well despite being narrower than the true 1.3 px width; this asymmetry should not be generalized without further tests. The BIC stopping rule is provisional and assumes an independent Gaussian residual model; its nominal statistical interpretation may be compromised by structured/correlated residuals.

## Comparators

- Existing local-maximum detector: the already executed 150-condition grid is the baseline negative result.
- Iterative PSF subtraction with the declared BIC stopping rule: primary candidate method.
- Fixed-seven-component fit initialized from truth-jittered positions: explicitly labelled informed-start oracle/control, never a blind detector.
- If practical, a fixed-seven-component fit initialized from detector-uniform positions: diagnostic control for optimizer-start sensitivity, not a candidate-count selector.

## Evaluation plan

### Stage 1: deterministic geometry

Start with the existing seven-source synthetic geometry and the same 21 x 21 detector and 1.3 px integrated Gaussian PSF. Add controlled separation variants (compact, nominal, and expanded geometry) without changing the candidate-generation rules.

### Stage 2: noise

For each geometry, run at least 20 independent seeds for:
- noiseless observations;
- Gaussian read noise with standard deviations 1 and 3 detector-count units;
- Poisson counting noise generated from non-negative expected pixel counts.

Both the detector and fit receive only the resulting observation and declared model assumptions. Repeated seeds are used to estimate variability, not to select the best-looking seed.

### Stage 3: model mismatch

Repeat selected conditions with assumed PSF widths 1.1, 1.3, and 1.5 px while the synthetic generator remains fixed at its declared width. Keep the primary detection rule and BIC penalty unchanged.

### Metrics

Report separately:
- candidate count selected by the observation-only stopping rule;
- true-source recall and candidate precision after one-to-one assignment within a declared 1 px radius;
- false-positive and missed-source counts;
- localization error for matched sources (mean, median, RMSE, and maximum);
- source-assignment swaps and duplicate detections;
- residual sum of squares, BIC sequence, and optimizer convergence;
- performance distributions across seeds, not only averages.

A candidate count of seven is not itself a success. A successful condition requires all seven truth sources matched within the declared radius and no unmatched candidates. Report partial recovery honestly.

## Hold-out and anti-peeking controls

- Freeze the geometries, seeds, PSF assumptions, stopping rule, and matching radius before running the scored grid.
- Use one geometry/seed subset for debugging and a disjoint set for held-out evaluation.
- Do not adjust the BIC threshold, PSF width, minimum separation, or background estimator after viewing held-out truth scores.
- If any rule is changed after results are inspected, label the next run exploratory and create a fresh held-out set.
- Publish all failed runs and all selected/rejected candidate sequences.

## Decision gates

1. **Implementation gate:** unit tests establish deterministic outputs, truth-free candidate-generation inputs, finite fitted parameters, and correct detector-coordinate conventions.
2. **Detection gate:** proceed only if held-out precision and recall are stable across seeds and geometries. Do not start the joint seven-source fit merely because the selected count equals seven.
3. **Localization gate:** compare integrated and centre-sampled forward models only on the same detected candidate sets and observations. Keep detection error separate from conditional localization error.
4. **Generalization gate:** no broad claim until noise and PSF-mismatch results are reported across the predeclared grid.

## Current status

The existing local-maximum detector failed the tested grid: it returned one candidate in all 150 scored conditions and matched one of seven synthetic sources. The iterative PSF-subtraction method above has passed an initial single-scene synthetic demonstration and a 180-trial Gaussian-noise / assumed-PSF-width grid. It is promising under this one geometry for assumed widths 1.1–1.3 px, but degrades sharply at 1.5 px and at the highest tested noise level. The robustness/generalization gates remain open because source geometry is fixed, Poisson noise is not tested, and the BIC residual model is provisional.

## Interpretation limit

This is a controlled synthetic point-source experiment. Even a successful result would not establish performance on astronomical images, arbitrary extended structure, crowded real fields, or Aimy's original data. Real-image validation would require documented image provenance, detector calibration, PSF characterization, and an independently frozen evaluation protocol.
