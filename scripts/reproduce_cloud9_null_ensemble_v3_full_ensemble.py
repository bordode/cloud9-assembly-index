"""Strict full-ensemble reproduction and archive-integrity audit.

This script reproduces the archived fixed seed set and validates the archive
schema before comparing outputs. It does not modify the archived JSON.
"""
import hashlib
import json
import multiprocessing as mp
import os
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np
import scipy

from research.validation.recovered_cloud9_null_ensemble_v3_corrected import (
    N_WORKERS,
    run_single_halo,
)

ARCHIVE = Path("research/null-ensemble/cloud9_null_ensemble_v3.json")
SOURCE = Path("research/validation/recovered_cloud9_null_ensemble_v3_corrected.py")
SCRIPT = Path(__file__)
OUTPUT = Path("v3_full_ensemble_reproduction.json")
EXPECTED_SEEDS = list(range(1000, 1100))
EXPECTED_MI_LENGTH = 15
TOLERANCE = 1e-10
FIELDS = (
    "A_c_bits", "mi_values", "collapse_z", "z_form",
    "peak_height_sigma", "env_bias", "n_mergers", "spin_lambda", "gas_frac",
)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite_number(value, label):
    require(isinstance(value, (int, float)) and not isinstance(value, bool),
            f"{label} must be numeric")
    require(np.isfinite(float(value)), f"{label} must be finite")


def validate_archive(archive):
    require(isinstance(archive, dict), "Archive root must be a JSON object")
    members = archive.get("ensemble_members")
    require(isinstance(members, list), "ensemble_members must be a list")
    require(len(members) == len(EXPECTED_SEEDS),
            f"Expected exactly {len(EXPECTED_SEEDS)} archive members; got {len(members)}")

    seeds = []
    for index, member in enumerate(members):
        require(isinstance(member, dict), f"Member {index} must be an object")
        missing = [field for field in ("seed", *FIELDS) if field not in member]
        require(not missing, f"Member {index} missing fields: {missing}")
        seed = member["seed"]
        require(isinstance(seed, int) and not isinstance(seed, bool),
                f"Member {index} seed must be an integer")
        seeds.append(seed)
        finite_number(member["A_c_bits"], f"seed {seed} A_c_bits")
        finite_number(member["z_form"], f"seed {seed} z_form")
        for field in ("peak_height_sigma", "env_bias", "spin_lambda", "gas_frac"):
            finite_number(member[field], f"seed {seed} {field}")
        require(isinstance(member["n_mergers"], int) and member["n_mergers"] >= 0,
                f"seed {seed} n_mergers must be a non-negative integer")
        require(member["collapse_z"] is None or np.isfinite(float(member["collapse_z"])),
                f"seed {seed} collapse_z must be null or finite")
        mi = member["mi_values"]
        require(isinstance(mi, list) and len(mi) == EXPECTED_MI_LENGTH,
                f"seed {seed} mi_values must contain {EXPECTED_MI_LENGTH} values")
        for j, value in enumerate(mi):
            finite_number(value, f"seed {seed} mi_values[{j}]")

    require(len(set(seeds)) == len(seeds), "Archive contains duplicate seeds")
    require(sorted(seeds) == EXPECTED_SEEDS,
            f"Archive seeds must be exactly {EXPECTED_SEEDS[0]}–{EXPECTED_SEEDS[-1]}")
    return {row["seed"]: row for row in members}


def equal_value(actual, expected):
    if isinstance(actual, list):
        return (isinstance(expected, list) and len(actual) == len(expected)
                and all(abs(float(a) - float(e)) <= TOLERANCE
                        for a, e in zip(actual, expected)))
    if actual is None or expected is None:
        return actual is expected
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return abs(float(actual) - float(expected)) <= TOLERANCE
    return actual == expected


def main():
    require(ARCHIVE.is_file(), f"Archive not found: {ARCHIVE}")
    require(SOURCE.is_file(), f"Recovered source not found: {SOURCE}")
    archived = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    expected = validate_archive(archived)

    seeds = sorted(expected)
    with mp.Pool(N_WORKERS) as pool:
        actual_rows = pool.map(run_single_halo, seeds)

    require(len(actual_rows) == len(EXPECTED_SEEDS),
            f"Expected {len(EXPECTED_SEEDS)} generated members; got {len(actual_rows)}")
    actual_seeds = [row.get("seed") for row in actual_rows]
    require(actual_seeds == EXPECTED_SEEDS,
            "Generated seed sequence does not match the frozen expected sequence")

    member_results = []
    for actual in actual_rows:
        reference = expected[actual["seed"]]
        missing = [field for field in FIELDS if field not in actual]
        require(not missing, f"Generated seed {actual['seed']} missing fields: {missing}")
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
    require(np.isfinite(values).all(), "Generated A_c values contain non-finite values")

    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        git_commit = os.environ.get("GITHUB_SHA")

    summary = {
        "audit_type": "strict_fixed_seed_full_ensemble_reproduction",
        "all_members_match": all(row["match"] for row in member_results),
        "matching_members": sum(row["match"] for row in member_results),
        "mismatching_members": [row for row in member_results if not row["match"]],
        "n": len(seeds),
        "expected_seed_min": EXPECTED_SEEDS[0],
        "expected_seed_max": EXPECTED_SEEDS[-1],
        "mi_values_per_member": EXPECTED_MI_LENGTH,
        "comparison_fields": list(FIELDS),
        "tolerance": TOLERANCE,
        "actual_mean": float(values.mean()),
        "archived_mean": float(archived_values.mean()),
        "actual_population_sd": float(values.std(ddof=0)),
        "archived_population_sd": float(archived_values.std(ddof=0)),
        "actual_sample_sd": float(values.std(ddof=1)),
        "archived_sample_sd": float(archived_values.std(ddof=1)),
        "actual_z_population_sd": float((87.3-values.mean())/values.std(ddof=0)),
        "actual_z_sample_sd": float((87.3-values.mean())/values.std(ddof=1)),
        "provenance": {
            "git_commit": git_commit,
            "github_sha": os.environ.get("GITHUB_SHA"),
            "archive_path": str(ARCHIVE),
            "archive_sha256": sha256(ARCHIVE),
            "recovered_source_path": str(SOURCE),
            "recovered_source_sha256": sha256(SOURCE),
            "comparator_path": str(SCRIPT),
            "comparator_sha256": sha256(SCRIPT),
            "python_version": sys.version,
            "platform": platform.platform(),
            "numpy_version": np.__version__,
            "scipy_version": scipy.__version__,
        },
        "member_results": member_results,
    }
    OUTPUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items()
                      if k != "member_results"}, indent=2))
    if not summary["all_members_match"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
