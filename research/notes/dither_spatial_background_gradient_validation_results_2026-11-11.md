# Spatial-background-gradient validation — results (2026-11-11)

## Execution record

- Repository: `bordode/cloud9-assembly-index`
- Branch: `research/dithered-stack-control-protocol`
- Pull request: [#41](https://github.com/bordode/cloud9-assembly-index/pull/41)
- Workflow: [Run #8](https://github.com/bordode/cloud9-assembly-index/actions/runs/43117565787)
- Executed commit: `2af3613520e413d796d38ff8df495986057dc374`
- Workflow conclusion: success; development benchmark, independent uniform-background validation, spatial-gradient validation, and all artifact uploads passed.
- Spatial-gradient artifact: `dither-spatial-background-gradient-validation` (270 trial records; artifact ID `13898249234`; ZIP SHA-256 `6b0675866a0c5b9ac17eb39af7c2dfc042de63d296adfcb197157221e8ffa7d0`).
- Python tests: [Run #520](https://github.com/bordode/cloud9-assembly-index/actions/runs/43117570039), success.
- Protocol: [spatial-gradient validation protocol](dither_spatial_background_gradient_validation_protocol_2026-11-11.md).

## Frozen design

- 30 fresh paired seeds: `2026111300–2026111329`, disjoint from development and prior uniform-background validation seeds.
- Richardson–Lucy iterations fixed at **2** before validation; no retuning.
- Mean background rate fixed at 0.5 expected counts per detector pixel per total-exposure unit.
- Horizontal linear gradient amplitudes: 0.0, 0.25 and 0.45. The detector-fixed map is (0.5 + a x), where (x) spans −1 to +1 across detector columns. Corresponding ranges are 0.50–0.50, 0.25–0.75 and 0.05–0.95; all have mean 0.5.
- Exact same map supplied to every frame's Poisson reconstruction likelihood.
- Nine stationary, nine aligned-dither and nine off-grid-dither frames per seed.
- Same three-source scene and detector/reconstruction geometry as prior validation.
- Primary metric: fixed-interior relative RMSE. Secondary metrics: known-centre aperture centroid and absolute flux errors.
- Paired per-seed differences; 95% t confidence intervals, n=30 at each gradient amplitude.

## Primary outcome: relative RMSE

Lower is better. Means below are across 30 seeds. Percentage reductions are computed from the mean paired dither-minus-stationary difference divided by the stationary-arm mean at that gradient amplitude.

| Gradient amplitude | Background range | Nine stationary | Aligned dither | Aligned reduction | Off-grid dither | Off-grid reduction |
|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 0.50–0.50 | 0.32534 | 0.15585 | 52.10% | 0.15460 | 52.48% |
| 0.25 | 0.25–0.75 | 0.32574 | 0.15867 | 51.29% | 0.15602 | 52.10% |
| 0.45 | 0.05–0.95 | 0.32632 | 0.15481 | 52.56% | 0.15916 | 51.23% |

## Paired inference

Differences are calculated per seed as dither minus stationary; negative values favour dither. Intervals are 95% t confidence intervals for the mean paired difference.

| Gradient amplitude | Aligned − stationary RMSE difference [95% CI] | Off-grid − stationary RMSE difference [95% CI] |
|---:|---:|---:|
| 0.00 | −0.16949 [−0.17480, −0.16418] | −0.17075 [−0.17418, −0.16731] |
| 0.25 | −0.16707 [−0.17250, −0.16164] | −0.16972 [−0.17524, −0.16420] |
| 0.45 | −0.17151 [−0.17600, −0.16703] | −0.16716 [−0.17103, −0.16330] |

All six paired RMSE intervals exclude zero in favour of dither. The magnitude of the reduction remains approximately 51–53% across the three tested gradient amplitudes.

## Aligned versus off-grid

Off-grid minus aligned paired RMSE differences (negative favours off-grid):

- Amplitude 0.00: −0.00126 [−0.00770, +0.00518]
- Amplitude 0.25: −0.00265 [−0.01019, +0.00489]
- Amplitude 0.45: +0.00435 [−0.00179, +0.01049]

All three intervals include zero. This validation does not establish an RMSE advantage for either aligned or off-grid dithering.

## Secondary metrics

Paired centroid-error differences (dither minus stationary) all have 95% intervals overlapping zero:

- Aligned: +0.00042 [−0.00533, +0.00618], −0.00319 [−0.00958, +0.00320], and −0.00136 [−0.00820, +0.00547] for amplitudes 0.00, 0.25 and 0.45.
- Off-grid: +0.00411 [−0.00286, +0.01107], −0.00342 [−0.00986, +0.00303], and −0.00275 [−0.01005, +0.00454].

Paired absolute aperture-flux-error differences favour both dither arms at all three amplitudes; all six 95% intervals exclude zero:

- Aligned: −0.02125 [−0.03017, −0.01234], −0.01341 [−0.02179, −0.00503], and −0.01426 [−0.02324, −0.00529].
- Off-grid: −0.01998 [−0.02807, −0.01188], −0.01491 [−0.02228, −0.00754], and −0.01950 [−0.02736, −0.01165].

## Interpretation boundary

This is an independent-seed result for a controlled synthetic setting. It supports persistence of the dither-associated relative-RMSE and aperture-flux-error advantages under the three tested **known, detector-fixed, horizontal linear background maps**.

It does not test blind/unknown background estimation. The exact background map is supplied to the reconstruction likelihood. Vertical or curved gradients, temporal drift, source-correlated backgrounds, read noise, dark-current drift, PSF mismatch, blind source detection, and realistic calibration/systematic effects remain untested. Off-grid shifts still use bilinear high-resolution cell interpolation. No universal dither benefit or general reconstruction stopping rule is claimed.

The two-iteration setting was fixed before validation; this experiment does not establish that two iterations is generally optimal. Preserve the raw JSON artifact with this report.
