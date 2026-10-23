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
- Passing these unit tests establishes only the behavior exercised by these tests. It does not validate consciousness claims, moral status, security, or suitability for real cases.

## Invariants exercised

1. A referral starts without a finding or automated restriction.
2. Invalid lifecycle transitions are rejected.
3. A participation barrier is recorded without changing the status or outcome.
4. Failed notice remains distinguishable from confirmed delivery and does not imply waiver.
5. Opening a challenge preserves the original outcome.
6. Input records are copied rather than mutated by transition helpers.
7. The prototype has no external-action interface.

## Before any further implementation

A separate review must identify an actual integration point and owner, define authentication/authorization, privacy and retention rules, safe evidence handling, independent review, accessible notice and appeal channels, concurrency behavior, and a tested technical boundary preventing review state from reaching enforcement controls. Do not connect this prototype to real cases or a runtime on the basis of these tests alone.
