# Poisson proposal-fit diversity audit

## Question

The top-five/BIC experiment repeatedly shows a small mean recovery gain, but most successful proposal fits have nearly identical BIC values. Do the alternatives actually converge to the same fitted scene, or do materially different source configurations exist and get selected?

## Design

Replay the same predeclared top-five/BIC 90-trial synthetic grid and fresh seed range used by PR #37. No detector decision rule, proposal ranking, likelihood, optimizer, BIC penalty, or stopping rule is changed. The only detector instrumentation is recording each proposal fit's fitted source coordinates, amplitudes, and background in the candidate-step diagnostics.

After detection, compare candidate fitted scenes within each greedy step:
- Match source coordinates one-to-one using minimum-total-distance assignment.
- Compute RMS and maximum matched positional displacement in pixels.
- Compute relative RMS amplitude difference and absolute background difference.
- Compare BIC/deviance spread alongside scene-configuration spread.
- Classify numerical near-ties using predeclared positional thresholds: RMS <= 1e-3 px and <= 1e-2 px. Also report broader differences above 0.05 px; these are descriptive bins, not correctness thresholds.
- Use truth only after detection to assess whether selected and non-selected fitted scenes differ in post-hoc recovery score. Truth must never influence fitting, assignment among proposals, or selection.

## Primary outputs

- Number of proposal steps with at least two successful fits.
- Distribution of pairwise scene RMS displacement, max displacement, relative amplitude RMS, background difference, and BIC difference.
- Fractions of pairwise comparisons that are near-identical at 1e-3 and 1e-2 px, and materially separated above 0.05 px.
- Whether BIC spreads correlate with configuration differences.
- For each step, selected versus alternative candidate post-hoc matched-source scores, reported strictly as audit only.
- Runtime cost and optimizer function evaluations.

## Controls and limitations

- Same 90 synthetic observations, same fresh seeds starting 20261900, same geometry/exposure grid as PR #37.
- The diagnostic run repeats the detector, so it is an audit/replay, not an independent new recovery benchmark.
- Coordinate assignment between fitted scenes is diagnostic and can be ambiguous for nearly coincident or weak sources.
- Positional similarity does not guarantee identical amplitudes or likelihood; all dimensions are reported.
- The thresholds classify numerical similarity only; they do not establish scientific equivalence.
- Results do not establish performance on real astronomical images.

## Status

Predeclared diagnostic audit. No conclusions until tests, full benchmark and artifact inspection complete.
