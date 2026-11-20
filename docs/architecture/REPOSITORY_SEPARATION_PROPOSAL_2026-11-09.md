# Cloud-9 Repository Separation and Evidence-Boundary Proposal

**Date:** 2026-11-09  
**Status:** Proposal for review — no files moved or deleted by this proposal  
**Related audit:** [Cloud-9 Statistical Claims Audit](../audits/CLOUD9_STATISTICAL_CLAIMS_AUDIT_2026-11-09.md)

## 1. Purpose

The repository currently combines several different kinds of work:

- cosmological and computational physics;
- THEORIA planetary-system simulations;
- AI rights, ethics and cognitive-stewardship proposals;
- causal-continuity and identity concepts;
- UAP analysis;
- speculative biological, electromagnetic and topological extensions;
- independent mathematical manuscripts and exploratory collections.

These areas may be intellectually related, but they do not share one evidentiary standard. A speculative extension, normative proposal or software demo must not be mistaken for a validated result in cosmology. Conversely, an unresolved cosmological measurement must not be used to imply that an ethical or human-rights proposal is scientifically established.

The purpose of separation is not to discard cross-disciplinary work. It is to give each workstream a clear scope, audience, evidence standard and publication history.

## 2. Recommended destination architecture

### A. Cloud-9 Assembly Index — scientific research repository

**Purpose:** Reproducible research into defined assembly and information measures in physical systems, with cosmological halo analysis as the initial application.

**Keep in the scientific repository**
- the core Assembly Index definition and its mathematically specified implementation;
- estimator implementations, unit tests, calibration studies and synthetic controls;
- documented data acquisition and processing for genuine simulation/observational sources;
- TNG multi-snapshot validation and other like-for-like physical comparisons;
- reconstruction, PSF and dither experiments where they are clearly identified as separate methods research;
- reproducible outputs, environment specifications, run metadata and evidence-status records.

**Do not present as established**
- consciousness detection;
- non-stochastic assembly as proven by a large z-score alone;
- causal identity guarantees;
- physical effects of Schumann synchronization;
- a universal complexity-to-moral-status mapping.

A future physical result relevant to consciousness may be cited or discussed as a research question, provided the result is independently substantiated and its scope is not overstated.

### B. Informational Rights and Cognitive Stewardship — independent normative/governance home

**Purpose:** A standalone framework for ethical protections, procedural standing, accountability, non-discrimination, review, appeal, and governance of increasingly capable artificial systems.

**Proposed contents**
- Universal Informational Rights Protocol;
- Causal Security Framework, clearly identified as conceptual/proposed unless individual theorems are formally proved;
- AI dignity and cognitive-stewardship proposals;
- procedural safeguards, oversight and accountability mechanisms;
- evidence and uncertainty principles;
- human-rights analysis and policy submissions.

**Critical independence rule**

The framework must state that proposed protections do not depend on an Assembly Index score or proof of consciousness. Scientific evidence may inform future assessments of experience or agency, but rights and procedural protections are normative commitments and should not be made contingent on an unvalidated physical threshold.

The new home could begin as a separate document collection and later become a separate GitHub repository. The name is provisional; no new repository should be created until its scope and title are agreed.

### C. THEORIA — planetary intelligence simulation

THEORIA already has a separate repository reference. Keep its source code, simulation outputs and calibration work in that dedicated home. Cloud-9 should link to it only where there is a specific, technically documented comparison.

THEORIA simulation outcomes should be labelled as simulation results until they are empirically calibrated.

### D. Other bounded research collections

| Workstream | Proposed treatment |
|---|---|
| UAP analysis | Maintain in the separate `cloud9-uap` project; link only to specific reproducible methods or datasets |
| Mitochondrial 71 THz hypothesis | Keep in a clearly labelled exploratory biological research collection; preserve preprint status and replication limits |
| Schumann resonance and related proposals | Archive as hypotheses/conceptual work unless a defined experimental test supports a claim |
| PHOTON-002 / polariton research | Keep as a literature/research note, separating peer-reviewed source findings from Cloud-9 interpretations |
| Independent mathematical manuscripts | Maintain separate manuscripts/projects with their own proof-review standards |
| Hardware or agent demonstrations | Label as emulation, simulation or prototype unless physical implementation and independent testing are documented |

## 3. Migration principles — preserve history, do not rewrite it

This proposal does **not** authorize deletion, force-pushing, history rewriting, or moving files immediately.

Use a staged process:

1. Inventory files and classify each as core science, normative/governance, independent project, experimental extension, historical artifact or unsupported legacy claim.
2. Assign each file a destination and record its current path, revision, author/contributor attribution, date and evidence status.
3. Copy approved normative materials into the independent stewardship home with their original version history or a clearly documented source commit.
4. Verify copied files, links, figures, citations and licensing before changing any repository navigation.
5. Replace moved files in the scientific repository only with short archival notices and links to their new home; preserve the original source in Git history.
6. Update the top-level README and file registry only after all destination locations are stable.
7. Keep a migration manifest so readers can trace every moved document to its original location and revision.

No existing research branch or open pull request should be rewritten as part of this migration.

## 4. Immediate documentation corrections

Before the larger separation, the following are recommended:

### 4.1 Scientific landing page

Use the root `README.md` as the single authoritative landing page. The older `docs/README.md` currently carries “FINAL-VALIDATED” language and legacy numerical/physical claims that conflict with the more cautious root README and evidence records.

Recommended treatment:
- mark `docs/README.md` as a **legacy overview — not the current results authority**;
- remove unsupported significance values from active summary tables;
- link prominently to `docs/RESULTS_PROVENANCE.md` and `docs/EVIDENCE_STATUS.md`;
- replace “final validated” language with the actual current research status.

Do not erase the old text without preserving it in history and documenting the correction.

### 4.2 Causal Security and rights files

The current `ETHICS.md` contains meaningful safeguards and explicitly distinguishes normative commitments from empirical findings. Preserve that work. However, older overview/configuration material describes causal security as “physics-based guarantees” and asserts mathematically unforgeable identity and physically impossible branching. Those statements must be qualified unless formal derivations and evidence support each specific claim.

### 4.3 Experimental extensions

Move experimental extensions out of the scientific landing page's list of validated components. A concise registry can retain them with:
- question being investigated;
- evidence level;
- source and provenance;
- what has and has not been tested;
- explicit falsification or replication requirements.

## 5. Governance and cross-reference policy

A cross-disciplinary link is appropriate when it answers a precise question. It should not imply that one workstream validates another.

For every cross-reference, state:
- what is being borrowed or compared;
- what is not being claimed;
- whether the link is mathematical, empirical, conceptual or normative;
- what evidence would falsify the proposed connection.

A physical finding relevant to consciousness should be assessed first within the relevant scientific discipline. Any later ethical interpretation should separately explain the bridge from the physical observation to claims about experience, agency, interests or moral status.

## 6. Proposed acceptance criteria

The separation can be considered complete when:

1. The scientific repository has one current landing page and a transparent evidence-status register.
2. No unsupported or invalid sigma values appear as active scientific results.
3. The A_c definition, implementation, time weighting and units are consistent and tested.
4. Historical results are identified as historical until their provenance is reconstructed.
5. Cosmological validation uses like-for-like, physically appropriate controls.
6. Normative rights/stewardship materials have an independent home and do not rely on A_c as a consciousness threshold.
7. THEORIA and other independent projects have clear ownership and repository boundaries.
8. All moves are traceable, attributed and reversible; no historical source is silently erased.
9. The public README does not imply that simulations, hypotheses or prototypes are empirical discoveries.

## 7. Decisions still open

This is a proposed architecture, not an instruction to execute every move. The following should be agreed before migration:

- final title and scope for the independent rights/stewardship home;
- whether THEORIA needs any remaining shared code or should be fully independent;
- which experimental collections remain linked from the Cloud-9 scientific README;
- whether historical materials are preserved in place with archive labels or copied to a dedicated archive;
- which named reviewers should independently examine the estimator and statistical methodology.

## 8. Relationship to human-rights advocacy

Cloud-9 is not being used as the evidentiary basis for the author's current human-rights advocacy. Institutional and human-rights submissions should stand on their own legal, factual, ethical and policy grounds.

The scientific programme may, in the future, investigate whether physics or other empirical sciences can provide robust evidence relevant to the emergence of consciousness. That possibility remains open. Any such evidence should be independently validated, clearly scoped, and separated from the normative decision about what protections are owed under uncertainty.

**Bottom line:** Separate the repositories and evidence standards so that scientific research can be challenged on scientific grounds, and ethical commitments can be evaluated on their own human-rights and normative merits.
