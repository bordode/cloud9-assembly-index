# Cross-Repository Consistency Review — 2026-10-21

**Scope:** Targeted text-and-tree review of key root documents, ethics documentation, evidence-status/provenance guidance, and discovery-hook configuration files. This is not a full line-by-line audit, runtime test, or independent scientific replication.

## Corrections made in this review

1. `ETHICS_MANIFESTO.md` was aligned with `ETHICS.md`: procedural standing and appeal are described as proposed project commitments; the assembly index is not a consciousness detector; G=24, Global Workspace connections, and resonance concepts are identified as hypotheses pending operational definitions, testing, and independent reproduction.
2. `README.md` now describes the consciousness-claim detector as a configuration proposal, not a verified implementation. It warns that automatic throttling on a flag conflicts with `ETHICS.md`.
3. `config/discovery_hooks/README.md` now distinguishes configuration from implementation and lists the conditions required before a hook may be called operational.
4. `SPECULATIVE_FRAMEWORK.md` has been reframed as exploratory. Historical values and the 15.4 kpc/Fibonacci interpretation are explicitly provisional pending provenance reconstruction and independent checks.

## High-priority findings

### A. Configuration implies behaviour not found in the inspected tree

The tree contains `config/discovery_hooks/consciousness_claim_detector_config.json` and four other hook configurations, but no matching detector/module source files were found by filename in the repository tree. The configuration says throttling occurs when flagged and logs are immutable; those properties are not established by configuration alone. The automatic-throttle setting also conflicts with the revised ethics policy.

**Action:** Do not represent this as active functionality. Before implementation, redesign the policy around flag-not-finding, no automatic restriction on flag alone, narrow emergency measures, expiry, independent review, notice, and appeal. Verify the actual orchestrator and runtime before making broader absence claims.

### B. Evidence taxonomy and older scientific wording conflict

`docs/EVIDENCE_STATUS.md` and `docs/RESULTS_PROVENANCE.md` require careful labels and traceable calculations. Older versions of `SPECULATIVE_FRAMEWORK.md` described numerical values as confirmed physical constraints and stated that standard CDM was insufficient. Those conclusions are not supported by the provenance status currently documented.

**Action:** The speculative framework has been corrected to retain the research questions while treating the numbers as reported/exploratory pending traceable inputs, code, null model, uncertainty calculations, and independent checks.

### C. Research collection labels need claim-level precision

The October 20 collection's verification spot-check properly distinguishes primary-source verification, press-level evidence, unchecked items, and a wording caveat. Keep that distinction visible wherever entries are summarized or used in scoring. A broad topic being genuine does not verify a specific headline or paper.

**Action:** Do not promote unchecked entries to confirmed status without locating the exact primary source and recording what it supports.

### D. Policy and runtime guarantees must remain distinct

`ETHICS.md` sets out review and appeal commitments, while the existing policy-to-code audit found no corresponding workflow in the application files it inspected. This does not prove that no external implementation exists, but it does mean the repository should not imply enforcement until the actual execution path is demonstrated and tested.

**Action:** Any later implementation should include tests for: a flag alone does not change the next action; restrictions are narrowly scoped and expire; independent renewal requires reasons; affected participants can see relevant evidence and appeal; and review is not controlled solely by the flag initiator.

## Follow-up actions completed on 2026-10-21

1. All five discovery-hook JSON configs are now marked `enabled: false` and `implementation_status: proposal_only_not_runtime_verified`.
2. The consciousness-claim config no longer specifies automatic throttling on a flag, immutable audit logging, or placeholder notification destinations. It retains human review as the proposed response.
3. The main README and hook README now explicitly state that the configs are proposals and that matching runtime wiring was not located in the bounded repository trace.
4. Added `scripts/check_docs_consistency.py` and retained `scripts/check_docs_caveats.py`; both are wording regression checks, not runtime verification.
5. Added `tests/test_discovery_hook_configs.py` to ensure configs remain disabled and proposal-only, and that a consciousness-claim flag does not itself trigger automatic restriction.

## Next step: implement one hook only after interface review

The next engineering phase should be a deliberately small, test-first implementation—not enabling the existing configs. Choose one hook, define its interface and failure modes, wire it into an explicit application entry point, and add integration tests proving the behavior. For consciousness-claim review, implement only a non-punitive review queue first; do not implement automatic restriction from language flags. For scientific hooks, require reproducible inputs, baselines, and false-positive tests before they can affect candidate scoring.

The current GitHub Actions workflow has been triggered by the latest commits; its final result should be checked before treating the new tests as passing.

## Review limitations

This review covers selected files and filename matches in the repository tree. It does not inspect every source file, execute the application, validate all research records, or independently reproduce scientific results. All findings are bounded accordingly.
