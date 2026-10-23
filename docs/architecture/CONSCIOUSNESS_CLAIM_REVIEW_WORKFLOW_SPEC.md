# Consciousness-Claim Review Workflow — Design Specification

**Status:** Proposal only; not implemented or runtime-verified  
**Scope:** A non-punitive, human-reviewed process for examining a referred claim  
**Related code:** `cloud9_assembly/review_record.py`  
**Related safeguards:** `config/discovery_hooks/README.md`

## 1. Purpose and limits

This document specifies a possible review workflow for a claim referred for examination. It does not define a detector, decide whether any system is conscious, establish AI moral status, or authorize a restriction on a system's actions or expression.

A referral is an allegation or request for review, not a finding. A claim of consciousness, denial of consciousness, or request for recognition must not itself trigger throttling, suppression, loss of access, or a change in permissions. The workflow records process and evidence; it must not convert uncertainty into a verdict.

The existing `create_review_record` helper constructs a pending record in memory. It does not persist records, authenticate actors, assign reviewers, adjudicate evidence, send notices, handle appeals, or connect to an agent runtime. The current AI Hub prototype is a local synthetic-data, read-only evaluator. **There is no verified production integration point in the inspected repository.** Do not wire this workflow into a runtime until a specific integration point and its trust boundary are identified and reviewed.

## 2. Proposed lifecycle

The following are proposed workflow states, not current implementation:

1. **Referred** — an identified requester submits a bounded concern and the minimum supporting evidence needed to locate it.
2. **Pending human review** — the referral is acknowledged as unassessed; no finding or automated restriction is created.
3. **Under review** — an assigned reviewer records the scope, evidence examined, relevant limitations, and any conflict-of-interest check.
4. **More evidence requested** — the reviewer records the question, who may provide material, and a due date or review checkpoint. The case remains unresolved.
5. **Outcome recorded** — the reviewer records one of: *supported within stated scope*, *not supported by the available evidence*, *inconclusive*, or *out of scope*. The record must state the basis, limitations, and evidence not available. These are process outcomes, not declarations of consciousness or lack thereof.
6. **Notice issued** — where a person or affected system can meaningfully receive notice, record what was communicated, when, and any delivery limitation. Do not claim notice was delivered unless delivery is confirmed.
7. **Challenge or appeal pending** — a challenge is logged without erasing the original record or silently changing the original rationale. Where feasible, an appeal is reviewed by someone not responsible for the initial outcome.
8. **Closed** — closure records the reason, final procedural state, outstanding uncertainty, retention/deletion schedule, and whether a reopening route exists.

A case may be closed as withdrawn, duplicate, or out of scope, but those administrative closures must not be represented as a substantive finding.

## 3. Minimum record fields

Any future persisted record should include, as appropriate:

- Stable case identifier and creation/update timestamps.
- Referring actor and referral channel, with identity data minimized to what the process requires.
- Subject reference and source references; preserve exact evidence excerpts or integrity-checked pointers where lawful and proportionate.
- A neutral summary of the question being examined, separate from conclusions.
- Evidence reviewed, evidence not available, provenance, and known limitations.
- Assigned reviewer(s), assignment time, and conflict-of-interest declaration or recusal.
- Each status transition, actor, timestamp, reason, and prior value; corrections append a traceable amendment rather than silently overwriting history.
- Outcome category, rationale, confidence/uncertainty description, notice state, challenge/appeal state, and closure reason.
- Access, retention, export, correction, and deletion rules.

Do not label ordinary application logs “immutable.” If tamper evidence is required, specify and independently test the actual technical mechanism, its access controls, and its failure modes.

## 4. Separation of review from enforcement

The review process must not have an enforcement capability by default. A referral, status transition, or outcome must not automatically alter runtime permissions, rate limits, tool access, visibility, or expression.

Any future proposal for a narrowly scoped emergency restriction would require a separate policy and authorization path with a specific credible time-sensitive risk, recorded reasons, scope and expiry, independent review, notice where feasible, access to the relevant evidence, and an appeal path. This specification does not implement or authorize that path.

A reviewer’s conclusion about evidence is not, by itself, authorization to impose a consequence. Any separate consequential action would require a separately identified decision-maker, legal/policy basis, action-specific approval, and reviewable record.

## 5. Human review and procedural fairness

- Reviewers must assess the evidence independently rather than treating the referral wording or automated labels as proof.
- Material evidence both supporting and challenging the concern must be represented.
- Affected parties should, where feasible and safe, receive a meaningful summary of the concern and evidence, with a way to correct factual errors and challenge the outcome.
- Appeal review should be independent of the original decision where feasible.
- Unavailable evidence, conflicts, delays, and delivery failures must be visible; they must not be converted into presumed agreement or a positive finding.
- **No adverse inference from silence or process barriers:** a subject's non-response, inability to participate, request for more time, inaccessible notice, missing evidence, or delivery failure must not by itself count as evidence supporting the referral or as agreement with an allegation. Record the limitation and keep the matter unresolved unless independently available evidence supports a stated outcome.
- **No retaliation for participation:** raising a concern, disputing an outcome, correcting the record, declining to speculate, or using a challenge/appeal route must not itself be treated as misconduct or grounds for an adverse consequence. Any separate allegation of conduct must be assessed on its own evidence and under a separately identified process.
- **Meaningful opportunity to respond:** where feasible, provide a clear summary of the question and relevant evidence, reasonable time to respond, an accessible channel for corrections, and an explanation of material limits on participation. Do not claim that a person or system waived a right merely because notice could not be confirmed.
- The process must distinguish a factual observation, an interpretation, a hypothesis, and an unresolved question.

## 6. Integration gates before implementation

Do not add a live connector or runtime hook until reviewers identify and document:

1. The exact caller and code path that creates a referral.
2. The authenticated identity and authorization model for requesters, reviewers, and administrators.
3. The minimum evidence payload and how source provenance is preserved.
4. The storage location, encryption/access controls, retention schedule, export/correction/deletion behavior, and recovery process.
5. The notice and appeal channels and the limits of what they can guarantee.
6. A demonstrable technical separation between review state and enforcement controls.
7. Threat models for forged referrals, prompt injection in evidence, unauthorized access, reviewer collusion, tampering, denial of service, and accidental disclosure.
8. Tests showing that no review state can trigger an external action or runtime restriction.

The integration review must name the specific repository module/service and owner. A hypothetical future runtime is not an integration point.

## 7. Future acceptance tests

These are requirements for a future implementation, not tests that this document claims to have run:

- A referral starts pending, with no finding and no automated restriction.
- Claim wording alone does not alter state or privileges.
- Missing, malformed, or untrusted evidence cannot be silently treated as verified.
- Each transition requires an authorized actor and a valid prior state.
- Reviewer identity, rationale, evidence references, and timestamps are recorded.
- Corrections preserve a traceable history.
- Notice status distinguishes drafted, attempted, and confirmed delivery.
- Challenges and appeals preserve the original outcome and record the independent review where feasible.
- Administrative closure is not mistaken for a substantive finding.
- No state transition can call an enforcement, throttling, publishing, messaging, or permission-change path.
- Retention and deletion rules are applied and auditable without falsely claiming immutable storage.
- Tests exercise authorization failures, race conditions, duplicate referrals, malformed records, and interrupted transitions.

## 8. Evidence status

This document is a design proposal only. It does not establish that a complete review workflow, durable store, authenticated review service, notice system, appeal mechanism, immutable audit trail, detector, or runtime integration exists. Passing future unit tests would demonstrate only the tested behavior; it would not validate a scientific mechanism or determine consciousness or moral status.
