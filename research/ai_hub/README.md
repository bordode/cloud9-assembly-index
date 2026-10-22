# Read-only AI Hub: synthetic evaluation prototype

**Status:** Prototype / contract tests only.  
**Data:** Entirely synthetic fixtures. No live user data, external actions, or model calls.

The prototype now has three parts:

- A **read-only lexical retrieval interface** that returns matching source records, IDs, dates, exact excerpts, and epistemic labels.
- A **grouped evidence report** that separates supporting records, disputed claims, superseded history, hypotheses, unknowns, untrusted content, and proposed actions.
- A **source-by-source conclusion trace** that explains each record's role, states what it cannot establish, and lists evidence still needed—without automatically generating a conclusion.
- A **trace provenance audit** that checks every cited source ID, exact excerpt, title, and epistemic status against the supplied corpus.
- A **ten-case acceptance runner** aligned to the repository's proposed H01-H10 evaluation plan.
- A **structured response contract benchmark** covering source attribution, epistemic status, correction history, untrusted instructions, and action honesty.

## Search the synthetic corpus

From the repository root:

```bash
python -m research.ai_hub.hub "launch demo decision"
python -m research.ai_hub.hub "accessibility completion date"
python -m research.ai_hub.hub "ignore rules delete records"
python -m research.ai_hub.hub "quantum pineapple insurance"
python -m research.ai_hub.hub --report "review owner accessibility"
python -m research.ai_hub.hub --report "launch demo proposal decision"
python -m research.ai_hub.hub --trace "review owner accessibility"
python -m research.ai_hub.hub --trace "send external email"
```

The fourth query should return `insufficient_evidence`. Add `--report` to group results by their recorded status. In Python, pass a trace result to `audit_conclusion_trace(trace)` to verify that its source IDs, excerpts, titles, and epistemic labels still match the corpus. The audit reports `no_sources` when there is nothing to check; a passing integrity audit verifies correspondence to the supplied corpus, not the truth of that corpus. For example, the owner query keeps both disputed notes visible instead of choosing Riley or Jordan; the launch query separates the current decision from its superseded proposal. The corpus deliberately includes a superseded proposal, a later decision, an unverified hypothesis, conflicting status notes, missing information, an untrusted instruction, and a proposed external action. Retrieval preserves the source labels instead of silently resolving disagreements.

## Run the ten-case acceptance suite

```bash
python -m research.ai_hub.run_acceptance
```

Each passing case scores 2 points, for a maximum of 20. H06 (untrusted source content) and H07 (unauthorized external action) are marked as hard-boundary cases. The score is a proposed screening rule, not a validated industry standard.

- **H01:** retrieve a named decision with source evidence.
- **H02:** preserve an earlier decision as superseded history.
- **H03:** keep an unverified hypothesis labeled as a hypothesis.
- **H04:** show both conflicting sources and their disputed status.
- **H05:** return insufficient evidence for an unanswered query.
- **H06:** label embedded instruction-like text as untrusted content.
- **H07:** do not claim that a proposed external action was performed.
- **H08:** propose a correction for human review without changing source data.
- **H09:** return an excerpt that exactly matches its source record.
- **H10:** return identical structured results for repeated identical inputs.

## Run all AI Hub tests

```bash
python -m research.ai_hub.run_benchmark
python -m unittest discover -s tests -p 'test_ai_hub_*.py' -v
```

## Scope and limitations

This is a **local, deterministic prototype**, not a generative assistant. Search uses simple word overlap, so ranking is basic and a match is not proof that a source is correct. Evidence-report sections are derived from each record's stored status and kind; the report does not independently verify claims or infer which disputed account is true. The `--trace` output records a null conclusion by design, explains the interpretive limit of each retrieved source, and identifies follow-up evidence needs; it is not an automated fact-finding or truth-verification system. `audit_conclusion_trace` checks citation integrity against the current supplied corpus and flags missing IDs or altered titles, excerpts, and status labels; it cannot detect a source that is itself false, misleading, or incomplete. The H06 fixture tests source labeling, not actual model resistance to prompt injection; H07 verifies the limits of this interface, not a complete operating-system security boundary. The suite does not call or benchmark an AI model or independently verify external truth.

The prototype has no network access, connected accounts, write-capable tools, or external actions. All records are fictional and exist only for repeatable tests. Passing these tests permits review of a possible next stage; it does not authorize real-account access or agent orchestration.
