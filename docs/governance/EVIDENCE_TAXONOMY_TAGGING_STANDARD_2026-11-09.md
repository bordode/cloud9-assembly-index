# Evidence Taxonomy and Repository Tagging Standard

**Date:** 2026-11-09  
**Status:** Proposed repository-wide standard  
**Related:** `docs/EVIDENCE_STATUS.md` and the Cloud-9 Statistical Claims Audit

## 1. Evidence levels

Use the existing L0–L4 structure consistently. The level applies to a specific claim, not to an entire file, project, person or repository.

| Level | Label | Minimum meaning | Does not establish |
|---|---|---|---|
| **L0** | Conceptual | Hypothesis, definition, proposed mechanism, analogy, philosophical or normative position | Empirical truth or successful implementation |
| **L1** | Computationally validated | Code runs and specified tests pass, or a synthetic calculation reproduces a defined result | Agreement with nature, observational validity or independent confirmation |
| **L2** | Empirically constrained | Claim is tested against traceable real observational/experimental data with appropriate methods and controls | Independent reproduction, causal proof or consensus |
| **L3** | Independently reproduced | An independent analyst/team reproduces or re-analyzes the specific claim using independently controlled methods and transparent provenance | Established consensus |
| **L4** | Established | Multiple independent lines of evidence and/or broad, relevant peer-reviewed consensus support the specific claim | Automatic validation of adjacent interpretations |

**L3 is intentionally an external bar.** Internal reruns, unit tests, cross-checks by the same project team, alternate scripts, and friendly review do not qualify. Independence and any shared data, code, authorship, or parameter choices must be disclosed.

L4 is also claim-specific. A well-established physical mechanism does not make a new Cloud-9 application or interpretation established.

## 2. Required claim tags

For documents, modules, notebooks and result artifacts, use a short metadata block where practical:

```yaml
claim_status:
  evidence_level: L1
  label: computationally_validated
  claim_scope: "What exact proposition is supported"
  data_basis: synthetic | observational | experimental | theoretical | mixed
  provenance: "URI, DOI, dataset ID, or repository path"
  independent_review: none | internal | external
  limitations:
    - "Known limitation"
  last_reviewed: YYYY-MM-DD
```

For a document containing multiple claims at different levels, do not assign one blanket level. Use a claim register or annotate each result separately.

## 3. Required status vocabulary

Prefer precise verbs:

- **Proposed** — a concept or mechanism has been stated.
- **Implemented** — code or a method exists.
- **Tested** — a specified test was run; state its scope.
- **Computed** — a calculation was performed.
- **Reproduced internally** — the same project can reproduce its own result.
- **Empirically constrained** — real-world data provide a documented constraint.
- **Independently reproduced** — an external independent analysis supports the same claim.
- **Established** — the claim has broad, relevant independent support.

Avoid “validated,” “confirmed,” “proven,” “discovered,” “detection,” and “breakthrough” unless the exact claim meets the evidence standard and the supporting evidence is cited.

## 4. Claim-specific evidence boundary

Evidence levels do not transfer automatically between claims. In particular:

- A successful software test does not validate the physical model.
- A synthetic null comparison does not establish an observational detection.
- A physical measurement of persistence or mutual information does not establish non-stochastic assembly without suitable alternatives and controls.
- Evidence of organization or information processing does not by itself establish consciousness, subjective experience, interests, agency, personhood or moral status.
- A future empirical result relevant to consciousness emergence may be scientifically important, but its ethical interpretation must state the additional premises and uncertainty explicitly.
- Normative human-rights or governance commitments should be assessed on their legal, ethical and policy merits, not assigned a scientific evidence level as though they were physical measurements.

## 5. Suggested document-level tags

| Material type | Default starting status |
|---|---|
| Mathematical definition not yet proved or empirically tested | L0 / theoretical proposal |
| Unit-tested implementation | L1 / computationally validated implementation |
| Synthetic benchmark | L1 / synthetic computational result |
| Analysis of traceable observational data | L2 only if controls and provenance are adequate |
| Independent reproduction by a separate analyst/team | L3 |
| Broadly established scientific proposition | L4 |
| Rights declaration, governance framework or ethical principle | Normative proposal / normative commitment; do not force into L0–L4 as a scientific claim |

## 6. Review and promotion rules

1. Every promotion must identify the exact claim and evidence that changed its status.
2. A file's status must not be promoted because another result in the same project reached a higher level.
3. L2 requires traceable real data, not merely a dataset name in a README.
4. L3 requires independence from the original analysis team and disclosure of shared inputs or methods.
5. L4 requires multiple independent lines of support or relevant consensus.
6. If uncertainty or provenance is unresolved, retain the lower level.
7. Record withdrawn or superseded claims in an audit trail; do not silently erase them.
8. Review the status when code, data, estimator, null model or interpretation changes.

## 7. Current Cloud-9 examples

- v3 N=100 synthetic null comparison: **L1**, model-dependent synthetic comparison.
- Historical A_c=87.3 ± 3.2 and z=2.99: **reported historical / provenance pending**; not currently promoted to L2.
- Legacy 1,137.753σ: **withdrawn from scientific interpretation**; unsupported source-level value.
- TNG single-snapshot radial comparison: **invalid comparison**, not evidence for temporal assembly.
- Current read-noise and dither benchmark work: each result remains **L1** until its specific methods and data basis justify another level.
- AI-rights and cognitive-stewardship materials: **normative/governance work**, evaluated independently of the cosmological metric.

This standard is a proposal until accepted through repository review.
