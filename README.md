# Cloud-9 Assembly Index

**Research status:** Exploratory computational research; key historical measurements remain under provenance review.  
**Author:** Dean Bordode  
**License:** MIT  
**Project DOI:** [10.5281/zenodo.18335567](https://doi.org/10.5281/zenodo.18335567)

Cloud-9 investigates whether information-theoretic measures of temporal structure can help characterize assembly in simulated physical systems, initially focusing on dark-matter halo density fields. Its central research quantity is an Assembly Index, denoted A_c, constructed from mutual-information estimates across successive states.

**The repository does not currently establish that the Assembly Index detects non-stochastic assembly, consciousness, intelligence, agency, or moral status.** Those are distinct propositions requiring different evidence and, where appropriate, separate normative arguments.

This README is the current scientific landing page. Older project overviews are retained as historical records and are not authoritative descriptions of current evidence.

---

## Current evidence status

| Work item | Current status | What can responsibly be said |
|---|---|---|
| Synthetic Null Ensemble v3 | **L1 — computational / synthetic** | A reported standardized separation of approximately 8.62 within one N=100 synthetic ensemble. It is model-dependent, not a discovery significance or direct ΛCDM validation. |
| Historical halo result | **Reported historical; provenance unresolved** | Older materials report A_c = 87.3 ± 3.2 bits and z ≈ 2.99. The original calculation and null provenance have not been reconstructed. |
| Exploratory z ≈ 3.04 calculation | **L1 — exploratory** | Uses a simulated/refined standard error; it is not independent confirmation. |
| Historical 10,000-halo ensemble | **Execution/output unverified** | Described in older methodology text, but the inspected repository does not establish the run manifest, seeds and output artifact. |
| TNG temporal validation | **Pending** | A like-for-like, multi-snapshot analysis with documented provenance and controls is still required. |
| Dither / reconstruction experiments | **Separate computational methods research** | Synthetic reconstruction benchmarks; conclusions are limited to their stated scenes, noise models, operators and checkpoints. |

See:
- [Evidence status and claim taxonomy](docs/EVIDENCE_STATUS.md)
- [Results provenance](docs/RESULTS_PROVENANCE.md)
- [Statistical claims audit](docs/audits/CLOUD9_STATISTICAL_CLAIMS_AUDIT_2026-11-09.md)
- [Legacy significance withdrawal rationale](docs/audits/LEGACY_SIGNIFICANCE_WITHDRAWAL_METHODOLOGY_NOTE_2026-11-09.md)
- [v3 estimator and synthetic null-model source audit](docs/audits/V3_MI_ESTIMATOR_AND_NULL_MODEL_SOURCE_AUDIT_2026-11-09.md)

### Important interpretation limits

Mutual information measures statistical dependence. Temporal dependence or persistence can arise from ordinary gravitational evolution, conservation laws, common causes, correlated initial conditions, smoothing and numerical effects. A large mutual-information value alone does not distinguish these explanations.

The current N=100 synthetic comparison has limited empirical tail resolution. Its reported z ≈ 8.62 is a descriptive standardization relative to that particular generated ensemble. It must not be interpreted as an 8.62σ detection or as proof of non-stochastic assembly.

The historical values **1,137.753σ** and **1,011.53σ** are withdrawn from scientific interpretation: the former lacks a located statistical derivation and appears as a fixed value in legacy/demo material; the latter comes from a comparison between non-equivalent temporal and spatial quantities. Their historical occurrences are preserved for auditability.

The v3 estimator and assembly calculation also require further methodological work, including:
- agreement between the stated time-integral definition and the numerical time-weighting;
- calibration for spatial dependence among sampled grid locations;
- assessment of bias from clipping negative finite-sample MI estimates;
- estimator, resolution, sample-size and time-step convergence;
- matched physical null models and a complete uncertainty budget.

A generic concern about high-dimensional KSG estimation should not be misrepresented as an established defect of the inspected v3 calculation: it estimates dependence between two scalar density samples. Spatial dependence and estimator bias remain separate, testable concerns.

---

## Research scope

The scientific scope of this repository is the definition, implementation, calibration and testing of assembly/information measures in physical systems, with cosmological halo analysis as the initial application.

### Core research questions

1. Can the proposed A_c quantity be defined with consistent units and a reproducible time-integration rule?
2. Does the estimator recover known mutual information in controlled cases?
3. How sensitive is it to spatial autocorrelation, finite samples, smoothing, resolution and estimator settings?
4. Does it distinguish physically meaningful temporal organization from appropriately matched stochastic and ΛCDM controls?
5. Can results be reproduced from versioned data, code, environment and run manifests?

### What would strengthen the evidence

Future analyses should provide:
- traceable simulation or observational data identifiers and access conditions;
- immutable code commit and environment;
- complete run manifest, seed list and parameter settings;
- independent calibration data distinct from target and null data;
- matched controls preserving relevant physical properties and selection;
- empirical exceedance counts and uncertainty intervals, not only Gaussian z-scores;
- convergence and sensitivity analyses;
- external independent reproduction before using that label.

No result should be promoted merely because a script executes or an internal test passes.

---

## Evidence levels

The repository uses claim-specific levels:

| Level | Label | Meaning |
|---|---|---|
| **L0** | Conceptual | Hypothesis, proposed method or research question |
| **L1** | Computationally validated | Specified code/tests or synthetic calculation run successfully |
| **L2** | Empirically constrained | Tested against traceable real data with appropriate controls |
| **L3** | Independently reproduced | Reproduced or re-analyzed by an independent external analyst/team |
| **L4** | Established | Supported by multiple independent lines of evidence or relevant scientific consensus |

These levels apply to individual claims, not entire repositories. Internal reruns and unit tests do not qualify as L3. See the [proposed evidence taxonomy and tagging standard](docs/governance/EVIDENCE_TAXONOMY_TAGGING_STANDARD_2026-11-09.md).

---

## Repository map

- research/null-ensemble/ — synthetic null-ensemble experiment and associated outputs.
- research/validation/ — validation notes and status for physical-data comparisons.
- research/ — analysis scripts and computational experiments; each result must be read with its own data and limitations.
- tests/ — software tests. Passing tests establish only the behavior covered by those tests.
- docs/EVIDENCE_STATUS.md — evidence rules and current classifications.
- docs/RESULTS_PROVENANCE.md — historical numerical provenance record.
- docs/audits/ — dated methodological and claims audits.

Other workstreams that have historically appeared alongside Cloud-9—including THEORIA, AI governance, causal-security proposals, UAP analyses, biological hypotheses and independent mathematical manuscripts—are not evidence for the cosmological claims. A repository separation proposal is under review; no historical materials have been silently deleted or moved.

---

## Consciousness and ethical interpretation

The possibility that future physics, neuroscience or other empirical sciences may provide evidence relevant to the emergence of consciousness remains an open research question. Cloud-9's current Assembly Index is **not** a validated consciousness detector, and no A_c threshold is established as a test of subjective experience, agency, personhood or moral status.

Any future physical evidence must first be evaluated within the relevant scientific discipline. An ethical interpretation would then need to state its additional premises and uncertainties. Rights and procedural protections should not be made contingent on an unvalidated cosmological score.

Cloud-9 is not the evidentiary basis for the author's current human-rights advocacy. That advocacy stands on its own legal, factual, ethical and policy grounds.

---

## Contributing and reporting results

When adding a result, include:
1. the exact claim and evidence level;
2. data provenance and licensing;
3. code commit, environment and run identifier;
4. estimator, parameters, seeds and null construction;
5. uncertainty and sensitivity analyses;
6. limitations and known failure modes;
7. whether review was internal or independent.

Use cautious, claim-specific language. Prefer proposed, implemented, tested, computed, empirically constrained and independently reproduced only when their definitions are met. Avoid discovered, confirmed, proven or established without the corresponding evidence.

---

## License

This repository is licensed under the MIT License. Consult the license file and individual data/source terms before reusing third-party material.
