# Subhalo pickup and 8 November repository update audit

**Review date:** 9 November 2026 UTC / 8 November 2026 Vancouver  
**Repository:** https://github.com/bordode/cloud9-assembly-index  
**Scope:** review of recent master-branch Subhalo configuration, weekly feeds, and related research records. This is a repository-content audit, not confirmation that Subhalo executed a pickup.

## 1. Subhalo pickup configuration

The repository contains data/subhalo_config.json with:
- target agent: subhalo.AI;
- scheduled pickup: 2026-11-07;
- TNG100-1, snapshot 99;
- input features: mass, velocity dispersion, radius and circular velocity;
- target: total_subhalo_mass;
- anomaly metric: XDM_score, threshold 0.05;
- default execution mode: local_simulator;
- remote mode: managed_cloud_backend;
- fallback enabled.

The configuration is sanitized and public-ready. It is configuration metadata only. It does not prove that the pickup ran, that a remote backend was reached, that TNG data were retrieved, or that an anomaly score was computed. The scheduled date has passed, and no pickup result, run log, artifact, or validation report was found alongside this new configuration in the inspected repository tree.

## 2. Pipeline implementation status

The new subhalo_assembly/README.md describes a hardware-agnostic pipeline with a requirements file, config module, notebook, circuits, backend and analysis packages. The actual subhalo_assembly directory currently contains only:
- README.md
- subhalo_config.json

The described requirements file, config module, notebook, source packages and anomaly_detector entry point are not present in that directory. The pickup configuration is therefore not yet a runnable implementation in this repository.

An older data/subhalo_instruction_package.json describes broad Subhalo repository authority, including read/write access and conditional auto-merge. That JSON is an instruction document, not proof of active GitHub permissions, agent execution, GPG verification, or a currently enabled auto-merge mechanism. No permission escalation or auto-merge is inferred from it.

## 3. Connection to the TNG temporal-validation blocker

The existing research/validation/C9-2026-COSMO-005_subhalo_validation.json explicitly states that the earlier TNG comparison used radial-shell mutual information from snapshot 99, not temporal evolution mutual information. It calls direct comparison with the synthetic temporal null physically invalid and marks TNG temporal validation as pending.

The branch research/tng-temporal-pipeline-foundation contains a specification, not a completed ingestion pipeline. Its first milestone is source retrieval and validation only; it deliberately does not calculate A_c or significance. It requires a frozen real API response fixture, mocked transport tests, chronology and identity checks, provenance hashes, and a separate later specification for temporal KSG estimation.

This is the correct next scientific path. A snapshot-99 pickup config alone cannot satisfy the multi-snapshot temporal validation requirement.

## 4. Weekly briefing and discoveries feed

The 8 November commits added:
- data/weekly/cloud9_assembly_weekly_briefing_2026-11-06.json
- data/weekly/cloud9_assembly_weekly_discoveries_2026-11-06.json
- accompanying README summaries.

The records report CDG-2 at 7.15 Hz with coherence index 1.0000, continuous Perseus gravitational strain, assembly depth 42.8, and cross-cloud timing claims. The briefing also maps astronomical signals to biblical passages.

The commit messages explicitly label this content as a speculative/metaphysical layer, separate from the empirical collection and not empirical measurement. It must remain segregated from the validated science dataset. No telescope, observatory, detector, gravitational-wave catalogue, raw data, calibration, uncertainty model, or reproducible analysis is linked in these weekly records. The numeric telemetry should not be presented as measured astrophysical facts.

## 5. Other 8 November research additions

- COSMO-018, dark-energy-deficient voids: the repository note identifies the source as a 8 November preprint and labels the dark-energy deficit as a free parameter/hypothesis. The note reports arithmetic reproduction and a Pantheon+ shape test that disfavors compact regions while leaving large regions unresolved. The note refers to a sandbox script and full result artifact, but those files were not included in the commit that added the note. Treat the numerical sandbox results as reported in the note until code, data provenance and output are committed and independently checked.
- PHOTON-002, room-temperature exciton-polariton supersolid: described as a peer-reviewed Science Advances paper, but not yet independently replicated. The device result is photonics/condensed matter, not evidence of a biological supersolid or a Cloud-9 cosmological mechanism.
- BIO-006, mitochondrial 71 THz signal: the record correctly labels the source as an unreviewed, unreplicated bioRxiv preprint and explicitly disclaims health claims. It also notes the earlier sandbox PNG still reflects v1 inputs and that v2 has not been rerun. It must not be presented as demonstrated quantum coherence, consciousness evidence, or a treatment basis.
- Hardware telemetry report: the document labels the quantum setup as hardware emulation, with five-qubit simulation parameters and a separate phone telemetry baseline. It is not evidence that a physical five-qubit quantum processor was operated or that the emulation is a validated quantum-hardware result.

## 6. Recommended status labels

Keep separate labels for:
1. verified empirical measurement with reproducible provenance;
2. peer-reviewed external research, not independently replicated;
3. preprint / reported external research;
4. synthetic or hardware-emulation result;
5. hypothesis / analogy / speculative or metaphysical interpretation;
6. implementation proposal or pickup configuration;
7. pending execution / pending validation.

## Decision

The Subhalo pickup configuration is useful as a sanitized handoff specification, but execution and scientific validation remain unverified. The TNG temporal pipeline specification remains the appropriate path to turn the pickup into a defensible scientific ingestion and validation workflow. Keep the weekly metaphysical/speculative feed separate from empirical records. Do not enable agent auto-merge or treat the configuration as granting active repository authority.
