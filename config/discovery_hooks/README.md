# Discovery Hooks — Configuration Status and Integration Limits

This directory contains five JSON configuration proposals. All five are currently marked `enabled: false` and `implementation_status: proposal_only_not_runtime_verified`. **They are not established as operational modules.** A configuration file is not evidence that its named module exists, is imported, receives configuration, or has passed tests.

## Lifecycle states

- `proposal_only_not_runtime_verified`: disabled; the named implementation is not established as present.
- `implemented_disabled_pending_activation`: the named module and class exist and import, but the hook remains disabled.
- `implemented_enabled_runtime_verified`: the module and class exist, and runtime integration has been verified. Activation still requires separate review of scientific validity, safety, and operational risks.

The configuration tests enforce agreement between each status and its `enabled` flag. The binding test's non-test filename-reference check is only a weak placeholder; it does not prove that a loader instantiates the class or passes configuration into it. Replace it with a test of the real loader/orchestrator entry point when that exists.

## Configurations

- `contamination_scorer_config.json` — proposed background-contamination workflow.
- `host_gravity_emulator_config.json` — proposed host-structure baseline workflow.
- `state_budget_monitor_config.json` — proposed resource-budget heuristic.
- `mundane_mechanism_catalog_config.json` — proposed ordinary-mechanism checks.
- `consciousness_claim_detector_config.json` — proposed handling of AI messages discussing subjective experience or rights.

## Bounded repository trace

A repository-tree inspection and targeted code searches found these configuration files and documentation references, but no matching named hook implementation or runtime call site in the inspected repository. This is a bounded finding, not proof that no external or unindexed implementation exists. The main Flask API inspected exposes data and analysis endpoints and does not wire these hooks.

## Requirements before activation

1. Implement the named module and define its interface.
2. Trace configuration loading from an application/orchestrator entry point.
3. Add unit and integration tests, including failure and disabled-state behavior.
4. Document logs, retention, access control, and tamper evidence; a path ending in `.jsonl` is not an immutable audit log.
5. Only then consider enabling a hook, after review of its scientific validity and operational risks.

## Special rule for consciousness-claim review

The configuration is proposal-only and disabled. A flag is an allegation, not a finding; it must not itself trigger throttling or suppress expression. The config sets `throttle_autonomous_actions_when_flagged` to `false` and does not claim immutable logging. Any narrowly scoped emergency restriction would require a specific credible time-sensitive risk, recorded reasons, an expiry, independent review, notice where feasible, access to the evidence, and an appeal path.

## Evidence and governance

These files are design artifacts until implementation is confirmed. Do not describe them as implemented safeguards or validated scientific mechanisms merely because they are present. Use `docs/EVIDENCE_STATUS.md` for evidence labels and `docs/ethics/ETHICS-policy-to-code-audit-2026-10-19.md` for the bounded policy-to-code findings.
