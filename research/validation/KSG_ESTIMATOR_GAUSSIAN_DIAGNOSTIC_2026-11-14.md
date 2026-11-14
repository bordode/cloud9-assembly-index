# Recovered v3 KSG estimator: Gaussian diagnostic

**Date:** 2026-11-14  
**Workflow:** [43654133609](https://github.com/bordode/cloud9-assembly-index/actions/runs/43654133609)  
**Commit:** `9c6e8bd6305aa57b818ef8f76ea6debfd4c042de`  
**Artifact:** `v3-full-ensemble-reproduction`, ID `14137018992`

## Purpose and limits

This diagnostic compares the recovered v3 `ksg_mi_2d` implementation, unchanged, with analytic mutual information for bivariate Gaussian pairs. It includes an independence control and two correlated cases at sample sizes 1,200 and 3,000, with three deterministic replicates per condition.

This is a small diagnostic, not a complete estimator validation or certification. It does not establish accuracy for spatially structured cosmological density fields, dependent samples, ties, nonlinear dependencies, or TNG data.

## Results

Analytic Gaussian mutual information is:

```
I(X;Y) = -0.5 * log2(1 - rho^2)
```

| N | Correlation | Analytic MI (bits) | Three estimates (bits) | Median error (bits) |
|---:|---:|---:|---|---:|
| 1,200 | 0.0 | 0.0000 | 0.0360, 0.0051, 0.0000 | +0.0051 |
| 1,200 | 0.5 | 0.2075 | 0.1976, 0.1711, 0.2151 | −0.0099 |
| 1,200 | 0.8 | 0.7370 | 0.7242, 0.6804, 0.7454 | −0.0128 |
| 3,000 | 0.0 | 0.0000 | 0.0000, 0.0174, 0.0000 | 0.0000 |
| 3,000 | 0.5 | 0.2075 | 0.1993, 0.2155, 0.2061 | −0.0014 |
| 3,000 | 0.8 | 0.7370 | 0.7231, 0.6977, 0.6877 | −0.0393 |

## Interpretation

The implementation returned small values for the independent controls and estimates reasonably close to the analytic Gaussian values in these limited tests. The largest absolute median error in this small grid was approximately 0.0393 bits.

This is encouraging preliminary evidence, but the number of replicates is too small to estimate bias or uncertainty robustly. The implementation also clips negative estimates to zero, which affects the independence-control distribution and should be evaluated explicitly rather than interpreted as proof of unbiasedness.

## Required next estimator tests

1. Increase replicate counts substantially and report distributions / confidence intervals.
2. Test permutation and shuffled-pair controls while preserving marginal distributions.
3. Test nonlinear dependence with known or independently benchmarked MI.
4. Test repeated, quantized and tied values to examine radius-boundary handling.
5. Compare against a maintained reference KSG implementation with matched conventions.
6. Sweep sample size, k, normalization and dependence strength.
7. Assess dependence from spatial sampling and adjacent snapshots before applying the estimator to TNG.

## Reproduction status in the same workflow

The strict 100-seed archived ensemble comparator also passed in this workflow: 100/100 members matched across all nine fields, including all 15 MI values per member, at tolerance `1e-10`.

**Claim boundary:** this diagnostic is a preliminary Gaussian calibration check only. It does not validate the physical model, the time-integrated interpretation of `A_c`, or the representativeness of the synthetic null for real cosmological evolution.
