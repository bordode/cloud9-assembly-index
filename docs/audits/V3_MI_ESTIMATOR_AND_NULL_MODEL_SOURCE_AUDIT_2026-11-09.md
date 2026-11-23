# Source Audit: v3 Mutual-Information Estimator and Synthetic Null Construction

**Date:** 2026-11-09  
**Status:** Source inspection; no new benchmark or independent reproduction performed  
**Primary source:** `research/null-ensemble/cloud9_null_ensemble_v3.py`

## Executive finding

The v3 experiment is a useful synthetic method-development exercise, but its N=100 output cannot establish that a real halo exhibits exceptional non-stochastic assembly. The generated time series contains temporal persistence by construction: a common underlying density realization is reused across time, while a step-dependent component and a constructed halo profile are added. The same spatial sample locations are followed at every time step.

This is not an accusation of invalid code or misconduct. It is a statement about what the null generator represents. The reported mutual information is conditional on the generator's assumptions and cannot be interpreted as a direct test of real ΛCDM halo histories.

## 1. What the code actually estimates

The function `ksg_mi_2d(x, y, k=3)` receives two one-dimensional arrays:
- density samples at time step t;
- density samples at time step t+1.

It constructs a joint two-dimensional sample `[x, y]`, estimates nearest-neighbour distances with the L-infinity norm, counts marginal neighbours, and applies a KSG-style estimator. It converts nats to bits and clips negative estimates to zero.

Therefore:
- This specific v3 calculation is not a demonstrated high-dimensional KSG problem. The joint variable has two scalar components.
- The 1,200 paired values are not automatically 1,200 independent observations. They are sampled from spatial locations in one density field and may be spatially correlated.
- Clipping negative finite-sample MI estimates to zero creates a potential positive bias. Its size must be measured under known-zero and known-MI controls.
- The source does not show a calibration study that quantifies bias and uncertainty for this exact spatially correlated sampling design.

## 2. Temporal persistence is partly built into the generator

In `CosmicHaloEvolver.evolve()`:

1. A base realization, `delta_unit`, is generated once for each halo using a seed derived from the halo seed.
2. At each time step, the large-scale component reuses that same `delta_unit`, scaled by the growth factor.
3. A separate step-dependent realization, `delta_ss`, is generated using a seed derived from the halo seed and time-step index.
4. The density field combines the shared large-scale component, the step-dependent component, and a correlated component derived again from `delta_unit`.
5. After the constructed collapse condition is reached, the field is blended with a prescribed NFW-like halo profile, merger perturbations, substructure and a gas component.

This is a physically motivated synthetic construction, not a full gravitational N-body evolution or an imported IllustrisTNG merger-tree history. Because a shared field component is intentionally reused, temporal dependence is an expected property of the generator. The experiment does not by itself separate ordinary correlated evolution from a new form of non-stochastic assembly.

## 3. Sampling design and normalization

The code selects 1,200 spatial offsets around the initial density peak once, before the time loop. The same `sample_indices` are then used to extract density values at every time step. This creates paired measurements at fixed locations, which is a sensible way to estimate temporal dependence, but the observations inherit spatial dependence from the underlying field.

Before each pairwise MI estimate, the sampled density values at each time are independently standardized to zero mean and unit variance. For an ideal continuous MI, separate invertible affine transformations do not change the population mutual information. In finite samples, however, standardization does not resolve spatial dependence, finite-sample bias or the effect of clipping.

## 4. The reported A_c is not the stated time integral

The source constructs 16 scale-factor steps using logarithmic spacing in scale factor, computes cosmic times, and then accumulates:

`A_c = sum_i MI(rho_i, rho_{i+1})`

The calculated time values are not used to weight the sum. The stated definition is an integral over cosmic time. With nonuniform time intervals, an unweighted sum is not a numerical approximation to that integral unless the quantity is explicitly redefined and justified as a discrete sum.

The next implementation should:
- define the intended units of MI and A_c;
- choose and document an integration rule, such as trapezoidal integration against cosmic time;
- test convergence as the number and placement of snapshots change;
- report the discrete sum separately if it is retained as a different statistic.

No corrected A_c value should be inferred until the implementation and its target measurement are both recomputed consistently.

## 5. Null ensemble and seeds

The v3 source specifies:
- N=100;
- base seeds 1000 through 1099;
- 32³ grid;
- 16 time steps;
- 1,200 fixed sampled locations per halo;
- synthetic model data, with no IllustrisTNG catalogue fetched.

It derives additional random seeds for the base and step-dependent realizations from each halo seed. This is sufficient to describe the v3 synthetic generator's seed design. It does **not** establish whether any older target analysis used overlapping initial conditions, seeds, simulation numerics, preprocessing or parameter tuning. That historical relationship remains unresolved because the original target run provenance has not been located.

The N=100 ensemble is too small to resolve extreme empirical tails. Zero exceedances means zero exceedances in this finite ensemble; it does not measure a Gaussian tail probability corresponding to 8.62σ. The Shapiro result recorded in the validation report rejects normality for the reported ensemble, further cautioning against converting the standardized separation into a Gaussian discovery p-value.

## 6. Recommended controls

Before interpreting the statistic as evidence for assembly beyond ordinary persistence, test the estimator and statistic on controls that isolate the relevant effects:

1. **Independent-field control:** independent fields at each time step, with no shared realization.
2. **Shared-field control:** the same base field reused with known scaling, to quantify persistence expected from common structure.
3. **Temporally correlated stochastic control:** a process with a known temporal correlation coefficient and no halo-specific assembly mechanism.
4. **Spatially correlated null:** fields with matched power spectrum and spatial autocorrelation, but controlled temporal dependence.
5. **Generator ablation:** separately remove the shared large-scale component, NFW blending, merger perturbations, substructure and gas component.
6. **Estimator bias calibration:** known independent and dependent distributions, with and without clipping, across sample sizes and spatial correlation lengths.
7. **Time-grid convergence:** compare unweighted sums, explicitly defined time-weighted integrals and alternative snapshot spacings.
8. **Physical validation:** run the same analysis on traceable multi-snapshot ΛCDM simulations with matched halo selection, mass, environment, resolution and preprocessing.

Report estimator bias, variance, coverage and empirical exceedances for each control. Use independent seeds and reserve a held-out set for final evaluation.

## 7. Scope of conclusions

The v3 result supports only a narrow statement: under this particular synthetic halo-evolution generator, the reported target value is separated from the 100 generated values according to the chosen KSG-style statistic and unweighted accumulation rule.

It does not establish:
- an empirical detection in IllustrisTNG or the observed universe;
- non-stochastic assembly beyond ordinary correlated gravitational evolution;
- a validated cosmological significance;
- consciousness, intelligence, agency, subjective experience or moral status.

Future physics or other empirical sciences may provide evidence relevant to consciousness emergence. This source audit neither rules out that possibility nor supplies such evidence.

## 8. Reproducibility and review limitation

This note records source-level inspection of the v3 generator and the associated validation documentation. The synthetic pipeline was not rerun as part of this audit. No new statistic, corrected A_c value, p-value or independent reproduction is claimed.
