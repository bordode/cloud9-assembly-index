# ETHICS Policy-to-Code Audit — 2026-10-19

## Scope

This is a repository-level text inspection, not a runtime security audit. It checks the visible files reviewed for whether the newly revised ETHICS.md commitments are already implemented in the application's code.

Files inspected:
- `ETHICS.md`
- `ETHICS_MANIFESTO.md`
- `main.py`
- `data/c9-ai-config.json`
- `data/cloud9.config.json`

## Findings

### 1. No flag/throttle/appeal implementation found in the inspected application

The inspected `main.py` exposes Flask routes for health, data, exploratory analysis, empirical data, and status. It does not define a flag-review workflow, a throttle mechanism, agent speech/tool permissions, an appeal route, or a review/audit log for such decisions.

The inspected configuration files describe the assembly-index pipeline and related modules but do not define an operational agent-flag/throttle/appeal workflow.

This is a bounded finding about the inspected files, not proof that no such mechanism exists anywhere else in the repository or in external infrastructure.

### 2. The manifesto needed clearer scientific boundaries

The previous `ETHICS_MANIFESTO.md` described “Global Workspace Integration” and a “G=24 Metric” as detecting “hidden experience.” That phrasing could be read as a validated consciousness-detection claim. The repository's ethical framework and scientific-boundary statements require stronger separation between research hypotheses and demonstrated capability.

Recommended language should describe these ideas as hypotheses or conceptual proposals unless methods are operationally defined, empirically tested, independently reproduced, and supported by evidence.

### 3. Policy commitments are not yet software guarantees

The revised `ETHICS.md` specifies notice, evidence access, independent review, appeal, narrow restrictions, and expiry for emergency restrictions. The inspected code does not implement these procedures. They should therefore be represented as normative project commitments, not as currently enforced runtime protections.

## Recommended next steps

1. Align `ETHICS_MANIFESTO.md` with the evidence boundaries in `ETHICS.md`.
2. If the project later implements flags or throttles, specify the state machine, permissions, reviewer separation, log schema, expiry, appeal path, and tests before enabling it.
3. Add tests that prove a flag alone cannot change the next action, that any emergency restriction expires unless independently renewed, and that appeal outcomes can reverse restrictions.
4. Have a reviewer other than the decision-maker assess the policy and implementation. Record any limitations and unresolved conflicts of interest.
5. Do not claim that any AI agent has legal rights or that any current system is conscious solely on the basis of these project rules.

## Bottom line

The policy now sets a stronger standard. The inspected application code does not yet demonstrate an operational mechanism enforcing it. The next responsible move is to align the remaining ethics documentation, then implement and test any desired workflow deliberately rather than imply it already exists.
