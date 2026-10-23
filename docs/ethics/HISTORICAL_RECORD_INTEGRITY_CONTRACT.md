# Historical Record Integrity Contract (Design-Only)

**Status:** Proposed requirements for a future implementation  
**Applies to:** The synthetic review-workflow prototype and any future implementation derived from it  
**Runtime status:** Not implemented; this document is not evidence of tamper resistance, authenticated identity, or production readiness.

## Purpose

Define what a future system must demonstrate before it describes case history as preserved, traceable, or tamper-evident. The current Python prototype returns deep-copied dictionaries and keeps event/history data in ordinary mutable in-memory structures. Those behaviours are useful for synthetic tests, but they do not establish durable or trustworthy audit history.

## Required distinctions

These are separate properties and must not be conflated:

1. **Copy independence:** modifying a returned copy does not mutate the particular input object passed to a helper. This is a limited in-process property.
2. **Record consistency:** fields and links satisfy the documented schema and cross-record rules. Schema checks do not prove that the record is genuine.
3. **Historical preservation:** a prior closure, outcome, or decision remains retrievable as originally recorded. This requires storage and access controls beyond a mutable dictionary.
4. **Traceability:** every correction, review decision, or authorized reopening action is a distinct event linked to the relevant case, request, prior event/version, and resulting event/version.
5. **Identity and authority:** the system independently verifies who acted and whether that actor was authorized for the specific action. A caller-supplied actor label or authority-basis string is not verification.
6. **Integrity assurance:** the system can detect defined classes of unauthorized modification and explain the threat model, trust assumptions, and limits of that detection. A checksum attached to data that the same untrusted actor can rewrite is not sufficient.

## Normative requirements for a future implementation

### R1 — Preserve the original record

- A closure and its associated outcome must not be silently overwritten by a later request, challenge, correction, or reopening decision.
- The system must retain a stable identifier for the original case and a version or event identifier for the closure and outcome in force at the time of the request.
- A snapshot may help compare values, but a copied snapshot alone is not proof that the source was authentic or unchanged.

**Acceptance test:** after a correction or reopening workflow, retrieve the original closure/outcome and demonstrate that its recorded values and identifiers remain available and unchanged.

### R2 — Represent changes as linked events

- A correction, post-closure review decision, and reopening authorization must be represented as separate events, not as edits to the original event.
- Each event must link to the case, the applicable request, and the prior event/version it relies on.
- The record must distinguish a request to reopen, a decision authorizing reopening, and an actual state transition. One must never imply another.
- If a real reopening occurs, it must be a separately authorized and auditable state transition with its own timestamp, actor identity, authority evidence, scope, and reason.

**Acceptance test:** a test can reconstruct the ordered event sequence and identify which event introduced each change, without inferring authorization from a request or recommendation.

### R3 — Verify identity and authority separately

- Authenticate the actor through a defined identity mechanism.
- Check action-specific authority at the time of the action; retain enough evidence to audit the decision without exposing unnecessary personal data.
- Record reviewer-independence/conflict checks as verified, failed, or unverified—not as a free-text assertion alone.
- On missing, invalid, or unverifiable authority, fail closed for the privileged action while preserving the request and recording the failure where safe.

**Acceptance test:** caller-supplied labels such as `"reviewer"` or `"authorized"` cannot satisfy authentication or authorization checks.

### R4 — Define and test the integrity threat model

Before claiming tamper-evident history, document:
- which actors and failure modes the design is intended to detect;
- who controls the storage, integrity keys, backups, and verification process;
- how event ordering, deletion, replay, rollback, and key compromise are handled;
- how verification failures are surfaced, investigated, and preserved;
- how retention, deletion, privacy, access, export, and legal obligations interact with history preservation.

Use an append-only or otherwise independently protected event store and an integrity-verification method appropriate to that threat model. A hash chain, signature, or external checkpoint may be a component, but none alone proves that the original input was true, that an authorized person acted, or that every possible tampering event will be detected.

**Acceptance test:** controlled alteration, deletion, reordering, replay, and rollback scenarios are tested against the stated threat model; expected failures are explicit and cannot be reported as successful verification.

### R5 — Preserve privacy and procedural fairness

- Collect only evidence needed for the review and integrity purpose.
- Document retention and deletion rules, access controls, correction mechanisms, and how affected parties can challenge inaccurate records.
- A failed notice attempt or absent response must not be treated as receipt, consent, waiver, or agreement.
- Integrity controls must not convert an unverified allegation into a finding, or make a consciousness/moral-status claim itself grounds for punitive treatment.

**Acceptance test:** tests and documentation show that notice failure, non-response, or a disputed record does not silently become an adverse finding or waiver.

### R6 — State limits plainly

The interface and documentation must distinguish:
- recorded versus independently verified;
- requested versus authorized versus executed;
- in-memory test data versus durable records;
- schema validity versus authenticity;
- integrity detection versus truth of the underlying content.

**Acceptance test:** user-facing status labels do not describe a record as immutable, authenticated, authorized, delivered, or tamper-proof unless the corresponding mechanism exists and has been tested.

## Current prototype boundary

The current synthetic prototype does **not** implement durable storage, authenticated identities, authority enforcement, an append-only event store, cryptographic verification, trusted timestamps, backup/rollback protection, or a real reopening transition. Its event arrays and snapshots are ordinary Python data. Deep-copy behaviour and input validation must not be described as historical integrity.

All tests must continue to use fictional synthetic fixtures. This document does not authorize production use, real-case ingestion, external actions, or activation of discovery hooks. Existing proposal-only hooks must remain disabled until their behavioural and integration tests explicitly replace disabled-state assertions.

## Readiness gate

Do not claim historical integrity or mark a production workflow ready until the design has:
1. a reviewed threat model and data-lifecycle policy;
2. authenticated identity and action-specific authorization;
3. durable event/version storage with independent integrity verification;
4. tests for modification, deletion, ordering, replay, rollback, concurrency, and recovery;
5. privacy, accessibility, notice, correction, and appeal procedures;
6. independent review of the implementation and its stated limitations.

Passing unit tests is evidence only for the behaviours those tests actually exercise.
