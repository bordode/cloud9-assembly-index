# Cloud-9 v3: independent code-level methods review

**Review date:** 2026-11-14  
**Scope:** recovered corrected v3 implementation and the 100-member reproduction comparator  
**Status:** static review; no changes to historical source or master

## Executive assessment

The 100-member reproduction is a strong computational result: the corrected recovery implementation reproduces the archived member outputs within the declared tolerance. This review does not overturn that finding.

It does, however, identify methodological issues that must be resolved before interpreting the output as a physically validated time-integrated cosmological assembly statistic. Most importantly, the implementation labels a sum of adjacent-snapshot mutual-information estimates as a temporal integration, while the snapshots are non-uniformly spaced in cosmic time. The code also uses an approximate cosmic-time conversion that ignores the supplied H0 argument.

These are review findings about the recovered synthetic model, not evidence that the archived reproduction is arithmetically wrong.

## Findings

### Finding 1 — The reported temporal quantity is a sum, not a time integral

**Location:** `recovered_cloud9_null_ensemble_v3_corrected.py`, temporal MI block around lines 295–307.

The code computes a KSG estimate between each adjacent pair of snapshots and accumulates it as:

```python
mi = ksg_mi_2d(rho_t_norm, rho_tp1_norm, k=3)
A_c += mi
```

There is no multiplication by the elapsed cosmic time `t[i+1] - t[i]`, nor another quadrature weight. The scale-factor grid is logarithmic, so adjacent snapshots are not equally spaced in cosmic time.

**Implication:** the present `A_c` is a discrete sum of adjacent-snapshot mutual-information values. It is not, as implemented, a time integral in units such as bit·Gyr. Its value can depend on snapshot cadence and placement. Calling it “integrated over cosmic time” is not justified without a defined estimand and weighting rule.

**Required resolution:** decide whether the intended observable is (a) a sum of transition information across a specified sequence, (b) a time-averaged quantity, or (c) a continuous-time integral of a defined information rate. State the units and discretization rule. Do not silently add weights to the archival reproduction; any revised estimator must be versioned as a new method.

### Finding 2 — The cosmic-time helper ignores its H0 argument

**Location:** `cosmic_time_Gyr`, around lines 70–78.

The function accepts `H0`, but sets `H0_Gyr = 1.0 / 14.4` as a fixed approximation. Consequently, changing the supplied Hubble parameter does not change the time conversion. The integral also omits radiation density, which may matter at the high-redshift end of the integration.

**Implication:** the time coordinate is not consistently derived from the cosmological parameters supplied to the model. This matters for relaxation times and for any future time-weighted statistic.

**Required resolution:** use a documented cosmology implementation with consistent units and parameters (including radiation where appropriate), or explicitly constrain and justify the approximation. Add numerical tests against a trusted cosmology calculator/library over the full redshift range used.

### Finding 3 — The synthetic density evolution is phenomenological, not a TNG-equivalent simulation

**Location:** halo evolution block, especially density-field construction and post-collapse profile blending.

The code combines generated Gaussian random fields, prescribed growth factors, a threshold-triggered collapse rule, a phenomenological transition function, an imposed NFW-like profile, merger perturbations, and stochastic substructure. These are modelling choices. The implementation itself says it does not fetch an IllustrisTNG catalogue.

**Implication:** matching the archived ensemble establishes that the synthetic generator is reproducible. It does not establish that its halo histories, density fields, merger histories, or temporal correlations are statistically representative of IllustrisTNG or ΛCDM structure formation.

**Required resolution:** use actual TNG snapshots and merger-tree links for external validation. Treat the synthetic generator as a null-model prototype unless and until its distributions and temporal dependencies are calibrated against simulation data.

### Finding 4 — KSG estimator needs independent estimator validation

**Location:** `ksg_mi_2d`, around lines 83–110.

The implementation uses a joint-space k-nearest-neighbour radius, marginal neighbour counts, and a KSG-style digamma expression. The marginal counts are obtained with inclusive radius queries after adding a small epsilon. This deserves explicit tie/boundary testing against a trusted implementation, particularly for repeated or quantized values and finite samples.

**Implication:** deterministic reproduction of the archived values does not establish estimator accuracy or absence of finite-sample bias. Normalizing each snapshot's sample to zero mean and unit variance also does not remove dependence induced by spatial sampling, repeated locations, or shared field structure.

**Progress and remaining resolution:** the Gaussian, permutation and independent scikit-learn cross-checks identified a persistent quantitative discrepancy in the recovered implementation. A further 20-replicate raw-output diagnostic now points to marginal-radius boundary handling as a leading explanation. The recovered function uses the joint kth-neighbour distance plus `1e-12` and inclusive marginal radius counts. A separate strict-below-kth-radius variant changed every replicate and shifted Gaussian rho=0.5 means from 0.1808 to 0.2151 bits at N=1,200, and from 0.1830 to 0.2047 bits at N=3,000, compared with analytic MI 0.2075 bits. The current convention included about 0.5 additional marginal neighbours per dimension on average. Raw shuffled estimates also demonstrate that `max(0, MI)` clipping masks negative finite-sample values. These results make the boundary convention a leading hypothesis, not a completed correction: the exact KSG Algorithm 1 inequality and count convention must be checked, followed by hand-constructed boundary and tie-heavy tests. The historical estimator remains unchanged. See the [Gaussian diagnostic](KSG_ESTIMATOR_GAUSSIAN_DIAGNOSTIC_2026-11-14.md), [permutation/nonlinear diagnostic](KSG_ESTIMATOR_PERMUTATION_NONLINEAR_DIAGNOSTIC_2026-11-17.md), [reference cross-check](KSG_ESTIMATOR_REFERENCE_CROSSCHECK_2026-11-17.md), and [raw boundary diagnostic](KSG_ESTIMATOR_RAW_BOUNDARY_DIAGNOSTIC_2026-11-23.md), with workflows [43986162321](https://github.com/bordode/cloud9-assembly-index/actions/runs/43986162321), [43987689799](https://github.com/bordode/cloud9-assembly-index/actions/runs/43987689799), and [45095297552](https://github.com/bordode/cloud9-assembly-index/actions/runs/45095297552). The estimator is not certified.

### Finding 5 — The reproduction comparator should harden archive integrity checks

**Location:** `scripts/reproduce_cloud9_null_ensemble_v3_full_ensemble.py`.

The comparator builds a dictionary keyed by seed and then runs the keys. It does not explicitly fail on duplicate archived seeds, an unexpected seed set, a member count other than 100, missing expected fields, or non-finite numeric values. Its current successful run remains evidence for the archive as it was supplied, but these omissions weaken the comparator as a reusable audit tool.

**Required resolution:** add explicit assertions for archive member count, unique and exact seed list (1000–1099 if that remains the frozen specification), required schema, finite numeric values, expected vector length (15), and output count. Record the archived JSON SHA-256, recovered source SHA-256, environment versions, workflow commit, and command in the artifact manifest. Keep this hardening separate from the already completed reproduction result.

## Recommended order of work

1. Preserve the archived JSON and recovered source as immutable evidence.
2. Freeze the intended mathematical definition and units of the Cloud-9 statistic before changing its implementation.
3. Validate the KSG estimator independently.
4. Replace or validate the approximate cosmological time calculation.
5. Build the TNG temporal validation dataset and protocol described in the companion plan.
6. Only then create a new, versioned estimator and compare it with the archived v3 score.

## Claim boundary

The defensible current statement is:

> The archived 100-member synthetic ensemble has been reproduced from the recovered v3 implementation after a documented constructor-keyword correction, with all nine compared fields matching at tolerance 1e-10. The result establishes computational reproducibility of that synthetic artifact. The temporal statistic's interpretation, estimator calibration, and representativeness of real cosmological evolution remain to be independently validated.

This is a static code-level review, not an external peer review and not a validation against TNG data.
