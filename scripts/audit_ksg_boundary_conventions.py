#!/usr/bin/env python3
"""Paired audit of legacy-inclusive and strict-boundary KSG-1 conventions.

The legacy estimator is imported unchanged from the calibration harness. The
strict estimator uses the kth joint max-norm radius without inflation and
counts marginal neighbours strictly inside that radius. Both estimators see
the exact same Gaussian samples in every replicate.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree
from scipy.special import digamma

_LEGACY_PATH = Path(__file__).with_name("run_mi_estimator_calibration.py")
_LEGACY_SPEC = importlib.util.spec_from_file_location("mi_calibration_legacy", _LEGACY_PATH)
if _LEGACY_SPEC is None or _LEGACY_SPEC.loader is None:
    raise ImportError(f"cannot load legacy calibration module from {_LEGACY_PATH}")
_LEGACY = importlib.util.module_from_spec(_LEGACY_SPEC)
_LEGACY_SPEC.loader.exec_module(_LEGACY)

draw_pair = _LEGACY.draw_pair
gaussian_mi_bits = _LEGACY.gaussian_mi_bits
legacy_inclusive_estimator = _LEGACY.ksg_mi_2d_raw


def strict_marginal_counts(values: np.ndarray, radii: np.ndarray) -> np.ndarray:
    """Count other observations with absolute distance strictly below radius."""
    values = np.asarray(values, dtype=np.float64).reshape(-1)
    radii = np.asarray(radii, dtype=np.float64).reshape(-1)
    if values.size != radii.size:
        raise ValueError("values and radii must have the same length")
    if not np.all(np.isfinite(values)) or not np.all(np.isfinite(radii)):
        raise ValueError("values and radii must be finite")
    if np.any(radii <= 0):
        raise ValueError("radii must be strictly positive; tied zero-radius neighbours need an explicit tie policy")

    tree = cKDTree(values[:, None])
    candidates = tree.query_ball_point(values[:, None], r=radii, p=np.inf)
    return np.fromiter(
        (np.count_nonzero(np.abs(values[idx] - values[i]) < radii[i]) - 1
         for i, idx in enumerate(candidates)),
        dtype=np.int64,
        count=values.size,
    )


def ksg_mi_2d_strict(x: np.ndarray, y: np.ndarray, k: int = 3) -> float:
    """KSG-1 estimate in bits with strict marginal-radius counts."""
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    y = np.asarray(y, dtype=np.float64).reshape(-1)
    if x.shape != y.shape:
        raise ValueError("x and y must have the same number of observations")
    n = x.size
    if k < 1 or n < k + 1:
        raise ValueError("require 1 <= k < number of observations")
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError("x and y must contain only finite values")

    joint = np.column_stack((x, y))
    distances, _ = cKDTree(joint).query(joint, k=k + 1, p=np.inf)
    eps = distances[:, k]
    nx = strict_marginal_counts(x, eps)
    ny = strict_marginal_counts(y, eps)
    estimate_nats = (
        digamma(k) - np.mean(digamma(nx + 1) + digamma(ny + 1)) + digamma(n)
    )
    return float(estimate_nats / np.log(2.0))


def run_comparison(sample_sizes: list[int], ks: list[int], rhos: list[float],
                   replicates: int, seed: int) -> dict:
    root_rng = np.random.default_rng(seed)
    rows = []
    for n in sample_sizes:
        for k in ks:
            if k >= n:
                raise ValueError(f"k={k} must be smaller than n={n}")
            for rho in rhos:
                legacy_values, strict_values = [], []
                for _ in range(replicates):
                    rng = np.random.default_rng(root_rng.integers(0, 2**63 - 1))
                    x, y = draw_pair(n, rho, rng)
                    legacy_values.append(legacy_inclusive_estimator(x, y, k=k))
                    strict_values.append(ksg_mi_2d_strict(x, y, k=k))
                truth = gaussian_mi_bits(rho)
                legacy = np.asarray(legacy_values)
                strict = np.asarray(strict_values)
                rows.append({
                    "sample_size": n,
                    "k": k,
                    "rho": rho,
                    "true_mi_bits": truth,
                    "replicates": replicates,
                    "legacy_inclusive_mean_bits": float(legacy.mean()),
                    "legacy_inclusive_bias_bits": float((legacy - truth).mean()),
                    "legacy_inclusive_rmse_bits": float(np.sqrt(np.mean((legacy - truth) ** 2))),
                    "strict_mean_bits": float(strict.mean()),
                    "strict_bias_bits": float((strict - truth).mean()),
                    "strict_rmse_bits": float(np.sqrt(np.mean((strict - truth) ** 2))),
                    "paired_strict_minus_legacy_mean_bits": float(np.mean(strict - legacy)),
                    "paired_difference_sd_bits": float(np.std(strict - legacy, ddof=1))
                    if replicates > 1 else 0.0,
                })
    return {
        "study": "paired_ksg_boundary_convention_audit",
        "seed": seed,
        "replicates_per_condition": replicates,
        "sample_sizes": sample_sizes,
        "k_values": ks,
        "correlations": rhos,
        "legacy_convention": (
            "Historical harness/v3: kth joint radius + 1e-12; inclusive "
            "marginal query_ball_point counts."
        ),
        "strict_convention": (
            "KSG-1 strict marginal counts: uninflated kth joint max-norm "
            "radius; count marginal distances strictly less than radius."
        ),
        "interpretation_limits": [
            "This isolates a boundary-convention difference on independent bivariate Gaussian controls.",
            "It does not validate spatial or temporal dependence assumptions.",
            "It does not alter the historical v3 estimator or its archived outputs.",
            "Do not apply a correction factor to historical A_c values from this comparison.",
        ],
        "results": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=100)
    parser.add_argument("--sample-sizes", type=int, nargs="+",
                        default=[64, 128, 256, 512, 1200])
    parser.add_argument("--ks", type=int, nargs="+", default=[2, 3, 5, 10])
    parser.add_argument("--rhos", type=float, nargs="+", default=[0.0, 0.2, 0.5, 0.8])
    parser.add_argument("--seed", type=int, default=20261110)
    parser.add_argument("--output", type=Path,
                        default=Path("ksg_boundary_convention_audit.json"))
    args = parser.parse_args()
    if args.replicates < 2:
        parser.error("--replicates must be at least 2")
    if any(n < 4 for n in args.sample_sizes):
        parser.error("sample sizes must be at least 4")
    if any(k < 1 for k in args.ks):
        parser.error("k values must be positive")
    if any(not np.isfinite(r) or abs(r) >= 1 for r in args.rhos):
        parser.error("each rho must be finite and have abs(rho) < 1")

    result = run_comparison(args.sample_sizes, args.ks, args.rhos,
                            args.replicates, args.seed)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"Conditions: {len(result['results'])}; replicates/condition: {args.replicates}")
    print("Paired boundary-convention comparison only; no p-value or sigma conversion.")


if __name__ == "__main__":
    main()
