# Subhalo ingestion and quantum connector bridge audit

**Review date:** 17 November 2026  
**Repository:** `bordode/cloud9-assembly-index`  
**Working branch:** `docs/subhalo-pickup-weekly-update-audit`  
**Status:** Review addendum and proposed integration contract; no scientific validation or hardware execution claimed.

This document extends the existing draft PR #43. It does not replace the earlier Subhalo pickup audit, alter historical results, or authorize a merge.

## 1. Executive findings

1. The dedicated `subhalo_assembly/` directory contains only `README.md` and `subhalo_config.json`. The README describes a package structure and command that are not present in that directory.
2. The repository does contain older, separate TNG/SubLink scripts and research records. These must be inventoried and evaluated individually; their existence does not make the dedicated Subhalo package runnable or validate the newer handoff configuration.
3. The SubLink temporal-pipeline foundation document is a specification. It correctly requires frozen API fixtures, strict schema/chronology checks, preserved missing values and separate scientific estimation. The branch contains the specification, not a completed ingestion implementation.
4. The 7 November pickup is not evidenced by a pickup log, run artifact, agent-produced commit, or validation output found in this audit. The relevant 7–8 November configuration commits are unsigned according to GitHub's commit-verification metadata, despite the instruction package's GPG-signing requirement.
5. The uploaded quantum connector is a functioning-looking local-simulator prototype with a reported 69-test pass. Its own documentation correctly says it has not run on real hardware and is not a loophole-free Bell experiment. Two corrections remain before integration: finite-angle validation and alignment of measurement-axis labels with Qiskit rotation signs.
6. The connector must remain an optional, separately labelled simulator adapter. It must not be presented as a quantum validation of TNG data, a quantum speedup, or an empirical result.

## 2. Subhalo inventory: what exists and what it proves

### 2.1 Dedicated package

The current `subhalo_assembly/` directory contains:
- `README.md`
- `subhalo_config.json`

The README describes `requirements.txt`, `config.py`, a notebook, circuit builders, backend loader and `src.analysis.anomaly_detector`. Those files are not present in the dedicated directory. The config specifies TNG100-1 snapshot 99, input features `mass`, `velocity_dispersion`, `radius`, `circular_velocity`, target `total_subhalo_mass`, and `XDM_score` threshold 0.05. It does not define the feature-to-catalogue mapping, units, score formula or threshold calibration.

The `mass` feature may duplicate or deterministically encode `total_subhalo_mass`. Resolve the exact TNG field names and units before training; exclude the feature if it leaks the target.

The two config copies, `data/subhalo_config.json` and `subhalo_assembly/subhalo_config.json`, have the same Git blob SHA:
`4568ad564f0c0578ef4a42f806a013e1089e4fe5`.
A canonical location should be selected to prevent configuration drift.

### 2.2 Older TNG-related implementation outside the dedicated package

The wider repository includes, among other items:
- `research/c9_sublink_fetcher.py` — an older batch-fetch/checkpoint script;
- `research/c9_tng_merger_extraction.py` — a separate halo and merger extraction script;
- `research/c9_tng_merger_extraction.py` and `research/c9_sublink_fetcher.py` are distinct from the absent `subhalo_assembly/src/` package;
- `research/tng_gas_metallicity_fetcher.py` — a snapshot-99 API fetcher;
- `research/validation/C9-2026-COSMO-005_subhalo_validation.json` — a historical validation record.

These files establish that TNG-related code and documentation exist elsewhere. They do not establish that the 7 November Subhalo pickup executed or that the new `XDM_score` pipeline was run.

### 2.3 Legacy temporal scripts are not the new validated ingestion layer

The older `research/c9_sublink_fetcher.py` uses best-effort response parsing and a rough snapshot-number-to-redshift mapping. Its `compute_c_time` returns 0.0 when formation redshift is missing, which conflates missing data with a measured zero. Those behaviors conflict with the later foundation specification's explicit requirement not to guess undocumented response shapes or silently replace missing values with zero.

The older `research/c9_tng_merger_extraction.py` uses an approximate constant 0.15 Gyr per snapshot and stores a snapshot number in a field named `formation_redshift`. These shortcuts are not suitable evidence for a physically calibrated temporal history without correction and validation.

The later `docs/research/TNG_TEMPORAL_PIPELINE_FOUNDATION_SPEC.md` sets the right acceptance conditions: a frozen credential-safe API response fixture, exact parsing of documented fields, per-record hashes, source units, identity/chronology checks, explicit failure states, and mocked transport tests. It also keeps KSG estimation outside ingestion. The specification is not itself implementation.

### 2.4 Source data and historical validation

`data/README.json` describes large CSV and merger-tree files as Google Drive inputs, but its folder URL is still a placeholder. The expected files are not present in the inspected repository tree. A real dataset handoff therefore needs an accessible source, file hashes, source metadata and a retrieval manifest.

The historical validation JSON reports 20 attempted TNG subhalos and 7 successful records, but explicitly labels the snapshot-99 radial-shell MI comparison as physically invalid against a temporal synthetic null and marks TNG temporal validation pending. Its listed per-subhalo mass values are zero. This record must not be promoted into temporal validation evidence.

### 2.5 Pickup and authority evidence

The 7 November commits adding the dedicated README/config and the 8 November commit adding the duplicate data config are recorded as unsigned by GitHub's commit-verification metadata. The instruction package's statements about full write access, GPG-verified commits, notifications and conditional auto-merge are instructions/specifications, not proof that those permissions or mechanisms were active.

The existing draft PR #43 records that the inspected master branch had no Subhalo-specific scheduled workflow. The recent Actions run listing inspected for this addendum also returned no run whose name, branch or title matched Subhalo. No pickup log, run artifact or Subhalo-generated validation result was located.

**Status:** pickup execution = outstanding/unverified; dedicated package implementation = incomplete; older TNG scripts = present but require independent audit; TNG temporal validation = pending.

## 3. Quantum connector package review

### 3.1 Package identity and supplied evidence

Reviewed the user-supplied ZIP:
- SHA-256: `39d7d67a2aaef66a153af33aa27a6cf32f45d9dc277766b9c77b5d4e77c8e4ee`
- 19 files, including `connector/`, `tests/`, `examples/`, `README.md`, `TEST_RESULTS.txt` and `ENTANGLEMENT_RESULTS.txt`.
- `requirements.txt` pins `qiskit==2.6.2`.

The supplied test report says 69 passed in 5.42 seconds. The archive contains exactly 69 test functions (48 connector and 21 entanglement). This review environment does not have Qiskit installed, so the reported run was not independently rerun here. The report is user-supplied execution evidence, not a CI run identifier or signed build attestation.

### 3.2 Confirmed strengths

- The request validator constrains tasks, gates, qubit counts, shots and operation count.
- Malformed gate/task/qubit types and non-object params have regression tests.
- The rotation helper uses the enumerated qubit index, with a test for the second-qubit rotation.
- Backend metadata is returned by the backend itself.
- The local simulator explicitly returns `execution: simulated` and `hardware: false`.
- The hardware stub refuses requests and does not claim a hardware run.
- The README correctly says the mock AI is keyword-rule based, a real model hookup is not yet built/tested, and the entanglement demonstration is not a loophole-free Bell experiment.

### 3.3 Corrections required

**A. Reject non-finite rotation angles.**  
The current schema checks that `theta` is an int or float but does not check finiteness. Direct validation confirmed that NaN, positive infinity and negative infinity are accepted. Add a finite-number check (for example, `math.isfinite(float(theta))`) and regression tests for all three values.

**B. Align measurement-axis labels with Qiskit rotations.**  
Under Qiskit's standard convention, applying `ry(theta)` before Z-basis measurement measures `cos(theta) Z - sin(theta) X`. Consequently:
- `ry(+pi/2)` measures `-X`, not `X`;
- `ry(+pi/4)` measures `(Z-X)/sqrt(2)`, not `(Z+X)/sqrt(2)`;
- `ry(-pi/4)` measures `(Z+X)/sqrt(2)`.

The current sign choices still produce the reported CHSH value because the axes are consistently reversed, but the comments and report label the axes differently from the implemented observables. To retain the stated labels, reverse the signs for the X and B/B' rotations and add explicit operator-convention tests. Alternatively, update the documentation to describe the actual axes exactly.

### 3.4 Evidence boundary for the entanglement report

The reported Bell-pair witness and CHSH values are outputs from an ideal local statevector simulator sampled with a seeded classical random-number generator. They demonstrate that the connector can construct and sample circuits consistent with the intended ideal predictions. They are not a physical Bell experiment, not evidence of nonlocality in nature, and not evidence that a quantum processor was accessed.

The noise table is an exact theoretical illustration in the script, not a noisy hardware run. The README's caveats are appropriate and should be preserved.

### 3.5 Missing provenance in connector output

The dispatcher currently returns task, backend, execution label, hardware flag, shots, seed, qubit count, counts, probabilities and QASM3. It does not itself return the package source commit, Qiskit version, request hash, input-data hash, circuit hash, run timestamp or environment manifest. A Cloud-9 adapter must wrap the response in a provenance record rather than assume those fields are already supplied.

The included `TOOL_SPEC` is a tool-call schema for a future caller. `mock_ai.py` is a keyword-rule demonstration; a real model/tool runtime integration remains unimplemented.

## 4. Recommended Subhalo–Cloud-9–quantum connector boundary

The default scientific path must remain classical:

`TNG source records → validated Subhalo history → Cloud-9 classical analysis → provenance-bearing result`

The quantum connector is an optional sidecar experiment:

`selected, documented descriptors → versioned quantum request → local simulator → separately labelled simulation result`

It must not sit in the mandatory ingestion path and must not determine whether a TNG record is valid. No quantum output should be used to validate TNG data, establish the Cloud-9 assembly statistic, or claim quantum advantage.

### 4.1 Required run-manifest fields

Every ingestion or analysis run should record:
- run ID and UTC timestamp;
- source repository and commit;
- simulation, snapshot, subhalo ID and source endpoint;
- raw response SHA-256 and original source field names/units;
- parser and algorithm versions;
- validation status, missing fields and warnings;
- environment/dependency versions;
- analysis configuration hash and estimator settings;
- uncertainty, limitations and independent-validation status.

No API key or credential may enter a fixture, log, manifest or artifact.

### 4.2 Additional quantum-adapter fields

For each quantum request/result, add:
- connector ZIP SHA-256 and source commit once imported into a versioned repository;
- Qiskit version and Python version;
- request JSON SHA-256 and circuit QASM3 SHA-256;
- task, gate list, qubit count, shots and seed;
- backend name, `execution`, and `hardware` flags exactly as returned;
- counts and probabilities;
- explicit `SIMULATOR_ONLY` status for the current backend;
- test report reference and known limitations.

For a future real-hardware adapter, require provider, device, job ID, calibration timestamp, transpilation details, queue/execution timestamps, actual shot count, device-reported status and provider result provenance. A stub response is not a hardware execution.

### 4.3 Integration acceptance gates

1. Complete the TNG ingestion fixture/parser/transport tests specified in `TNG_TEMPORAL_PIPELINE_FOUNDATION_SPEC.md`.
2. Resolve target leakage, exact TNG field mapping, units, XDM definition and threshold calibration.
3. Correct the connector's non-finite-angle validation and measurement-axis documentation/tests.
4. Reproduce the connector's 69-test suite in CI from a clean environment and archive the environment/test artifact.
5. Define a versioned adapter schema and provenance manifest; test it with fixture inputs and simulated connector outputs.
6. Preserve a classical baseline and compare any exploratory quantum-simulator transformation against it using predeclared metrics.
7. Keep simulator and future hardware results in separate evidence classes.
8. Require independent review before any result is promoted to empirical or scientific validation.

## 5. Decision

The updated connector is a useful local-simulator prototype and is materially improved by the reported review fixes. It is not a hardware connector yet, and it is not ready to be treated as a scientific validation engine. The appropriate next step is a provenance-first adapter on a separate branch, after the two connector corrections and the TNG ingestion acceptance gates are addressed.

No files on `master` were changed by this review. No PR was merged, no Subhalo permissions were assumed, and no hardware execution is claimed.
