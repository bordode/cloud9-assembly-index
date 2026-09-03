# Cloud-9 Evidence Status and Claim Taxonomy

**Status:** Active research governance document  
**Date:** 2026-09-02

This document defines how Cloud-9 results, hypotheses, software tests, and normative proposals must be described. It is intended to prevent computational success from being mistaken for empirical confirmation or established science.

## Evidence levels

| Level | Label | Meaning | What it does **not** mean |
|---|---|---|---|
| **L0** | Conceptual | Idea, hypothesis, analogy, proposed mechanism, philosophical position, or research question | Not evidence that the claim is true |
| **L1** | Computational / sandbox validated | Code executes, internal tests pass, synthetic calculations reproduce a stated result, or a pipeline behaves as designed | Not validation against the physical universe or independent empirical confirmation |
| **L2** | Empirically constrained | Uses genuine observational or experimental data with documented provenance and methodology, with appropriate statistical controls | Not necessarily independent reproduction or causal explanation |
| **L3** | Independently reproduced | A result has been independently re-analyzed or reproduced using independently controlled data/code/methods | Not automatically established consensus |
| **L4** | Established | Supported by multiple independent lines of evidence and/or strong peer-reviewed consensus | Not a guarantee that every related Cloud-9 interpretation is established |

## Reporting rules

1. **PASS means the stated test passed.** It does not mean the underlying scientific hypothesis was proven.
2. A synthetic null ensemble is evidence about the behavior of the implemented synthetic model. It is not a direct substitute for a matched cosmological simulation or observational dataset.
3. A numerical z-score is meaningful only in the context of its null model, selection procedure, estimator, uncertainty calculation, and provenance.
4. Statistical thresholds must be distinguished from measured results. A configurable software threshold is not an observed sigma value.
5. Historical or imported values remain historical until their code, inputs, assumptions, and output can be traced.
6. Observational relevance is not the same thing as validation of Cloud-9. A real dataset can constrain a hypothesis without independently reproducing the Cloud-9 metric.
7. Terms such as **verified, confirmed, validated, discovered, established, proven,** and **empirical measurement** require claim-specific evidence. They must not be used merely because software ran successfully.
8. Claims about consciousness, intelligence, agency, personhood, or substrate independence are hypotheses or normative positions unless supported by evidence appropriate to those claims. Assembly complexity alone must not be presented as a validated consciousness detector.
9. Ethical and human-rights proposals may be strongly stated as normative commitments, but they must be clearly separated from empirical scientific findings.
10. When evidence is mixed, use the lower defensible level and explain what remains unresolved.

## Current Cloud-9 examples

### Synthetic Null Ensemble v3 — L1

The v3 null ensemble is a reproducible synthetic comparison using N=100 generated halos and a KSG-style temporal mutual-information estimator. Its reported z≈8.62 is a model-dependent synthetic statistic. It is not a direct ΛCDM validation, a discovery claim, or an empirical detection in real simulation/observational data.

### Historical halo result — provisional / below L2

The historical A_c = 87.3 ± 3.2 bits and reported z=2.99σ result remains a reported historical result while its original calculation and provenance are reconstructed. It should not be described as independently verified.

### Exploratory z≈3.04 result — L1 / exploratory

The result recorded in `results/cloud9_analysis.json` is an exploratory calculation using a simulated/refined standard error. It is not independent confirmation of the historical halo result.

### 5.41 threshold — software configuration

The default 5.41 value in the application is a configurable software threshold. It is not a measured 5.41σ cosmological result and must not be described as a validated physical threshold.

## Claim-status vocabulary

Prefer:

- **Computed** — a calculation was performed.
- **Reproduced internally** — the repository reproduces its own stated computational result.
- **Synthetic comparison** — comparison against generated or simulated null data.
- **Reported historical result** — inherited from earlier work whose provenance is not yet fully reconstructed.
- **Exploratory** — useful for hypothesis generation but not confirmatory.
- **Empirically constrained** — grounded in documented real-world data.
- **Independently reproduced** — confirmed by an independent analysis.
- **Hypothesis / proposed mechanism** — explicitly unresolved.
- **Normative proposal** — an ethical, governance, or rights position rather than an empirical finding.

Avoid using **proof**, **discovery**, **confirmed**, or **validated** unless the evidence level and claim-specific methodology justify the term.

## Relationship to provenance

`docs/RESULTS_PROVENANCE.md` remains the canonical numerical-provenance record. This document supplies the broader evidence vocabulary used when reviewing new research collections and documentation.
