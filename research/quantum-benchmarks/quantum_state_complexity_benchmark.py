"""
Cloud-9 Assembly Index: Quantum State-Distribution Complexity & Stability Benchmark
----------------------------------------------------------------------------------
Hardware-agnostic Qiskit / Python benchmark script to measure:
  1. Shannon Entropy (H)
  2. Normalized Distribution Concentration (%)
  3. Jensen-Shannon Divergence (JSD) against ideal noiseless baseline
  4. Dynamical Decoupling (XY4, XY8, XY16, XY32) noise-suppression trade-offs

Dependencies:
  pip install qiskit qiskit-aer numpy scipy
"""

import hashlib
import json
from typing import Dict, List, Tuple
import numpy as np
from scipy.spatial.distance import jensenshannon
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, thermal_relaxation_error


def deterministic_seed_angles(seed_string: str, num_qubits: int) -> List[float]:
    """Derives reproducible Ry rotation angles in [0, pi] from a SHA-256 digest."""
    digest = hashlib.sha256(seed_string.encode("utf-8")).hexdigest()
    hash_int = int(digest, 16)
    angles = []
    for i in range(num_qubits):
        byte_val = (hash_int >> (8 * i)) & 0xFF
        angles.append((byte_val / 256.0) * np.pi)
    return angles


def build_ring_entangled_circuit(
    num_qubits: int = 6,
    seed_string: str = "cloud9_baseline_v1",
    dd_sequence: str = "XY16",
    idle_delay_ns: int = 480,
) -> QuantumCircuit:
    """
    Constructs a closed-ring, cross-bridged entangled register with an active
    XY-series dynamical decoupling window to benchmark coherence stability.
    """
    qc = QuantumCircuit(num_qubits, num_qubits)
    angles = deterministic_seed_angles(seed_string, num_qubits)

    # 1. State initialization
    for q in range(num_qubits):
        qc.ry(angles[q], q)
    qc.barrier()

    # 2. Closed-ring entanglement + cross-diameter CNOT bridges
    for q in range(num_qubits):
        qc.cx(q, (q + 1) % num_qubits)
    half = num_qubits // 2
    for q in range(half):
        qc.cx(q, q + half)
    qc.barrier()

    # 3. Active Dynamical Decoupling (XY4 / XY8 / XY16 / XY32)
    pulse_patterns = {
        "NONE": [],
        "XY4": ["X", "Y", "X", "Y"],
        "XY8": ["X", "Y", "X", "Y", "Y", "X", "Y", "X"],
        "XY16": [
            "X", "Y", "X", "Y", "Y", "X", "Y", "X",
            "X", "Y", "X", "Y", "Y", "X", "Y", "X",
        ],
        "XY32": [
            "X", "Y", "X", "Y", "Y", "X", "Y", "X",
            "X", "Y", "X", "Y", "Y", "X", "Y", "X",
            "Y", "X", "Y", "X", "X", "Y", "X", "Y",
            "Y", "X", "Y", "X", "X", "Y", "X", "Y",
        ],
    }

    pulses = pulse_patterns.get(dd_sequence.upper(), [])
    if pulses:
        dt = max(1, idle_delay_ns // len(pulses))
        for q in range(num_qubits):
            qc.delay(dt // 2, q, unit="ns")
        for idx, axis in enumerate(pulses):
            for q in range(num_qubits):
                if axis == "X":
                    qc.x(q)
                else:
                    qc.y(q)
            gap = dt // 2 if idx == len(pulses) - 1 else dt
            for q in range(num_qubits):
                qc.delay(gap, q, unit="ns")
        qc.barrier()

    qc.measure(range(num_qubits), range(num_qubits))
    return qc


def build_realistic_noise_model(
    t1_us: float = 210.0,
    t2_us: float = 220.34,
    single_qubit_err: float = 0.0003,
    two_qubit_err: float = 0.0035,
) -> NoiseModel:
    """Builds a transmon superconducting noise model for local validation."""
    noise_model = NoiseModel()
    t1_ns = t1_us * 1e3
    t2_ns = t2_us * 1e3

    err_1q = depolarizing_error(single_qubit_err, 1)
    err_2q = depolarizing_error(two_qubit_err, 2)
    err_delay = thermal_relaxation_error(t1_ns, t2_ns, 30.0)

    noise_model.add_all_qubit_quantum_error(err_1q, ["ry", "x", "y"])
    noise_model.add_all_qubit_quantum_error(err_2q, ["cx"])
    noise_model.add_all_qubit_quantum_error(err_delay, ["delay"])
    return noise_model


def counts_to_prob_vector(counts: Dict[str, int], num_qubits: int) -> np.ndarray:
    """Converts Qiskit bitstring counts into a full 2^N probability vector."""
    total_shots = sum(counts.values())
    dim = 2 ** num_qubits
    probs = np.zeros(dim, dtype=np.float64)
    for bitstring, count in counts.items():
        idx = int(bitstring, 2)
        probs[idx] = count / total_shots
    return probs


def compute_complexity_metrics(
    counts: Dict[str, int],
    ideal_probs: np.ndarray,
    num_qubits: int,
) -> Dict[str, float]:
    """Computes Shannon entropy, distribution concentration, and JSD."""
    probs = counts_to_prob_vector(counts, num_qubits)
    nonzero = probs[probs > 0]
    shannon_h = float(-np.sum(nonzero * np.log2(nonzero)))
    concentration_pct = float((1.0 - (shannon_h / float(num_qubits))) * 100.0)
    jsd = float(jensenshannon(probs, ideal_probs, base=2) ** 2)
    dominant_state = max(counts, key=counts.get)

    return {
        "shannon_entropy_bits": round(shannon_h, 4),
        "distribution_concentration_pct": round(concentration_pct, 4),
        "jensen_shannon_divergence": round(jsd, 4),
        "dominant_state": dominant_state,
        "dominant_probability_pct": round((counts[dominant_state] / sum(counts.values())) * 100.0, 2),
    }


def run_benchmark_suite(num_qubits: int = 6, shots: int = 8192) -> Dict:
    """Executes ideal baseline and noisy decoupling benchmarks."""
    ideal_sim = AerSimulator()
    noisy_sim = AerSimulator(noise_model=build_realistic_noise_model())

    # Ideal baseline (no noise, no decoupling)
    qc_ideal = build_ring_entangled_circuit(num_qubits=num_qubits, dd_sequence="NONE")
    ideal_counts = ideal_sim.run(transpile(qc_ideal, ideal_sim), shots=shots).result().get_counts()
    ideal_probs = counts_to_prob_vector(ideal_counts, num_qubits)
    ideal_metrics = compute_complexity_metrics(ideal_counts, ideal_probs, num_qubits)

    sequences = ["NONE", "XY4", "XY8", "XY16", "XY32"]
    noisy_results = {}

    for seq in sequences:
        qc = build_ring_entangled_circuit(num_qubits=num_qubits, dd_sequence=seq)
        t_qc = transpile(qc, noisy_sim, optimization_level=3)
        counts = noisy_sim.run(t_qc, shots=shots).result().get_counts()
        metrics = compute_complexity_metrics(counts, ideal_probs, num_qubits)
        metrics["transpiled_depth"] = t_qc.depth()
        noisy_results[seq] = metrics

    return {
        "benchmark": "cloud9_state_distribution_complexity",
        "num_qubits": num_qubits,
        "shots": shots,
        "ideal_baseline": ideal_metrics,
        "noisy_decoupling_runs": noisy_results,
    }


if __name__ == "__main__":
    report = run_benchmark_suite(num_qubits=6, shots=8192)
    print(json.dumps(report, indent=2))
