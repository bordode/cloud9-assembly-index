# Synthetic Review Workflow Prototype

**Status:** Experimental, synthetic-only, in-memory prototype. Not production-ready.

This prototype translates a narrow subset of the proposed review lifecycle into pure Python functions and tests. It exists to exercise procedural invariants before any integration is considered.

## Deliberate limits

- Only fictional test records should be used.
- No database, file persistence, network calls, model calls, detector, authentication, identity verification, reviewer assignment, notice delivery, or appeal service exists.
- No API route or agent/runtime integration is added.
- There is no enforcement capability. The prototype does not alter permissions, throttle, suppress, publish, message, or invoke external actions.
- The actor labels in records are descriptive test inputs, not authenticated identities.
- The event list is ordinary mutable application data, not an immutable or tamper-evident audit log.
- A `confirmed` notice result requires a caller-supplied reference string, but this prototype does not validate the reference, inspect delivery evidence, or independently verify receipt. The reference is metadata, not proof.
- Notice-result state checks enforce only this narrow rule: a notice may be drafted after an outcome is recorded; attempted, confirmed, or failed results require the workflow to be in `notice_issued`. This is a synthetic lifecycle check, not a delivery mechanism or proof of service.
- An outcome already present in a record cannot be overwritten through the generic transition helper. No correction or reconsideration process is implemented; that requires a separately specified and reviewed process.
- A pending challenge cannot be closed through the generic transition helper. This deliberately fails closed until a distinct challenge-resolution process is specified; it is not a complete appeals service.
- Passing these unit tests establishes only the behavior exercised by these tests. It does not validate consciousness claims, moral status, security, or suitability for real cases.

## Invariants exercised

1. A referral starts without a finding or automated restriction.
2. Invalid lifecycle transitions are rejected.
3. A participation barrier is recorded without changing the status or outcome.
4. Notice results are constrained to the expected lifecycle states.
5. Failed notice remains distinguishable from confirmed delivery and does not imply waiver.
6. A confirmation label requires a reference field, without treating that field as verified delivery evidence.
7. An existing outcome cannot be silently overwritten.
8. A pending challenge cannot be closed via the generic transition helper, and the original outcome is preserved.
9. Input records are copied rather than mutated by transition helpers.
10. The prototype has no external-action interface.

## Before any further implementation

A separate review must identify an actual integration point and owner, define authentication/authorization, privacy and retention rules, safe evidence handling, independent review, accessible notice and appeal channels, concurrency behavior, and a tested technical boundary preventing review state from reaching enforcement controls. Any real notice-confirmation mechanism would need a separately designed and independently reviewed evidence-verification process. Any challenge-resolution or outcome-correction process must preserve the prior outcome, record the reasons and evidence for a change, and provide a meaningful review path. Do not connect this prototype to real cases or a runtime on the basis of these tests alone.
