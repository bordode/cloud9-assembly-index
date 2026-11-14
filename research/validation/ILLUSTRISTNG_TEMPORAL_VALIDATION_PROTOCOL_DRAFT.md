# Cloud-9: IllustrisTNG temporal validation protocol — preregistration draft

**Date:** 2026-11-14  
**Status:** design draft; no TNG data processed  
**Purpose:** test whether the recovered synthetic null model's temporal behaviour is representative of real simulated cosmological structure, without treating the existing 8.62σ comparison as a discovery claim.

## 1. Gate zero: define the estimand before touching data

The existing implementation sums 15 adjacent-snapshot mutual-information estimates on a logarithmic scale-factor grid. It does not calculate a time-weighted integral. Before TNG analysis begins, the research team must choose and document one primary estimand:

- **Transition-sum estimand:** sum of adjacent-snapshot MI values for a fixed, declared snapshot sequence. Units: bits per specified sequence; cadence-dependent by definition.
- **Time-averaged estimand:** a declared time-weighted average of a well-defined MI trajectory over a fixed cosmic-time interval. Units: bits.
- **Integrated-rate estimand:** define an information rate first, then integrate it over cosmic time. Units depend on the rate definition, e.g. bits.

Do not retrofit one definition into the old JSON. Preserve v3 as an archival result and assign any changed estimator a new version identifier.

The observable corresponding to the reported Cloud-9 value of 87.3 must also be operationally specified, including data source, spatial scale, units, preprocessing, estimator, uncertainty and selection. If its construction is not demonstrably comparable to the TNG statistic, a direct Z-score comparison is not valid.

## 2. Data and provenance

Use public IllustrisTNG data products appropriate to the target question (simulation run, snapshots, subhalo catalogue, merger trees, and particle/cell fields as required). Record:

- simulation name and resolution;
- snapshot numbers and scale factors / redshifts;
- cosmological parameters and unit conventions;
- exact data product and download identifiers;
- subhalo/halo catalogue and merger-tree method;
- target halo selection query and all inclusion/exclusion criteria;
- file checksums, software versions, scripts, and execution environment.

Use the TNG documentation and data release definitions as the authority for field meanings and units. Do not infer physical equivalence from matching labels alone.

## 3. Halo selection and temporal identity

Predefine a target halo mass and redshift window based on the scientific question and the Cloud-9 comparison's operational definition. Select halos using a reproducible catalogue query, not visual inspection of favourable examples.

Track each halo through time using the official merger-tree descendant links. Record mergers, disruptions, central/satellite status, and missing or ambiguous links. Define in advance how to handle branch changes and major mergers. Do not treat unrelated halos at successive snapshots as one trajectory.

Use a sufficiently large and justified halo sample. Report the full selection function and the number of halos lost at each tracking stage.

## 4. Spatial representation and matched samples

Choose one primary representation that can be defined consistently across snapshots, for example:

- density field on a fixed comoving grid in a declared region around the tracked halo; or
- matched gas/dark-matter tracer elements or particle IDs where the scientific question requires Lagrangian tracking.

State whether the analysis is Eulerian (fixed spatial locations) or Lagrangian (following matter elements). These answer different questions and must not be mixed without an explicit mapping.

Specify smoothing, grid resolution, boundary treatment, density definition, physical/comoving units, and treatment of baryons. Keep the same representation and preprocessing across all compared snapshots and null/control conditions.

For an Eulerian analysis, use the same comoving coordinate frame and a fixed spatial mask. For a Lagrangian analysis, document particle/cell identity and mass weighting. Avoid selecting only high-density or well-behaved locations after seeing the MI results.

## 5. Temporal sampling

Select snapshots across a declared cosmic-time interval. Because TNG snapshot spacing is not generally uniform in cosmic time, preserve exact scale factors and cosmic times.

Primary analysis must use a predeclared temporal grid or explicit quadrature rule. Include sensitivity analyses to snapshot cadence and missing snapshots. If the estimand is a transition sum, label it as cadence-dependent and compare only matched snapshot sequences.

## 6. Mutual-information estimator validation

Before applying the estimator to TNG:

1. Test the implementation on independent variables, where MI should approach zero within uncertainty.
2. Test Gaussian pairs with known analytic MI over multiple correlation strengths.
3. Test non-linear dependent pairs and tie-heavy / quantized samples.
4. Run permutation and temporal-shuffle nulls.
5. Sweep sample size, k, normalization and spatial resolution.
6. Cross-check against a maintained reference implementation.
7. Quantify finite-sample bias and uncertainty using repeated subsampling or bootstrap methods that respect spatial/temporal dependence.

Freeze the estimator, k, metric, tie handling, normalization and uncertainty procedure before examining the primary TNG comparison.

## 7. Nulls and controls

At minimum, include:

- temporal permutation/shuffle controls that break temporal correspondence while preserving snapshot marginals;
- spatially shuffled controls that test dependence on spatial structure;
- matched random regions or halos outside the target selection;
- resolution and smoothing controls;
- cadence-matched synthetic nulls processed through the exact same pipeline.

The null ensemble must be large enough to estimate the tail region relevant to any claimed significance. A 100-member ensemble cannot resolve an extreme tail at the level implied by an 8.6σ Gaussian extrapolation. Report empirical exceedance counts and confidence bounds; do not translate zero exceedances into zero probability.

## 8. Primary outcomes and reporting

Predeclare one primary statistic and a small number of secondary diagnostics. Report:

- distribution across halos and snapshots;
- between-halo and within-halo uncertainty separately;
- effect sizes and confidence intervals;
- empirical null exceedance and its uncertainty;
- sensitivity to resolution, cadence, smoothing, sample size, estimator settings and halo selection;
- all exclusions, failed tracks and missing data;
- reproducible scripts and checksums.

Do not use a Gaussian Z-score as the sole tail calibration unless the null distribution's shape and tail behaviour justify it. If the null is non-Gaussian, use an appropriate empirical or model-based calibration with transparent assumptions.

## 9. Decision rules

- **Pass for computational validity:** data lineage, units, halo tracking, and estimator tests pass; results reproduce from a clean environment.
- **Pass for temporal representativeness:** synthetic and TNG distributions agree within predeclared tolerances across primary and key secondary diagnostics, with sensitivity analyses supporting robustness.
- **Inconclusive:** sample size, resolution, tracking, estimator bias, or null-tail precision is insufficient.
- **Fail:** key discrepancies persist or the statistic is not comparable to the Cloud-9 observable.

A pass on computational validity is not a pass on physical representativeness. A pass on representativeness is not, by itself, a discovery claim.

## 10. Current status

- Archived v3 synthetic ensemble: reproduced after documented constructor-keyword correction.
- Estimator calibration: not yet completed.
- Cosmological time calculation validation: not yet completed.
- IllustrisTNG data acquisition and temporal analysis: not started.
- Direct Cloud-9 observable comparability: requires operational definition and provenance.

**No claim of real-data ΛCDM temporal validation is made by this protocol.**
