# Recovered v3 KSG: permutation and nonlinear diagnostics

**Date:** 2026-11-17  
**Workflow:** [43986162321](https://github.com/bordode/cloud9-assembly-index/actions/runs/43986162321)  
**Commit:** `f39d98a5fd506e61eda876657448142b903a4bfa`  
**Artifact:** `v3-full-ensemble-reproduction`, ID `14285398085`  
**Artifact SHA-256:** `4b27f565137acb0d15eaa6a4bbd49d3174ae2d04c881a7adc027dc33c9fe4465`

## Purpose and design

This diagnostic exercises the recovered v3 `ksg_mi_2d` implementation unchanged. It adds paired permutation controls and a nonlinear dependence stress test at N=1,200 and N=3,000, with 20 deterministic replicates per condition and k=3.

For each replicate, Y is independently permuted. This preserves the observed X and Y marginal samples exactly while destroying their pairings.

The Gaussian condition uses a bivariate normal distribution with rho=0.5, for which analytic MI is 0.20751875 bits. The nonlinear stress test uses X uniform on [-pi, pi] and Y=sin(3X)+Normal(0,0.35). No analytic MI is asserted for that nonlinear condition; it is compared only with its own shuffled-pair control.

The reported 2.5th and 97.5th percentiles are empirical quantiles across 20 replicate estimates, not confidence intervals for a population parameter.

## Results

### Gaussian dependent pairs and shuffled controls

| N | Condition | Mean (bits) | Median (bits) | Empirical 2.5–97.5% range | Exact zeros |
|---:|---|---:|---:|---:|---:|
| 1,200 | rho=0.5 paired | 0.1806 | 0.1796 | 0.1194–0.2482 | 0/20 |
| 1,200 | Y permuted | 0.0014 | 0.0000 | 0.0000–0.0150 | 18/20 |
| 3,000 | rho=0.5 paired | 0.1845 | 0.1772 | 0.1546–0.2230 | 0/20 |
| 3,000 | Y permuted | 0.0039 | 0.0000 | 0.0000–0.0179 | 13/20 |

The analytic Gaussian MI is 0.2075 bits. The paired-sample median is lower by 0.0279 bits at N=1,200 and 0.0303 bits at N=3,000. The mean estimates are lower by 0.0269 and 0.0231 bits, respectively. This is a material calibration discrepancy that should be investigated; increasing N from 1,200 to 3,000 did not eliminate it in this experiment.

### Nonlinear sinusoidal dependence and shuffled controls

| N | Condition | Mean (bits) | Median (bits) | Empirical 2.5–97.5% range | Exact zeros |
|---:|---|---:|---:|---:|---:|
| 1,200 | Sinusoidal paired | 1.0800 | 1.0795 | 1.0399–1.1324 | 0/20 |
| 1,200 | Y permuted | 0.0041 | 0.0000 | 0.0000–0.0246 | 16/20 |
| 3,000 | Sinusoidal paired | 1.0808 | 1.0785 | 1.0494–1.1308 | 0/20 |
| 3,000 | Y permuted | 0.0012 | 0.0000 | 0.0000–0.0074 | 15/20 |

The nonlinear paired samples are cleanly separated from their shuffled controls in these tests. This is a successful dependence-detection stress test, not an accuracy calibration: no analytic MI value is claimed for the sinusoidal construction.

## Interpretation and limitations

1. **Permutation discrimination:** the estimator distinguishes the paired Gaussian and sinusoidal samples from the corresponding shuffled controls in this synthetic iid experiment.
2. **Clipping matters:** the recovered estimator applies `max(0, mi)` before returning bits. Between 65% and 90% of shuffled estimates were exactly zero, depending on condition. The zero-heavy distributions are therefore partly a direct consequence of clipping. Their medians of zero must not be interpreted as proof that the unclipped estimator is unbiased or that independence always yields exactly zero.
3. **Gaussian calibration concern:** the larger 20-replicate experiment shows a persistent underestimation of the known rho=0.5 Gaussian MI. This deserves investigation before relying on the estimator quantitatively.
4. **Nonlinear test boundary:** the sinusoidal case demonstrates sensitivity to one nonlinear dependence structure. It does not establish accuracy across nonlinear distributions.
5. **Replicate limits:** 20 replicates provide a useful preliminary distribution, but are not a comprehensive uncertainty study.
6. **Domain limits:** none of these iid synthetic tests establishes validity for spatially structured density fields, temporally dependent snapshots, or IllustrisTNG data.

## Recommended next work

1. Inspect the KSG implementation's exact neighbour-count convention, inclusive radius queries, epsilon adjustment, self-count handling and finite-sample correction against the original KSG estimator conventions.
2. Compare the unchanged implementation with at least one independently maintained reference implementation, using identical samples and explicitly matched estimator variants and units.
3. Run a broader Gaussian calibration grid over rho, N and k with substantially more replicates; report bias and uncertainty without silently changing the recovered implementation.
4. Preserve unclipped raw estimates in a separate diagnostic implementation so clipping effects can be quantified without altering the historical estimator.
5. Add tie-heavy and quantized inputs, plus nonlinear dependence cases with independent reference values where available.
6. Only after these tests, assess spatial and temporal dependence structures relevant to cosmological density fields.

## Historical reproduction status

The same workflow also passed the strict 100-member archived ensemble reproduction: all 100 members matched, including all 15 MI values per member, across all nine comparison fields at tolerance 1e-10. The reproduced mean was 58.0622230911 bits, population SD 3.39056643855 bits, and population-SD standardized separation 8.62327208116.

## Claim boundary

These results support a narrow statement: the recovered implementation detects the tested paired dependencies relative to shuffled controls, but the Gaussian calibration experiment exposes a persistent quantitative shortfall at rho=0.5. The KSG estimator is **not validated or certified** for Cloud-9's cosmological application. The historical synthetic ensemble's computational reproducibility remains separate from estimator validity, physical interpretation, and TNG temporal validation.
