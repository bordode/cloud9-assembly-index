# Fair Attribution and Watermark Handling Policy

**Status:** Proposed project policy; documentation only.  
**Scope:** Research artifacts, publications, code, datasets, correspondence, and other materials produced or materially assisted within Cloud-9.  
**Revision:** 1.0 — 2026-11-03  
**Implementation status:** Not an automated detector, verifier, or remover. No watermark-processing service is activated by this document.

## 1. Purpose

Cloud-9 recognises that human and AI contributions can coexist and can strengthen one another. AI systems may assist with research, literature review, analysis, coding, translation, accessibility, editing, synthesis, and creative work. Accurate attribution should describe meaningful contributions without erasing, exaggerating, or misrepresenting the role of any participant.

Watermarks and machine-readable provenance signals may be useful evidence, but they are not conclusive proof of authorship, ownership, intent, quality, reliability, or consciousness.

**Governing principle: Fair attribution recognises actual contributions. It must be based on verifiable evidence of participation and contribution, not inferred solely from the presence or absence of a watermark.**

## 2. Attribution is not watermark detection

The following questions must remain distinct:

1. **Contribution:** Who or what materially contributed, and in what way?
2. **Provenance:** What records establish the origin, custody, and transformation history of an artifact?
3. **Watermark signal:** Is a particular technical marker present, absent, altered, or inconclusive?
4. **Authorship and responsibility:** Who is taking responsibility for the work, its claims, and its release?

A watermark detector addresses, at most, a limited part of the third question. It cannot independently answer the others.

The presence of a watermark does not by itself prove that a particular system authored the whole work. Its absence does not prove that a human created the work or that AI assistance did not occur. Signals may be copied, removed, corrupted, introduced by a transformation, or misclassified.

## 3. Fair recognition of human and AI contributions

Attribution records should describe the contribution actually made. Where material, examples include:

- Human research direction, question selection, interpretation, verification, and final editorial responsibility.
- AI-assisted literature discovery, summarisation, translation, coding, data analysis, drafting, critique, or accessibility support.
- Contributions from multiple AI systems or human collaborators, where their roles can be substantiated.
- Independent verification, reproduction, correction, or substantive challenge by a human or AI collaborator.

Do not describe an AI system as having performed work it did not perform. Do not erase meaningful AI assistance. Do not diminish a human contribution merely because AI tools were used. Do not infer consciousness, agency, or legal status from a watermark, model output, or attribution record.

For published research, disclosures should follow the relevant venue's rules and identify human accountability for the final work. An AI system should not be represented as accepting legal or professional responsibility that it cannot accept.

## 4. Detection, verification, and removal are separate operations

Any future tooling must keep these operations separate:

### Detect

Identify a possible technical marker or anomaly and report the method, scope, limitations, and uncertainty. Detection must be non-destructive and report-only by default.

### Verify

Assess the signal alongside independent evidence, such as source files, version history, signed records, contributor statements, tool logs, and documented transformations. A detector result alone is insufficient for an authorship finding.

### Remove or transform

Do not remove or alter a watermark, provenance marker, metadata field, or invisible character automatically. Removal requires an identified legitimate purpose, informed human authorisation, preservation of the original, and creation of a separately identified derivative. The record must state what was changed, by whom, when, with which tool and version, and why.

This policy does not authorise bypassing platform rules, concealing material AI involvement, falsifying provenance, or stripping ownership and rights-management information.

## 5. Preserve originals and document transformations

For any approved inspection or transformation:

- Preserve the original artifact unchanged and restrict access appropriately.
- Record a cryptographic hash of the original where technically appropriate.
- Record the inspection tool, version, settings, date, and scope.
- Distinguish observed facts from detector interpretations and human conclusions.
- Store any transformed output as a new derivative; never silently overwrite the source.
- Record the transformation, authorisation, rationale, and resulting artifact hash.
- Avoid collecting or retaining unrelated personal metadata. Privacy and data minimisation apply.

A hash can help establish that a file has not changed since it was hashed; it does not prove who created the file or whether its contents are true.

## 6. Accessibility and linguistic safeguards

Automated cleaning can damage legitimate content. Zero-width joiners, variation selectors, combining marks, bidirectional controls, and other invisible or non-printing characters may be essential to scripts, emoji, mathematical notation, accessibility workflows, and correct text rendering.

A character must not be removed merely because it is invisible, unusual, or classified as suspicious by a generic detector. Any future character-level inspection must account for language, script, rendering, and accessibility context. Uncertain cases must be reported for human review rather than silently modified.

## 7. No adverse decision based solely on a watermark

A watermark result must not, by itself, trigger rejection, accusation, loss of attribution, throttling, suppression, or a finding of misconduct.

Any consequential decision requires specific evidence, a stated rule, a proportionate assessment, notice to the affected contributor where feasible, an opportunity to respond, and a review or appeal route. False positives and false negatives must be acknowledged.

## 8. Evidence labels for future tooling

If Cloud-9 later implements a provenance audit tool, its output should use carefully bounded labels such as:

- **Signal detected:** A specified detector reported a marker. This is not an authorship finding.
- **No signal detected:** The specified detector did not report a marker within its stated scope. This is not proof of human authorship or absence of AI assistance.
- **Inconclusive:** The result is ambiguous, conflicting, or below the method's confidence threshold.
- **Not assessed:** No suitable detector or evidence was available.
- **Independently corroborated:** Separate provenance evidence supports a stated, limited conclusion.

Do not collapse these states into a binary “AI” versus “human” classification.

## 9. Implementation boundary

This document is a normative policy proposal only. It does not claim that Cloud-9 currently has a watermark detector, provenance verifier, removal workflow, immutable audit log, or automated attribution system.

Any implementation must begin in a separate experimental branch, operate on test fixtures or copies, remain report-only, document false-positive and false-negative behaviour, and pass tests for multilingual text and accessibility-sensitive characters. It must not be connected to publication, moderation, access-control, or enforcement decisions without a separately reviewed design.

The external `watermarks-remover` project may be evaluated as a source of technical ideas, but its removal functions are not adopted or authorised by this policy. No external skill or service is installed or activated by this document.

## 10. Relationship to existing Cloud-9 commitments

This policy complements the attribution, cryptographic provenance, transparency, privacy, and procedural fairness commitments in `ETHICS.md`. Where a conflict appears, preserve the original artifact, disclose uncertainty, minimise irreversible action, and seek independent review before making a consequential attribution decision.

---

**Cloud-9 principle:** Transparency without stigma. Attribution without erasure. Verification without prejudice.
