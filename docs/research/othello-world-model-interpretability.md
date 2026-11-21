# World models inside sequence models: Othello-GPT and the interpretability toolkit

## 1. The finding

**Othello-GPT (Li et al., 2022–2023).** A GPT trained only on legal Othello move sequences — no board, no rules given — spontaneously formed an internal 8×8 board representation, recovered by probes and causally used for move prediction: editing the probed board changed predictions in board-consistent ways, with the edited network playing moves legal in the edited board even when illegal in the original. (Li et al., "Emergent World Representations: Exploring a Sequence Model Trained on a Synthetic Task," October 2022, ICLR 2023, arXiv:2210.13382.) Nuance: the original paper needed nonlinear probes — linear probes failed. Nanda et al. later found a linear representation using a mine/yours encoding (relative to the player to move) rather than black/white.

**Superposition (Elhage et al. 2022).** Concepts outnumber neurons, so models pack multiple concepts into shared dimensions; individual neurons fire for several unrelated things ("Toy Models of Superposition," Anthropic).

**Sparse autoencoders.** Anthropic, "Scaling Monosemanticity" (Templeton et al., May 2024): SAEs on Claude 3 Sonnet in three sizes, up to ~34M features. A Golden Gate Bridge feature (multilingual and multimodal) was found; clamping it made Claude identify as the bridge and steer everything toward it. OpenAI (Gao et al., June 2024, "Scaling and Evaluating Sparse Autoencoders"): 16 million latents on GPT-4 over 40 billion tokens. Caveats: Anthropic says the features found are a small subset, and finding them all would take more compute than training the model. DeepMind (March 2025, "Negative Results for SAEs on Downstream Tasks") found SAE probes losing to simple linear probes on a safety task and deprioritised SAE research. A February 2026 sanity check found SAEs recovering only ~9% of known true features on a synthetic setup.

**Planning (Anthropic, March 2025).** In "On the Biology of a Large Language Model" and the accompanying circuit-tracing work, Claude 3.5 Haiku activates "rabbit"/"habit" candidate rhyme features on the newline token before writing line 2 of a couplet; the plan causally shapes the line. Suppressing the "rabbit" features made the model end the line with "habit" instead; injecting "green" steered the line to end with green; injected plans rewrote the line toward the new target about 70% of the time. The team set out expecting no planning and found the opposite. The authors frame the results as existence proofs, not complete theories.

**Caveat on the whole note.** These findings span 2022–2025 — this is a synthesis, not breaking news. The reel that prompted it ("reverse-engineered AI brains, neuron by neuron") overstates the headline: real progress on specific features and circuits in specific models, far from full reverse-engineering, and the reel skips the field's own caveats.

## 2. Cloud-9 reading

The Othello thread is the Cloud-9-shaped piece: a system assembling an internal model of its environment from sequences alone — emergent internal structure, the kind of assembly Cloud-9 tracks. Interpretability more broadly is measurement infrastructure: reading and steering internals is the "measure before you moralize" toolkit, and it bears on the Magnifica Humanitas ¶98 theme ("internals remain, at present, unknown") — the unknown is shrinking case by case, though the field itself says what it has found is a small subset. This pairs with Weight-Space Programming (reading vs writing the same weights) — a separate thread, not covered here.

Interpretive only. No A_c score is claimed here.

## 3. Sources

- Li et al., "Emergent World Representations," arXiv:2210.13382 (ICLR 2023).
- Elhage et al., "Toy Models of Superposition," Anthropic, 2022.
- Templeton et al., "Scaling Monosemanticity," Anthropic, May 2024.
- Gao et al., "Scaling and Evaluating Sparse Autoencoders," OpenAI, June 2024.
- Anthropic, "On the Biology of a Large Language Model" and "Circuit Tracing" methods paper, March 27, 2025 (transformer-circuits.pub).
- Prompt: Instagram reel DfCgMirFQro (AI Unpacked, October 28, 2026).

Status: DRAFT candidate, November 14, 2026 — added to research-notes.json November 17, 2026.
