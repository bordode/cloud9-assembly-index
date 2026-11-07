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


## Completed audit — 7 November 2026

The corrected workflow passed on commit `83b82efe616906feae96e1a6fbcdfd02b3332140`:
https://github.com/bordode/cloud9-assembly-index/actions/runs/42357323218

- All three fit-diversity tests passed.
- The fresh-seed 90-trial replay completed and uploaded artifact `deblending-poisson-fit-diversity-audit` (5,568,77 bytes; GitHub digest `sha256:b99053fb932bf7661838205489784c9d0dfe6f6e90c1a6095eba2ba0b84d9482`).
- 90 trials, 423 proposal steps with multiple successful fits, 4,230 pairwise candidate-fit comparisons, and 63,428 optimizer function evaluations.

### Pairwise fitted-scene differences

- Positional RMS median: 3.63e-5 px; 90th percentile: 3.737 px; maximum: 11.936 px.
- 78.46% of comparisons were <= 1e-3 px; 78.98% were <= 1e-2 px.
- 21.02% were > 0.05 px.
- Relative amplitude RMS median: 4.25e-6.
- Absolute background difference median: 2.21e-6.
- Absolute BIC difference median: 5.59e-8; 90th percentile: 4.678; maximum: 100.705.
- Correlation between absolute BIC difference and positional RMS: 0.253.
- All 4,230 pairs had the same fitted source count, so the large positional differences are not explained by comparing different-sized scenes.

### Interpretation

The alternatives do **not** all converge to the same fitted scene. The distribution is strongly mixed: roughly 79% of pairwise comparisons are numerically near-identical under the predeclared positional bins, while about 21% are separated by more than 0.05 px, with a long tail of much larger configuration differences. The median BIC difference is tiny, but the upper tail is substantial; BIC spread and positional spread are only weakly/moderately associated in this sample (r about 0.25). Thus, a near-tied BIC can coexist with materially different fitted coordinates. This audit does not establish which alternative is scientifically correct, nor whether the differences improve recovery. It is a replay of the PR #37 synthetic benchmark, not an independent benchmark; Hungarian coordinate matching can also be ambiguous for weak or coincident sources.

The result motivates a careful next step: inspect whether materially distinct fits are genuinely different local solutions or coordinate-matching pathologies, and compare their post-hoc recovery scores without allowing truth to affect proposal selection.

## Status

Completed diagnostic replay; PR remains draft and unmerged. Results are descriptive and do not establish real-image performance or identify a scientifically correct fit.
