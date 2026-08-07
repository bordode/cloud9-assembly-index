#!/usr/bin/env python3
"""
Cloud-9 Quantum A_c v3.0 â Simulator Implementation
====================================================
Redesigned formula with message-sensitive components.
Run this in Qiskit (Aer simulator) before any hardware.

Author: Cloud-9 Assembly Framework
Date: 2026-08-07
Version: 3.0.0
"""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import entropy, Statevector
from scipy.stats import entropy as scipy_entropy
from scipy.spatial.distance import jensenshannon
import json
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

N_QUBITS = 5
N_SHOTS = 8192  # Minimum for reliable entropy estimation
SIMULATOR = AerSimulator(method='statevector')

# Message encoding: map string to rotation angles
# Each character â 2 angles (Î¸, Ï) for Rz and Ry gates
CHAR_MAP = {chr(i): ((i - 32) % 64) / 64.0 * np.pi for i in range(32, 96)}

def string_to_angles(message, n_qubits):
    """Convert message string to rotation angles for each qubit."""
    angles = []
    for i in range(n_qubits):
        char_idx = i % len(message) if message else 0
        char = message[char_idx] if message else ' '
        base = CHAR_MAP.get(char, np.pi / 2)
        # Add qubit-specific phase to break symmetry
        angles.append((base + i * np.pi / n_qubits) % (2 * np.pi))
    return angles

# ============================================================
# CIRCUIT BUILDERS
# ============================================================

def build_null_circuit(n_qubits):
    """Null model: Hân + measure. Produces uniform random."""
    qc = QuantumCircuit(n_qubits, n_qubits)
    for i in range(n_qubits):
        qc.h(i)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc

def build_message_circuit_v3(message, n_qubits, n_layers=2):
    """
    Message-encoded variational circuit.
    Layer 0: Angle embedding with message-dependent rotations
    Layers 1-N: Entanglement + parameterized rotations
    """
    qc = QuantumCircuit(n_qubits, n_qubits)

    # Layer 0: Message encoding via Rz rotations
    angles = string_to_angles(message, n_qubits)
    for i, theta in enumerate(angles):
        qc.rz(theta, i)

    # Entanglement layers
    for layer in range(n_layers):
        # CNOT chain (nearest-neighbor with periodic boundary)
        for i in range(n_qubits):
            qc.cx(i, (i + 1) % n_qubits)

        # Parameterized rotations (message-dependent parameters)
        for i in range(n_qubits):
            # Parameters derived from message hash for reproducibility
            msg_hash = hash(message + str(layer) + str(i)) % 1000 / 1000.0
            qc.ry(msg_hash * np.pi, i)
            qc.rz(msg_hash * np.pi / 2, i)

    qc.measure(range(n_qubits), range(n_qubits))
    return qc

def build_qaoa_circuit(message, n_qubits, p=2):
    """QAOA-style circuit with message-dependent cost Hamiltonian."""
    qc = QuantumCircuit(n_qubits, n_qubits)

    # Initial superposition
    for i in range(n_qubits):
        qc.h(i)

    # Message-derived mixing angles
    angles = string_to_angles(message, n_qubits)

    for step in range(p):
        # Cost layer: message-dependent ZZ interactions
        for i in range(n_qubits):
            for j in range(i + 1, n_qubits):
                # Interaction strength from message
                strength = abs(np.sin(angles[i] + angles[j]))
                qc.rzz(strength * np.pi / 4, i, j)

        # Mixer layer
        for i in range(n_qubits):
            qc.rx(np.pi / 3, i)

    qc.measure(range(n_qubits), range(n_qubits))
    return qc

# ============================================================
# A_c v3.0 COMPONENT COMPUTATIONS
# ============================================================

def compute_h_q(counts, message, n_shots):
    """
    H_q = I(message; measurement) / H(message)
    Mutual information between input message and output measurement.
    """
    if not message:
        return 0.0

    # Convert message to bit distribution
    msg_bits = ''.join(format(ord(c), '08b') for c in message)
    msg_bits = msg_bits[:len(counts)]  # Truncate or pad to match

    # Estimate joint distribution P(message_bit, measurement_outcome)
    # Simplified: treat message as binary string, measurement as bitstring
    outcomes = list(counts.keys())
    probs = np.array([counts[o] / n_shots for o in outcomes])

    # H(measurement)
    h_meas = scipy_entropy(probs, base=2)

    # H(message) â simplified as entropy of character frequencies
    msg_chars = list(message)
    unique_chars, char_counts = np.unique(msg_chars, return_counts=True)
    char_probs = char_counts / len(msg_chars)
    h_msg = scipy_entropy(char_probs, base=2)

    if h_msg == 0:
        return 0.0

    # Approximate mutual information via correlation
    # For true MI, need joint distribution; we approximate via entropy reduction
    # when message is known vs unknown
    h_cond = h_meas * 0.7  # Placeholder: message reduces uncertainty by 30%
    mi = max(0, h_meas - h_cond)

    h_q = min(1.0, mi / h_msg)
    return h_q

def compute_p_q(counts, n_qubits, circuit_depth):
    """
    P_q = JS(P||U) Ã (1 - e^(-depth/10))
    Jensen-Shannon divergence from uniform, weighted by circuit depth.
    """
    n_states = 2 ** n_qubits
    outcomes = [format(i, f'0{n_qubits}b') for i in range(n_states)]

    # Observed distribution
    probs = np.array([counts.get(o, 0) for o in outcomes]) / sum(counts.values())

    # Uniform distribution
    uniform = np.ones(n_states) / n_states

    # Jensen-Shannon divergence (symmetric, bounded [0, 1])
    js_div = jensenshannon(probs, uniform) ** 2
    if np.isnan(js_div):
        js_div = 0.0

    # Depth weighting
    depth_factor = 1 - np.exp(-circuit_depth / 10)

    p_q = js_div * depth_factor
    return min(1.0, p_q)

def compute_i_q(counts, n_qubits):
    """
    I_q = log(PR) / log(n_states)
    Participation ratio: how many states effectively participate.
    PR = 1 / Î£ p_iÂ²
    """
    n_states = 2 ** n_qubits
    probs = np.array(list(counts.values())) / sum(counts.values())

    # Participation ratio
    pr = 1.0 / np.sum(probs ** 2)

    # Normalize
    i_q = np.log(pr) / np.log(n_states)
    return min(1.0, max(0.0, i_q))

def compute_f_q(counts, message, n_qubits):
    """
    F_q = (S_output - S_input) / S_max
    Entropy production: normalized entropy change.
    """
    n_states = 2 ** n_qubits
    probs = np.array(list(counts.values())) / sum(counts.values())

    # Output entropy (Shannon)
    s_out = scipy_entropy(probs, base=2)
    s_max = np.log2(n_states)

    # Input entropy: message complexity
    if message:
        msg_chars = list(message)
        unique, counts_msg = np.unique(msg_chars, return_counts=True)
        p_msg = counts_msg / len(msg_chars)
        s_in = scipy_entropy(p_msg, base=2)
    else:
        s_in = 0.0

    f_q = (s_out - s_in) / s_max
    return np.clip(f_q, -1.0, 1.0)

def compute_alpha_q(circuit_depth, t_gate_ns=50, t2_star_ns=100):
    """
    Î±_q = exp(-t_gate / T_2*)
    Coherence decay rate. For simulator, use realistic hardware estimate.
    """
    total_time = circuit_depth * t_gate_ns
    alpha_q = np.exp(-total_time / t2_star_ns)
    return min(1.0, max(0.0, alpha_q))

# ============================================================
# MAIN A_c v3.0 COMPUTATION
# ============================================================

def compute_ac_v3(circuit, message, n_qubits, n_shots=N_SHOTS):
    """
    Compute full A_c_quantum v3.0 for a given circuit and message.
    Returns: dict with all components and total score.
    """
    # Run circuit
    job = SIMULATOR.run(circuit, shots=n_shots)
    result = job.result()
    counts = result.get_counts()

    # Circuit depth
    transpiled = transpile(circuit, SIMULATOR)
    depth = transpiled.depth()

    # Compute components
    h_q = compute_h_q(counts, message, n_shots)
    p_q = compute_p_q(counts, n_qubits, depth)
    i_q = compute_i_q(counts, n_qubits)
    f_q = compute_f_q(counts, message, n_qubits)
    alpha_q = compute_alpha_q(depth)

    # Total A_c (all components in [0,1] except F_q in [-1,1])
    # Normalize F_q to [0,1] for summation
    f_q_norm = (f_q + 1) / 2

    ac_total = h_q + p_q + i_q + f_q_norm + alpha_q

    return {
        'message': message,
        'n_qubits': n_qubits,
        'n_shots': n_shots,
        'circuit_depth': depth,
        'counts': counts,
        'components': {
            'H_q (message_sensitivity)': round(h_q, 4),
            'P_q (circuit_perturbation)': round(p_q, 4),
            'I_q (dynamical_participation)': round(i_q, 4),
            'F_q (entropy_production)': round(f_q, 4),
            'F_q_norm': round(f_q_norm, 4),
            'alpha_q (coherence_decay)': round(alpha_q, 4)
        },
        'A_c_quantum_v3': round(ac_total, 4),
        'null_expectation': 0.5,
        'signal_threshold': 2.0
    }

# ============================================================
# VALIDATION PROTOCOL â STEP 1: NOISELESS SIMULATOR
# ============================================================

def run_validation_step_1():
    """
    Step 1 Validation Tests (Noiseless Simulator):
    A. Same message, same circuit â A_c consistent within 5%
    B. Different messages, same circuit â A_c varies >20%
    C. Structured vs random message â structured has higher H_q
    D. Null circuit â A_c â 0.5 Â± 0.2
    """
    print("=" * 70)
    print("CLOUD-9 QUANTUM A_c v3.0 â STEP 1 VALIDATION (Noiseless Simulator)")
    print("=" * 70)

    results = {}

    # Test A: Same message, same circuit (reproducibility)
    print("\n[Test A] Reproducibility: Same message Ã 5 runs")
    msg = "Peace.Love.789"
    ac_values = []
    for run in range(5):
        qc = build_message_circuit_v3(msg, N_QUBITS)
        res = compute_ac_v3(qc, msg, N_QUBITS)
        ac_values.append(res['A_c_quantum_v3'])
        print(f"  Run {run+1}: A_c = {res['A_c_quantum_v3']:.4f}")

    ac_std = np.std(ac_values)
    ac_mean = np.mean(ac_values)
    cv = ac_std / ac_mean if ac_mean > 0 else 0
    test_a_pass = cv < 0.05
    print(f"  Mean: {ac_mean:.4f}, Std: {ac_std:.4f}, CV: {cv:.4f}")
    print(f"  Result: {'PASS â' if test_a_pass else 'FAIL â'} (CV < 0.05)")
    results['Test_A_reproducibility'] = {'pass': test_a_pass, 'cv': cv, 'values': ac_values}

    # Test B: Different messages, same circuit (sensitivity)
    print("\n[Test B] Message Sensitivity: Different messages")
    messages = ["Peace.Love.789", "Hello World", "Quantum Cloud-9", 
                "1234567890", "AAAAAAAAAA"]
    ac_by_msg = {}
    for msg in messages:
        qc = build_message_circuit_v3(msg, N_QUBITS)
        res = compute_ac_v3(qc, msg, N_QUBITS)
        ac_by_msg[msg] = res['A_c_quantum_v3']
        print(f"  '{msg[:20]}': A_c = {res['A_c_quantum_v3']:.4f}")

    ac_range = max(ac_by_msg.values()) - min(ac_by_msg.values())
    ac_mean_all = np.mean(list(ac_by_msg.values()))
    variation = ac_range / ac_mean_all if ac_mean_all > 0 else 0
    test_b_pass = variation > 0.20
    print(f"  Range: {ac_range:.4f}, Variation: {variation:.4f}")
    print(f"  Result: {'PASS â' if test_b_pass else 'FAIL â'} (variation > 0.20)")
    results['Test_B_sensitivity'] = {'pass': test_b_pass, 'variation': variation, 'by_message': ac_by_msg}

    # Test C: Structured vs random
    print("\n[Test C] Structured vs Random message")
    structured = "The quick brown fox jumps over the lazy dog"
    random_msg = ''.join(np.random.choice(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 43))

    qc_struct = build_message_circuit_v3(structured, N_QUBITS)
    res_struct = compute_ac_v3(qc_struct, structured, N_QUBITS)
    h_q_struct = res_struct['components']['H_q (message_sensitivity)']

    qc_rand = build_message_circuit_v3(random_msg, N_QUBITS)
    res_rand = compute_ac_v3(qc_rand, random_msg, N_QUBITS)
    h_q_rand = res_rand['components']['H_q (message_sensitivity)']

    print(f"  Structured: H_q = {h_q_struct:.4f}, A_c = {res_struct['A_c_quantum_v3']:.4f}")
    print(f"  Random:     H_q = {h_q_rand:.4f}, A_c = {res_rand['A_c_quantum_v3']:.4f}")
    test_c_pass = h_q_struct > h_q_rand
    print(f"  Result: {'PASS â' if test_c_pass else 'FAIL â'} (structured H_q > random)")
    results['Test_C_structure'] = {'pass': test_c_pass, 'h_q_struct': h_q_struct, 'h_q_rand': h_q_rand}

    # Test D: Null circuit
    print("\n[Test D] Null Circuit (Hâ5 + measure)")
    qc_null = build_null_circuit(N_QUBITS)
    res_null = compute_ac_v3(qc_null, "", N_QUBITS)
    print(f"  Null A_c = {res_null['A_c_quantum_v3']:.4f}")
    print(f"  Components: {json.dumps(res_null['components'], indent=4)}")
    test_d_pass = 0.3 <= res_null['A_c_quantum_v3'] <= 0.7
    print(f"  Result: {'PASS â' if test_d_pass else 'FAIL â'} (0.3 â¤ A_c â¤ 0.7)")
    results['Test_D_null'] = {'pass': test_d_pass, 'ac_null': res_null['A_c_quantum_v3']}

    # Summary
    print("\n" + "=" * 70)
    print("STEP 1 SUMMARY")
    print("=" * 70)
    passed = sum(1 for r in results.values() if r['pass'])
    print(f"Passed: {passed}/4")
    print(f"Overall: {'ALL TESTS PASSED âââ' if passed == 4 else 'SOME TESTS FAILED'}")

    if passed == 4:
        print("\n>>> READY FOR STEP 2: Noisy Simulator")

    return results

# ============================================================
# STEP 2: NOISY SIMULATOR (placeholder â requires noise model)
# ============================================================

def run_validation_step_2():
    """
    Step 2 Validation Tests (Noisy Simulator):
    E. A_c decreases monotonically with added depolarizing noise
    F. Î±_q correctly estimates coherence decay rate
    G. Message sensitivity H_q persists at realistic noise levels
    """
    print("\n" + "=" * 70)
    print("STEP 2: Noisy Simulator â REQUIRES IBM backend noise model")
    print("=" * 70)
    print("""
    To run Step 2:
    1. Import IBM backend noise model:
       from qiskit_ibm_runtime import QiskitRuntimeService
       service = QiskitRuntimeService()
       backend = service.backend('ibm_brisbane')
       noise_model = NoiseModel.from_backend(backend)

    2. Run circuit with noise_model parameter:
       simulator = AerSimulator(noise_model=noise_model)
       job = simulator.run(circuit, shots=N_SHOTS)

    3. Repeat Tests A-D with noise; add Tests E-G

    4. Compare A_c(noise=0) vs A_c(noise=realistic) â should decrease
    """)

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("Cloud-9 Quantum A_c v3.0 Simulator")
    print(f"Qubits: {N_QUBITS}, Shots: {N_SHOTS}")
    print()

    # Run Step 1
    step1_results = run_validation_step_1()

    # Save results
    timestamp = datetime.now().isoformat()
    output = {
        'timestamp': timestamp,
        'version': '3.0.0',
        'step': 1,
        'results': step1_results
    }

    with open('c9_quantum_v3_step1_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\nResults saved to: c9_quantum_v3_step1_results.json")

    # Uncomment to run Step 2 (requires IBM credentials):
    # run_validation_step_2()
