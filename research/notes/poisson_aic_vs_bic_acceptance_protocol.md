# Poisson AIC versus BIC acceptance benchmark

## Question

The adaptive proposal pilot showed that terminal candidate fits reduced Poisson deviance but failed BIC because the three-parameter source penalty exceeded the deviance improvement. This experiment tests whether that is a BIC-specific selection effect and whether a less conservative AIC threshold changes recovery and false-extra rates.

## Six paired methods

| Proposal policy | BIC acceptance | AIC acceptance |
|---|---|---|
| Fixed top-five | `bic_top5` | `aic_top5` |
| Fixed top-ten | `bic_top10` | `aic_top10` |
| Adaptive five-to-ten | `bic_adaptive` | `aic_adaptive` |

All six methods receive the same Poisson count image within each trial. The only intended differences are proposal depth and information-criterion acceptance.

## Criteria

For (k=3N+1) fitted parameters and (n) pixels:

- Poisson AIC = deviance + (2k)
- Poisson BIC = deviance + (k\ln(n))

A candidate is accepted only if the chosen criterion decreases. Within a given proposal step, candidate fits have the same source count and parameter count, so AIC and BIC rank those candidate fits in the same order; their acceptance thresholds across source counts differ.

## Paired design

- 27 trials, three per cell.
- Geometry scales 0.8, 1.0 and 1.2.
- Exposures 1.0, 0.1 and 0.03.
- Fresh seed range begins at 20262100.
- Same pixel-integrated PSF family, Poisson objective, parameterization, bounds, optimizer tolerances and residual proposal map.
- Truth withheld from detection and used only for post-run Hungarian scoring within 1 px.

## Outcomes

Matched and missed truths, unmatched candidates, selected source count, exact seven-source recovery, proposal fits, optimizer evaluations, accepted/rejected steps, and adaptive expansion rescue counts. Report paired differences for AIC versus BIC at each proposal depth and for adaptive/fixed proposal policies within each criterion.

## Limitations

This is an exploratory synthetic benchmark, not a universal model-selection comparison. BIC's (n) is taken as pixel count under the current independent-Poisson-pixel model. If effective observations are correlated or the likelihood assumptions are wrong, the nominal BIC penalty may not have its usual interpretation. AIC can accept more complex fits but may also increase unmatched extras. No real astronomical performance claim follows.
