# Subhalo quantum connector package review — 19 November 2026

**Repository:** `bordode/cloud9-assembly-index`  
**Pull request:** #43 — `docs/subhalo-pickup-weekly-update-audit`  
**Review scope:** the two separately supplied archives `quantum-connector-ai-adapter-prototype.zip` and `quantum-connector-ai-tool-review.zip`, plus the technical review subsequently supplied by Gemini.  
**Status:** source-package inspection and evidence-boundary addendum; no physical QPU run, live model integration, independent test reproduction, or scientific validation is claimed.

This addendum supplements `SUBHALO_QUANTUM_CONNECTOR_BRIDGE_AUDIT_2026-11-17.md`. It does not silently replace the earlier package review: the two November 19 archives are treated as the specific artifacts reviewed here.

## 1. Evidence classification

### Directly inspected in the supplied archives

The adapter prototype archive contains, among other files:

- `src/connector/ai_adapter.py`
- `src/connector/backends.py`
- `src/connector/circuits.py`
- `src/connector/dispatcher.py`
- `src/connector/schema.py`
- `src/connector/entanglement.py`
- `src/connector/mock_ai.py`
- `src/requirements.txt`
- `README.md`, `TEST_RESULTS.txt`, and `ENTANGLEMENT_RESULTS.txt`
- examples and tests for the connector and entanglement routines.

The package pins `qiskit==2.6.2`. The local simulator uses Qiskit statevector probabilities and NumPy sampling. Its result metadata identifies execution as simulated and hardware as false. The hardware backend stub deliberately raises a backend-unavailable error; it does not submit a physical quantum job.

The dispatcher builds circuits from validated requests and returns simulation results, metadata and QASM3 output. The adapter exposes `tool_definition()` and `execute_tool_call(name, arguments)`. The mock caller uses fixed keyword matching; no live OpenAI, Gemini, Anthropic or other model-provider SDK/transport is wired into the archive.

The entanglement module constructs Bell/GHZ-style circuits and compares a simulated Bell pair with a classically correlated control. The supplied report describes seeded local-simulator sampling, witness calculations, CHSH estimates and idealized white-noise calculations.

### Source-reported, not independently reproduced

`TEST_RESULTS.txt` reports **69 passed in 5.42 seconds**. This is a static package-supplied test record. The complete suite has not yet been independently rerun in a clean Cloud-9 environment pinned to the supplied Qiskit version. Do not describe the 69 tests as independently reproduced.

`ENTANGLEMENT_RESULTS.txt` reports the numerical Bell/control correlations, witness values, CHSH values and noise sweep. These are results reported by the package's own local simulator run, not physical quantum-device measurements.

## 2. Confirmed documentation/interface defect

The implementation in `src/connector/ai_adapter.py` defines:

- `tool_definition()`
- `execute_tool_call(name, arguments)`

The README and the separate integration guide in the review archive instead document an import path and callable named:

- `connector.ai_tool`
- `handle_tool_call()`

The documented import/call contract therefore does not match the adapter module and callable shipped in the prototype archive. A host application following the documented example may fail at import or invocation.

**Required correction:** choose one public interface and make the implementation, README, integration guide, examples and tests agree. If compatibility is required, ship and test an explicit compatibility module/re-export. Add a runnable host-loop example that exercises the documented path. Do not claim live LLM integration merely because a JSON tool schema can be generated and a local payload dispatched.

The previous Gemini review also refers to `connector/circuit.py`, `connector/validator.py` and `connector/simulator.py`. Those are not the corresponding filenames in the adapter archive inspected for this addendum; the archive uses plural `circuits.py` and includes `backends.py`, `dispatcher.py` and `schema.py`. Future reviews must use the actual archive inventory rather than carry forward filenames from another revision.

## 3. Mathematical interpretation and limits

The following theoretical checks are appropriate for the stated two-qubit Bell-state convention:

- `H(q0)` followed by `CX(q0,q1)` prepares `|Phi+>` in the ideal circuit model.
- The fidelity expression `F = (1 + <XX> - <YY> + <ZZ>)/4` gives 1 for the ideal `|Phi+>` state and has a 1/2 separable-state ceiling for this Bell-fidelity witness.
- The CHSH local-hidden-variable bound is 2 and the Tsirelson bound is `2*sqrt(2)`.
- For the isotropic two-qubit white-noise mixture `rho = (1-p)|Phi+><Phi+| + p I/4`, the Bell fidelity is `1 - 3p/4`; the witness entanglement threshold is `p < 2/3`. The ideal CHSH value scales as `2*sqrt(2)*(1-p)`, giving a CHSH-violation threshold `p < 1 - 1/sqrt(2)`.

These are analytic criteria, not proof that every implementation detail in the archive has been independently verified. In particular, a finite-shot CHSH uncertainty must be computed from the actual four measured correlators and shot counts; the idealized `sqrt(2/N)` expression applies only under its stated ideal equal-shot assumptions.

The archive's reported values are generated using an ideal local simulator and seeded classical sampling. They demonstrate consistency with the simulated circuit model. They are not a loophole-free Bell test, evidence of physical nonlocality, a QPU run, quantum advantage, or a validated scientific instrument.

The white-noise table is an idealized theoretical model. It must not be described as a measured hardware-noise characterization unless an actual calibrated device-noise experiment is supplied.

## 4. Correct capability classification

| Category | Current status |
|---|---|
| Directly inspected | Qiskit local-simulator implementation; structured request/dispatch path; QASM3 export path; explicit simulated/hardware metadata; hardware stub refuses execution; adapter function names and documentation mismatch. |
| Source-reported | 69 passing tests; Bell/control correlation results; witness and CHSH numerical results; idealized noise sweep. |
| Analytically checkable | Bell-state, witness, CHSH and Werner-state threshold formulae described above. Analytic correctness does not certify the corresponding source implementation. |
| Proposed / incomplete | Provider-neutral schema intended for future model tool calling; host integration described in documentation but not coherently packaged; live LLM integration. |
| Explicitly absent in this archive | Physical QPU execution; provider SDK/runtime connection; demonstrated quantum advantage; realistic calibrated hardware noise characterization. |

## 5. Prioritized acceptance actions

### P0 — public API consistency
1. Standardize the module and function names.
2. Update every README, integration guide and example to the selected interface.
3. Add an executable host-tool-loop example.
4. Add tests that import and call exactly the documented public interface.

### P1 — input and execution safeguards
1. Confirm custom-gate names are allowlisted; do not use unrestricted dynamic attribute lookup on raw JSON gate names.
2. Reject NaN and positive/negative infinity for all numeric gate parameters.
3. Bound qubit count, operation count and shot count to safe documented limits for local statevector execution.
4. Return structured errors for malformed requests rather than exposing raw tracebacks.
5. Test multi-qubit measurement ordering and QASM3 round-trip behavior against explicit expected mappings.

### P1 — mathematical implementation checks
1. Test measurement-axis labels against the actual Qiskit rotation signs.
2. Test the witness sign convention and the separable-state boundary.
3. Test CHSH correlator construction, local and Tsirelson bounds, and finite-shot uncertainty propagation.
4. Test the two distinct white-noise thresholds and explicitly name the noise parameterization.
5. Keep the classical control a genuine 50/50 `|00>`/`|11>` mixture or a clearly defined local-hidden-variable control, not a deliberately weak single product-state strawman.

### P2 — independent reproducibility and provenance
1. Re-run the complete suite in a clean environment pinned to Qiskit 2.6.2 and archive machine-readable test output.
2. Record Python/Qiskit versions, source commit, request hash, circuit/QASM hash, seed, shots and backend metadata for each run.
3. Add tests for adapter schema generation and malformed tool-call arguments.
4. Keep simulator results and any future hardware results in separate evidence classes.

## 6. Cloud-9 integration decision

**Recommendation: retain as an isolated experimental software prototype only.**

The connector may be preserved in a dedicated experimental tooling area after the interface defect is corrected. It must not be inserted into the mandatory TNG ingestion or Cloud-9 scientific-analysis path. It must not validate TNG data, establish the Assembly Index, or be described as a physical quantum instrument.

The Subhalo–Cloud-9 research path remains classical and provenance-first:

`TNG source records -> validated Subhalo history -> classical Cloud-9 analysis -> provenance-bearing result`

The simulator may be an optional side experiment:

`documented descriptors -> versioned quantum request -> local simulator -> separately labelled simulation result`

No simulator output should determine data validity or scientific acceptance.

## 7. Relationship to the 15-repository manifest

The 15 names in the Gemini digest are an **unverified project manifest**, not a verified list of 15 operational repositories. Each entry requires a separate check of repository existence, current tree, implemented source, tests, external-service/hardware connections and reproducible evidence. A name, README, configuration or architecture description is not proof of an operational capability.

## Decision record

This addendum records a package-level review and acceptance conditions. It does not assert that Subhalo has completed the corrections, that the test suite has been independently reproduced, or that any physical quantum hardware was used. The PR remains draft and unmerged pending review.
