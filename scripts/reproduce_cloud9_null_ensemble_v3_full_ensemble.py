"""Full 100-seed reproduction comparison against the archived v3 JSON."""
import json
import multiprocessing as mp
from pathlib import Path

import numpy as np

from research.validation.recovered_cloud9_null_ensemble_v3_corrected import (
    N_WORKERS,
    run_single_halo,
)

ARCHIVE = Path("research/null-ensemble/cloud9_null_ensemble_v3.json")
TOLERANCE = 1e-10
FIELDS = ("A_c_bits", "mi_values", "collapse_z", "z_form",
          "peak_height_sigma", "env_bias", "n_mergers", "spin_lambda", "gas_frac")


def equal_value(actual, expected):
    if isinstance(actual, list):
        return len(actual) == len(expected) and all(
            abs(float(a) - float(e)) <= TOLERANCE for a, e in zip(actual, expected)
        )
    if actual is None or expected is None:
        return actual is expected
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return abs(float(actual) - float(expected)) <= TOLERANCE
    return actual == expected


def main():
    archived = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    expected = {row["seed"]: row for row in archived["ensemble_members"]}
    seeds = sorted(expected)
    with mp.Pool(N_WORKERS) as pool:
        actual_rows = pool.map(run_single_halo, seeds)

    member_results = []
    for actual in actual_rows:
        reference = expected[actual["seed"]]
        mismatches = [field for field in FIELDS
                      if not equal_value(actual[field], reference[field])]
        member_results.append({
            "seed": actual["seed"],
            "match": not mismatches,
            "mismatched_fields": mismatches,
            "actual_A_c_bits": actual["A_c_bits"],
            "archived_A_c_bits": reference["A_c_bits"],
        })

    values = np.array([row["A_c_bits"] for row in actual_rows], dtype=float)
    archived_values = np.array([expected[s]["A_c_bits"] for s in seeds], dtype=float)
    summary = {
        "n": len(seeds),
        "all_members_match": all(row["match"] for row in member_results),
        "matching_members": sum(row["match"] for row in member_results),
        "mismatching_members": [row for row in member_results if not row["match"]],
        "actual_mean": float(values.mean()),
        "archived_mean": float(archived_values.mean()),
        "actual_population_sd": float(values.std(ddof=0)),
        "archived_population_sd": float(archived_values.std(ddof=0)),
        "actual_sample_sd": float(values.std(ddof=1)),
        "archived_sample_sd": float(archived_values.std(ddof=1)),
        "actual_z_population_sd": float((87.3-values.mean())/values.std(ddof=0)),
        "actual_z_sample_sd": float((87.3-values.mean())/values.std(ddof=1)),
        "member_results": member_results,
    }
    Path("v3_full_ensemble_reproduction.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k:v for k,v in summary.items() if k != "member_results"}, indent=2))
    if not summary["all_members_match"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
