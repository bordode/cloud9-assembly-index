# Hidden-background estimation validation results

**Date:** 2026-11-11  
**Repository:** `bordode/cloud9-assembly-index`  
**Branch:** `research/dithered-stack-control-protocol`  
**Workflow run:** [#43119728933](https://github.com/bordode/cloud9-assembly-index/actions/runs/43119728933)  
**Benchmark commit:** `0cb6bb05671e418aae5ad6dde48bb93106bd30a9`  
**Artifact:** `dither-blind-background-estimation-validation` (ID `13899818413`)  
**Artifact SHA-256:** `ec540e923f774c4b1905a5aa6bfd25eca199926e408350d187213faf145c257e`

## Question

Does the reconstruction benefit from dither persist when the true detector background map is withheld and estimated from calibration pixels?

## Design

- 30 fresh paired seeds: `2026111400–2026111429`, disjoint from earlier validation seeds.
- Three horizontal background-gradient amplitudes: 0, 0.25, and 0.45, with true map `0.5 + amplitude*x`; `x` spans -1 to +1 across detector columns.
- Nine frames per arm, total exposure 1.0 per arm; stationary, aligned-dithered, and off-grid-dithered conditions.
- Richardson–Lucy iterations fixed at two.
- Independent source and background Poisson counts; no read noise.
- The true background map was used only to generate observations and score estimation. It was not supplied to reconstruction.
- Estimator: non-negative Poisson maximum-likelihood fit of left/right endpoint rates using only the outer three detector-pixel border, followed by linear interpolation across detector width.
- 270 trial records total (30 seeds × 3 gradients × 3 observing conditions).

## Primary result: relative RMSE

Mean relative RMSE by condition, followed by the mean paired dither-minus-stationary difference and its 95% confidence interval. Negative paired differences favour dither.

| Gradient amplitude | Stationary mean RMSE | Aligned mean RMSE | Aligned reduction | Aligned paired difference (95% CI) | Off-grid mean RMSE | Off-grid reduction | Off-grid paired difference (95% CI) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 0.3251 | 0.1534 | 52.8% | -0.1717 [-0.1763, -0.1670] | 0.1605 | 50.6% | -0.1645 [-0.1695, -0.1595] |
| 0.25 | 0.3252 | 0.1606 | 50.6% | -0.1646 [-0.1708, -0.1583] | 0.1631 | 49.8% | -0.1621 [-0.1674, -0.1568] |
| 0.45 | 0.3267 | 0.1574 | 51.8% | -0.1693 [-0.1746, -0.1640] | 0.1611 | 50.7% | -0.1656 [-0.1705, -0.1606] |

All six paired 95% confidence intervals exclude zero. The dither-associated relative-RMSE advantage therefore replicated in this experiment even though reconstruction received an estimated rather than known background map.

## Secondary results

- **Absolute aperture-flux error:** Lower for both dither conditions than stationary in all six gradient/condition comparisons; all six paired 95% confidence intervals for dither-minus-stationary error exclude zero.
- **Centroid error:** No consistent advantage. Aligned-versus-stationary paired intervals include zero at all three gradient levels. Off-grid differences vary by gradient: a modest increase at gradient 0 and a modest reduction at gradient 0.45, with no stable overall pattern.
- **Background-map estimation:** Background-map RMSE and mean-background absolute error are not consistently different between observing conditions; paired intervals include zero across all three gradient levels. Thus, the primary reconstruction gain is not accompanied by a clearly demonstrated improvement in the background estimator itself.
- **Aligned versus off-grid dither:** Paired relative-RMSE intervals include zero at all three gradient levels. This experiment does not establish superiority of either dither pattern.

## Interpretation

This is an independent synthetic validation of a substantial dither-associated reconstruction improvement under a constrained estimated-background condition. It is stronger than the earlier known-background tests because the true map was not passed to reconstruction.

It is not unconstrained blind background estimation. The estimator assumes that the outer three-pixel detector border is source-free and representative of the same detector-fixed horizontal linear background field. The background model family is therefore known and deliberately restricted.

## Limitations

- Horizontal linear gradients only; no vertical, curved, temporal, or source-correlated backgrounds.
- No read noise, PSF mismatch, or realistic calibration-region systematics.
- The source-free outer-border calibration assumption may fail in real observations.
- Off-grid shifts retain bilinear high-resolution cell interpolation.
- Synthetic three-source scene and fixed two-iteration reconstruction; no claim of generality to other scenes, instruments, or reconstruction settings.

## Conclusion

The dither-associated relative-RMSE advantage replicated across all three tested gradient amplitudes with an estimated, rather than known, background map: approximately 49.8–52.8% lower mean relative RMSE than stationary acquisition, with all paired confidence intervals excluding zero. The appropriate claim is limited to this synthetic setup and its source-free-border, horizontal-linear-background calibration assumption. A next robustness test should challenge that assumption—for example, contaminated border pixels, imperfect calibration, or background-model mismatch—before making broader claims.

**Workflow status:** all steps in run #43119728933 completed successfully, including this validation and artifact upload.
