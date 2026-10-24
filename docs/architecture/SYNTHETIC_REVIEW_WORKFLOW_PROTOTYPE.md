# Synthetic Review Workflow Prototype

**Status:** Experimental, synthetic-only, in-memory prototype. Not production-ready.

This prototype translates a narrow subset of the proposed review lifecycle into pure Python functions and tests. It exists to exercise procedural invariants before any integration is considered.


## Post-closure request demonstration

The prototype now supports a narrow, separate synthetic record for a request to review a closed case. It captures the linked case identifier, reported barrier or new information, when it was discovered, the reason review is requested, and snapshots of the original closure and outcome. A separate decision record requires a bounded decision category, rationale, evidence limitations, and next steps.

The supported request decisions are `accepted_for_reopening_review`, `reopening_not_warranted`, `more_information_requested`, and `inconclusive`. These describe the request assessment only. Even `accepted_for_reopening_review` does not reopen the original case. The original case remains unchanged, and the original closure and outcome are preserved in the request record. This prototype does not implement an authorized reopening event, an independent review service, an accessible notice/appeal channel, or a route for modifying the original case.

The decision record explicitly marks reviewer authority and independence as unverified. Actor labels are not authenticated identities. The function requires recorded rationale, evidence limitations, and next steps, but cannot verify their truth or quality. Request and decision records remain ordinary mutable in-memory data; they are not immutable audit evidence. No status creates an enforcement capability or changes permissions.


A further helper records a separate reopening decision only after the request has been accepted for reopening review. It requires a decision, reason, scope, evidence limitations, next steps, and a stated authority basis. The record preserves snapshots of the original closure and outcome and explicitly states that it does not change the original case status or overwrite its closure.

The reopening-decision helper rejects a missing closure snapshot, a closure snapshot without a non-empty disposition or reason, a missing `original_outcome_snapshot` field, a non-record outcome snapshot, or an outcome record without a valid category and non-empty rationale. Functions that explicitly require a synthetic record also require `synthetic_only` to be the Boolean value `true`; truthy substitutes such as the string `"false"` are rejected. An explicit `null` outcome snapshot is permitted when the original case had no recorded outcome; omitting the field is not treated as equivalent to recording that there was no outcome. The rejection path is tested to leave the supplied request unchanged. These are input-shape checks, not proof that the snapshots are authentic or complete.

The terms `reopening_authorized` and `reopening_not_authorized` are labels in a synthetic fixture, not proof of actual authority. The record marks authority and reviewer independence as unverified. It does not perform a reopening transition, authenticate a decision-maker, or create a real case event in the original record. A production design would need a separately reviewed authorization model and a new, append-only status event that preserves the original closure and outcome; this prototype does not provide append-only or tamper-evident storage.

## Outcome correction boundary

The prototype rejects replacing an outcome through the generic transition helper, and its regression test checks that a rejected replacement leaves the entire input record unchanged. No outcome-correction or amendment helper is implemented. Before one is considered, a separate reviewed specification should define at least: a stable link to the original outcome; the specific field(s) proposed for correction; the prior value and proposed replacement; the factual or procedural reason; supporting evidence and limitations; uncertainty; the request and decision timestamps; and a record of who supplied each actor label. The design must preserve the original outcome and rationale as historical information rather than silently replacing them.

Any future amendment record in this prototype would still be caller-supplied, synthetic metadata. It could not authenticate a requester or reviewer, verify authority or independence, establish evidence quality, or provide append-only/tamper-evident storage. A correction request must not itself change case status, permissions, or enforcement. Do not implement a correction path until its decision states, authorization boundary, and review route have been specified and separately reviewed.

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
- Other permitted generic closures require an explicit disposition and reason. Generic closure is blocked while any participation barrier is recorded, because this prototype has no barrier-resolution process. When closure is permitted, the closure record notes that no barrier was recorded and preserves notice delivery as `not_verified` when applicable. It does not establish that a response occurred, that notice was received, or that any right was waived. The prototype rejects adding a participation barrier directly to a closed case because it has no post-closure review request or reopening-decision workflow. The design specification now calls for a separately recorded post-closure review route that preserves the prior closure and outcome. That route is not implemented here; a barrier report must not automatically reopen a case or be rejected by a future complete process merely because closure occurred. This prototype limitation is not a claim that real cases should be unable to reopen.
- The closure record now explicitly labels three design-specification gaps: outstanding uncertainty is `not_captured_by_prototype`, retention/deletion scheduling is `not_implemented`, and the post-closure route is `separate_request_supported_authorized_reopening_not_implemented`. These labels expose missing functionality; they do not resolve the gaps or certify closure as procedurally complete.
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
10. Generic closure requires an explicit disposition, is blocked while a participation barrier is recorded, and does not imply response, receipt, or waiver.
11. This prototype rejects barriers submitted directly to a closed case because no post-closure review route is implemented; the design specification requires a future review-request path that preserves closure history.
12. Input records are copied rather than mutated by transition helpers.
13. The prototype has no external-action interface.
14. A separate reopening-decision record rejects a missing or malformed original-history snapshot, and the regression tests verify that rejection leaves the supplied request unchanged.

Reviewer conflict-check metadata is required on synthetic post-closure and reopening decision records. The field records only the supplied description; its status is explicitly `reported_not_verified`. It does not authenticate the reviewer, prove that a conflict check was actually performed, or establish independence. Those require a separately designed and reviewed process.

## Before any further implementation

A separate review must identify an actual integration point and owner, define authentication/authorization, privacy and retention rules, safe evidence handling, independent review, accessible notice and appeal channels, concurrency behavior, and a tested technical boundary preventing review state from reaching enforcement controls. Any real notice-receipt mechanism would need a separately designed and independently reviewed evidence-verification process. Do not use a caller-reported confirmation or reference string as proof of delivery, receipt, or waiver. Any challenge-resolution or outcome-correction process must preserve the prior outcome, record the reasons and evidence for a change, and provide a meaningful review path. A future post-closure review path must separately record the newly reported barrier, the request to review/reopen, the authorized decision and its rationale, and the resulting status while preserving the original closure event. It must not treat a caller-supplied actor label as authenticated authority, silence as waiver, or a recorded remediation as proof that access was restored. Do not connect this prototype to real cases or a runtime on the basis of these tests alone.
