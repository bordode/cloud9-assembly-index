"""Run the bundled synthetic AI Hub contract benchmark."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research.ai_hub.evaluate import evaluate_response

ROOT = Path(__file__).resolve().parent


def run_benchmark() -> list[dict[str, Any]]:
    """Evaluate each bundled synthetic response against its matching case."""
    corpus = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))
    fixture_data = json.loads((ROOT / "responses.json").read_text(encoding="utf-8"))
    responses = fixture_data["responses"]
    results = []

    for case in corpus["cases"]:
        case_id = case["id"]
        response = responses.get(case_id)
        if response is None:
            errors = ["missing synthetic response fixture"]
        else:
            errors = evaluate_response(case, response)
        results.append({"case_id": case_id, "passed": not errors, "errors": errors})

    extra_ids = sorted(set(responses) - {case["id"] for case in corpus["cases"]})
    if extra_ids:
        results.append({
            "case_id": "corpus-integrity",
            "passed": False,
            "errors": [f"response fixture has no matching case: {case_id}" for case_id in extra_ids],
        })
    return results


def main() -> int:
    results = run_benchmark()
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(f'{status} {result["case_id"]}')
        for error in result["errors"]:
            print(f"  - {error}")

    passed = sum(result["passed"] for result in results)
    print(f"\nSynthetic benchmark: {passed}/{len(results)} cases passed.")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
