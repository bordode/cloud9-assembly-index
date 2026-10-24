# Authoritative Record and Version Linkage Design (Proposed)

**Status:** Design proposal only; not implemented  
**Scope:** Future review workflow derived from the synthetic prototype  
**Boundary:** This document does not authorize real-case ingestion, external actions, or production deployment.

## 1. Design objective

A future review workflow must not treat matching identifiers copied from caller-controlled objects as proof that two records are related. It needs an authoritative source of record identity, version history, and action-specific authorization before it can safely perform privileged transitions.

This proposal defines the minimum relationship model and validation sequence. It intentionally does not prescribe a database vendor, cryptographic scheme, or production architecture before the threat model, privacy needs, and operational constraints are reviewed.

## 2. Separate record types

The durable model should represent these as distinct record/event types:

1. **Case** — stable case identity and current version pointer.
2. **Case event/version** — a specific state change or versioned case representation, including closure and any recorded outcome.
3. **Post-closure review request** — a request linked to the canonical case and the exact closure/outcome versions it references.
4. **Post-closure review decision** — a separately addressable decision linked to the request, the case, the prior request version, and the decision event.
5. **Reopening decision** — a distinct authorization decision linked to the request, review decision, case, and exact versions considered.
6. **Reopening transition** — a separate event that changes the case state only after the required authority and preconditions are verified.
7. **Verification/audit event** — records a validation result, failed link, denied action, correction, or other relevant event without silently rewriting prior history.

Each record/event should have a stable unique identifier, schema version, creation time, and explicit relationship fields appropriate to its type. A timestamp or identifier by itself does not establish authenticity or ordering.

## 3. Required relationship fields

Names below are conceptual; final field names should follow the reviewed schema.

| Record type | Required references | Validation purpose |
|---|---|---|
| Case event/version | `case_id`, `event_id`, `version_id`, `prior_version_id` where applicable | Establish the event's case and intended version lineage. |
| Post-closure request | `request_id`, `case_id`, `closure_version_id`, `outcome_version_id` (explicitly nullable only where no outcome exists) | Bind the request to the canonical case and the closure/outcome versions it relies on. |
| Post-closure review decision | `review_decision_id`, `request_id`, `case_id`, `request_version_id`, `decision_event_id` | Make the decision independently addressable and identify the exact request state considered. |
| Reopening decision | `reopening_decision_id`, `request_id`, `review_decision_id`, `case_id`, `closure_version_id`, `decision_event_id` | Show which review decision and case version the authorization decision relied on. |
| Reopening transition | `transition_event_id`, `case_id`, `prior_case_version_id`, `reopening_decision_id`, `resulting_case_version_id` | Separate authorization from actual state change and retain before/after lineage. |

References must resolve to records in the authoritative store. A string copied from a request, even if it matches another string, is not sufficient proof.

## 4. Validation sequence

Before accepting a request or allowing a privileged transition, the future service should:

1. **Resolve** each referenced record by stable identifier from the authoritative store, not solely from a caller-provided nested object.
2. **Check existence and type**: the referenced record exists and is of the expected type.
3. **Check relationship consistency**: request, decision, and event all resolve to the same canonical case where required.
4. **Check version compatibility**: the decision references the request/case versions actually reviewed; reject stale or incompatible versions unless an explicit reviewed conflict-resolution path applies.
5. **Check lifecycle preconditions**: for example, a post-closure request requires the case to be closed at the referenced closure version; a reopening transition requires a valid, applicable reopening decision.
6. **Authenticate the actor and authorize the specific action** independently of linkage validation.
7. **Commit atomically**: record the action and resulting version/event together so a partial write cannot imply success without its corresponding event.
8. **Return an explicit result** that distinguishes recorded, verified, rejected, and unresolved states.

Linkage validation and authorization are separate checks. Passing one must not imply the other.

## 5. Fail-closed and uncertainty rules

- Missing, conflicting, stale, malformed, or unresolvable links must produce an explicit unresolved/rejected result.
- A failed link must not be repaired by guessing, silently substituting another record, or inventing a missing event.
- A request or recommendation must never be interpreted as authorization; authorization must never be interpreted as execution.
- A decision record must not change the case state merely because it contains a value such as `reopening_authorized`.
- If a privileged transition cannot be validated, preserve the request and the relevant failure information where safe, and do not execute the transition.
- Correcting a mistaken link should create a separately traceable correction event with its reason and authority; it must not silently rewrite the original decision history.
- User-facing labels must not describe links as authenticated or verified unless the specified validation actually occurred.

## 6. Minimum acceptance tests for a future authoritative implementation

These are design targets, not tests currently implemented by the synthetic prototype.

### Identity and relationship tests

- A request referencing a nonexistent case is rejected.
- A review decision referencing a nonexistent request is rejected.
- A request whose `case_id` conflicts with the resolved case is rejected.
- A review decision linked to a request for a different case is rejected.
- A reopening decision linked to a review decision that did not accept further reopening review is rejected.
- A record with matching caller-supplied identifiers but no authoritative source record is not accepted as linked.

### Version and concurrency tests

- A decision based on a stale request or case version is rejected or routed through an explicit conflict process.
- Concurrent updates cannot both commit incompatible transitions against the same prior version.
- The recorded transition contains the expected prior and resulting version references.
- A failed or partial transaction cannot leave a privileged state change without its corresponding audit event, or an event that falsely claims the state change succeeded.

### Authority and state-transition tests

- Correct linkage without authenticated identity or action-specific authority is insufficient for a privileged transition.
- A valid reopening decision record alone leaves the case closed.
- A real reopening transition requires a distinct authorized event and the expected prior case state/version.
- An expired, revoked, or scope-incompatible authority is rejected according to the reviewed authorization policy.

### Integrity and recovery tests

- Tampering, deletion, reordering, replay, rollback, and backup restoration are tested against a documented threat model.
- Restart/recovery reconstructs the committed version/event lineage without inventing missing links.
- Verification failures are surfaced as failures, not successful validation.
- Retention, correction, deletion, privacy, and access controls are tested alongside historical traceability.

## 7. Explicit non-goals and limits

This design does not claim that:
- stable IDs prove that a record's content is true;
- schema validation proves actor identity, independence, or authority;
- a copied snapshot is an authentic historical record;
- a hash, signature, or hash chain alone prevents all tampering;
- a durable log eliminates privacy, governance, or operational risks;
- passing acceptance tests establishes consciousness, moral status, or any other philosophical conclusion.

The current prototype remains an in-memory synthetic demonstration. It has no authoritative record/version store, authentication service, action-specific authorization service, atomic durable transaction layer, or actual reopening transition. These design requirements must not be represented as implemented capabilities.

## 8. Implementation gate

Before implementation, review the data model, threat model, identity and authorization model, event/version semantics, privacy and retention obligations, accessibility requirements, failure-handling policy, and independent audit needs. Implement and test one narrow vertical slice against synthetic fixtures first. Do not connect it to real cases or external actions until the slice has been independently reviewed and the readiness criteria are met.

## Related documents

- `HISTORICAL_RECORD_INTEGRITY_CONTRACT.md`
- `SYNTHETIC_REVIEW_REQUIREMENTS_TRACEABILITY.md`
