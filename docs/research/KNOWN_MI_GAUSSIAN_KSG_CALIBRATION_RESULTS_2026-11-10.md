# Known-MI Gaussian KSG Calibration: First Results

**Run date:** 2026-11-10  
**Code commit:** `15cfe8e988a01c6f8e081aaedc5232db6a36f7f2`  
**Workflow:** MI estimator known-information calibration, run #6  
**Artifact:** `mi-estimator-calibration-c44a6b121f41c0db803de5e595d4ced9151c38e7`  
**Seed:** 20261109  
**Replicates:** 100 per condition  
**Conditions:** 80 (5 sample sizes × 4 k values × 4 correlations), 8,000 total estimates  
**Estimator:** KSG-1, max-norm joint neighbourhood, exact v3-style radius/count convention; raw and zero-clipped summaries

## 1. Execution and software checks

The dedicated workflow completed successfully. Dependency installation, all five focused calibration tests, the full 80-condition experiment, and artifact upload passed. The separate repository Python test workflow (#485) also passed.

The JSON artifact is the machine-readable source for every value summarized below. This report is a descriptive reading of that artifact, not a new independent replication.

## 2. Main findings

### 2.1 Raw estimates show systematic negative finite-sample bias

Across the four k values, mean raw bias under independent Gaussian controls improved as sample size increased:

| N | Mean raw bias across k (bits) | Mean raw RMSE across k (bits) |
|---:|---:|---:|
| 64 | -0.1215 | 0.1510 |
| 128 | -0.0815 | 0.1077 |
| 256 | -0.0611 | 0.0801 |
| 512 | -0.0448 | 0.0600 |
| 1,200 | -0.0277 | 0.0393 |

For nonzero Gaussian correlations, the raw estimator also showed negative bias throughout this tested grid. At N=1,200, the mean raw bias across k was -0.0296 bits at rho=0.2, -0.0254 bits at rho=0.5, and -0.0223 bits at rho=0.8.

This is a finite-sample calibration finding for the tested bivariate Gaussian distributions and implementation. It does not establish the estimator's behavior for other marginals, nonlinear dependencies, spatially dependent samples, or the full v3 time series.

### 2.2 Zero-clipping changes the estimator's behavior substantially

For the true-zero independent controls, the raw estimates were negative in approximately 85–90% of replicates across the sample-size grid. Clipping moved the average close to zero: mean clipped bias across k ranged from +0.0050 bits at N=64 to +0.0023 bits at N=1,200.

That apparent near-zero mean is not evidence that clipping is harmless. It is produced by replacing every negative estimate with exactly zero. At N=1,200, the mean fraction set to zero under independent controls was about 85%.

For weak dependence (rho=0.2), clipping reduced the average negative bias but did not remove it: mean clipped bias across k was approximately -0.017 to -0.018 bits for N=64 through N=1,200.

For stronger dependence (rho=0.5 and 0.8), estimates were rarely or never negative at larger sample sizes, so clipping did not materially change the results. Raw negative bias remained.

### 2.3 Larger k reduced error in this particular grid

Averaged over sample sizes and nonzero correlations, raw RMSE decreased from approximately 0.146 bits at k=2 to 0.080 bits at k=10. This is a descriptive pattern in this tested design, not a basis for selecting k on the same data or assuming k=10 is generally optimal.

## 3. Interpretation

The first calibration does **not** justify treating the current estimator as calibrated or unbiased. It identifies a measurable negative finite-sample bias in the Gaussian controls, and shows that zero-clipping conceals negative estimates by creating a point mass at zero. The residual bias persists even at N=1,200.

Accordingly:

- Do not interpret a clipped estimate near zero as proof of zero dependence.
- Do not compare clipped and unclipped summaries as if they were interchangeable statistics.
- Do not apply a universal correction factor from this grid to v3 outputs.
- Do not choose k solely because it looks best in this calibration grid; any tuning requires a separate training/calibration set and held-out evaluation.
- Do not translate these bias summaries into p-values, sigma scores, or cosmological evidence.

The v3 generator and its historical output were not modified by this experiment.

## 4. What this experiment did not test

The harness currently evaluates independent-observation, bivariate Gaussian controls only. It does not yet test:

1. nonlinear dependence with known MI;
2. non-Gaussian marginals;
3. spatial correlation or effective sample size;
4. fixed-location dependence across adjacent snapshots;
5. temporal null processes or the v3 generator's shared-field persistence;
6. empirical coverage of confidence intervals for individual estimates;
7. sensitivity to alternative KSG counting conventions, tie handling, or radius tolerances.

The reported percentile interval across replicate estimates is descriptive. The bootstrap interval is for mean estimator bias across independent replicate datasets; it is not an interval for an individual estimate and does not substitute for a coverage study.

## 5. Decision and next steps

**Decision:** retain the estimator as an exploratory diagnostic only. Do not promote its outputs to calibrated scientific measurements or use this first grid to revise historical significance claims.

Next, in order:

1. Audit the estimator implementation against the precise KSG-1 counting convention, including strict versus inclusive marginal-radius counts and the fixed (10^{-12}) radius offset. Preserve the historical v3 implementation while testing alternatives side by side.
2. Add nonlinear and non-Gaussian known-MI controls.
3. Add an explicit interval-coverage study using independent replicate datasets.
4. Only after these checks, proceed to spatially correlated fields and temporal null controls.

A successful software workflow establishes that the experiment ran and produced an artifact. It does not by itself establish estimator adequacy.

## 6. Reproducibility

The full result file is retained as the GitHub Actions artifact for workflow run #6 (90-day retention). The workflow is linked from PR #44. All 80 condition rows, replicate counts, bootstrap intervals, raw estimates summaries, clipped summaries, seed and limitations are included in the JSON artifact.


## 7. Paired KSG boundary-convention audit — 2026-11-10

A follow-up paired audit completed on the same review-branch commit,
`b8b68b57164166ff5b87068a57ce0b2c3c1af3cd`. It evaluated 80 Gaussian
conditions (N=64, 128, 256, 512, 1,200; k=2, 3, 5, 10; rho=0, 0.2, 0.5,
0.8), with 100 paired replicate datasets per condition: 8,000 paired
comparisons.

The comparison was between two **combined implementation conventions**:

- Historical harness/v3-style: kth joint radius plus (10^{-12}), with
  inclusive marginal ball counts.
- Strict KSG-1-style: uninflated kth joint max-norm radius, with marginal
  distances counted strictly below that radius.

Because the radius offset and marginal inclusion rule change together, this
audit does not separately identify the contribution of each change. The
historical v3 implementation and archived outputs were not modified.

### 7.1 Aggregate results

| N | Historical mean bias (bits) | Strict mean bias (bits) | Historical mean RMSE (bits) | Strict mean RMSE (bits) |
|---:|---:|---:|---:|---:|
| 64 | -0.1427 | -0.0140 | 0.1848 | 0.1279 |
| 128 | -0.0920 | +0.0003 | 0.1280 | 0.0936 |
| 256 | -0.0635 | +0.0023 | 0.0907 | 0.0658 |
| 512 | -0.0472 | -0.0003 | 0.0692 | 0.0510 |
| 1,200 | -0.0265 | +0.0043 | 0.0429 | 0.0339 |

Across all 80 condition cells, the strict convention had lower RMSE in 79
cells and lower absolute bias in 79 cells. The one exception was
N=1,200, k=10, rho=0.8: the historical convention was already very close to
the known MI (bias -0.00034 bits; RMSE 0.0347), while the strict convention
had bias +0.0198 bits and RMSE 0.0401.

The average paired shift (strict minus historical estimate) was positive
across the tested grid, declining from about +0.129 bits at N=64 to +0.031
bits at N=1,200. The direction and magnitude varied by condition.

### 7.2 Interpretation and limits

This is strong evidence that the **combined strict convention tested here**
behaves better on this particular independent bivariate-Gaussian grid than
the historical inclusive-plus-offset convention. It is not proof that the
strict implementation is universally superior, unbiased for other
distributions, or valid for spatially/temporally dependent data. The
N=1,200, k=10, rho=0.8 exception also cautions against describing the
strict convention as uniformly better.

The audit does not justify retroactively correcting historical (A_c)
values, applying a universal offset, or replacing the historical v3
estimator silently. Preserve the archived estimator and results. Any future
candidate estimator change should be separately versioned and tested against
non-Gaussian, nonlinear, tie/duplicate, spatial-dependence, and temporal-null
controls, with held-out evaluation.

### 7.3 Reproducibility and duplicate workflow check

The paired audit and original Gaussian calibration both completed and
uploaded artifacts in workflow runs #15 and #16. The two runs were triggered
against the same commit and used fixed seeds. Their corresponding JSON files
were byte-for-byte identical (SHA-256):

- Gaussian calibration:
  `cca7f2c4431c2e34001019db64c77237fae54fc63d4d5ea6565ce50abf26cb88`
- Paired convention audit:
  `0b07fe0b7d3967a3f8997da3a827f6ac322be7235ec9d40b7fa99320c736de40`

Each artifact contains 80 condition rows with 100 replicates per condition;
all reported numeric fields were finite. Identical outputs demonstrate
deterministic reproduction under the same code, seed, and environment. They
are not two statistically independent replications.

**Decision:** the paired audit supports advancing the strict convention as a
candidate for further validation, not changing v3 or promoting the estimator
to a calibrated scientific measurement. Nonlinear/non-Gaussian controls,
interval coverage, and spatial/temporal null tests remain outstanding.
