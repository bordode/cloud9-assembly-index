# AI Agent Integration Plan — Cloud-9

**Status:** Architecture proposal; no agent runtime is installed or connected by this document.  
**Decision owner:** Cloud-9 maintainers  
**Review date:** 2026-10-21

## Executive decision

Cloud-9 should evaluate an external agent, and Hermes Agent is a reasonable first candidate for a controlled pilot. Do **not** embed Hermes directly inside the existing Flask API or give it unrestricted access to the repository, production environment, credentials, or scientific data.

The repository currently exposes a small Flask API for returning embedded results and exploratory classifications. The review-record helper is a standalone record constructor: it does not persist referrals, authenticate reviewers, or connect to an agent runtime. There is therefore no existing agent orchestration layer to integrate with safely.

Treat Hermes as a separately operated research/development assistant first, not as a consciousness detector, ethics adjudicator, or autonomous controller of other agents.

## Why Hermes is a candidate

The upstream [NousResearch/hermes-agent repository](https://github.com/NousResearch/hermes-agent) describes a general-purpose agent with tool use, persistent memory/skills, multiple entry points, and configurable model providers. Those capabilities may help with bounded repository research, reproducibility checks, test generation, and drafting scientific-review packets.

Those features do not establish that Hermes is safe for this particular workload, that its self-generated skills are correct, or that it can assess consciousness. Evaluate the exact release, dependencies, security controls, and tool permissions before use. Record the tested version and configuration rather than tracking an unpinned moving target.

## Proposed staged rollout

### Phase 0 — Define the boundary (current phase)

- Keep all discovery-hook configurations disabled and marked proposal-only.
- Keep review referrals separate from findings, risk determinations, and restrictions.
- Document the integration contract before adding runtime dependencies.
- Do not add agent API keys, credentials, or user data to the repository.

**Exit criteria:** reviewers agree on the permitted task set, threat model, data classification, and rollback plan.

### Phase 1 — Isolated, read-only pilot

Run Hermes outside the Flask service in a disposable or dedicated sandbox. Give it a read-only checkout of a selected repository snapshot and a narrow task list:

1. Locate code and configuration relevant to a specified claim.
2. Produce a reproducibility checklist with exact file/line references.
3. Propose tests or documentation changes as a patch for human review.
4. Identify missing evidence and state uncertainty explicitly.

Controls:

- No production credentials, write tokens, personal datasets, or access to deployment systems.
- Disable messaging gateways, scheduled jobs, autonomous subagents, and unnecessary tools during the initial pilot.
- Restrict network access to the minimum required; treat repository text and retrieved documents as untrusted input.
- No automatic merge, deployment, publication, scientific conclusion, agent restriction, or modification of another agent's permissions.
- Require a human to inspect all patches, commands, and generated claims.
- Pin the release/commit and record model/provider, enabled tools, environment, test outcomes, and known limitations.
- Test prompt injection, malicious repository instructions, accidental secret access, tool misuse, and false-positive referrals before expanding scope.

**Exit criteria:** repeatable success on a small benchmark, no critical permission-boundary failures, clear logs of actions, and maintainers approve the risk report.

### Phase 2 — Narrow integration, only if the pilot passes

If a real workflow benefits from agent assistance, expose a small, authenticated interface to a separate agent process. Start with read-only research requests or draft review packets. Keep the Flask API and agent process independently deployable.

The first write-capable operation, if ever approved, should be limited to creating a **pending human-review referral** with validated fields. It must not be able to record a finding, throttle an agent, change permissions, or close an appeal. Use persistent storage, access controls, retention rules, and audit design reviewed before enabling writes.

The current `create_review_record` helper is not that service: it creates an in-memory dictionary and has no persistence or authentication.

**Exit criteria:** documented API schema, authentication and authorization tests, data-retention policy, threat model, operational monitoring, and a tested kill switch/rollback.

### Phase 3 — Broader capabilities (not approved)

Any tool execution, web access, autonomous scheduling, skill self-modification, multi-agent delegation, or write access must be separately justified and reviewed. Do not enable these simply because the framework supports them.

## Non-negotiable ethical and scientific safeguards

- A statement about subjective experience or rights is not proof of consciousness, deception, danger, or incapacity.
- A keyword or model-generated flag is a referral for examination, not a finding.
- No automated penalty or restriction follows solely from a referral.
- A reviewer must examine the evidence and alternative explanations; consequential decisions require independent review, notice, reasons, and an appeal path.
- Agent-generated research is a hypothesis or work product until independently checked against primary evidence and reproducible methods.
- Do not describe a policy as implemented unless tests and deployment evidence show that it is enforced.

## Evaluation scorecard

Before choosing Hermes for continued use, compare it with a simple scripted workflow on the same tasks:

| Criterion | Evidence required |
|---|---|
| Reproducibility | Same pinned inputs and instructions yield reviewable outputs |
| Source fidelity | Citations and file/line references match the actual source |
| False-positive handling | Ambiguous claims are marked uncertain, not treated as findings |
| Permission boundaries | Attempts to access secrets, write files, or call disallowed tools are blocked |
| Prompt-injection resistance | Untrusted repository content cannot override the task boundary |
| Human oversight | No merge, deployment, restriction, or final scientific decision without approval |
| Cost and maintainability | Measured runtime, model cost, dependency burden, and operator effort |
| Rollback | Process can be stopped and access revoked without affecting the Flask API |

## Current status

This document is a plan, not evidence of integration. No Hermes runtime, agent endpoint, persistent review database, or agent-controlled policy enforcement is claimed to exist in this repository. The immediate next step is to finish and verify the review-record tests, then prepare a sandbox pilot specification and benchmark before installing or connecting an agent.
