# Hidden-background estimation validation results

Date: 2026-11-11  
Repository: `bordode/cloud9-assembly-index`  
Branch: `research/dithered-stack-control-protocol`  
Workflow run: [43119728933](https://github.com/bordode/cloud9-assembly-index/actions/runs/43119728933)  
Benchmark commit: `0cb6bb05671e418aae5ad6dde48bb93106bd30a9`  
Artifact: `dither-blind-background-estimation-validation`  
Artifact SHA-256: `ec540e923f774c4b1905a5aa6bfd25eca199926e408350d187213faf145c257e`

## Question

Does the reconstruction benefit from dither persist when the true detector background map is withheld and must be estimated from observations?

## Design

- 30 fresh paired seeds: `2026111400–2026111429`, disjoint from earlier validation seeds.
- Three horizontal background-gradient amplitudes: 0, 0.25, and 0.45, with true map (b(x)=0.5+a x), where (x) spans -1 to +1 across detector columns.
- Nine frames per arm, total exposure 1.0 per arm; stationary, aligned-dithered, and off-grid-dithered.
- Richardson–Lucy iterations fixed at two.
- Independent source and background Poisson counts; no read noise.
- The true background map was used only to generate observations and score estimation. Reconstruction received an estimated map.
- Estimator: non-negative Poisson maximum-likelihood fit of left/right endpoint rates using only the outer three detector-pixel border, then linear interpolation across detector width.
- 270 trial records total (30 seeds × 3 gradients × 3 observing conditions).

## Primary result: relative RMSE

Mean paired per-seed relative RMSE reductions against stationary observations:

| Gradient amplitude | Aligned dither | 95% CI | Off-grid dither | 95% CI |
|---:|---:|---:|---:|---:|
| 0.00 | 52.81% | 51.42–54.19% | 50.60% | 49.13–52.07% |
| 0.25 | 50.61% | 48.71–52.50% | 49.84% | 48.24–51.44% |
| 0.45 | 51.82% | 50.22–53.41% | 50.66% | 49.24–52.09% |

All six paired 95% confidence intervals exclude zero. The benefit therefore replicated in this experiment even though the reconstruction was supplied only with an estimated background map.

## Secondary results

- Absolute aperture-flux error was lower for both dither conditions than stationary in all six gradient/condition comparisons; all six paired 95% confidence intervals for dither-minus-stationary error exclude zero.
- Centroid error did not show a consistent advantage. Most paired intervals include zero; the off-grid condition at gradient 0.45 showed a modest reduction.
- Background-map RMSE and mean-background error were not consistently different between observing conditions; paired intervals generally include zero.
- Aligned versus off-grid dither RMSE differences were small and their paired 95% confidence intervals included zero at all three gradient levels. This experiment does not establish superiority of either dither pattern.

## Interpretation

This is a successful independent synthetic validation of a substantial dither-associated reconstruction improvement under a constrained estimated-background condition. It is stronger than the earlier known-background tests because the true map was not passed to reconstruction.

It is not unconstrained blind background estimation. The estimator assumes that the outer three-pixel detector border is source-free and representative of the same detector-fixed horizontal linear background field. The background model family is therefore known and deliberately restricted.

## Limitations

- Horizontal linear gradients only; no vertical, curved, temporal, or source-correlated backgrounds.
- No read noise, PSF mismatch, or realistic calibration-region systematics.
- The source-free outer-border calibration assumption may fail in real observations.
- Off-grid shifts retain bilinear high-resolution cell interpolation.
- Synthetic three-source scene and fixed two-iteration reconstruction; no claim of generality to other scenes, instruments, or reconstruction settings.

## Conclusion

The dither-associated relative-RMSE advantage replicated across all three tested gradient amplitudes with an estimated, rather than known, background map. The appropriate claim is limited to this synthetic setup and its source-free-border, horizontal-linear-background calibration assumption. A next robustness test should challenge that assumption (for example, contaminated borders or a gradient model mismatch) before making broader claims.
