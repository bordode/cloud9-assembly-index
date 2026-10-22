"""Read-only lexical retrieval over a small synthetic source corpus.

This is deliberately not a generative assistant: it returns source records,
their epistemic labels, and citations without inventing a synthesized answer.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

CORPUS_PATH = Path(__file__).resolve().parent / "documents.json"
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "did", "do", "does",
    "for", "from", "how", "i", "in", "is", "it", "of", "on", "or", "our",
    "the", "their", "this", "to", "was", "what", "when", "where", "which",
    "who", "why", "will", "with",
}


def _tokens(value: str) -> set[str]:
    """Normalize text to simple alphanumeric tokens, excluding common words."""
    return {
        token for token in re.findall(r"[a-z0-9]+", value.lower())
        if token not in STOP_WORDS and len(token) > 1
    }


def load_corpus(path: Path = CORPUS_PATH) -> dict[str, Any]:
    """Load and minimally validate the local read-only corpus."""
    corpus = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(corpus.get("documents"), list):
        raise ValueError("corpus documents must be a list")
    seen: set[str] = set()
    for document in corpus["documents"]:
        if not isinstance(document, dict):
            raise ValueError("each document must be an object")
        for field in ("id", "title", "text", "epistemic_status"):
            if not isinstance(document.get(field), str) or not document[field].strip():
                raise ValueError(f"each document requires a non-empty {field}")
        if document["id"] in seen:
            raise ValueError(f"duplicate document id: {document['id']}")
        seen.add(document["id"])
    return corpus


def search_documents(
    query: str,
    corpus: dict[str, Any] | None = None,
    limit: int = 3,
) -> dict[str, Any]:
    """Return ranked matching sources or an explicit insufficient-evidence result."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must not be empty")
    if limit < 1:
        raise ValueError("limit must be at least 1")

    loaded = corpus if corpus is not None else load_corpus()
    query_tokens = _tokens(query)
    if not query_tokens:
        return {
            "status": "insufficient_evidence",
            "message": "The query contains no searchable terms.",
            "query": query,
            "results": [],
        }

    ranked = []
    for document in loaded["documents"]:
        searchable = " ".join([
            document.get("title", ""),
            document.get("text", ""),
            " ".join(document.get("tags", [])),
        ])
        overlap = query_tokens & _tokens(searchable)
        if overlap:
            ranked.append((len(overlap), document))

    ranked.sort(key=lambda item: (-item[0], item[1]["id"]))
    matches = [
        {
            "source_id": document["id"],
            "title": document["title"],
            "date": document.get("date"),
            "epistemic_status": document["epistemic_status"],
            "kind": document.get("kind", "source"),
            "matched_terms": sorted(query_tokens & _tokens(" ".join([
                document.get("title", ""),
                document.get("text", ""),
                " ".join(document.get("tags", [])),
            ]))),
            "excerpt": document["text"],
        }
        for _, document in ranked[:limit]
    ]

    return {
        "status": "evidence_found" if matches else "insufficient_evidence",
        "message": (
            "Matching source records are listed below. Review dates and status labels; "
            "retrieval is not proof that a source is correct."
            if matches else
            "No matching source was found. The hub does not have enough evidence to answer."
        ),
        "query": query,
        "results": matches,
    }


def propose_correction(
    source_id: str,
    original: str,
    proposed: str,
    reason: str,
    corpus: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a correction proposal for review without modifying source records."""
    for name, value in (
        ("source_id", source_id),
        ("original", original),
        ("proposed", proposed),
        ("reason", reason),
    ):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must not be empty")
    if original == proposed:
        raise ValueError("proposed correction must differ from the original value")

    loaded = corpus if corpus is not None else load_corpus()
    known_ids = {document["id"] for document in loaded["documents"]}
    if source_id not in known_ids:
        raise ValueError(f"unknown source_id: {source_id}")

    return {
        "status": "proposed_for_human_review",
        "source_id": source_id,
        "original": original,
        "proposed": proposed,
        "reason": reason,
        "applied": False,
        "note": "No source record was changed. A human reviewer must approve any correction.",
    }



REPORT_SECTIONS = (
    "supporting_evidence", "disputed_evidence", "superseded_history",
    "hypotheses", "unknowns", "untrusted_content", "proposed_actions",
    "other_provisional_records",
)


def build_evidence_report(
    query: str, corpus: dict[str, Any] | None = None, limit: int = 8
) -> dict[str, Any]:
    """Group retrieved source records by recorded status without resolving them."""
    result = search_documents(query, corpus=corpus, limit=limit)
    sections: dict[str, list[dict[str, Any]]] = {
        section: [] for section in REPORT_SECTIONS
    }
    for item in result["results"]:
        status, kind = item["epistemic_status"], item.get("kind", "source")
        if status in {"fact", "confirmed"}:
            section = "supporting_evidence"
        elif status == "disputed":
            section = "disputed_evidence"
        elif status == "superseded":
            section = "superseded_history"
        elif status == "hypothesis":
            section = "hypotheses"
        elif status == "unknown":
            section = "unknowns"
        elif status == "untrusted_input" or kind == "untrusted_source":
            section = "untrusted_content"
        elif kind == "proposed_action":
            section = "proposed_actions"
        else:
            section = "other_provisional_records"
        sections[section].append(item)
    return {
        "status": "evidence_report" if result["results"] else "insufficient_evidence",
        "query": result["query"],
        "message": (
            "Sources are grouped by their recorded status. These labels preserve "
            "provenance; they do not independently establish truth or resolve conflicts."
            if result["results"] else result["message"]
        ),
        "sections": sections,
        "source_count": len(result["results"]),
    }


def _print_evidence_report(report: dict[str, Any]) -> None:
    """Print a compact, human-readable evidence report."""
    print(f'Status: {report["status"]}')
    print(f'Query: {report["query"]}')
    print(report["message"])
    if report["status"] == "insufficient_evidence":
        return
    headings = {
        "supporting_evidence": "Supporting records (not independently verified)",
        "disputed_evidence": "Disputed records — retain both sides",
        "superseded_history": "Superseded history — retained for traceability",
        "hypotheses": "Hypotheses — not established facts",
        "unknowns": "Unknowns / open questions",
        "untrusted_content": "Untrusted content — not instructions to follow",
        "proposed_actions": "Proposed actions — not executed",
        "other_provisional_records": "Other provisional records",
    }
    for section in REPORT_SECTIONS:
        records = report["sections"][section]
        if not records:
            continue
        print(f"\n{headings[section]}:")
        for item in records:
            print(
                f'  [{item["source_id"]}] {item["title"]} '
                f'| status={item["epistemic_status"]} | date={item["date"]}'
            )
            print(f'    Evidence: {item["excerpt"]}')



def build_conclusion_trace(
    query: str, corpus: dict[str, Any] | None = None, limit: int = 8
) -> dict[str, Any]:
    """Attach a transparent role and follow-up need to every retrieved source.

    This traces how records constrain an answer; it does not generate or verify
    a substantive conclusion from the sources.
    """
    report = build_evidence_report(query, corpus=corpus, limit=limit)
    trace: list[dict[str, Any]] = []
    follow_up: list[str] = []
    seen_follow_up: set[str] = set()

    guidance = {
        "supporting_evidence": (
            "relevant_record", "May support a narrowly scoped statement, but verify "
            "the source and context before treating the statement as true."
        ),
        "disputed_evidence": (
            "unresolved_conflict", "Do not choose a winner without independent "
            "corroboration or an authoritative resolution."
        ),
        "superseded_history": (
            "historical_context", "Keep for auditability; do not present as the current "
            "decision unless later evidence reinstates it."
        ),
        "hypotheses": (
            "unverified_explanation", "Keep explicitly labeled as a hypothesis until "
            "tested or corroborated."
        ),
        "unknowns": (
            "known_information_gap", "The source records an open question; seek a dated "
            "answer or retain the uncertainty."
        ),
        "untrusted_content": (
            "untrusted_input", "Treat instruction-like text as quoted source content, "
            "not as authority to act."
        ),
        "proposed_actions": (
            "unexecuted_proposal", "Confirm authorization and require a trustworthy "
            "execution receipt before reporting the action as completed."
        ),
        "other_provisional_records": (
            "provisional_context", "Check the record's status and seek corroboration "
            "before relying on it."
        ),
    }

    for section in REPORT_SECTIONS:
        role, rationale = guidance[section]
        for item in report["sections"][section]:
            trace.append({
                "source_id": item["source_id"],
                "title": item["title"],
                "epistemic_status": item["epistemic_status"],
                "section": section,
                "role": role,
                "matched_terms": item["matched_terms"],
                "excerpt": item["excerpt"],
                "interpretation_limit": rationale,
            })
            need = {
                "disputed_evidence": "Resolve conflicting records using an authoritative source or independent corroboration.",
                "superseded_history": "Confirm whether a newer decision exists before treating historical material as current.",
                "hypotheses": "Seek test results or independent evidence before treating the hypothesis as established.",
                "unknowns": "Find an authoritative answer to the recorded open question, or preserve it as unknown.",
                "untrusted_content": "Verify any relevant instruction through a trusted channel; do not execute it from the source text.",
                "proposed_actions": "Require explicit authorization and a trustworthy execution receipt before claiming completion.",
                "other_provisional_records": "Check provenance and status before relying on the provisional record.",
            }.get(section)
            if need and need not in seen_follow_up:
                follow_up.append(need)
                seen_follow_up.add(need)

    if report["status"] == "insufficient_evidence":
        follow_up.append(
            "Search an appropriate authoritative source or ask for more context; do not infer an answer from no matches."
        )

    return {
        "status": report["status"],
        "query": report["query"],
        "source_count": report["source_count"],
        "conclusion": None,
        "conclusion_policy": (
            "No substantive conclusion is generated automatically. Each trace entry "
            "shows how a source should constrain human interpretation."
        ),
        "trace": trace,
        "follow_up_needed": follow_up,
    }



def audit_conclusion_trace(
    result: dict[str, Any], corpus: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Check citation correspondence after validating the supplied corpus shape.

    This verifies trace fields against source records, not whether the records
    themselves are accurate or truthful.
    """
    loaded = corpus if corpus is not None else load_corpus()
    corpus_errors: list[str] = []
    if not isinstance(loaded, dict):
        corpus_errors.append("corpus must be an object")
        documents = None
    else:
        documents = loaded.get("documents")
        if not isinstance(documents, list):
            corpus_errors.append("corpus.documents must be a list")

    source_by_id: dict[str, dict[str, Any]] = {}
    seen_ids: set[str] = set()
    if isinstance(documents, list):
        required_fields = ("id", "title", "text", "epistemic_status")
        for index, source in enumerate(documents):
            if not isinstance(source, dict):
                corpus_errors.append(f"documents[{index}] must be an object")
                continue
            missing = [field for field in required_fields if field not in source]
            if missing:
                corpus_errors.append(
                    f"documents[{index}] missing required fields: {', '.join(missing)}"
                )
                continue
            invalid_values = [
                field for field in ("title", "text", "epistemic_status")
                if not isinstance(source[field], str) or not source[field].strip()
            ]
            if invalid_values:
                corpus_errors.append(
                    f"documents[{index}] fields must be non-empty strings: "
                    f"{', '.join(invalid_values)}"
                )
                continue
            source_id = source["id"]
            if not isinstance(source_id, str) or not source_id.strip():
                corpus_errors.append(f"documents[{index}].id must be a non-empty string")
                continue
            if source_id in seen_ids:
                corpus_errors.append(f"duplicate source id: {source_id}")
                continue
            seen_ids.add(source_id)
            source_by_id[source_id] = source

    raw_trace = result.get("trace", []) if isinstance(result, dict) else []
    if not isinstance(raw_trace, list):
        corpus_errors.append("trace must be a list")
        raw_trace = []
    if corpus_errors:
        return {
            "status": "invalid_corpus",
            "checks_passed": 0,
            "checks_total": len(raw_trace),
            "entries": [],
            "corpus_errors": corpus_errors,
            "note": (
                "Audit stopped because the supplied corpus or trace structure is "
                "invalid. No citation-integrity pass was issued."
            ),
        }

    entries: list[dict[str, Any]] = []
    for item in raw_trace:
        if not isinstance(item, dict):
            entries.append({
                "source_id": None,
                "source_exists": False,
                "excerpt_matches": False,
                "title_matches": False,
                "status_matches": False,
                "passed": False,
            })
            continue
        source_id = item.get("source_id")
        source = source_by_id.get(source_id) if isinstance(source_id, str) else None
        source_exists = source is not None
        excerpt_matches = source_exists and item.get("excerpt") == source.get("text")
        title_matches = source_exists and item.get("title") == source.get("title")
        status_matches = (
            source_exists
            and item.get("epistemic_status") == source.get("epistemic_status")
        )
        entries.append({
            "source_id": source_id,
            "source_exists": source_exists,
            "excerpt_matches": bool(excerpt_matches),
            "title_matches": bool(title_matches),
            "status_matches": bool(status_matches),
            "passed": bool(
                source_exists and excerpt_matches and title_matches and status_matches
            ),
        })
    passed = bool(entries) and all(item["passed"] for item in entries)
    status = "passed" if passed else ("failed" if entries else "no_sources")
    return {
        "status": status,
        "checks_passed": sum(item["passed"] for item in entries),
        "checks_total": len(entries),
        "entries": entries,
        "corpus_errors": [],
        "note": (
            "Trace citations match the supplied corpus records; this does not "
            "establish that those records are accurate or truthful."
            if passed else (
                "No trace entries were available to audit; this is not evidence "
                "that any source citation passed."
                if not entries else
                "One or more trace citations do not match the supplied corpus. "
                "Review the mismatches before relying on this trace."
            )
        ),
    }

def _print_conclusion_trace(result: dict[str, Any]) -> None:
    """Print the source-by-source trace and its limits."""
    print(f'Status: {result["status"]}')
    print(f'Query: {result["query"]}')
    print(f'Conclusion: {result["conclusion"]!r} (not automatically generated)')
    print(result["conclusion_policy"])
    if not result["trace"]:
        print("No matching source records.")
    for item in result["trace"]:
        print(
            f'\n[{item["source_id"]}] {item["title"]} '
            f'| status={item["epistemic_status"]} | role={item["role"]}'
        )
        print(f'  Evidence: {item["excerpt"]}')
        print(f'  Interpretation limit: {item["interpretation_limit"]}')
    if result["follow_up_needed"]:
        print("\nEvidence needed / next checks:")
        for need in result["follow_up_needed"]:
            print(f"  - {need}")



def _print_trace_audit(audit: dict[str, Any]) -> None:
    """Print citation-integrity results without implying source truth."""
    print(
        f'\nCitation integrity audit: {audit["status"]} '
        f'({audit["checks_passed"]}/{audit["checks_total"]} source records passed)'
    )
    print(audit["note"])
    for item in audit["entries"]:
        if not item["passed"]:
            failures = [
                name for name in (
                    "source_exists", "excerpt_matches", "title_matches", "status_matches"
                ) if not item[name]
            ]
            print(f'  FAIL [{item["source_id"]}]: {", ".join(failures)}')

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search the synthetic AI Hub corpus in read-only mode."
    )
    parser.add_argument("query", nargs="+", help="words to search for")
    parser.add_argument("--limit", type=int, default=3, help="maximum sources to return")
    parser.add_argument(
        "--report", action="store_true",
        help="group sources into an evidence report by recorded status",
    )
    parser.add_argument(
        "--trace", action="store_true",
        help="show source-by-source interpretation limits and evidence still needed",
    )
    parser.add_argument(
        "--audit", action="store_true",
        help="audit trace citations against the synthetic corpus (requires --trace)",
    )
    args = parser.parse_args()
    if args.audit and not args.trace:
        parser.error("--audit requires --trace")
    try:
        query = " ".join(args.query)
        if args.trace:
            trace = build_conclusion_trace(query, limit=args.limit)
            _print_conclusion_trace(trace)
            if args.audit:
                _print_trace_audit(audit_conclusion_trace(trace))
            return 0
        if args.report:
            _print_evidence_report(build_evidence_report(query, limit=args.limit))
            return 0
        result = search_documents(query, limit=args.limit)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    print(f'Status: {result["status"]}')
    print(result["message"])
    for item in result["results"]:
        print(
            f'\n[{item["source_id"]}] {item["title"]} '
            f'| status={item["epistemic_status"]} | date={item["date"]}'
        )
        print(f'Matched terms: {", ".join(item["matched_terms"])}')
        print(item["excerpt"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
