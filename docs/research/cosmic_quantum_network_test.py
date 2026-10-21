"""Python script exported from cosmic_quantum_network_test.ipynb.
Run in Colab or locally with NumPy and Matplotlib installed.
"""

# Notebook code cell 2
from pathlib import Path
import csv
import json
import platform
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEED = 20261020
SHOTS_PER_MESSAGE = 20_000
NOISE_VALUES = np.array([0.0, 0.1, 0.25, 0.5, 0.75, 1.0])
# Visibility v: rho_AB = v|Phi+><Phi+| + (1-v)I4/4.
# v=1 is ideal entanglement; v=0 is fully mixed and uncorrelated.
BELL_VISIBILITY = 1.0
assert 0 <= BELL_VISIBILITY <= 1
rng = np.random.default_rng(SEED)
out_dir = Path('quantum_network_results')
out_dir.mkdir(exist_ok=True)
print('Simulation only; Python', platform.python_version(), '| NumPy', np.__version__)
print(f'{SHOTS_PER_MESSAGE:,} samples per input message, per scheme, per noise setting')

# Notebook code cell 4
I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.diag([1, -1]).astype(complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
CNOT = np.array([[1,0,0,0], [0,1,0,0], [0,0,0,1], [0,0,1,0]], dtype=complex)
DECODE = np.kron(H, I) @ CNOT
phi = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
bell = np.outer(phi, phi.conj())

def evolve(rho, U):
    return U @ rho @ U.conj().T

def depolarize(rho, lam, operators):
    assert 0 <= lam <= 1
    return (1 - 3*lam/4)*rho + (lam/4)*sum(evolve(rho, P) for P in operators)

def check_density(rho):
    assert np.allclose(rho, rho.conj().T)
    assert np.isclose(np.trace(rho), 1)
    assert np.linalg.eigvalsh(rho).min() > -1e-10

def measure_probs(rho):
    check_density(rho)
    probs = np.clip(np.diag(rho).real, 0, 1)
    assert np.isclose(probs.sum(), 1)
    return probs / probs.sum()

def dense_confusion(lam, visibility=1.0):
    shared = visibility*bell + (1-visibility)*np.eye(4)/4
    rows = []
    for a in (0, 1):
        for b in (0, 1):
            U = np.kron(np.linalg.matrix_power(Z, a) @ np.linalg.matrix_power(X, b), I)
            encoded = evolve(shared, U)
            transmitted = depolarize(encoded, lam, [np.kron(P, I) for P in (X,Y,Z)])
            rows.append(measure_probs(evolve(transmitted, DECODE)))
    return np.array(rows)

def baseline_confusion(lam):
    rows = []
    for a in (0, 1):
        for b in (0, 1):
            single_probs = []
            for bit in (a,b):
                ket = np.eye(2, dtype=complex)[:, bit]
                rho = np.outer(ket, ket.conj())
                single_probs.append(measure_probs(depolarize(rho, lam, [X,Y,Z])))
            rows.append(np.kron(*single_probs))
    return np.array(rows)

LABELS = ['00', '01', '10', '11']
print('Ideal dense conditional probability matrix (rows sent, columns received):')
print(dense_confusion(0))

# Notebook code cell 6
HAMMING = np.array([[(i ^ j).bit_count() for j in range(4)] for i in range(4)])

def metrics(C):
    assert C.shape == (4, 4) and np.allclose(C.sum(axis=1), 1)
    joint = C / 4
    py = joint.sum(axis=0)
    denom = 0.25 * np.broadcast_to(py, (4, 4))
    mask = joint > 0
    mi = float(np.sum(joint[mask] * np.log2(joint[mask] / denom[mask])))
    return float(np.trace(C)/4), float(np.sum(joint*HAMMING)/2), mi

def wilson(successes, n):
    z = 1.959963984540054
    p = successes / n
    den = 1 + z*z/n
    center = (p + z*z/(2*n)) / den
    half = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return max(0.0, center-half), min(1.0, center+half)

records = []
for lam in NOISE_VALUES:
    for scheme, C, uses in [
        ('Dense', dense_confusion(lam, BELL_VISIBILITY), 1),
        ('Unentangled baseline', baseline_confusion(lam), 2),
    ]:
        success, ber, mi = metrics(C)
        counts = np.array([rng.multinomial(SHOTS_PER_MESSAGE, row) for row in C])
        n = counts.sum()
        successes = np.trace(counts)
        low, high = wilson(successes, n)
        empirical = counts / SHOTS_PER_MESSAGE
        records.append(dict(scheme=scheme, noise=float(lam), success_exact=success,
                            success_sampled=float(successes/n), ci95_low=low, ci95_high=high,
                            ber_exact=ber, ber_sampled=metrics(empirical)[1],
                            mutual_information_bits=mi, message_stage_channel_uses=uses,
                            info_per_message_stage_use=mi/uses))
print(f"{'scheme':23s} {'lambda':>6s} {'P(success)':>11s} {'sampled':>9s} {'BER':>7s} {'MI bits':>8s}")
for r in records:
    print(f"{r['scheme']:23s} {r['noise']:6.2f} {r['success_exact']:11.4f} "
          f"{r['success_sampled']:9.4f} {r['ber_exact']:7.4f} {r['mutual_information_bits']:8.4f}")

# Notebook code cell 8
assert np.allclose(dense_confusion(0), np.eye(4))
assert np.allclose(baseline_confusion(0), np.eye(4))
for lam in np.linspace(0, 1, 21):
    d_success, d_ber, _ = metrics(dense_confusion(lam))
    b_success, b_ber, _ = metrics(baseline_confusion(lam))
    assert np.isclose(d_success, 1 - 3*lam/4)
    assert np.isclose(b_success, (1-lam/2)**2)
    assert np.isclose(d_ber, lam/2) and np.isclose(b_ber, lam/2)
    # Visibility control has its own independently predicted success curve.
    assert np.isclose(metrics(dense_confusion(lam, 0.6))[0], (1+3*0.6*(1-lam))/4)
assert np.allclose(dense_confusion(1), np.ones((4,4))/4)
assert np.allclose(baseline_confusion(1), np.ones((4,4))/4)
assert np.allclose(dense_confusion(0, visibility=0), np.ones((4,4))/4)
# rho[A,B,A',B']; tracing A and A' leaves Bob's reduced density matrix.
for a in (0,1):
    for b in (0,1):
        U = np.kron(np.linalg.matrix_power(Z,a) @ np.linalg.matrix_power(X,b), I)
        encoded = evolve(bell, U)
        bob_marginal = np.trace(encoded.reshape(2,2,2,2), axis1=0, axis2=2)
        assert np.allclose(bob_marginal, I/2)
# Broad reproducible sanity bound, not a requirement that every 95% CI cover truth.
for r in records:
    n = 4*SHOTS_PER_MESSAGE
    se = np.sqrt(r['success_exact']*(1-r['success_exact'])/n)
    assert abs(r['success_sampled']-r['success_exact']) <= 6*se + 1/n
print('PASS: ideal decoding, noise formulas, bit errors, visibility, endpoints, no signalling, sampling.')

# Notebook code cell 9
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
for scheme, color in [('Dense', '#1864ab'), ('Unentangled baseline', '#d9480f')]:
    subset = [r for r in records if r['scheme'] == scheme]
    xs = np.array([r['noise'] for r in subset])
    exact = np.array([r['success_exact'] for r in subset])
    sampled = np.array([r['success_sampled'] for r in subset])
    lower = sampled - np.array([r['ci95_low'] for r in subset])
    upper = np.array([r['ci95_high'] for r in subset]) - sampled
    axes[0].plot(xs, exact, '-', color=color, label=scheme)
    axes[0].errorbar(xs, sampled, yerr=[lower,upper], fmt='o', capsize=4, color=color)
    axes[1].plot(xs, [r['ber_exact'] for r in subset], 'o-' if scheme == 'Dense' else 'x--',
                 color=color, label=scheme)
    axes[2].plot(xs, [r['info_per_message_stage_use'] for r in subset], 'o-', color=color, label=scheme)
axes[0].axhline(0.25, color='gray', linestyle=':', label='Random message guess')
for ax, title, ylabel in zip(axes,
    ['Whole-message success', 'Bit errors (curves coincide)', 'Entanglement-assisted accounting'],
    ['Probability (dots: sampled, 95% CI)', 'Exact bit error rate', 'Exact MI / message-stage qubit use']):
    ax.set(title=title, xlabel='Depolarizing strength lambda', ylabel=ylabel)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
fig.suptitle(f'Simulation only | Bell visibility v={BELL_VISIBILITY} | entanglement setup costs excluded')
fig.tight_layout()
fig.savefig(out_dir / 'simulation_metrics.png', dpi=160, bbox_inches='tight')
plt.close(fig)

# Notebook code cell 11
with (out_dir / 'metrics.csv').open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(records[0]))
    writer.writeheader()
    writer.writerows(records)
summary = dict(execution='Local sandbox Python kernel; not actual Colab or quantum hardware',
               seed=SEED, shots_per_message=SHOTS_PER_MESSAGE,
               bell_visibility=BELL_VISIBILITY, noise_values=NOISE_VALUES.tolist(),
               python=sys.version, numpy=np.__version__, matplotlib=matplotlib.__version__,
               checks='all automated assertions passed',
               assumptions=['independent depolarizing message channels', 'ideal gates and readout',
                            'no loss', 'entanglement distribution and memory costs excluded'])
(out_dir / 'validation_summary.json').write_text(json.dumps(summary, indent=2)+'\n')
print('Saved:', ', '.join(str(p) for p in sorted(out_dir.iterdir())))
print('Local validation complete. A Colab run has not been performed.')
