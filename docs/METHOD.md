# Method and guardrails for Cloud-9 analysis

*Adopted from the guardrails drawn up for the subHalo agent (science-context pack, November 2026). These are the rules the work is held to, including where they make the flagship claim weaker.*

## Separation of evidence classes

Every entry is labelled as one of:

1. **Established** — replicated, in the peer-reviewed literature, not disputed at its core.
2. **Emerging** — a small number of results, plausible but not yet independently replicated.
3. **Exploratory** — our own computation on public or simulated data, reproducible but not externally validated.
4. **Speculative or cultural** — resonance, Tesla, pyramids, ancient technology, singularity forecasts. Explicitly separated from testable science and never counted as support.

## Analysis rules

1. Never infer consciousness, agency, rights, or new physics from a complexity, assembly, or information score.
2. Require matched nulls, uncertainty estimates, robustness checks, and negative results before any separation is called a signal.
3. Do not force analogies between DNA, AI, quantum systems, and cosmology. An analogy is a hypothesis-generation tool, not evidence.
4. Treat CHIME, TDA, quantum materials, and CP-Assembly ideas as promising but domain-specific research directions, not as automatic support for Cloud-9.
5. State the convention for every p-value and every tail probability, and state the resolution limit of the ensemble that produced it.

## On the null comparisons for A_c = 87.3 bits

Two comparisons exist and they point in opposite directions. Both must travel together:

| comparison | null | result | status |
|---|---|---|---|
| vs synthetic semi-analytic ensemble (N=100) | μ = 58.06, σ = 3.39 bits | z = +8.62 (0/100 halos ≥ 87.3) | experimental, non-Gaussian null, not a discovery claim |
| vs simulated CDM halos (reported in the subHalo pack) | μ = 95.97 bits | z = −1.25, i.e. **below** the null mean | reported, not yet reproduced in this repository |

The second row is the uncomfortable one and it is not an error to report it: against simulated CDM halos, the reported 87.3 bits is *less* spatially complex than the average halo, not more. Any public statement of the 87.3-bit result that omits this comparison is incomplete. Reproducing it from a checked-in ensemble is the outstanding task.

The z = 1011σ real-TNG100-1 radial comparison already in `research/validation/README.md` remains flagged invalid: different estimator, different geometry.
