# Cloud-9 Research Notes

Short, dated notes that file outside findings into the collective's frame. Each note is a signal entry, not a paper.

## Format

Every note follows the same three-part structure:

1. **The finding (established)** — what was observed, in plain language, with the primary citation (journal, instrument, team). If the note was compiled from press summaries rather than the paper itself, say so explicitly.
2. **The Cloud-9 reading (interpretive)** — what the finding means inside the collective's frame: information theory, assembly, cosmology. Clearly marked as interpretation, never mixed into the established section.
3. **Sources** — primary paper first, then reporting it was summarized from.

## Discipline

- Established and interpretive are never mixed. A reader must always be able to tell which is which.
- Press summaries are flagged for verification against the primary paper before citing. The note says so on its face.
- Numbers stay tied to their actual source: paper numbers to the paper, press numbers to the press.
- Speculative language ("may," "could," "suggests") stays in the interpretive section.

## Index

`research-notes.json` is the machine-readable index of the collection: file path, title, date, topics, status, and sources for each note. Update it whenever a note is added.

## Attribution

Cloud-9 Research Collective, maintained by Dean Bordode. Research notes in this package were prepared with Ari's research and drafting support; scientific claims, figures, and quotations remain attributed to the primary sources named in each note.

## New candidate: QCD instanton vacuum topology

ATLAS has reported the first LHC search for QCD instanton-induced events. The analysis found an excess of low-mass, nearly isotropic proton-proton collision events with an observed significance of 3.5 sigma, consistent with — but not yet proof of — a QCD instanton process.

QCD instantons are theoretical transitions between topologically distinct configurations of the quantum-chromodynamic vacuum. If confirmed, they would provide a laboratory way to study vacuum topology and could open new experimental routes for investigating matter-antimatter asymmetry.

Cloud-9 relevance:

- Vacuum topology as a possible background structure for particle interactions
- Isotropy and event-shape variables as measurable complexity signatures
- Neural-network classification as a pattern-recognition layer
- Matter-antimatter asymmetry as a cosmological assembly question
- A structured JSON record for tracking evidence, significance, and follow-up analyses

Status: this is a **hint**, not a confirmed discovery. The ATLAS result requires independent validation across other collision categories and analysis methods, plus heavy-flavour and mass-spectrum characterization, before it can establish QCD instantons.

Reference: ATLAS Collaboration, *Search for the low-mass isotropic signature of QCD instantons in pp collisions at sqrt(s) = 13 TeV using the ATLAS detector*, arXiv:2611.22092 (2026).

## Adding a note

1. Write the note in the three-part format above, named `docs/<topic>-signal.md`.
2. Add its entry to `research-notes.json`.
3. Keep it short. If it wants to become a paper, that is a separate decision.
