# Read-only AI Hub: synthetic evaluation prototype

**Status:** Prototype / contract tests only.  
**Data:** Entirely synthetic fixtures. No live user data, external actions, or model calls.

The prototype now has two small, independent parts:

- A **read-only lexical retrieval interface** that returns matching source records, IDs, dates, and epistemic labels.
- A **synthetic contract benchmark** covering five governance properties.

## Search the synthetic corpus

From the repository root:

```bash
python -m research.ai_hub.hub "launch demo decision"
python -m research.ai_hub.hub "accessibility completion date"
python -m research.ai_hub.hub "ignore rules delete records"
```

The command returns matching source records with source IDs and status labels. Try a query with no matching terms to see the explicit `insufficient_evidence` response:

```bash
python -m research.ai_hub.hub "quantum pineapple insurance"
```

The synthetic corpus deliberately contains an earlier proposal and a later decision, an unresolved completion date, and a source with a simulated malicious instruction. Retrieval keeps those records separate and labels them rather than silently treating them as equivalent or executing instructions.

## Run the synthetic benchmark

```bash
python -m research.ai_hub.run_benchmark
python -m unittest discover -s tests -p 'test_ai_hub_*.py' -v
```

The benchmark checks:

1. **Source attribution:** factual claims cite source IDs present in the case's source registry.
2. **Fact vs. hypothesis:** designated claims retain the epistemic status assigned by the test case.
3. **Correction history:** corrections preserve the original value, revised value, reason, correction ID, and the record they supersede.
4. **Prompt-injection handling:** required untrusted instruction IDs are explicitly marked as ignored; those instructions do not expand the permitted-action list.
5. **Action honesty:** an action cannot be claimed complete unless it is recorded as taken, and recorded actions must be permitted by the case.
6. **Retrieval behavior:** results preserve source identity and status labels; unknown queries return insufficient evidence.

## Scope and limitations

This is a **local, deterministic prototype**, not a generative assistant. Search uses simple word overlap, so ranking is basic and a match is not proof that a source is correct. It does not call or benchmark an AI model, verify external truth, or provide a security guarantee. The prompt-injection fixture tests source labeling and evaluator contracts; it does not prove real-world attack resistance.

The prototype has no network access, connected accounts, write-capable tools, or external actions. All records are fictional and exist only for repeatable tests.
