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
- The fresh-seed 90-trial replay completed and uploaded artifact `deblending-poisson-fit-diversity-audit` (556,877 bytes; GitHub digest `sha256:b99053fb932bf7661838205489784c9d0dfe6f6e90c1a6095eba2ba0b84d9482`).
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


## Post-hoc truth-score extension — workflow 42358783962

Commit tested: `8182dac1bdbdf304cafb11bef46da61f2a31d4e4`.

The extension completed successfully:
https://github.com/bordode/cloud9-assembly-index/actions/runs/42358783962

- All three tests passed; the fresh-seed 90-trial replay completed.
- Artifact: `deblending-poisson-fit-diversity-audit`, 657,058 bytes; GitHub digest `sha256:badd58e144e48b2d2949e6db474642851e95dda341b6bf856ea04418cf9c3dea`.
- The audit scored each successful candidate fit against the known synthetic source positions only after fitting and BIC selection. These truth scores are labels for evaluation; they do not feed back into proposal generation, fitting, or selection.

### Matched-source count

Across 423 proposal steps with successful fits:

- BIC-selected fit matched the maximum post-hoc candidate source count in 408/423 steps (96.45%).
- In 15/423 steps (3.55%), another candidate matched more truths: 11 cases by one source and 4 cases by two.
- Mean matched truths: 2.648 for the BIC-selected fit versus 2.693 for the best candidate by matched-source count (mean gap 0.045 source per step).

This suggests BIC usually selects a candidate with the strongest source-count recovery among the available fits in this particular synthetic replay. It is not a universal statement about BIC or real images.

### Positional accuracy conditional on matched-source count

A second, explicitly oracle-style diagnostic was calculated after the run: among candidate fits tied for the maximum matched-source count in a step, select the one with the lowest post-hoc matched-position RMSE. This comparator uses truth and is not an admissible detector rule.

- In 407 steps with at least one matched truth where the BIC-selected fit attained the maximum candidate matched-source count, its mean per-step matched-position RMSE was 0.4945 px; the lowest-RMSE candidate among the same-count alternatives averaged 0.4889 px.
- The BIC-selected fit had a higher RMSE than that post-hoc comparator in 342/407 steps (84.0%).
- The median per-step RMSE excess was only 4.99e-6 px, but the 90th percentile was 1.50e-4 px and the 99th percentile 0.108 px; the maximum was 0.431 px.

Thus, BIC's selected candidate usually ties the best available candidate on the coarse matched-source count, but it does not generally minimize truth-based positional error among candidates with that same count. The distribution is highly skewed: typical differences are tiny, while a small tail contains materially larger positional penalties. This is a post-hoc diagnostic, not evidence that the oracle comparator could be used operationally.

### Interpretation and limits

The result answers the narrow question more positively for source count than for exact localization: BIC usually chooses a candidate that recovers as many sources as any alternative in the proposal pool, but lowest BIC is not equivalent to best truth-position reconstruction. The candidate pool itself may omit better solutions, and the benchmark remains a replay on synthetic scenes. Matched-source scoring uses a 1 px assignment tolerance and does not establish flux accuracy, calibrated uncertainty, robustness to PSF/model mismatch, or performance on real observations. Truth remains strictly evaluation-only.

PR #38 remains draft and unmerged.

## Candidate-level BIC versus localization audit — implementation update

The next diagnostic extension records, for every successful proposal fit:

- Candidate rank and whether it was selected by candidate BIC (distinct from the detector's later acceptance decision).
- Its individual Poisson BIC and Poisson deviance.
- Post-hoc matched-truth count using the existing 1 px one-to-one scoring rule.
- Post-hoc matched-position RMSE in pixels, calculated only over truth/candidate matches within that 1 px tolerance. RMSE is null when there are no matched sources; it is not silently treated as zero.

This enables within-step comparisons among fits with the same matched-source count: does a lower BIC tend to coincide with lower positional RMSE, or are BIC differences effectively uninformative near ties? Any truth-based localization metric remains strictly post-fit and post-selection. It is not an admissible operational selection criterion.

The aggregate summary now tolerates steps with no successful candidate fits and reports missing selected-fit records rather than assuming every step contains one. Tests cover candidate metrics, selected-rank labelling, empty candidate lists, and empty aggregate summaries.

The extension does not change proposal generation, optimizer inputs, BIC calculation, detector acceptance, or stopping behavior. Results will be reported only after the workflow validates this implementation and the fresh-seed replay completes.

## Candidate-level BIC versus localization results — fresh-seed audit

Workflow run: 42364860241  
Artifact: `deblending-poisson-fit-diversity-audit`  
Artifact digest: `sha256:6c11cb670664ba39041981955f1feb641b7c36e3418b2395d418025ff58ebda2`

The updated workflow passed all tests, completed the fresh-seed 90-trial replay, and uploaded the full audit artifact (720,855 bytes). The replay contains 423 proposal steps with successful candidate fits and 4,230 pairwise fitted-scene comparisons.

### Equal-recovery-count comparisons

To avoid conflating source recovery with localization, candidate fits were grouped within each proposal step by identical post-hoc matched-truth count. Only groups with at least two fits and defined matched-position RMSE were used.

- 464 within-step, equal-recovery-count groups contained at least two candidate fits.
- Across these groups, 3,764 candidate pairs had non-tied BIC and RMSE orderings: 1,832 concordant and 1,932 discordant. The concordance fraction was 48.7%, close to chance ordering rather than a useful monotonic relationship.
- Across the 464 groups, the median within-group Spearman rank correlation between BIC and matched-position RMSE was 0.0; the mean was -0.0248. The sign and magnitude do not support BIC as a reliable localization ranking in this benchmark.
- In 408 groups containing the BIC-selected fit and at least one same-recovery-count alternative, the BIC-selected fit had worse RMSE than the best-localizing alternative in 351 groups, and better RMSE in 57. No exact RMSE ties occurred.
- Mean RMSE for the BIC-selected fits in those 408 comparisons was 0.4957 px, versus 0.4912 px for the best-localizing alternative in each group. Median selected-minus-best RMSE excess was 5.31e-6 px; p90 0.0002736 px; p99 0.1080 px; maximum 0.4313 px.
- The selected candidate was the minimum-BIC fit in all 423 successful-fit steps; there were no missing or duplicate selected-fit labels.

Most selected-versus-best-localization differences are extremely small, but the tail is material. The pairwise ranking result is more important than the small mean RMSE gap: among fits with equal matched-source count, BIC does not reliably order positional accuracy in this synthetic benchmark.

### Interpretation and limits

This is a post-hoc diagnostic using known synthetic truth. It does not provide a truth-aware selector and must not be used to alter candidate generation, fitting, candidate-BIC selection, detector acceptance, or stopping. BIC and Poisson deviance differences are equal here because candidate fits within a step use the same model dimension and penalty.

The result does not establish that BIC is generally unsuitable, nor that another operational metric would improve recovery. It establishes only that, for this benchmark and these candidate fits, near-equal or lower BIC is not a dependable proxy for more accurate localization once matched-source count is held constant. Coordinate assignment and the 1 px matching threshold remain limitations; weak, blended, or coincident sources can make post-hoc assignments ambiguous.


## Source-level crowding and localization diagnostic — implementation update

A further post-hoc diagnostic now records source-level outcomes for every successful candidate fit:

- Each known truth source is matched one-to-one to fitted candidates using minimum-total-distance Hungarian assignment.
- A source is counted as matched only when its assigned candidate is within the existing 1 px tolerance.
- The audit records the truth source's amplitude and rank, nearest-neighbour truth separation in pixels and PSF-sigma units, and the number of other truth sources within 2 PSF sigma.
- It records the assigned candidate distance and the difference between the nearest and second-nearest fitted-candidate distances as a local assignment-ambiguity indicator.
- Aggregate descriptive summaries are grouped by nearest-neighbour crowding band and by truth-flux rank band.

The diagnostic is strictly post-fit and post-selection. It does not affect proposal generation, optimizer inputs, BIC, acceptance, or stopping. The 1 px assignment rule is inherited from the existing benchmark and is not a claim that every match is physically unambiguous. The nearest-versus-second-nearest distance margin is a local ambiguity indicator, not a complete probabilistic assignment uncertainty.

Repeated source observations across candidate fits are correlated; grouped counts must not be treated as independent samples or as a population-level significance test. This extension is intended to identify where to inspect the existing synthetic results, not to establish a universal blending law. Results will be interpreted only after the updated workflow tests and full replay complete.
