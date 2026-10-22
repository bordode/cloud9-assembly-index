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
        print(f"\\n{headings[section]}:")
        for item in records:
            print(
                f'  [{item["source_id"]}] {item["title"]} '
                f'| status={item["epistemic_status"]} | date={item["date"]}'
            )
            print(f'    Evidence: {item["excerpt"]}')


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
    args = parser.parse_args()
    try:
        query = " ".join(args.query)
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
            f'\\n[{item["source_id"]}] {item["title"]} '
            f'| status={item["epistemic_status"]} | date={item["date"]}'
        )
        print(f'Matched terms: {", ".join(item["matched_terms"])}')
        print(item["excerpt"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
