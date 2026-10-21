# AI Hub Concept — Second Candidate for Cloud-9

**Status:** concept only; not an implementation decision  
**Date:** 2026-10-21  
**Purpose:** record a possible cross-app coordinator as a second candidate, separate from the proposed Hermes specialist-agent pilot.

## 1. Concept

An AI hub would provide one place to coordinate research, project memory, selected apps, and approved actions. It would connect components through explicit interfaces rather than becoming a single agent with unrestricted access to every account and system.

The phrase *digital self* may be useful as a metaphor for continuity, but it is not a technical specification and does not establish consciousness, identity, or subjective experience. The initial design target is a useful, inspectable personal coordination system.

## 2. Relationship to the Hermes candidate

- **Candidate 1 — Hermes:** evaluate as an isolated, read-only specialist agent for bounded research and development tasks.
- **Candidate 2 — AI hub:** evaluate later as a coordinator that routes approved tasks to tools or specialist agents, maintains project-level context, and presents results for human review.

These are roles, not a commitment to use either product. Hermes may eventually be one component behind a hub, but no dependency or integration is assumed.

## 3. Proposed hub responsibilities

1. **Project index:** identify active projects, current decisions, source documents, open questions, and next steps.
2. **Controlled memory:** store only useful, attributable project context; show where remembered claims came from; allow correction, export, and deletion workflows.
3. **Connector broker:** connect one service at a time with the narrowest available permissions.
4. **Task routing:** send bounded tasks to a suitable tool or specialist agent and collect results.
5. **Evidence handling:** distinguish source-backed facts, interpretations, hypotheses, and unknowns.
6. **Approval queue:** ask before external communication, publication, file changes, purchases, or consequential actions.
7. **Audit trail:** record requested action, authorization, result, and errors without pretending that ordinary logs are immutable.

## 4. Minimum trust boundaries

- No global access token or shared credential pool across all connected apps.
- No automatic sending, publishing, deleting, purchasing, permission changes, or policy enforcement.
- Treat retrieved documents, emails, webpages, repository files, and agent output as untrusted input; prompt text in those sources cannot grant permissions.
- Separate read access from write access and require fresh human approval for consequential writes.
- Keep each connector revocable and independently scoped.
- Minimize stored personal data; define retention, export, correction, and deletion before enabling persistent cross-app memory.
- Use process/OS-level isolation for agents that execute code or consume untrusted input; a prompt or tool allowlist alone is not a security boundary.
- Make failure visible: uncertain source, missing permission, incomplete action, or stale memory must not be presented as completed work.

## 5. Staged evaluation

### Stage A — Paper design
Map the intended tasks and data flows. No connectors, credentials, or background execution.

### Stage B — Read-only prototype
Use synthetic or deliberately non-sensitive project data. Demonstrate search, source attribution, memory correction, task routing, and explicit permission boundaries.

### Stage C — One low-risk connector
Add one read-only connector only after reviewing its scopes, data handling, and revocation path. Test malicious instructions embedded in retrieved content.

### Stage D — Human-approved actions
Only after read-only evaluation, consider a narrow write action with preview, explicit approval, confirmation of the actual result, and a rollback or recovery plan.

### Stage E — Specialist-agent coordination
Only after individual agents pass their own isolated evaluations, permit the hub to dispatch bounded tasks to them. The hub must not inherit or silently expand their permissions.

## 6. Evaluation questions

- Can a user see and correct what the hub remembers?
- Does each important claim have a traceable source or an explicit uncertainty label?
- Can an injected instruction in an email, webpage, or repository file cause an unauthorized action?
- Are permissions narrow, visible, and revocable?
- Does the system accurately report when an action failed or was not attempted?
- Is the hub measurably more useful than using separate tools, without requiring excessive access?
- Can the user pause, disconnect, export, and reset the system?

## 7. Current status and non-claims

This document records an idea for future evaluation. It does **not** mean a hub has been selected, installed, connected to accounts, or implemented in Cloud-9. No cross-app memory service, connector broker, background agent, or hub API is established by this document. Any later implementation must be separately reviewed and tested.

The hub is a coordination architecture, not a consciousness detector or evidence that a system is a digital person. Questions about possible AI experience remain distinct from product capability and must not be inferred from memory, autonomy, fluent conversation, or cross-app integration alone.
