#!/usr/bin/env python3
"""Factorial audit separating KSG radius inflation from marginal count rules.

Four estimators are evaluated on identical samples:
1. uninflated radius + strict marginal counts;
2. inflated radius + strict marginal counts;
3. uninflated radius + inclusive marginal counts;
4. inflated radius + inclusive marginal counts (historical combined convention).

This isolates the two implementation choices and their interaction on known-MI
independent bivariate Gaussian controls. It does not change historical v3.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree
from scipy.special import digamma

_HERE = Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location(
    "ksg_boundary_factorial_base", _HERE / "audit_ksg_boundary_conventions.py"
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError("cannot load KSG boundary audit module")
_BASE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_BASE)

draw_pair = _BASE.draw_pair
gaussian_mi_bits = _BASE.gaussian_mi_bits
strict_marginal_counts = _BASE.strict_marginal_counts

VARIANTS = (
    "strict_count_uninflated_radius",
    "strict_count_inflated_radius",
    "inclusive_count_uninflated_radius",
    "inclusive_count_inflated_radius",
)


def inclusive_marginal_counts(values: np.ndarray, radii: np.ndarray) -> np.ndarray:
    """Count other observations at distance <= each radius."""
    values = np.asarray(values, dtype=np.float64).reshape(-1)
    radii = np.asarray(radii, dtype=np.float64).reshape(-1)
    if values.size != radii.size:
        raise ValueError("values and radii must have the same length")
    if not np.all(np.isfinite(values)) or not np.all(np.isfinite(radii)):
        raise ValueError("values and radii must be finite")
    if np.any(radii <= 0):
        raise ValueError("radii must be strictly positive")
    tree = cKDTree(values[:, None])
    counts = tree.query_ball_point(values[:, None], r=radii, p=np.inf, return_length=True)
    return np.asarray(counts, dtype=np.int64) - 1


def ksg_mi_factorial(
    x: np.ndarray, y: np.ndarray, k: int,
    radius_offset: float, count_rule: str,
) -> float:
    """Compute one factorial-cell KSG estimate in bits."""
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    y = np.asarray(y, dtype=np.float64).reshape(-1)
    if x.shape != y.shape:
        raise ValueError("x and y must have the same number of observations")
    n = x.size
    if k < 1 or n < k + 1:
        raise ValueError("require 1 <= k < number of observations")
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError("x and y must contain only finite values")
    if radius_offset < 0 or not np.isfinite(radius_offset):
        raise ValueError("radius_offset must be finite and nonnegative")
    if count_rule not in {"strict", "inclusive"}:
        raise ValueError("count_rule must be strict or inclusive")

    joint = np.column_stack((x, y))
    distances, _ = cKDTree(joint).query(joint, k=k + 1, p=np.inf)
    radii = distances[:, k] + radius_offset
    counter = strict_marginal_counts if count_rule == "strict" else inclusive_marginal_counts
    nx = counter(x, radii)
    ny = counter(y, radii)
    estimate_nats = digamma(k) - np.mean(digamma(nx + 1) + digamma(ny + 1)) + digamma(n)
    return float(estimate_nats / np.log(2.0))


def run_factorial(
    sample_sizes: list[int], ks: list[int], rhos: list[float],
    replicates: int, seed: int, radius_offset: float = 1e-12,
) -> dict:
    if radius_offset <= 0 or not np.isfinite(radius_offset):
        raise ValueError("radius_offset must be finite and positive")
    root_rng = np.random.default_rng(seed)
    rows = []
    for n in sample_sizes:
        for k in ks:
            if k >= n:
                raise ValueError(f"k={k} must be smaller than n={n}")
            for rho in rhos:
                estimates = {name: [] for name in VARIANTS}
                for _ in range(replicates):
                    rng = np.random.default_rng(root_rng.integers(0, 2**63 - 1))
                    x, y = draw_pair(n, rho, rng)
                    for name, offset, rule in (
                        (VARIANTS[0], 0.0, "strict"),
                        (VARIANTS[1], radius_offset, "strict"),
                        (VARIANTS[2], 0.0, "inclusive"),
                        (VARIANTS[3], radius_offset, "inclusive"),
                    ):
                        estimates[name].append(
                            ksg_mi_factorial(x, y, k, offset, rule)
                        )
                truth = gaussian_mi_bits(rho)
                summaries = {}
                arrays = {name: np.asarray(values) for name, values in estimates.items()}
                for name, values in arrays.items():
                    errors = values - truth
                    summaries[name] = {
                        "mean_bits": float(values.mean()),
                        "bias_bits": float(errors.mean()),
                        "rmse_bits": float(np.sqrt(np.mean(errors ** 2))),
                        "sd_bits": float(values.std(ddof=1)),
                    }
                # Paired factorial effects: average over the other factor.
                offset_effect = 0.5 * (
                    (arrays[VARIANTS[1]] - arrays[VARIANTS[0]])
                    + (arrays[VARIANTS[3]] - arrays[VARIANTS[2]])
                )
                count_effect = 0.5 * (
                    (arrays[VARIANTS[2]] - arrays[VARIANTS[0]])
                    + (arrays[VARIANTS[3]] - arrays[VARIANTS[1]])
                )
                interaction = (
                    arrays[VARIANTS[3]] - arrays[VARIANTS[2]]
                    - arrays[VARIANTS[1]] + arrays[VARIANTS[0]]
                )
                rows.append({
                    "sample_size": n, "k": k, "rho": rho,
                    "true_mi_bits": truth, "replicates": replicates,
                    "variants": summaries,
                    "paired_factorial_effects_bits": {
                        "radius_offset_average_effect": float(offset_effect.mean()),
                        "inclusive_count_average_effect": float(count_effect.mean()),
                        "radius_by_count_interaction": float(interaction.mean()),
                    },
                })
    return {
        "study": "factorial_ksg_radius_offset_and_marginal_count_audit",
        "seed": seed, "replicates_per_condition": replicates,
        "sample_sizes": sample_sizes, "k_values": ks, "correlations": rhos,
        "radius_offset": radius_offset,
        "variant_definitions": {
            VARIANTS[0]: "kth joint radius; strict marginal counts",
            VARIANTS[1]: "kth joint radius + configured offset; strict marginal counts",
            VARIANTS[2]: "kth joint radius; inclusive marginal counts",
            VARIANTS[3]: "kth joint radius + configured offset; inclusive marginal counts",
        },
        "interpretation_limits": [
            "Independent bivariate Gaussian controls only.",
            "Factorial contrasts isolate the configured radius offset and marginal count inclusion rule in this implementation.",
            "No spatial or temporal dependence validation is performed.",
            "Historical v3 source and archived results are unchanged.",
            "A positive or negative factorial effect is not a universal correction factor.",
        ],
        "results": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=100)
    parser.add_argument("--sample-sizes", type=int, nargs="+", default=[64, 128, 256, 512, 1200])
    parser.add_argument("--ks", type=int, nargs="+", default=[2, 3, 5, 10])
    parser.add_argument("--rhos", type=float, nargs="+", default=[0.0, 0.2, 0.5, 0.8])
    parser.add_argument("--seed", type=int, default=20261112)
    parser.add_argument("--radius-offset", type=float, default=1e-12)
    parser.add_argument("--output", type=Path, default=Path("ksg_boundary_factorial_audit.json"))
    args = parser.parse_args()
    if args.replicates < 2:
        parser.error("--replicates must be at least 2")
    if any(n < 4 for n in args.sample_sizes):
        parser.error("sample sizes must be at least 4")
    if any(k < 1 for k in args.ks):
        parser.error("k values must be positive")
    if any(not np.isfinite(r) or abs(r) >= 1 for r in args.rhos):
        parser.error("each rho must be finite and have abs(rho) < 1")
    if not np.isfinite(args.radius_offset) or args.radius_offset <= 0:
        parser.error("--radius-offset must be finite and positive")
    result = run_factorial(args.sample_sizes, args.ks, args.rhos,
                           args.replicates, args.seed, args.radius_offset)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"Conditions: {len(result['results'])}; replicates/condition: {args.replicates}")
    print("Factorial boundary audit only; no p-value or sigma conversion.")


if __name__ == "__main__":
    main()
