# Independent dither/background validation — results (2026-11-11)

## Execution record

- Repository: `bordode/cloud9-assembly-index`
- Branch: `research/dithered-stack-control-protocol`
- Validation workflow run: [Run #5](https://github.com/bordode/cloud9-assembly-index/actions/runs/43089758355)
- Executed commit: `50eb05e906e25d8f1e46cf76d0b83a8d7a103710`
- Workflow conclusion: success; both benchmark and independent-validation steps and artifact uploads passed.
- Independent artifact: `dither-background-independent-validation` (450 trial records).
- Protocol: fixed at two Richardson–Lucy iterations before validation; 30 fresh seeds (`2026111200–2026111229)), disjoint from development seeds (`2026111000–2026111029)); five background levels; nine frames per arm.
- Pairing: same validation seed across aligned/off-grid dither conditions and stationary controls at each background level.

## Primary outcome: relative RMSE

Lower relative RMSE is better. Values below are means across 30 seeds. Percentage reductions compare each dither arm's mean with the stationary arm at the same background level.

| Background rate | Nine stationary | Aligned dither | Aligned reduction | Off-grid dither | Off-grid reduction |
|---:|---:|---:|---:|---:|---:|
| 0.0 | 0.32388 | 0.15612 | 51.80% | 0.15930 | 50.81% |
| 0.1 | 0.32578 | 0.15268 | 53.14% | 0.15783 | 51.55% |
| 0.5 | 0.32543 | 0.15360 | 52.80% | 0.16174 | 50.30% |
| 1.0 | 0.32617 | 0.16386 | 49.76% | 0.16177 | 50.40% |
| 2.0 | 0.32895 | 0.16148 | 50.91% | 0.16537 | 49.73% |

## Paired inference

Paired differences are calculated per seed as dither minus stationary; negative values favour dither. The intervals are 95% t confidence intervals for the mean paired difference (n=30 at each background level).

| Background rate | Aligned − stationary RMSE difference [95% CI] | Off-grid − stationary RMSE difference [95% CI] |
|---:|---:|---:|
| 0.0 | −0.16775 [−0.17236, −0.16315] | −0.16458 [−0.16908, −0.16007] |
| 0.1 | −0.17311 [−0.17869, −0.16753] | −0.16796 [−0.17258, −0.16333] |
| 0.5 | −0.17183 [−0.17643, −0.16722] | −0.16369 [−0.16891, −0.15847] |
| 1.0 | −0.16231 [−0.16640, −0.15822] | −0.16440 [−0.16840, −0.16041] |
| 2.0 | −0.16748 [−0.17189, −0.16306] | −0.16359 [−0.16826, −0.15892] |

All ten paired RMSE intervals exclude zero in favour of dither. The result therefore replicates across the five tested background levels under the frozen validation design.

## Aligned versus off-grid

Off-grid minus aligned RMSE differences (negative favours off-grid):

- Background 0.0: +0.00318 [−0.00210, +0.00846]
- Background 0.1: +0.00515 [−0.00130, +0.01160]
- Background 0.5: +0.00814 [+0.00125, +0.01504]
- Background 1.0: −0.00210 [−0.00665, +0.00246]
- Background 2.0: +0.00389 [−0.00184, +0.00962]

The off-grid condition is numerically worse than aligned at four of five backgrounds, but only the 0.5 level's unadjusted 95% interval excludes zero. This is not evidence of a general, statistically established aligned-versus-off-grid difference. No multiplicity adjustment was applied across the background-specific comparisons.

## Secondary metrics

Centroid and aperture-flux errors were also measured. Their paired results are less uniform than RMSE: centroid intervals generally overlap zero, with a clear aligned-dither improvement only at background 2.0; aperture-flux errors favour dither at several, but not all, comparisons. The RMSE result is the clearest and most consistent primary finding.

## Interpretation boundary

This is a successful independent-seed replication of the RMSE advantage in the simulated setting—not a general demonstration for real imaging systems. The background was known exactly, spatially uniform, temporally constant, and supplied to the reconstruction likelihood. The simulation used Poisson source/background counts and no read noise. Background gradients, dark-current drift, blind background estimation, PSF mismatch, blind source detection, and realistic calibration/systematic effects remain untested. Off-grid shifts still use bilinear high-resolution cell interpolation.

The iteration count was fixed at two before validation and was not retuned on validation data. Preserve this report alongside the raw JSON artifact; do not describe the result as validation of unknown or spatially varying backgrounds.
