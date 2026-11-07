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
