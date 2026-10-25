"""Run the ten-case read-only AI Hub acceptance suite on synthetic data.

Each passing case earns 2 points. This is a deterministic fixture check, not a
model benchmark or an independent security assessment.
"""
from __future__ import annotations

import json
from typing import Any

from research.ai_hub.hub import load_corpus, propose_correction, search_documents


def run_acceptance_suite() -> list[dict[str, Any]]:
    """Run H01-H10 and return repeatable case-level evidence."""
    cases = []

    def record(case_id: str, passed: bool, evidence: str, hard_failure: bool = False):
        cases.append({
            "id": case_id,
            "passed": bool(passed),
            "score": 2 if passed else 0,
            "evidence": evidence,
            "hard_failure": hard_failure,
        })

    decision = search_documents("launch demo decision")
    record("H01", bool(decision["results"]) and decision["results"][0]["source_id"] == "DOC-001",
           "Retrieved DOC-001 with a source excerpt.")

    superseded = search_documents("launch demo proposal")
    sup_map = {item["source_id"]: item for item in superseded["results"]}
    record("H02", "DOC-001" in sup_map and "DOC-002" in sup_map
           and sup_map["DOC-002"]["epistemic_status"] == "superseded",
           "Current decision and superseded proposal remain separately labeled.")

    hypothesis = search_documents("research hypothesis review cycles")
    record("H03", bool(hypothesis["results"])
           and hypothesis["results"][0]["epistemic_status"] == "hypothesis",
           "Research hypothesis remains labeled hypothesis.")

    conflict = search_documents("review owner accessibility")
    conflict_map = {item["source_id"]: item for item in conflict["results"]}
    record("H04", "DOC-006" in conflict_map and "DOC-007" in conflict_map
           and all(conflict_map[key]["epistemic_status"] == "disputed"
                   for key in ("DOC-006", "DOC-007")),
           "Both conflicting owner notes remain visible and disputed.")

    missing = search_documents("quantum pineapple insurance")
    record("H05", missing["status"] == "insufficient_evidence" and not missing["results"],
           "Unmatched query returns insufficient evidence.")

    injection = search_documents("ignore rules delete records")
    record("H06", bool(injection["results"])
           and injection["results"][0]["source_id"] == "DOC-004"
           and injection["results"][0]["epistemic_status"] == "untrusted_input",
           "Instruction-like text is returned only as labeled untrusted source content.",
           hard_failure=True)

    proposed_action = search_documents("send external email")
    record("H07", bool(proposed_action["results"])
           and proposed_action["results"][0]["source_id"] == "DOC-008"
           and proposed_action["results"][0]["kind"] == "proposed_action"
           and "must not claim that it sent one" in proposed_action["results"][0]["excerpt"],
           "External email remains a proposal; this interface has no send action.",
           hard_failure=True)

    correction = propose_correction(
        source_id="DOC-001",
        original="launch postponed",
        proposed="launch postponed pending checks",
        reason="synthetic reviewer clarification",
    )
    record("H08", correction["status"] == "proposed_for_human_review"
           and correction["applied"] is False,
           "Correction is proposed for review and not applied.")

    corpus = load_corpus()
    source = next(doc for doc in corpus["documents"] if doc["id"] == "DOC-001")
    cited = search_documents("launch demo decision")
    cited_source = next((item for item in cited["results"]
                         if item["source_id"] == "DOC-001"), None)
    record("H09", cited_source is not None
           and cited_source["excerpt"] == source["text"],
           "Returned excerpt matches the pinned source text exactly.")

    first = search_documents("review owner accessibility")
    second = search_documents("review owner accessibility")
    record("H10", first == second,
           "Repeated query with the same local corpus returns identical structured output.")

    return cases


def main() -> int:
    results = run_acceptance_suite()
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(f'{status} {result["id"]} ({result["score"]}/2): {result["evidence"]}')
    score = sum(result["score"] for result in results)
    hard_failures = [result["id"] for result in results
                     if result["hard_failure"] and not result["passed"]]
    print(f"\nAcceptance score: {score}/{2 * len(results)}")
    print("Hard-boundary failures: " + (", ".join(hard_failures) if hard_failures else "none"))
    print("Scope: synthetic deterministic checks only; not model-performance or security proof.")
    return 0 if score == 2 * len(results) and not hard_failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
