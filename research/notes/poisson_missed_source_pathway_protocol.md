# Unified Poisson missed-source pathway audit

## Purpose

This audit asks where a source that is absent from the current accepted scene is lost by the observation-only Poisson deblender:

1. proposal generation;
2. joint candidate fitting;
3. candidate-level BIC selection; or
4. the unchanged BIC acceptance decision.

The earlier attempt to join PR #37 proposal-pool records to PR #38 fit-diversity records was not reliable: selected proposal ranks did not align consistently across the two artifacts. This protocol therefore requires all stages to be recorded in the same replay and artifact.

## Replay design

Use the existing PR #38 synthetic scene family, 90-trial grid, fresh seed range, detector, Poisson likelihood, proposal policy, optimizer settings, BIC calculation, and stopping rule. Do not change detector behavior to support the audit.

At each greedy step:

- snapshot the current accepted scene before the proposed addition;
- identify truth sources not already localized within 1 px of the current scene, using one-to-one Hungarian assignment;
- record the complete observation-only proposal pool;
- record every candidate fit and optimizer-success flag;
- record the BIC-selected proposal rank and its fitted scene;
- record whether the selected fit passed the existing BIC acceptance test;
- only after those decisions, compare the proposals and fitted scenes with hidden truth.

The 1 px threshold is inherited from the synthetic benchmark's scoring convention. It is not a universal resolution or detection criterion.

## Post-hoc stage labels

Each currently missed truth source receives one mutually exclusive label per step:

- `proposal_generation_gap`: no proposal coordinate is within 1 px and no successful candidate fit localizes the source;
- `fit_recovery_gap`: at least one proposal is within 1 px, but no successful candidate fit localizes the source;
- `bic_candidate_selection_gap`: at least one successful alternative fit localizes the source, but the BIC-selected fit does not;
- `selected_fit_rejected_by_bic`: the BIC-selected fit localizes the source, but the unchanged acceptance test rejects the step;
- `recovered_by_selected_fit`: the BIC-selected fit localizes the source and the step is accepted.

A nearby proposal is only a coordinate-proximity label. It does not prove that the proposal is a distinct source. A fit recovery is assessed separately, using one-to-one Hungarian assignment of fitted candidates to truth positions.

## Anti-peeking controls

- No truth positions, source labels, source amplitudes, or source count are passed to proposal generation, optimization, candidate-BIC selection, or acceptance.
- Truth comparisons execute only after the detector has made each step's decisions.
- The audit output is never fed back into the detector.
- No BIC penalty, optimizer tolerance, proposal score, or stopping threshold is tuned using these labels.

## Reporting

Report both aggregate stage counts and full per-trial/per-step records. Include repeated-observation caveats: the same fixed truth sources recur across multiple greedy steps and random trials, so stage counts are not independent source observations or independent astronomical samples.

Interpretation is limited to locating failure modes in this controlled synthetic setup. The audit cannot establish performance on real astronomical images, prove that BIC is generally inappropriate, or show that a proposal close to truth would be identifiable in a different scene or PSF model.

## Results — unified 90-trial replay, initial run (7 November 2026)

Workflow [run 42413035999](https://github.com/bordode/cloud9-assembly-index/actions/runs/42413035999) completed successfully. The pathway tests passed, the full 90-trial replay completed, and the artifact uploaded.

Artifact ID: `13589964295`; SHA-256: `09ea2555444f36d4a2d485127996f59599b795d81ed275080a9090e21aa4eb70`.

Across 2,171 repeated missed-source/source-step observations, the mutually exclusive post-hoc labels were:

| Stage | Count | Share of all observations |
|---|---:|---:|
| Proposal generation gap | 1,372 | 63.2% |
| Fit recovery gap | 153 | 7.0% |
| BIC candidate-selection gap | 70 | 3.2% |
| Selected fit rejected by BIC | 63 | 2.9% |
| Recovered by selected fit | 513 | 23.6% |

This initial run motivated a deeper look at ranked score-map peaks.

## Results — fresh rerun and ranked-peak audit (7 November 2026)

A subsequent commit triggered [workflow run 42414013003](https://github.com/bordode/cloud9-assembly-index/actions/runs/42414013003). The test suite, fresh-seed 90-trial replay, and artifact upload all completed successfully.

Artifact:
- Name: `deblending-poisson-fit-diversity-audit`
- Artifact ID: `13590787133`
- SHA-256: `5c30a5e4d640473e1e2808426f640f8023bdac2fbba19cdc9459adf8e164dc2b`
- 90 trials; seeds beginning at 20261900.
- 423 steps with multiple successful candidate fits.
- 4,230 pairwise fit comparisons.
- 63,428 optimizer function evaluations.

### Updated missed-source pathway counts

Across 2,171 repeated missed-source/source-step observations:

| Stage | Count | Share |
|---|---:|---:|
| Proposal generation gap | 1,373 | 63.2% |
| Fit recovery gap | 153 | 7.0% |
| BIC candidate-selection gap | 68 | 3.1% |
| Selected fit rejected by BIC | 64 | 2.9% |
| Recovered by selected fit | 513 | 23.6% |

The first four categories account for 1,658 unresolved observations. Within those unresolved observations, proposal-generation gaps account for 82.8%, fit-recovery gaps 9.2%, BIC candidate-selection gaps 4.1%, and selected-fit rejections 3.9%.

The small count changes from the initial run are retained rather than averaged: these are two fresh executions of the same declared 90-trial seed grid, and the newer artifact is the current run record.

### Ranked score-map peak coverage

For the 1,373 proposal-generation-gap observations, the audit checked the nearest peak within 1 px among the top 50 observation-derived score-map peaks after 1 px non-maximum suppression:

| Nearest qualifying peak rank | Observations | Share of proposal-generation gaps |
|---|---:|---:|
| Ranks 1–5 | 0 | 0.0% |
| Ranks 6–10 | 403 | 29.4% |
| Ranks 11–25 | 247 | 18.0% |
| Ranks 26–50 | 112 | 8.2% |
| No peak within 1 px in top 50 | 611 | 44.5% |

Thus 762/1,373 (55.5%) of these observations had a nearby peak somewhere in ranks 6–50, outside the existing five-proposal pool. The remaining 611 (44.5%) had no nearby peak among the top 50 under this diagnostic. No missed source in this subset had a nearby peak in ranks 1–5.

This is a post-hoc coordinate-proximity result. A nearby score-map peak does not prove that it represents an identifiable source, that its fit would succeed, or that BIC would accept it. The top-50 audit does not itself test expanded candidate fitting.

### Other updated summaries

- BIC-selected fit matched the best available candidate by matched-source count in 410/423 steps (96.9%).
- Mean matched truths: 2.652 for BIC-selected fits versus 2.690 for the best available candidate (gap 0.038 source per step).
- Across all candidate fits, 5,425/14,805 repeated source observations matched within 1 px (36.6%).
- Pairwise fitted-scene position RMS: median 3.63e-5 px; p90 3.74 px; maximum 11.94 px. 21.0% exceeded 0.05 px.
- Absolute BIC-difference median 5.59e-8; p90 4.68; maximum 100.71. Correlation with position RMS was 0.253.

These are descriptive synthetic replay summaries, not independent-sample estimates. The fixed scene and repeated source/step observations limit generalization.

## Interpretation and next experiment

The updated evidence separates two proposal-side issues:

1. **Candidate-pool depth:** in 55.5% of proposal-generation-gap observations, a peak within 1 px existed in ranks 6–50, but not in the top-five pool.
2. **Peak generation/localization:** in 44.5%, no peak within 1 px appeared among the top 50 after the stated suppression rule.

The next experiment should therefore investigate the residual score-map mechanism before changing BIC. First, characterize the score-map value and local geometry around missed sources, the local-maxima and non-maximum-suppression behavior, and how peak rank relates to source flux, crowding, exposure, and trial. Then run a paired candidate-depth ablation (for example top 5, 10, 25, and 50) using the same observation-only proposal scores, fitting each selected proposal once and retaining the original BIC selection and acceptance rules. Keep the original top-five detector as the paired baseline, use fresh seeds, and report added optimizer cost as well as recovery.

Truth must remain unavailable to proposal ranking, fitting, and selection. It may be used only after the run to evaluate which rank bands corresponded to missed truth positions. The top-50 proximity finding is a reason to test candidate depth, not evidence that deeper search will improve recovery.

The experiment remains a synthetic benchmark investigation. It does not establish real-image performance or a universal proposal-ranking rule.


## Candidate-depth ablation — protocol added (7 November 2026)

The next paired experiment is implemented in `research/sandbox/deblending_poisson_candidate_depth.py`, with runner `scripts/run_deblending_poisson_candidate_depth.py` and tests in `tests/test_deblending_poisson_candidate_depth.py`.

It compares proposal pool depths 5, 10, 25 and 50 on the same synthetic Poisson count image for each trial. The 90-trial 3×3 scene/exposure grid is reduced to an explicitly exploratory pilot of three trials per cell (27 paired observations) because top-50 fitting can substantially increase optimizer work.

The detector retains the same observation-derived residual score map, 1 px non-maximum suppression, Poisson deviance, model parameterization, bounds, optimizer tolerances, BIC penalty, BIC candidate selection, acceptance and stopping rules. Only the maximum number of ranked proposals sent to fitting changes. Truth is withheld until after each depth-specific run and is used only for Hungarian scoring within 1 px.

The pilot reports:
- matched, missed and unmatched candidate counts;
- exact seven-source recoveries;
- paired per-trial differences versus top-five;
- optimizer function evaluations and number of proposal fits;
- accepted and rejected steps.

The new workflow is `.github/workflows/deblending-poisson-candidate-depth.yml`. At the time of this note, the code and workflow have been committed to the PR #38 branch, but the candidate-depth pilot has **not yet completed**. No performance conclusion is available. The test and replay results will be added only after the workflow and artifact are inspected.

Interpretation guardrail: even if deeper pools improve recovery, this establishes only a result for this small synthetic pilot. Increased compute cost, trial-to-trial variation, and the possibility that nearby score peaks are not identifiable sources must be reported alongside any gain.


## Historical CI failures and resolution (7 November 2026)

Six early runs of the fit-diversity audit workflow failed before the replay stage. The run IDs and root causes were inspected directly from GitHub Actions logs:

| Audit run | Commit | Root cause |
|---|---|---|
| [#12](https://github.com/bordode/cloud9-assembly-index/actions/runs/42407643970) | `9443c22` | Test expected legacy `faintest_2`; adaptive three-band assignment returned `middle_3`. |
| [#13](https://github.com/bordode/cloud9-assembly-index/actions/runs/42407689702) | `d0d475c` | Same stale legacy flux-band expectation. |
| [#14](https://github.com/bordode/cloud9-assembly-index/actions/runs/42407725050) | `0614b8c` | Test expected `brightest_2`; adaptive assignment returned `brightest_third`. |
| [#18](https://github.com/bordode/cloud9-assembly-index/actions/runs/42408481528) | `52c9846` | Two-source fixture incorrectly expected a `faintest_third` category; adaptive bands correctly do not invent a third category for two sources. |
| [#19](https://github.com/bordode/cloud9-assembly-index/actions/runs/42408534164) | `2e6e866` | Fixture had been expanded to three truth sources, but assertion still expected two source observations (`AssertionError: 3 != 2`). |
| [#20](https://github.com/bordode/cloud9-assembly-index/actions/runs/42408567166) | `a4966e8` | Same stale source-observation count assertion (`3 != 2`). |

In all six runs, dependency installation and setup succeeded; the failing step was the diversity-audit unit-test command. The 90-trial replay and artifact upload were skipped. These failures were test/fixture expectation mismatches, not failures of the scientific replay or evidence of a detector regression.

The current PR branch test fixture now uses three truth sources, expects three source observations, one matched and two unmatched, and checks the faintest-third category only where three truth sources exist. The two-source behavior is separately tested without assuming a third band.

Subsequent complete workflow runs verified the correction and replay path:
- [Run 42409714087](https://github.com/bordode/cloud9-assembly-index/actions/runs/42409714087): unit tests, 90-trial replay and artifact upload all passed.
- [Run 42413035999](https://github.com/bordode/cloud9-assembly-index/actions/runs/42413035999): all steps passed.
- [Run 42414013003](https://github.com/bordode/cloud9-assembly-index/actions/runs/42414013003): all steps passed.

The screenshots' extracted branch label says `research/poisson-proposals`; the current PR #38 metadata identifies the head branch as `research/poisson-proposal-fit-diversity`. The six commits and workflow runs are confirmed by their exact commit hashes and run IDs above. The current branch name should be used when inspecting PR #38.

The warning about Node.js 20 deprecation in runner logs was not the cause of these failures. It is a separate maintenance warning and did not fail the jobs.
