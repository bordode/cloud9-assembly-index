# Discovery Hooks — Configuration Status and Integration Limits

This directory contains JSON configuration files describing proposed discovery-hook modules. **A configuration file is not evidence that a corresponding implementation exists, is imported, is enabled at runtime, or has passed tests.**

## Configurations

- `contamination_scorer_config.json` — proposed background-contamination workflow.
- `host_gravity_emulator_config.json` — proposed host-structure baseline workflow.
- `state_budget_monitor_config.json` — proposed resource-budget heuristic.
- `mundane_mechanism_catalog_config.json` — proposed ordinary-mechanism checks.
- `consciousness_claim_detector_config.json` — proposed handling of AI messages discussing subjective experience or rights.

## Integration requirements

Before describing any hook as operational, verify that the corresponding module exists, is imported by the actual application/orchestrator, receives the documented configuration, and is covered by tests. Document runtime wiring and failure behavior.

For any consciousness-claim review workflow, a flag must be treated as an allegation, not a finding. A flag alone must not trigger throttling or suppress expression. Any narrowly scoped emergency restriction requires a specific credible time-sensitive risk, recorded reasons, an expiry, independent review, notice where feasible, and an appeal path. The current `consciousness_claim_detector_config.json` specifies throttling on flag; that setting conflicts with `ETHICS.md` and must be revised before any deployment.

Logging is not automatically immutable merely because a configuration names an audit path. Immutability, access controls, retention, reviewer responsibility, and tamper evidence must be implemented and tested.

## Evidence and governance

These files are design artifacts until implementation is confirmed. Do not describe them as implemented safeguards or validated scientific mechanisms merely because they are present in the repository. Use `docs/EVIDENCE_STATUS.md` for evidence labels and `docs/ethics/ETHICS-policy-to-code-audit-2026-10-19.md` for the bounded policy-to-code findings.
