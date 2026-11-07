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

## Status

Implementation is in PR #38. Results are provisional until the workflow completes, all tests pass, and the complete artifact is inspected.


## Results — unified 90-trial replay (7 November 2026)

Workflow [run 42413035999](https://github.com/bordode/cloud9-assembly-index/actions/runs/42413035999) completed successfully. The pathway tests passed, the full 90-trial replay completed, and the artifact uploaded.

Artifact:
- Name: `deblending-poisson-fit-diversity-audit`
- Artifact ID: `13589964295`
- SHA-256: `09ea2555444f36d4a2d485127996f59599b795d81ed275080a9090e21aa4eb70`
- 90 trials; 423 steps with multiple successful candidate fits; 4,230 pairwise comparisons; 63,244 optimizer function evaluations.

Across 2,171 repeated missed-source/source-step observations, the mutually exclusive post-hoc labels were:

| Stage | Count | Share of all observations |
|---|---:|---:|
| Proposal generation gap | 1,372 | 63.2% |
| Fit recovery gap | 153 | 7.0% |
| BIC candidate-selection gap | 70 | 3.2% |
| Selected fit rejected by BIC | 63 | 2.9% |
| Recovered by selected fit | 513 | 23.6% |

The first four categories account for 1,658 unresolved source-step observations. Within that unresolved subset, proposal-generation gaps account for 82.8%, fit-recovery gaps 9.2%, BIC candidate-selection gaps 4.2%, and selected-fit BIC rejections 3.8%.

Interpretation: in this particular synthetic replay, most missed-source observations were not associated with a proposal coordinate within 1 px of the truth. Among the remaining unresolved cases, failures after a nearby proposal existed were less frequent; BIC selection and acceptance together account for a smaller share still. This makes proposal generation the clearest next investigation target. It does not establish that residual proposals are the dominant limitation for real astronomical data, other scenes, PSFs, noise models, or proposal thresholds.

The 513 recovered observations are included because those sources were absent from the current accepted scene at the start of the step but were recovered by the selected fit during that step. They are not counted as unresolved failures.

The denominator is repeated source/step observations over 90 trials of a fixed synthetic scene, not 2,171 independent astronomical sources. A 1 px proposal-proximity test is a diagnostic convention, not proof of source identifiability. All truth-based labels remain post-hoc and do not influence the detector.

Other same-run summaries reproduce the prior fit-diversity and localization findings: 423 selected-fit comparisons; BIC-selected fit matched the best available candidate by matched-source count in 408/423 steps; mean matched count 2.648 selected versus 2.693 best available. Across all candidate fits, 5,420/14,805 repeated source observations matched within 1 px (36.6%). These are descriptive synthetic benchmark summaries, not independent-sample estimates.

## Next experiment

Investigate the observation-derived residual proposal mechanism without changing BIC first. In the same replay design, record the residual score map around every currently missed truth source, local maxima and their suppression, proposal score/rank, and distance to the nearest missed truth. Test proposal-generation diagnostics separately from any detector change. If a proposal-policy variant is later tested, preserve the original detector as a paired baseline, use fresh seeds, and keep truth strictly out of the proposal policy and all selection decisions.
