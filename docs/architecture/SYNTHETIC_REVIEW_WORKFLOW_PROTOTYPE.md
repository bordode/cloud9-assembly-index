# Synthetic Review Workflow Prototype

**Status:** Experimental, synthetic-only, in-memory prototype. Not production-ready.

This prototype translates a narrow subset of the proposed review lifecycle into pure Python functions and tests. It exists to exercise procedural invariants before any integration is considered.

## Deliberate limits

- Only fictional test records should be used.
- No database, file persistence, network calls, model calls, detector, authentication, identity verification, reviewer assignment, notice delivery, or appeal service exists.
- No API route or agent/runtime integration is added.
- There is no enforcement capability. The prototype does not alter permissions, throttle, suppress, publish, message, or invoke external actions.
- The actor labels in records are descriptive test inputs, not authenticated identities.
- The event list and notice-result history are ordinary mutable in-memory application data, not immutable or tamper-evident audit logs.
- A `confirmation_reported` notice result requires a caller-supplied reference string, but this prototype does not validate the reference, inspect delivery evidence, or independently verify receipt. The field `notice_delivery_status` remains `not_verified`; neither the result label nor the reference means notice was delivered or received.
- Notice-result state checks enforce only this narrow rule: a notice may be drafted after an outcome is recorded and before issuance; attempted, confirmation-reported, or failed results require the workflow to be in `notice_issued`. The generic transition helper also requires a notice to be marked `drafted` before moving to `notice_issued`. These are synthetic lifecycle checks, not a delivery mechanism or proof of service.
- Each notice-result update appends an in-memory history entry containing the new result, prior result, actor label, reason, timestamp, and an explicit `unverified_metadata` marker. This makes changes visible in the returned fixture but does not prevent a caller from altering the list or establish an immutable audit trail.
- An outcome already present in a record cannot be overwritten through the generic transition helper. No correction or reconsideration process is implemented; that requires a separately specified and reviewed process.
- A pending challenge cannot be closed through the generic transition helper. This deliberately fails closed until a distinct challenge-resolution process is specified; it is not a complete appeals service.
- Passing these unit tests establishes only the behavior exercised by these tests. It does not validate consciousness claims, moral status, security, or suitability for real cases.

## Invariants exercised

1. A referral starts without a finding or automated restriction.
2. Invalid lifecycle transitions are rejected.
3. A participation barrier is recorded without changing the status or outcome.
4. Notice results are constrained to the expected lifecycle states, and notice issuance cannot skip the drafting step or reset to a draft state after issuance.
5. Failed notice remains distinguishable from a caller-reported confirmation; neither implies verified receipt or waiver.
6. A caller-reported confirmation requires a reference field, while delivery status remains explicitly `not_verified`.
7. Notice-result changes preserve prior entries in the returned in-memory history.
8. An existing outcome cannot be silently overwritten.
9. A pending challenge cannot be closed via the generic transition helper, and the original outcome is preserved.
10. Input records are copied rather than mutated by transition helpers.
11. The prototype has no external-action interface.

## Before any further implementation

A separate review must identify an actual integration point and owner, define authentication/authorization, privacy and retention rules, safe evidence handling, independent review, accessible notice and appeal channels, concurrency behavior, and a tested technical boundary preventing review state from reaching enforcement controls. Any real notice-receipt mechanism would need a separately designed and independently reviewed evidence-verification process. Do not use a caller-reported confirmation or reference string as proof of delivery, receipt, or waiver. Any challenge-resolution or outcome-correction process must preserve the prior outcome, record the reasons and evidence for a change, and provide a meaningful review path. Do not connect this prototype to real cases or a runtime on the basis of these tests alone.
