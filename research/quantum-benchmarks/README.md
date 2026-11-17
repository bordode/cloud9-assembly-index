Cloud-9 Assembly Index: Quantum State-Distribution Complexity & Stability Benchmarks
Date: 2026-11-16
Status: Sanitized & Ready for subhalo.AI GitHub Ingestion
Files:


* quantum_state_complexity_benchmark.py (Standalone Qiskit / Qiskit Aer benchmark script)
* cloud9_quantum_benchmarks_v1.1.json (Empirical QPU hardware metrics & pipeline schema)


________________


Overview
This package provides both the empirical hardware telemetry from the 156-qubit device and a reproducible Qiskit/Python benchmark script (quantum_state_complexity_benchmark.py) for the Cloud-9 Assembly Index repository. All non-scientific narratives, symbolic overlays, and personal identifiers have been removed.


In the Cloud-9 framework, these benchmarks quantify state-distribution complexity and stability—measuring how structured multi-qubit probability distributions maintain low Shannon entropy ($H$) and low Jensen-Shannon Divergence ($\text{JSD}$) against thermal relaxation ($T_1/T_2$) and depolarizing gate noise.


________________


Benchmark Script Usage (quantum_state_complexity_benchmark.py)
1. Install Dependencies
pip install qiskit qiskit-aer numpy scipy
2. Run Benchmark Suite
python quantum_state_complexity_benchmark.py
3. What It Evaluates
* Deterministic State Initialization: Converts a SHA-256 digest into repeatable $R_y(\theta)$ rotation angles across $N$ qubits.
* Ring + Cross-Bridge Entanglement: Builds a 6-qubit closed ring (0-1-2-3-4-5-0) with cross-diameter CNOT bridges (0-3, 1-4, 2-5).
* Dynamical Decoupling Sweep (NONE, XY4, XY8, XY16, XY32): Inserts alternating $X$ and $Y$ $\pi$-pulses inside a $480\text{ ns}$ idle window under a device-calibrated noise model ($T_1 = 210\ \mu\text{s}$, $T_2 = 220.34\ \mu\text{s}$).
* Complexity & Stability Metrics: Outputs JSON containing Shannon entropy ($H$), normalized distribution concentration $\left(1 - \frac{H}{N}\right) \times 100%$, transpiled circuit depth, and Jensen-Shannon Divergence ($\text{JSD}$) relative to the noiseless baseline.


________________


Empirical QPU Reference Findings (the 156-qubit device)
* Dynamical Decoupling Trade-Off: XY16 achieved the peak distribution concentration ($50.30%$–$50.35%$, $H = 1.4541\text{ bits}$, $\text{JSD} = 0.1546$), outperforming XY8 ($50.05%$) and XY32 ($49.01%$, where cumulative single-qubit microwave gate errors exceed idle dephasing suppression).
* Tripartite Non-Locality (Mermin-Svetlichny): Physical qubits [three-qubit set, low-error cluster] yielded $M_{\text{raw}} = 3.6738 \pm 0.0120$ and $M_{\text{mitigated}} = 3.7795 \pm 0.0138$ ($94.5%$ of the Tsirelson bound), exceeding both classical LHV ($2.0$) and Svetlichny hybrid ($2.8284$) thresholds.
* Topology & LNN Routing: Mapping to high-$T_2$ clusters ([adjacent high-T2 pair], $T_2 = 220.34\ \mu\text{s}$) and Linear Nearest-Neighbor (LNN) routing reduced circuit depth from $64$ to $18$ ($3.40\times$ stability gain).


________________


Integration Notes for subhalo.AI
* Target Repository: cloud9-assembly-index
* Recommended Placement:
   * research/quantum-benchmarks/quantum_state_complexity_benchmark.py
   * research/quantum-benchmarks/cloud9_quantum_benchmarks_v1.1.json
   * Link or merge this README section into the main README.md.

________________

Provenance and limits
* The hardware numbers in the JSON were recorded from device runs in November 2026 and are reproduced as recorded. The script reproduces the simulated path (state preparation, decoupling sweep, noise model), not the original hardware runs; re-running it will not regenerate the recorded device values.
* Figures referenced in earlier drafts are not included, because the plotting step was not preserved. Treat the JSON as the record.
* Device identity is deliberately omitted. Physical qubit indices are generalised in this public copy.
