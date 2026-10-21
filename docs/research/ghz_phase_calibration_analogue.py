"""Toy phase-calibration analogue based on Dean's three-qubit GHZ circuit.

This is a local ideal-statevector-style simulation with an explicitly injected
unitary phase error. It is NOT a silicon-spin-qubit experiment, a hardware
calibration, or randomized benchmarking. The compensation scan is a didactic
analogue of pairwise phase calibration.

Install in Colab or a Python environment with:
    pip install qiskit qiskit-aer
"""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def phase_probe(delta: float = 0.0, compensation: float = 0.0) -> QuantumCircuit:
    """Build a GHZ-style phase probe; delta is toy crosstalk phase in radians."""
    qc = QuantumCircuit(3, 3)

    # Prepare a GHZ state using the structure of Dean's original circuit.
    qc.h(1)
    qc.cx(1, 0)
    qc.cx(1, 2)

    # Set a pi/2 relative phase so X-basis parity is sensitive to small phase shifts.
    theta = np.pi / 8
    qc.p(theta, 0)
    qc.p(2 * theta, 1)
    qc.p(theta, 2)

    # Toy model: a neighboring active drive induces a phase on q0;
    # the calibration scan applies the opposite phase as compensation.
    qc.rz(delta, 0)
    qc.rz(-compensation, 0)

    # Rotate X-basis parity into ordinary Z-basis measurement.
    qc.h(range(3))
    qc.measure(range(3), range(3))
    return qc


def odd_parity_fraction(counts: dict[str, int]) -> float:
    shots = sum(counts.values())
    odd = sum(
        count
        for bitstring, count in counts.items()
        if bitstring.replace(" ", "").count("1") % 2 == 1
    )
    return odd / shots


def measure_parity(simulator, delta, compensation, shots, seed):
    circuit = phase_probe(delta=delta, compensation=compensation)
    compiled = transpile(circuit, simulator)
    counts = simulator.run(
        compiled, shots=shots, seed_simulator=seed
    ).result().get_counts()
    return odd_parity_fraction(counts), counts


def main():
    simulator = AerSimulator()
    shots = 4096
    injected_phase = 0.20

    # Reference behavior with no injected phase.
    baseline, _ = measure_parity(
        simulator, delta=0.0, compensation=0.0, shots=shots, seed=100
    )

    # Deliberately uncorrected parallel-drive phase error.
    uncorrected, _ = measure_parity(
        simulator, delta=injected_phase, compensation=0.0,
        shots=shots, seed=101
    )

    # Estimate compensation by scanning phases and matching the isolated baseline.
    candidates = np.linspace(-0.40, 0.40, 41)
    scan_results = []
    for index, candidate in enumerate(candidates):
        fraction, _ = measure_parity(
            simulator, delta=injected_phase, compensation=float(candidate),
            shots=shots, seed=200 + index
        )
        scan_results.append((abs(fraction - baseline), float(candidate), fraction))

    _, estimated_compensation, scan_fraction = min(scan_results)

    # Validate the chosen setting on a fresh shot seed.
    corrected, _ = measure_parity(
        simulator, delta=injected_phase,
        compensation=estimated_compensation, shots=shots, seed=999
    )

    print("Toy GHZ phase-calibration analogue (local Aer simulation)")
    print(f"Shots per setting: {shots}")
    print(f"Injected toy phase: {injected_phase:.3f} rad")
    print(f"Isolated baseline odd-parity fraction: {baseline:.4f}")
    print(f"Uncorrected odd-parity fraction:       {uncorrected:.4f}")
    print(f"Scan-selected compensation:            {estimated_compensation:.3f} rad")
    print(f"Parity at selected scan setting:       {scan_fraction:.4f}")
    print(f"Fresh-shot corrected fraction:         {corrected:.4f}")
    print("\nInterpretation: this only demonstrates sensitivity to an injected phase")
    print("and a toy compensation scan. It does not measure real device crosstalk,")
    print("gate fidelity, coherence, or the paper's randomized-benchmarking result.")


if __name__ == "__main__":
    main()
