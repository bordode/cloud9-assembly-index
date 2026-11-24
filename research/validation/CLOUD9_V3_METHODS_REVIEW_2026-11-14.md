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

**Progress and remaining resolution:** the Gaussian, permutation and independent scikit-learn cross-checks identified a persistent quantitative discrepancy in the recovered implementation. A 20-replicate raw-output diagnostic showed that the historical inclusive-radius-plus-epsilon convention changes every replicate relative to a strict-below-boundary variant; for Gaussian rho=0.5, the strict variant shifted the mean from 0.1808 to 0.2151 bits at N=1,200 and from 0.1830 to 0.2047 bits at N=3,000, against analytic MI 0.2075 bits. The historical function clips negative estimates to zero, masking negative finite-sample values.

A literature review of Kraskov, Stögbauer & Grassberger (2004) distinguishes the complete algorithms: Type I uses strict marginal counts within the joint kth-neighbour radius and the psi(n_x+1)+psi(n_y+1) expression; Type II uses inclusive counts in a rectangle whose X and Y half-widths are the maximum projected distances across the k joint-space neighbours. The X and Y maxima may be set by different neighbours (Fig. 1(b,c)); its expression includes -1/k. The recovered implementation appears to combine inclusive counts with the Type-I expression and omit the Type-II correction, so it is a hybrid rather than either complete variant.

The corrected Type-II implementation now uses the projected maxima across all k joint neighbours. The corrected comparison and hand-constructed boundary/tie test passed in [workflow 45366627801](https://github.com/bordode/cloud9-assembly-index/actions/runs/45366627801), commit `1456226e793adac670a36b9b2b6c4ee33bb5188d`; the artifact was downloaded and inspected. For Gaussian rho=0.5 (analytic MI 0.2075 bits), 20-replicate means at N=1,200 were Type I 0.2151, Type II 0.1324, and recovered hybrid 0.1808 bits; at N=3,000 they were 0.2047, 0.1537, and 0.1830 bits, respectively. Shuffled Gaussian means were 0.0038, -0.0709, and -0.0283 bits at N=1,200, and -0.0020, -0.0487, and -0.0222 bits at N=3,000. Thus Type I was closest to the analytic Gaussian target in this limited grid; Type II showed a larger downward finite-sample bias. These results are preliminary, not certification.

The primary source is [Kraskov et al. (2004)](https://doi.org/10.1103/PhysRevE.69.066138), especially Fig. 1(b,c), Eq. (9), and Sec. II C. The next validation step is an independent brute-force implementation of the Type-II geometry/counts, followed by broader replicate and k-sensitivity tests. No estimator is certified for spatially structured cosmological fields, temporally dependent samples, or IllustrisTNG. The historical estimator and archived score remain unchanged. See the [Gaussian diagnostic](KSG_ESTIMATOR_GAUSSIAN_DIAGNOSTIC_2026-11-14.md), [permutation/nonlinear diagnostic](KSG_ESTIMATOR_PERMUTATION_NONLINEAR_DIAGNOSTIC_2026-11-17.md), [reference cross-check](KSG_ESTIMATOR_REFERENCE_CROSSCHECK_2026-11-17.md), and [raw boundary diagnostic](KSG_ESTIMATOR_RAW_BOUNDARY_DIAGNOSTIC_2026-11-23.md).

A literature review of Kraskov, Stögbauer & Grassberger (2004) distinguishes the complete algorithms: Type I uses strict marginal counts within the joint kth-neighbour radius and the psi(n_x+1)+psi(n_y+1) expression; Type II uses inclusive counts in a rectangle whose X and Y half-widths are the maximum projected distances across the k joint-space neighbours. The X and Y maxima may be set by different neighbours (Fig. 1(b,c)); its expression includes -1/k. The recovered implementation appears to combine inclusive counts with the Type-I expression and omit the Type-II correction, so it is a hybrid rather than either complete variant.

Two Type-II implementation attempts have been withdrawn. The first incorrectly used the joint radius in both marginal spaces. The second used only the single kth-neighbour point's projected coordinates; its independent Gaussian control produced large positive estimates, exposing a second geometry error. The current implementation computes the maximum X and Y projections across all k joint neighbours independently, and the hand-built tie test checks a case where different neighbours determine the two radii. The full rerun is [workflow 45366578605](https://github.com/bordode/cloud9-assembly-index/actions/runs/45366578605); the numerical artifact has not yet been accepted. The earlier complete comparison [workflow 45366123048](https://github.com/bordode/cloud9-assembly-index/actions/runs/45366123048) passed its tests but its Type-II numerical results are withdrawn. The original KSG paper, especially Fig. 1(b,c), Eq. (9), and Sec. II C, supports the geometric distinction: [Kraskov et al. (2004)](https://doi.org/10.1103/PhysRevE.69.066138). The historical estimator remains unchanged. The estimator is not certified.

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
