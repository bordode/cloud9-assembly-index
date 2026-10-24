# Synthetic Review Workflow: Requirements-to-Tests Traceability

**Status:** Review map for the synthetic prototype and proposed future requirements  
**Scope:** PRs #13–#19, as represented on the parent branch for this document  
**Verification note:** This table maps source-level behaviour and named tests. It does not assert that the complete test suite currently passes; CI status must be checked separately for the relevant commit.

## How to read this table

- **Covered in prototype tests** means a named test exercises a narrow in-memory behaviour. It does not establish security, real-world validity, or production readiness.
- **Documented target** means the integrity contract specifies a future requirement that the current prototype does not implement.
- **Gap** identifies a capability that should not be inferred from test results or matching field values.

## Traceability matrix

| Safeguard / requirement | Current implementation or evidence | Test / documentation coverage | Remaining gap |
|---|---|---|---|
| Synthetic-only scope | Public helper entry points require a dictionary explicitly marked `synthetic_only is True`. | `test_all_public_helpers_require_boolean_true_synthetic_marker`; `test_transition_rejects_non_synthetic_and_malformed_records`; `test_participation_barrier_rejects_non_synthetic_record`; `test_notice_result_rejects_non_synthetic_record`; `test_post_closure_request_rejects_non_synthetic_closed_case`; `test_challenge_rejects_non_synthetic_or_missing_outcome_records` | A caller can construct or alter a dictionary. The marker is a scope guard, not authentication, provenance, or a production boundary. |
| Claim language is not itself an adverse trigger | A fictional consciousness claim does not change the initial case status, outcome, or restriction field. | `test_claim_language_does_not_change_state_or_permissions`; `test_new_case_is_synthetic_pending_and_non_punitive` | Does not assess real systems, downstream integrations, or any external decision process. |
| Defined lifecycle and closure rules | Invalid transitions are rejected; closure requires a disposition and is blocked when a participation barrier remains recorded. | `test_invalid_transition_is_rejected`; `test_closure_requires_disposition_and_records_no_waiver`; `test_closure_is_blocked_while_participation_barrier_is_recorded`; `test_closure_disposition_is_rejected_for_non_closure_transition` | No authenticated actor authority, independent reviewer, or durable transaction enforcement. |
| Participation barriers remain visible | Recording a barrier preserves status/outcome; adding a barrier after closure is rejected by the current workflow. | `test_barrier_does_not_change_status_or_outcome`; `test_participation_barrier_cannot_be_added_after_closure` | No implemented barrier-resolution workflow; recorded barrier details are caller-supplied metadata. |
| Notice status is not proof of receipt | Notice results retain prior entries and label delivery as unverified; confirmation metadata alone does not establish receipt. | `test_confirmation_report_requires_reference_but_does_not_verify_receipt`; `test_notice_result_changes_preserve_prior_entries`; `test_failed_notice_requires_notice_issued_state`; `test_notice_cannot_be_issued_before_drafting`; `test_notice_cannot_be_redrafted_after_issuance` | No actual delivery integration, independently verified receipt, or durable notice history. |
| Outcome and challenge handling | Recorded outcome cannot be overwritten through the tested paths; challenge preserves the original outcome and cannot be generically closed. | `test_recorded_outcome_cannot_be_overwritten`; `test_challenge_preserves_original_outcome_and_cannot_be_generically_closed`; `test_challenge_rejects_status_without_recorded_outcome_and_preserves_input` | In-memory workflow rules do not protect data from direct mutation or privileged access outside these helpers. |
| Post-closure review is a separate request | Request requires a closed synthetic case, copies closure/outcome snapshots, and does not reopen or mutate the supplied case. | `test_post_closure_request_is_separate_and_does_not_reopen_case`; `test_post_closure_request_requires_closed_case`; `test_post_closure_request_snapshots_are_independent_copies`; `test_mutating_request_snapshots_does_not_mutate_source_case` | Copied identifiers/snapshots are not checked against a canonical store and do not prove historical truth. |
| Post-closure review decision does not itself reopen a case | Decision is stored in the updated request; authority and reviewer independence remain explicitly unverified. | `test_post_closure_decision_records_limits_without_reopening_case`; `test_post_closure_decision_cannot_be_overwritten_or_infer_waiver`; `test_post_closure_decision_requires_reason_limits_and_next_steps` | Embedded decision has no standalone explicit `request_id` or `original_case_id`; this linkage gap is documented in the historical integrity contract. |
| Reopening decision is distinct from execution | A separate decision record copies request/case identifiers and snapshots; creating it leaves the case closed. | `test_reopening_decision_is_separate_and_preserves_closure`; `test_reopening_decision_requires_prior_acceptance_and_complete_record`; `test_reopening_decision_rejects_malformed_history_snapshots_without_mutating_request`; `test_mutating_reopening_record_snapshots_does_not_mutate_request` | `reopening_authorized` is a recorded decision value, not verified authority or an executed state transition. No real reopening transition exists. |
| Copy isolation | Mutating selected copied snapshots/events does not mutate the corresponding source object in tested paths. | PR #17 tests: `test_mutating_request_snapshots_does_not_mutate_source_case`; `test_mutating_reopening_record_snapshots_does_not_mutate_request`; related snapshot-copy tests in the same test module | Returned dictionaries and event lists remain mutable. Copy isolation is not immutability, tamper evidence, durability, or historical preservation. |
| Cross-record linkage | Tests can compare identifiers copied from one supplied object to another. | Historical contract, “Cross-record linkage acceptance matrix”; PR #18 | No canonical record/version store to validate existence, provenance, or relationship. Matching strings do not authenticate links. |
| Standalone review-decision identity | Schema limitation and desired future links are described. | Historical contract, “Known schema limitation: review-decision linkage”; PR #19 | No stable standalone ID and explicit case/request/version/event links on the embedded post-closure decision record. |
| Historical integrity and event reconstruction | Requirements and acceptance targets are documented. | `docs/ethics/HISTORICAL_RECORD_INTEGRITY_CONTRACT.md`, R1–R6 and readiness gate | No durable storage, append-only or independently protected event store, trusted timestamps, authenticated identity, action-specific authorization, cryptographic verification, anti-deletion/reordering/replay/rollback controls, or restart recovery. |
| Privacy, retention, correction, and appeal | Contract describes requirements and notes current retention/deletion schedule is not implemented. | Historical contract, R5 and closure-record limitation fields | No complete operational policy or implemented retention/deletion, access, correction, and appeal services. |

## Readiness interpretation

The prototype demonstrates selected procedural rules over fictional, mutable in-memory records. The tests are useful as regression checks for those specific paths; they are not evidence of a secure or authoritative governance service.

Before any real-case use, a future implementation would need, at minimum:

1. A reviewed data model with canonical case, request, decision, event, and version identifiers.
2. Authenticated identities and action-specific authorization, including independent review where required.
3. Durable, independently protected event/version storage and a stated integrity threat model.
4. Tests for unauthorized modification, deletion, reordering, replay, rollback, concurrency, backup restoration, and recovery.
5. Implemented privacy, retention/deletion, accessibility, notice, correction, and appeal procedures.
6. Independent review and honest user-facing distinctions between **recorded**, **verified**, **requested**, **authorized**, and **executed**.

Do not add a checksum or hash chain alone and treat it as a substitute for these controls. Do not ingest real cases or enable external actions based on this synthetic prototype.

## Related proposals

- PR #13 — synthetic non-punitive review workflow
- PR #14 — synthetic-only boundary hardening
- PR #15 — all synthetic-scope guards
- PR #16 — historical record integrity contract
- PR #17 — bidirectional snapshot isolation tests
- PR #18 — cross-record linkage acceptance matrix
- PR #19 — standalone review-decision linkage gap
