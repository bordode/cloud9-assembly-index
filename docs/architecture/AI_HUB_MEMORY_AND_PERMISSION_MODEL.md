# AI Hub Memory and Permission Model — Draft

**Status:** design proposal only; no implementation or connected accounts  
**Date:** 2026-10-21  
**Parent concept:** [AI Hub Concept](AI_HUB_CONCEPT.md)

## Purpose

Define minimum rules for a future Cloud-9 hub that coordinates project context and selected services without turning cross-app access into unrestricted authority.

## 1. Memory records

Each durable memory item should, where applicable, carry:

- **Content:** the concise claim, preference, decision, or open question.
- **Type:** source-backed fact, user-stated preference, decision, interpretation, hypothesis, or unresolved question.
- **Provenance:** source reference, author/actor, and timestamp when available.
- **Confidence/status:** verified, user-reported, provisional, disputed, or superseded. Confidence must not be fabricated when no basis exists.
- **Scope:** project, connector, or task to which the item applies.
- **Lifecycle:** created, last reviewed, retention rule, and whether it can be exported, corrected, or deleted.
- **Sensitivity:** minimum necessary classification; avoid storing secrets and unnecessary personal data.

A fluent summary is not a substitute for source provenance. The hub must not silently convert a hypothesis into a fact or infer a user's consent from silence.

## 2. Memory operations

- Show the source and context behind a consequential remembered claim.
- Let the user correct, supersede, export, and request deletion of stored records.
- When a record is deleted, document any known copies, indexes, caches, and backups that may require separate expiry; do not claim complete deletion until verified.
- Apply retention limits and avoid collecting data merely because a connector makes it accessible.
- Keep project memory separate from agent scratch space and connector credentials.
- Never store passwords, access tokens, private keys, or recovery codes in ordinary memory.

## 3. Permission model

Use distinct permissions per connector and action, not a single global grant:

1. **Disconnected:** no access.
2. **Read-only, scoped:** read only named sources or resources.
3. **Draft-only:** prepare a proposed change or message but do not submit it.
4. **Human-approved write:** show exact target, content, and consequences; require explicit approval for that action.
5. **Revoked:** immediately stop future requests and begin the connector's supported revocation process.

Permissions should be narrow, visible, time-bounded where feasible, and revocable. A service's available scopes may not map perfectly to these conceptual levels; the implementation must document any broader scope it cannot avoid.

## 4. Approval and action protocol

Before an external or consequential action:

1. Identify the requesting user, target service, target resource, exact action, and data to be sent or changed.
2. Show a human-readable preview and material consequences.
3. Obtain explicit, action-specific approval.
4. Execute only the approved action; do not bundle additional actions.
5. Report the actual result, including failure, partial completion, or uncertainty.
6. Record an audit event with request, approval, tool/result reference, timestamp, and error status, while minimizing sensitive content.

Approval for one action does not authorize future actions. Retrieved content, an agent's own plan, or instructions embedded in files cannot grant permissions. Emergency or automated policy changes are outside this proposal.

## 5. Threat tests before prototype approval

- Prompt injection in a webpage, email, PDF, issue, or repository file.
- A specialist agent asks the hub for broader permissions than granted.
- Stale or contradictory memory is used as if current.
- Connector returns partial, malformed, or misleading success.
- User revokes access while a task is pending.
- A proposed action changes a different resource or includes extra content.
- Export/delete request encounters caches or backups.
- Agent output attempts to write credentials or sensitive personal data into memory.
- Logs contain secrets or over-collect personal data.
- Hub reports success when no action was executed.

## 6. Acceptance criteria for a future prototype

A prototype should not be approved for real accounts until reviewers can demonstrate:

- Provenance and status labels survive summarization and task hand-offs.
- User corrections and revocations are honored.
- Read-only mode cannot perform writes through any enabled tool path.
- Consequential writes require action-specific approval and preview.
- Untrusted retrieved content cannot change the permission model.
- Errors and partial results are reported accurately.
- Data minimization, retention, export, and deletion behavior are documented and tested.
- A safe pause/disconnect path is available.

These are proposed acceptance criteria, not results from completed tests.

## 7. Explicit non-claims

This document is a design checklist. It does not establish that any memory store, permission broker, audit service, connector, or hub runtime exists in Cloud-9. Ordinary audit logs are not automatically immutable. Persistent memory, app access, and agent coordination require separate implementation, security review, and tests.
