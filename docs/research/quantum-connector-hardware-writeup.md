# Quantum connector: entanglement on real IBM hardware

The quantum connector ran a two-qubit entanglement test on a real IBM quantum computer (an IBM Quantum Heron-class device) and scored S = 2.717 on the CHSH test, well above the classical limit of 2. That shows the two qubits on the chip were genuinely entangled. It is a demonstration of entanglement on the device, not a loophole-free Bell test.

## The plain-language version 

**What we built.** A small program that lets ordinary code talk to a quantum computer. You send it a request, it checks the request, turns it into a quantum circuit, runs it, and sends back the results. First we ran it on a simulator on a regular computer. Then it was run on a real IBM quantum machine over the internet.

**What entanglement is.** Two particles get linked so that measuring one tells you something about the other, in a way that normal objects can't copy. Einstein called it "spooky action at a distance" and suspected there had to be a simpler explanation.

**The simple explanation people suspected.** Imagine two sealed envelopes, each with a card inside. Open one and it says red, open the other and it also says red. Nothing spooky: someone put matching cards in before they were sealed. The question is whether entangled particles are just like that, with their answers decided in advance.

**How the test settles it.** Instead of asking the two particles the same question every time, you ask them questions from different angles and add up how often they agree. There is a hard ceiling on the score you can get with answers decided in advance: 2. Quantum physics predicts you can go higher, up to about 2.83.

**What happened.** The real IBM machine scored 2.717. Pre-set answers can't get there. On about 98 out of every 100 runs, the two qubits matched exactly when they were supposed to. The other 2 or so were noise, because real hardware is never perfect.

**The honest caveat.** The two qubits sit right next to each other on the same chip, so in principle they could influence each other. The famous experiments that rule out every alternative explanation put the particles far apart, so no signal could pass between them in time. So the fair way to say it: we showed real entanglement on a real quantum computer, and our code worked on actual hardware, not just in a simulation.

## Results

| Measure | Real hardware | Simulator |
| --- | --- | --- |
| Device | IBM an IBM Quantum Heron-class device | Local simulator |
| CHSH score (S) | 2.717 | 2.811 |
| Classical limit | 2.000 | 2.000 |
| Quantum maximum | 2.828 | 2.828 |
| Matched outcomes (00 or 11) | 98.12% | 100% |
| Mismatched outcomes | 1.88% | 0% |

- **Bell pair counts:** 2,022 shots gave 00 and 1,997 gave 11, out of 4,096. The remaining 77 shots were mismatched.
- **Share of the quantum maximum:** 2.717 is about 96% of 2.828.
- **Non-entangled control (simulator):** S = 1.452, under the classical limit, as expected.
- **Software tests:** all 62 tests passed (43 for the connector, 19 for the entanglement test).
- **IBM job ID:** [retained in the private archive]

## What the result shows

- **Entanglement on the device.** A CHSH score of 2.717 cannot come from qubits whose outcomes were fixed in advance, given the usual assumptions of the test.
- **Statistical strength.** Assuming each of the four measurement settings used around 4,096 shots, the uncertainty on S is roughly plus or minus 0.02. That puts the result about 30 standard errors above 2, far stronger than a 3-sigma threshold. Confirm the shot count per setting before quoting this figure.
- **Working hardware path.** The connector, which had only a placeholder hardware adapter before, ran end to end on real IBM hardware.

## What the result does not show

- **Not a loophole-free Bell test.** Both qubits are on one chip, close together, with measurement settings chosen by the program rather than independent random choices made far apart. The locality loophole is open, so this does not by itself rule out local hidden variables.
- **Not beyond classical computers.** A two-qubit experiment is easy to simulate classically. The simulator here scored 2.811 on an ordinary computer.
- **Not unusually low noise.** An error of under 2% on a Bell pair is good for current IBM hardware, but it is in the normal range for modern devices rather than exceptional.
- **Not a phase transition.** S = 2 is a threshold set by the test, not a physical phase transition.

## Notes for publishing

- **API token.** Check that no IBM API key appears anywhere in the code, the JSON, or the commit history before pushing to a public repository.
- **Deprecation warning.** The run showed a warning that SamplerV2 is deprecated in qiskit-ibm-runtime 0.50.0. The code still ran. Use the replacement the warning message itself names, rather than guessing at a new import.
- **Suggested one-line summary:** Demonstrated two-qubit entanglement on IBM's an IBM Quantum Heron-class device, violating the CHSH inequality with S = 2.717 (classical bound 2, quantum maximum 2.828), using a classical-to-quantum connector that also passed 62 software tests in simulation.
