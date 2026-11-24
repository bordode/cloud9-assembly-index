# KSG Type-II independent full-estimator cross-check

**Date:** 2026-11-24  
**Branch:** `audit/null-ensemble-v3-provenance`  
**Workflow:** [run 45509633722](https://github.com/bordode/cloud9-assembly-index/actions/runs/45509633722)  
**Workflow commit:** `2a67ccfd5169bba66c8f27c43affc2e49f7e935e`  
**Artifact:** `v3-full-ensemble-reproduction`, ID `14975267747`  
**Artifact SHA-256:** `083ae005c5bc0b925d68a6a19d3c9552832271d5be637be2059b86974b27ad90`  
**Status:** computational cross-check passed; no statistical or domain certification

## Purpose

The preceding O(N²) check compared Type-II projected radii and inclusive marginal counts on a small continuous sample and one constructed tie-heavy anchor. It did not independently compare the complete estimator output. This study adds an independently implemented reference for the full Type-II calculation.

## Independent reference design

The implementation under test uses `scipy.spatial.cKDTree` for joint-space neighbours and marginal counts.

The reference implementation does not call `cKDTree`. It uses:

1. Chunked NumPy pairwise absolute coordinate differences.
2. Pairwise Chebyshev distance, `max(|dx|, |dy|)`, to identify the k joint-space neighbours.
3. Explicit ordering of the selected nearest neighbours before taking each k-prefix.
4. Independent `epsilon_x` and `epsilon_y` radii, each defined as the maximum projected distance across the k joint neighbours.
5. Direct inclusive marginal counts from the pairwise distance matrices.
6. The Type-II expression `psi(k) - 1/k + psi(N) - mean(psi(nx) + psi(ny))`, converted from nats to bits.

The direct pairwise count reference is intentionally separate from the tree-based count operation. It also avoids floating-point endpoint differences that can occur when translating a distance comparison into `x_i +/- epsilon` interval endpoints.

## Test design and results

- Sample sizes: N=1,200 and N=3,000.
- Replicates: 3 per condition and sample size.
- Conditions: independent standard normal X/Y; correlated bivariate Gaussian with rho=0.5.
- k values: 3, 10 and 50.
- Total comparisons: 36 (2 sample sizes × 3 replicates × 2 conditions × 3 k values).
- Numerical tolerance: 1e-10 bits for the final MI value; radii compared at absolute tolerance 1e-12; marginal counts required exact integer equality.

**Result: all 36 comparisons matched exactly.**

| Quantity | Maximum observed difference |
|---|---:|
| Type-II MI estimate | 0.0 bits |
| epsilon_x radius | 0.0 |
| epsilon_y radius | 0.0 |
| nx marginal counts | Exact match in every record |
| ny marginal counts | Exact match in every record |

The exact equality is expected here because both paths implement the same mathematical definition and floating-point operations yielded matching radii/counts on these continuous samples. It is evidence of implementation agreement on the tested inputs, not proof of statistical correctness.

## k-sensitivity context

The 20-replicate k-sensitivity study in the same workflow has analytic Gaussian MI 0.20751875 bits for rho=0.5. Selected Type-II means are:

| N | k | Independent Gaussian mean (bits) | Correlated Gaussian mean (bits) |
|---:|---:|---:|---:|
| 1,200 | 3 | -0.08450 | 0.12491 |
| 1,200 | 10 | -0.03399 | 0.16948 |
| 1,200 | 50 | -0.01316 | 0.18577 |
| 1,200 | 100 | -0.00977 | 0.17897 |
| 1,200 | 300 | -0.00368 | 0.13858 |
| 3,000 | 3 | -0.05129 | 0.15402 |
| 3,000 | 10 | -0.02045 | 0.18868 |
| 3,000 | 50 | -0.00933 | 0.20264 |
| 3,000 | 100 | -0.00641 | 0.20300 |
| 3,000 | 750 | -0.00213 | 0.14716 |

The independent-control mean moves toward zero as k grows, while the correlated-control estimate rises toward the analytic value over part of the k range and then falls at k=N/4. At N=3,000, k=50 and 100 are closest among these tested Type-II settings to the analytic value. At N=1,200, the correlated estimate remains materially low throughout the selected grid.

For comparison, Type-I independent-control means remain close to zero in this grid (roughly within ±0.0085 bits), while its correlated-Gaussian means are generally closer to the analytic target for the smaller and intermediate k values. These finite-sample results do not establish a universally preferred estimator or k.

## Failed reference attempts and correction record

Two initial workflow attempts failed at the new reference step and produced no artifact:

- Run [45509259014](https://github.com/bordode/cloud9-assembly-index/actions/runs/45509259014) used an early reference version that did not sort the selected `argpartition` neighbours before taking smaller k-prefixes. This was corrected by explicitly sorting the selected neighbours by their joint distances.
- Run [45509292301](https://github.com/bordode/cloud9-assembly-index/actions/runs/45509292301) then found a count mismatch: sorted-array interval endpoint counting could differ by floating-point rounding from direct inclusive distance comparisons. The reference was corrected to count directly from its independently computed pairwise distance matrices.

The final corrected implementation passed in run 45509633722. These failures are retained as part of the audit trail; no failed artifact was treated as evidence.

## Interpretation limits and next work

1. This validates computational agreement between the cKDTree implementation and a separately coded pairwise reference on the tested continuous iid Gaussian samples.
2. It does not certify the Type-II estimator's bias, variance, consistency, or suitability for the Cloud-9 application.
3. The k-sensitivity study uses 20 replicates and is preliminary. The independent implementation cross-check uses 3 replicates per condition and is a software-equivalence test, not a performance study.
4. Tie-heavy and quantized data require separate full-estimator testing. The current independent-reference comparison deliberately checks continuous samples with unambiguous kth-neighbour boundaries; existing hand-built tests cover selected tie geometry/count cases, not the complete estimator over a broad quantized-data grid.
5. No spatially structured cosmological fields, temporal dependence, or IllustrisTNG data are tested.
6. The recovered historical estimator, historical source, archived JSON, and 8.62σ comparison remain unchanged.

Primary estimator reference: Kraskov, Stögbauer & Grassberger (2004), *Estimating mutual information*, Physical Review E 69, 066138, [DOI](https://doi.org/10.1103/PhysRevE.69.066138), especially Algorithm 2, Fig. 1(b,c), Eq. (9), and Sec. II C.
