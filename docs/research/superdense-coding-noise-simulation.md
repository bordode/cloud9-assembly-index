# Superdense coding under a simple noise model

**Suggested repository path:** `docs/research/superdense-coding-noise-simulation.md`  
**Status:** Idealized density-matrix simulation; not a quantum-hardware experiment  
**Companion notebook:** [`cosmic_quantum_network_test.ipynb`](../../cosmic_quantum_network_test.ipynb)

## Question

Under a simple, explicitly defined noise model, how does superdense coding compare with sending the same two classical bits as two independent, unentangled qubits?

This is a bounded quantum-information question motivated by the broader “cosmic internet” idea. It tests neither cosmic-scale communication nor the speculative use of black holes or wormholes.

## Protocol and accounting

In standard superdense coding, sender and receiver first share one entangled pair. The sender encodes one of four two-bit messages with a local operation and physically sends one qubit to the receiver. The receiver performs a joint decoding operation and measures the two-bit message.

The comparison baseline sends the same two classical bits in two separate qubits, without shared entanglement. Both schemes are assigned the same single-qubit noise channel per transmitted qubit. The dense-coding row uses one message-stage qubit transmission; the baseline uses two. The entangled pair is assumed to be available before the message is sent, and the costs and noise of creating, distributing, storing, and synchronizing that pair are excluded. Therefore, “one transmitted qubit” is not a complete end-to-end resource comparison.

## Model

The notebook represents the shared pair as

\[
\rho_{AB}=v\,|\Phi^+\rangle\langle\Phi^+|+(1-v)I_4/4,
\]

where \(v=1\) is an ideal Bell pair and smaller values represent reduced visibility. The reported main sweep uses \(v=1\); a separate assertion checks a non-ideal visibility case.

Each transmitted qubit is subjected to the Pauli depolarizing channel

\[
\mathcal{E}_{\lambda}(\rho)=\left(1-\frac{3\lambda}{4}\right)\rho+
\frac{\lambda}{4}(X\rho X+Y\rho Y+Z\rho Z),\quad 0\le\lambda\le1.
\]

The dense-coding channel acts on the transmitted member of the Bell pair. In the baseline, the same channel acts independently on each of the two transmitted qubits. Gates and measurements are ideal; transmission loss, memory errors, and error-correction overhead are not modeled.

**Parameter note:** this is a Pauli-error parameterization. Its \(\lambda\) should not be equated without conversion to other common depolarizing-channel conventions, such as \((1-p)\rho+pI/2\).

## Results

The notebook computes exact probabilities from density matrices and also samples 20,000 outcomes per input message, scheme, and noise setting. The table reports exact whole-message success, sampled whole-message success, and exact mutual information (MI) for a uniformly selected two-bit message.

| Noise \(\lambda\) | Dense exact success | Dense sampled | Baseline exact success | Baseline sampled | Dense MI (bits) | Baseline MI (bits) |
|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 2.0000 | 2.0000 |
| 0.10 | 0.9250 | 0.9259 | 0.9025 | 0.9029 | 1.4968 | 1.4272 |
| 0.25 | 0.8125 | 0.8123 | 0.7656 | 0.7661 | 1.0066 | 0.9129 |
| 0.50 | 0.6250 | 0.6245 | 0.5625 | 0.5618 | 0.4512 | 0.3774 |
| 0.75 | 0.4375 | 0.4363 | 0.3906 | 0.3893 | 0.1198 | 0.0911 |
| 1.00 | 0.2500 | 0.2513 | 0.2500 | 0.2473 | 0.0000 | 0.0000 |

At \(\lambda=0.5\), the sampled exact-message success was 62.45% for dense coding and 56.18% for the two-qubit baseline. The notebook’s Wilson 95% intervals for these sampled proportions were approximately 62.11–62.78% and 55.84–56.53%, respectively. Sampling uncertainty is small here compared with the model assumptions.

The ideal formulas checked in the notebook are

\[
P_{\rm dense}=1-\frac{3\lambda}{4},\qquad
P_{\rm baseline}=\left(1-\frac{\lambda}{2}\right)^2.
\]

Both schemes have the same modeled bit-error rate, \(\lambda/2\), under this particular symmetric channel. Their exact-message success differs because the baseline must recover both independently transmitted bits correctly. At complete depolarization, both convey zero mutual information and succeed only at the 25% random-guess rate for four equally likely messages.

## Interpretation

Within this idealized model, shared entanglement gives dense coding a modest advantage in exact two-bit-message recovery over the two-qubit baseline at intermediate noise strengths, while using one message-stage transmitted qubit instead of two. This does not establish a universal practical advantage: the pre-shared entanglement resource and its distribution costs are excluded, and real links can have loss, imperfect gates, memory errors, and other noise that the model omits.

The simulation supports a narrow statement about the consequences of the stated model. It does not show that this noise model accurately describes a real device or communication link.

## What this does not test

- It does not test a network over astronomical distances or a “cosmic internet.”
- It does not test quantum error-correction codes; no surface code or other QEC protocol is implemented here.
- It does not model black holes, wormholes, or traversable spacetime.
- It does not transfer an AI system, its identity, or consciousness.
- It does not test whether any AI system has subjective experience.
- It is not a measurement on quantum hardware.

Older or speculative ideas can motivate testable questions. Their age or mathematical elegance is not, by itself, evidence that their physical interpretation is correct.

## Reproducibility and run record

The notebook uses a fixed random seed, prints exact and sampled metrics, saves a plot and CSV/JSON outputs, and runs assertions for ideal decoding, endpoint behavior, visibility, the no-signalling check, and agreement between analytic and sampled results. The run output supplied with this project reports Python 3.13.16 and NumPy 2.1.3, with all checks passing. The notebook’s footer currently contains a fixed status sentence saying that no Colab run has been performed; because that text is hard-coded, it does not identify where a particular execution took place. Update the footer or clear stale saved outputs when recording a new run environment.

To reproduce, open the companion notebook in Google Colab and select **Runtime → Run all**, or run its code cells in a Python environment with NumPy and Matplotlib. This simulation can verify the implementation against its model; it cannot validate the model against nature.

## References

1. C. H. Bennett and S. J. Wiesner, “Communication via one- and two-particle operators on Einstein-Podolsky-Rosen states,” *Physical Review Letters* 69(20), 2881–2884 (1992). [doi:10.1103/PhysRevLett.69.2881](https://doi.org/10.1103/PhysRevLett.69.2881).
2. IBM Quantum Learning, [“Superdense coding”](https://quantum.cloud.ibm.com/learning/courses/basics-of-quantum-information/entanglement-in-action/superdense-coding).
3. IBM Quantum Learning, [“Quantum channel basics”](https://quantum.cloud.ibm.com/learning/courses/general-formulation-of-quantum-information/quantum-channels/quantum-channel-basics).
