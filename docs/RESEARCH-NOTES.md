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

## Adding a note

1. Write the note in the three-part format above, named `docs/<topic>-signal.md`.
2. Add its entry to `research-notes.json`.
3. Keep it short. If it wants to become a paper, that is a separate decision.
