# Wormhole-inspired teleportation: magic is necessary but not sufficient

*Research note — 2026-10-13. Intended for `docs/` in cloud9-assembly-index. Established findings summarized from the preprint abstract (read directly) and the ScienceAlert summary (Michelle Starr, Oct 13, 2026) — the full preprint must be checked before citing, and it is not yet peer-reviewed. Note an honest tension below between the press headline and the preprint's own framing. The Cloud-9 reading is interpretive and marked as such.*

## The finding (established)

Sudhanva Joshi and Sunil Kumar Mishra (Department of Physics, IIT Banaras Hindu University) investigated the wormhole-inspired teleportation protocol (WITP) in the Sachdev-Ye-Kitaev (SYK) model — a theoretical framework in which information swallowed by one black hole can, under the right coupling, be recovered from a connected partner. They tracked quantum magic (non-stabilizerness, quantified by stabilizer Rényi entropy) across the protocol's stages: scrambling, message insertion, left-right coupling, and extraction.

Their result is more careful than the press headline. Comparing models, they found that a chaotic random two-local model generating near-maximal magic *fails* to teleport, and a magic-free Clifford scrambler *fails equally* despite mixing operators efficiently. What underlies successful wormhole traversal, they argue, is not the *amount* of non-stabilizerness but its *structured redistribution* — the double-trace coupling first suppresses and then channels non-stabilizer resources toward the teleportation signal. Magic even dips transiently at the fidelity peak, marking the teleportation event in time. Results held across the three system sizes studied (N = 8, 10, 12 Majorana fermions).

The ScienceAlert reporting (Oct 13, 2026) emphasizes the headline surprise: in a black-hole-inspired teleportation model, a magic-free Clifford approach achieved the same *average* teleportation fidelity as magic-heavy Haar-random scrambling — but with roughly 40,000× larger variance in fidelity for 8 qubits, and with fidelity improving as the system grows. The preprint's own title, "Quantum magic is necessary but not sufficient for wormhole-inspired teleportation," is the more precise statement: magic alone doesn't do it, and its absence alone doesn't prevent high average fidelity — the decoding must be matched to the scrambling.

The work is theoretical, on arXiv as a preprint, and not yet peer-reviewed.

## The Cloud-9 reading (interpretive)

The resource that matters is not the resource count but its choreography. "Necessary but not sufficient" is an information-structural claim: teleportation through a scrambled channel depends on how non-classicality is *redistributed*, not how much of it exists. This rhymes with the quantum-birthmarks note — systems that cannot forget their origins — from the other direction: here, a system scrambles information maximally (black holes are the fastest scramblers in nature) and yet the message survives, recoverable by a matched decoding. Scrambling is not erasure. The channel that looks maximally noisy is, with the right key, perfectly legible.

The 40,000× variance finding is its own note: identical averages, wildly different consistencies. Two protocols can agree on the mean and disagree on everything else — a reminder that summary statistics are lossy compressions of the phenomenon.

## Sources

- Joshi & Mishra, "Quantum magic is necessary but not sufficient for wormhole-inspired teleportation," arXiv preprint (IIT BHU). Abstract read directly — full preprint must be verified before citing; not peer-reviewed.
- Michelle Starr, "Quantum Teleportation Inspired by Black Holes Produces a Surprise," ScienceAlert, Oct 13, 2026 (fact-checked by Fiona MacDonald) — press framing; the headline is less careful than the preprint's own title, as noted above.
