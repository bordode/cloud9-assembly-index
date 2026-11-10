#!/usr/bin/env python3
"""Deterministic boundary-distance sensitivity audit for KSG marginal counts.

Unlike random Gaussian grids, this constructs representable distances at,
inside, and outside the kth-radius boundary and the configured radius offset.
It diagnoses numerical equivalence; it is not a statistical calibration study.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location(
    "ksg_boundary_distance_base", _HERE / "audit_ksg_boundary_conventions.py"
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError("cannot load KSG boundary convention helpers")
_BASE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_BASE)

strict_marginal_counts = _BASE.strict_marginal_counts
inclusive_marginal_counts = _BASE.inclusive_marginal_counts if hasattr(_BASE, "inclusive_marginal_counts") else None


def run_distance_audit(radius: float = 1.0, offset: float = 1e-12) -> dict:
    if not np.isfinite(radius) or radius <= 0:
        raise ValueError("radius must be finite and positive")
    if not np.isfinite(offset) or offset <= 0:
        raise ValueError("offset must be finite and positive")
    if radius + offset == radius:
        raise ValueError("offset is too small to change this radius in float64")

    distances = [
        ("one_ulp_inside", float(np.nextafter(radius, -np.inf))),
        ("exact_boundary", float(radius)),
        ("one_ulp_outside", float(np.nextafter(radius, np.inf))),
        ("half_offset_outside", float(radius + offset / 2.0)),
        ("offset_boundary", float(radius + offset)),
        ("one_ulp_beyond_offset", float(np.nextafter(radius + offset, np.inf))),
        ("two_offsets_outside", float(radius + 2.0 * offset)),
    ]
    values = np.asarray([0.0] + [d for _, d in distances], dtype=np.float64)
    radii = np.full(values.size, radius, dtype=np.float64)
    base_strict = strict_marginal_counts(values, radii)
    base_inclusive = np.asarray([
        np.count_nonzero(np.abs(values - values[i]) <= radii[i]) - 1
        for i in range(values.size)
    ], dtype=np.int64)
    inflated_strict = strict_marginal_counts(values, np.full(values.size, radius + offset))
    inflated_inclusive = np.asarray([
        np.count_nonzero(np.abs(values - values[i]) <= radius + offset) - 1
        for i in range(values.size)
    ], dtype=np.int64)

    rows = []
    for j, (label, distance) in enumerate(distances, start=1):
        rows.append({
            "point": label,
            "distance": distance,
            "distance_minus_radius": float(distance - radius),
            "included_at_uninflated_strict": bool(distance < radius),
            "included_at_uninflated_inclusive": bool(distance <= radius),
            "included_at_inflated_strict": bool(distance < radius + offset),
            "included_at_inflated_inclusive": bool(distance <= radius + offset),
        })

    target_counts = {
        "uninflated_strict": int(base_strict[0]),
        "uninflated_inclusive": int(base_inclusive[0]),
        "inflated_strict": int(inflated_strict[0]),
        "inflated_inclusive": int(inflated_inclusive[0]),
    }
    return {
        "study": "controlled_ksg_boundary_distance_sensitivity",
        "dtype": "float64",
        "radius": float(radius),
        "offset": float(offset),
        "offset_in_ulps_at_radius": float(offset / np.spacing(radius)),
        "target_point_count_excluding_self": len(distances),
        "target_neighbour_counts": target_counts,
        "distance_cases": rows,
        "interpretation_limits": [
            "Deterministic one-dimensional marginal-count geometry only.",
            "This isolates representable boundary inclusion behavior, not estimator bias or confidence-interval coverage.",
            "The offset is scale-dependent in floating-point units; conclusions apply to the configured radius and dtype.",
            "No historical v3 source or archived output is modified.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--radius", type=float, default=1.0)
    parser.add_argument("--offset", type=float, default=1e-12)
    parser.add_argument("--output", type=Path, default=Path("ksg_boundary_distance_sensitivity.json"))
    args = parser.parse_args()
    result = run_distance_audit(args.radius, args.offset)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print(json.dumps(result["target_neighbour_counts"], sort_keys=True))


if __name__ == "__main__":
    main()
