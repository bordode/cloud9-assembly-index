#!/usr/bin/env python3
"""Known-MI calibration for the repository's two-variable KSG-1 estimator.

This is a diagnostic harness, not a cosmological analysis. It deliberately
reports both raw and zero-clipped estimates; it does not turn estimates into
p-values or Gaussian sigma scores.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree
from scipy.special import digamma


def gaussian_mi_bits(rho: float) -> float:
    """Exact MI (bits) for a standard bivariate Gaussian with correlation rho."""
    if not np.isfinite(rho) or abs(rho) >= 1:
        raise ValueError("rho must be finite and satisfy abs(rho) < 1")
    return float(-0.5 * np.log2(1.0 - rho * rho))


def ksg_mi_2d_raw(x: np.ndarray, y: np.ndarray, k: int = 3) -> float:
    """Return the unclipped KSG-1 estimate in bits, using the max norm."""
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
    eps = np.nextafter(distances[:, k], 0.0)
    tx, ty = cKDTree(x[:, None]), cKDTree(y[:, None])
    nx = np.fromiter(
        (tx.query_ball_point([x[i]], r=eps[i], p=np.inf, return_length=True) - 1
         for i in range(n)), dtype=np.int64, count=n
    )
    ny = np.fromiter(
        (ty.query_ball_point([y[i]], r=eps[i], p=np.inf, return_length=True) - 1
         for i in range(n)), dtype=np.int64, count=n
    )
    estimate_nats = digamma(k) - np.mean(digamma(nx + 1) + digamma(ny + 1)) + digamma(n)
    return float(estimate_nats / np.log(2.0))


def draw_pair(n: int, rho: float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    x = rng.standard_normal(n)
    z = rng.standard_normal(n)
    y = rho * x + np.sqrt(1.0 - rho * rho) * z
    return x, y


def bootstrap_mean_interval(values: np.ndarray, rng: np.random.Generator,
                            draws: int = 2000) -> list[float]:
    """Percentile bootstrap interval over independent replicate estimates."""
    values = np.asarray(values, dtype=float)
    if values.size < 2:
        return [float("nan"), float("nan")]
    indices = rng.integers(0, values.size, size=(draws, values.size))
    means = values[indices].mean(axis=1)
    lo, hi = np.quantile(means, [0.025, 0.975])
    return [float(lo), float(hi)]


def summarize(estimates: list[float], truth: float, rng: np.random.Generator) -> dict:
    raw = np.asarray(estimates, dtype=float)
    clipped = np.maximum(raw, 0.0)
    error = raw - truth
    return {
        "replicates": int(raw.size),
        "true_mi_bits": float(truth),
        "raw_mean_bits": float(raw.mean()),
        "raw_median_bits": float(np.median(raw)),
        "raw_bias_bits": float(error.mean()),
        "raw_bias_bootstrap_95pct_ci_bits": bootstrap_mean_interval(error, rng),
        "raw_rmse_bits": float(np.sqrt(np.mean(error ** 2))),
        "raw_sd_bits": float(raw.std(ddof=1)) if raw.size > 1 else 0.0,
        "raw_median_absolute_error_bits": float(np.median(np.abs(error))),
        "raw_fraction_below_zero": float(np.mean(raw < 0.0)),
        "clipped_mean_bits": float(clipped.mean()),
        "clipped_bias_bits": float(np.mean(clipped - truth)),
        "clipped_fraction_equal_zero": float(np.mean(clipped == 0.0)),
        "empirical_raw_2_5_97_5_interval_bits": [
            float(v) for v in np.quantile(raw, [0.025, 0.975])
        ],
    }


def run_calibration(sample_sizes: list[int], ks: list[int], rhos: list[float],
                    replicates: int, seed: int) -> dict:
    root_rng = np.random.default_rng(seed)
    results = []
    for n in sample_sizes:
        for k in ks:
            if k >= n:
                raise ValueError(f"k={k} must be smaller than n={n}")
            for rho in rhos:
                estimates = []
                for _ in range(replicates):
                    # Independent child streams make each replicate reproducible.
                    rng = np.random.default_rng(root_rng.integers(0, 2**63 - 1))
                    x, y = draw_pair(n, rho, rng)
                    estimates.append(ksg_mi_2d_raw(x, y, k=k))
                truth = gaussian_mi_bits(rho)
                results.append({
                    "sample_size": n,
                    "k": k,
                    "rho": rho,
                    "condition": "independent_gaussian" if rho == 0 else "correlated_gaussian",
                    **summarize(estimates, truth, root_rng),
                })
    return {
        "study": "known_mi_gaussian_ksg_calibration",
        "estimator": "KSG-1, max-norm joint neighbourhood, raw and zero-clipped summaries",
        "units": "bits",
        "seed": seed,
        "replicates_per_condition": replicates,
        "sample_sizes": sample_sizes,
        "k_values": ks,
        "correlations": rhos,
        "confidence_interval_note": (
            "Bootstrap interval is for mean estimator bias across independent "
            "replicates; empirical estimate interval is descriptive, not a "
            "confidence interval for an individual estimate."
        ),
        "limitations": [
            "Independent observations only; no spatial or temporal dependence.",
            "Bivariate Gaussian controls only; nonlinear known-MI controls are not included.",
            "Finite-replicate summaries are calibration diagnostics, not p-values.",
            "This harness does not modify or replace the historical v3 estimator.",
        ],
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=100)
    parser.add_argument("--sample-sizes", type=int, nargs="+", default=[64, 128, 256, 512, 1200])
    parser.add_argument("--ks", type=int, nargs="+", default=[2, 3, 5, 10])
    parser.add_argument("--rhos", type=float, nargs="+", default=[0.0, 0.2, 0.5, 0.8])
    parser.add_argument("--seed", type=int, default=20261109)
    parser.add_argument("--output", type=Path, default=Path("mi_estimator_calibration.json"))
    args = parser.parse_args()
    if args.replicates < 2:
        parser.error("--replicates must be at least 2")
    if any(n < 4 for n in args.sample_sizes):
        parser.error("sample sizes must be at least 4")
    if any(k < 1 for k in args.ks):
        parser.error("k values must be positive")
    if any(not np.isfinite(r) or abs(r) >= 1 for r in args.rhos):
        parser.error("each rho must be finite and have abs(rho) < 1")

    result = run_calibration(args.sample_sizes, args.ks, args.rhos,
                             args.replicates, args.seed)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"Conditions: {len(result['results'])}; replicates/condition: {args.replicates}")
    print("No p-value or sigma conversion is performed.")


if __name__ == "__main__":
    main()
