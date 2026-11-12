# Calibration-border contamination stress-test results

**Date:** 2026-11-12  
**Repository:** `bordode/cloud9-assembly-index`  
**Branch:** `research/dithered-stack-control-protocol`  
**Workflow:** [#43187604902](https://github.com/bordode/cloud9-assembly-index/actions/runs/43187604902)  
**Workflow commit:** `f914cb5f5fe18a10d615661e2358b1539144e580`  
**Python tests:** [#43187612054 — success](https://github.com/bordode/cloud9-assembly-index/actions/runs/43187612054)  
**Artifact:** `dither-calibration-border-contamination-stress-test` (ID `13929865957`)  
**Downloaded ZIP SHA-256:** `53d7d19275ebd42e8027633edb2780aa851f223a0a2019e5c8faca670f3c7eb7`

## Question

Does the dither-associated reconstruction advantage persist when some of the detector-border pixels used for background calibration are contaminated by additional background counts?

## Frozen protocol

- 30 fresh paired seeds: `2026111500–2026111529`, disjoint from the preceding experiment seed ranges.
- Horizontal background gradient fixed at amplitude 0.25, with true map `0.5 + 0.25*x` and x spanning -1 to +1 across detector columns.
- Three contamination fractions: 0%, 5%, and 15% of the outer three-pixel border calibration region.
- Contaminated pixels receive an additional Poisson background rate of 1.0 per detector pixel per total-exposure unit.
- The same deterministic, seed-specific contamination mask is applied to all three acquisition arms. The estimator is not told which pixels are contaminated.
- Nine stationary, nine aligned-dither, and nine off-grid-dither frames per arm; total exposure 1.0.
- Richardson–Lucy reconstruction fixed at two iterations.
- 30 paired seeds per contamination level; paired per-seed differences and 95% t confidence intervals.
- 270 trial records total.

## Primary result: fixed-interior relative RMSE

Mean RMSE by arm and the relative reduction compared with stationary acquisition:

| Contaminated border fraction | Stationary mean RMSE | Aligned dither RMSE | Aligned reduction | Off-grid dither RMSE | Off-grid reduction |
|---:|---:|---:|---:|---:|---:|
| 0% | 0.3250 | 0.1558 | 52.1% | 0.1604 | 50.7% |
| 5% | 0.3243 | 0.1552 | 52.1% | 0.1603 | 50.6% |
| 15% | 0.3250 | 0.1588 | 51.1% | 0.1586 | 51.2% |

Paired dither-minus-stationary mean RMSE differences (all n=30):

| Contamination | Aligned difference (95% CI) | Off-grid difference (95% CI) |
|---:|---:|---:|
| 0% | -0.16920 [-0.17416, -0.16425] | -0.16465 [-0.17010, -0.15921] |
| 5% | -0.16909 [-0.17390, -0.16428] | -0.16402 [-0.16858, -0.15946] |
| 15% | -0.16620 [-0.17150, -0.16091] | -0.16636 [-0.16986, -0.16285] |

All six paired 95% confidence intervals exclude zero. In this tested synthetic setup, the relative-RMSE advantage persists at both contamination levels.

## What contamination did affect

The background estimator itself deteriorated substantially as more border pixels were contaminated. Mean background-map RMSE was:

| Contamination | Stationary | Aligned dither | Off-grid dither |
|---:|---:|---:|---:|
| 0% | 0.0394 | 0.0359 | 0.0491 |
| 5% | 0.0646 | 0.0585 | 0.0531 |
| 15% | 0.1659 | 0.1446 | 0.1486 |

At 15% contamination, the estimated background maps are materially less accurate than in the clean-border condition. Nevertheless, reconstruction relative RMSE remains substantially lower for both dither arms than for stationary acquisition. The primary result is therefore not evidence that the background estimator is immune to contamination; it shows that the reconstruction advantage survives this particular calibration error in the tested scene.

Absolute aperture-flux error also favours both dither arms over stationary acquisition at all three contamination levels. Centroid differences are less consistent and should not be described as a universal improvement.

Aligned-versus-off-grid paired relative-RMSE confidence intervals include zero at all three contamination levels. This experiment does not establish superiority of either dither geometry.

## Interpretation

The pre-specified primary result is positive: with 5% and 15% of calibration-border pixels contaminated by an additional Poisson background component, both dither patterns retain approximately 51% lower mean relative RMSE than stationary acquisition. All paired dither-versus-stationary confidence intervals exclude zero.

The important qualification is that calibration quality does degrade, especially at 15% contamination. The result is specific to this contamination mechanism, a fixed horizontal linear background model, the tested three-source scene, and two Richardson–Lucy iterations.

## Limitations and next tests

- Contamination is confined to the outer calibration border and uses a fixed additional Poisson rate.
- The underlying background remains a horizontal linear gradient; model mismatch is not tested.
- No vertical or curved structure, temporal drift, source-correlated background, read noise, PSF mismatch, or realistic instrument systematics are included.
- The estimator still assumes a horizontal linear field and uses all border pixels without robust outlier rejection.
- The next useful robustness step is to test a deliberately misspecified background shape (for example, a weak curved component) and/or temporally varying background, while keeping fresh seeds and fixed reconstruction settings.

## Conclusion

For the tested synthetic benchmark, the dither-associated reconstruction RMSE advantage is robust to the specified 5% and 15% calibration-border contamination levels. The estimated background map becomes less accurate as contamination increases, but the relative-RMSE benefit remains near 51%. This supports a bounded robustness claim—not a claim of general immunity to calibration defects or real-instrument background uncertainty.

**Workflow status:** all benchmark stages and artifact uploads completed successfully in run #43187604902. The corresponding Python test run #43187612054 also completed successfully.
