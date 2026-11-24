# Poisson source-count model-selection calibration protocol

**Experiment ID:** `C9-DEBLENDING-POISSON-MODEL-ORDER-CALIBRATION-001`  
**Status:** preregistered protocol; no results yet  
**Parent research:** paired AIC/BIC acceptance pilot (PR #42)  
**Data:** synthetic, with truth withheld from all detector and model-selection decisions

## 1. Research question

When the number of point sources is unknown, how well do nominal Poisson AIC and BIC select source count across controlled changes in scene complexity, source identifiability, image size, PSF width, flux contrast and background?

The previous 27-trial pilot showed that AIC accepted more sources and produced more unmatched candidates without a reliable recovery gain. That result is limited to one seven-source scene family, one PSF family and a small number of trials per condition.

This study is not designed to find a penalty that maximizes recovery on one synthetic scene. It is designed to estimate model-order calibration and identify conditions in which either criterion over-selects or under-selects.

## 2. Statistical model and key qualification

The primary arm retains the independent-Poisson-pixel observation model:

`Y_i \sim \operatorname{Poisson}(\mu_i(\theta))`

for disjoint detector pixels (i=1,\ldots,n), conditional on the pixel-integrated scene model. Under this data-generating model, PSF overlap changes the expected intensity in each pixel and couples fitted parameters; it does not by itself make disjoint pixel counts dependent. Therefore (n) is the number of observed pixels in the likelihood, not an arbitrary PSF-width-adjusted count.

There is a separate model-selection concern. Under a smaller-source model, an added source has non-negative amplitude; at zero amplitude its position is not identified. This is a boundary/non-identifiability situation, so the regularity assumptions behind textbook large-sample BIC approximations may not hold cleanly for source-number selection. The study will measure this behaviour empirically rather than presume that a different fixed penalty is correct.

The primary study will not add correlated read noise, resampling or rebinning. Those require distinct observation models and will be specified as later extensions.

## 3. Study structure: separate proposal generation from model selection

### Track A — fixed-candidate model-order calibration

1. Generate a candidate pool using a truth-blind, frozen proposal procedure.
2. Fit the same nested candidate models to each observation using the same Poisson likelihood, bounds, optimizer settings and stopping tolerances.
3. Record the best fit at each candidate source count, not only the greedy path's final model.
4. Apply AIC and BIC to the same fitted model ladder.
5. In a separate diagnostic control only, evaluate an oracle-informed candidate ladder whose initial locations are supplied from truth. Label this strictly as an upper-bound diagnostic, never as detector performance.

Track A asks whether the criteria choose the right model order when candidate availability and fit procedure are held as constant as possible.

### Track B — end-to-end detector

Run the full blind proposal-generation and acceptance pipeline with AIC and BIC on identical count images and paired seeds. Record proposal-generation failures, optimizer failures, model-selection rejections and final source-count errors separately.

Track B measures operational performance. A Track B miss must not automatically be attributed to the information criterion if the required candidate was never proposed or successfully fitted.

## 4. Controlled scene factors

Use a prespecified, balanced fractional-factorial scenario set rather than an unmanageably large full Cartesian product. Include the following factor levels across the scenario set:

| Factor | Planned levels |
|---|---|
| True source count | 0, 1, 3, 5, 7 |
| Nearest-neighbour separation | 1.0, 1.5, 2.0, 3.0 times PSF sigma |
| Flux contrast | 1:1, 1:3, 1:10 |
| PSF sigma | 1.0, 1.3, 2.0 pixels |
| Background | low, moderate, high; exact rates frozen in the implementation manifest |
| Image dimensions | 21×21, 31×31, 41×41, with matched crop/padding controls |

Include both regular and irregular source layouts. Freeze scene coordinates, amplitudes, PSF integration, background rates, exposure and seed schedule before running confirmatory trials. Keep source configurations and photon budgets documented so that changing image dimensions does not silently change the scene brightness or exposure.

Include blank/no-source scenes to measure false-positive model selection. Include single-source scenes to measure whether the procedure invents companions around a well-fitted source.

### Image-size and crop controls

For selected identical underlying scenes, compare:
- a native detector crop;
- a larger field containing the same source scene plus additional background-only pixels;
- a nested crop of that same generated field.

Do not interpret these as independent replications. They are paired sensitivity controls for the observation window and BIC's dependence on the number of observed pixels. The likelihood must include the background contribution in every retained pixel.

## 5. Paired execution and sample size

- Use identical Poisson observations for AIC and BIC within every trial.
- Use a frozen seed manifest and retain all per-trial records.
- Pilot at least 20 seeds per prespecified scenario to validate runtime, numerical stability and scoring.
- After the pilot, freeze the scenario set and analysis code; run at least 30 new seeds per scenario for confirmatory estimates. Do not reuse pilot seeds in confirmatory intervals.
- If computational limits require fewer trials, report the achieved count and uncertainty; do not describe an underpowered pilot as confirmatory.
- Keep optimizer tolerances, parameter bounds, PSF model, initialization policy and maximum source count identical between criteria.

## 6. Outcomes

### Primary model-order outcomes
- exact selected source-count rate;
- over-selection and under-selection rates;
- false-positive source count on blank scenes;
- source-count error distribution;
- calibration by true source count and scene condition.

### Source localization and detection outcomes
- matched truths and missed truths using a prespecified assignment method and tolerance;
- unmatched candidates;
- localization error for matched sources;
- flux error and uncertainty where available.

### Pipeline diagnostics
- proposal recall by rank;
- number of candidate fits attempted;
- optimizer convergence/failure;
- selected versus best available candidate;
- deviance, AIC and BIC for each fitted model order;
- Hessian/Jacobian conditioning or another declared identifiability diagnostic;
- boundary hits and near-zero fitted amplitudes;
- runtime and optimizer function evaluations.

Report paired AIC-minus-BIC differences with uncertainty intervals. Report results by condition, not just one pooled mean. Use bootstrap intervals clustered by generated scene/seed where appropriate; do not treat multiple methods on the same observation as independent samples.

## 7. Analysis plan

1. Validate the simulator and pixel-integrated forward model against noiseless cases before drawing Poisson observations.
2. Verify the likelihood and criterion calculations on small hand-checkable examples.
3. Freeze the proposal pool and candidate-model ladder before evaluating Track A criteria.
4. Keep the truth table inaccessible to detection and selection code; join it only after predictions are written.
5. Report Track A and Track B separately.
6. Estimate false-selection rates on zero-source and low-source scenes, and recovery/under-selection on crowded scenes.
7. Examine criterion behaviour against identifiability diagnostics, but do not infer causation from correlation alone.
8. Do not tune a penalty, effective sample size or decision threshold on confirmatory seeds.
9. If a modified criterion is proposed later, evaluate it on a new held-out seed set and report the nominal AIC/BIC baselines unchanged.

## 8. Decision rules and interpretation

- Retain BIC as the implementation default unless a broader, independently replicated result justifies a change.
- Do not switch to AIC merely because it selects more sources.
- A criterion is not declared superior on mean matched-source count alone; false extras, exact source-count calibration and uncertainty matter.
- If Track A performs well but Track B does not, investigate proposal generation and optimization before changing the criterion.
- If both tracks show systematic over/under-selection in specific conditions, describe the condition and uncertainty rather than proposing a universal correction.
- No real-astronomy performance claim follows from synthetic results.

## 9. Separate future extensions — not part of this protocol

1. **Correlated detector noise:** specify the physical noise process (for example, a Gaussian read-noise covariance component), simulate it, and use a likelihood that includes that covariance. Do not feed correlated observations to an independent-Poisson likelihood and call the result a BIC calibration.
2. **Resampling/rebinning:** propagate the transformed-data covariance and compare with fitting native detector pixels.
3. **Real-image validation:** only after simulator, likelihood, calibration and provenance checks; use independently characterized data and avoid treating unknown truth as known.

## 10. Reproducibility record

Before confirmatory execution, commit:
- scenario manifest and exact parameter values/units;
- seed manifest or deterministic seed-generation rule;
- simulator and forward-model version;
- candidate proposal and fitting configuration;
- analysis/scoring code and assignment tolerance;
- expected artifact schema;
- software versions and workflow identifier.

The output artifact must preserve per-trial observations' metadata, truth identifiers, blind predictions, candidate ladders, criterion values, diagnostics and post-hoc scores. Store aggregate summaries alongside—not instead of—the per-trial records.

**Current status:** protocol only. No new benchmark has been run, no result is implied, and no detector behaviour or default has changed.
