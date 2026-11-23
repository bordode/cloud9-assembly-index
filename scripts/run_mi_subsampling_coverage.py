#!/usr/bin/env python3
"""Empirical subsampling interval-coverage screening for the raw strict KSG-1 candidate.

Coverage trials are independent outer datasets. Overlapping subsets within an
outer dataset estimate its subsampling-root quantiles; they are not independent
coverage trials. The default configuration is a runtime screen, not validation.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
_CONTROL_PATH = _ROOT / "scripts" / "run_mi_nongaussian_calibration.py"
_SPEC = importlib.util.spec_from_file_location("mi_nongaussian_for_coverage", _CONTROL_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load known-MI controls from {_CONTROL_PATH}")
_CONTROL = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_CONTROL)

draw_control_pair = _CONTROL.draw_control_pair
gaussian_mi_bits = _CONTROL.gaussian_mi_bits
ksg_mi_2d_strict = _CONTROL.ksg_mi_2d_strict

QUANTILE_METHOD = "linear"


def _quantile_diagnostics(subsamples: int, levels: tuple[float, ...]) -> dict:
    """Describe empirical tail resolution using NumPy's linear quantile convention."""
    result = {}
    for level in levels:
        alpha = 1.0 - level
        probs = (alpha / 2.0, 1.0 - alpha / 2.0)
        result[str(int(round(level * 100)))] = {
            "lower_probability": probs[0],
            "upper_probability": probs[1],
            "expected_subsets_per_tail": float(subsamples * alpha / 2.0),
            "lower_linear_order_statistic_position_zero_based": float(probs[0] * (subsamples - 1)),
            "upper_linear_order_statistic_position_zero_based": float(probs[1] * (subsamples - 1)),
        }
    return result


def _intervals(point_estimate: float, roots: np.ndarray, n: int,
               levels: tuple[float, ...]) -> dict[str, tuple[float, float]]:
    """Invert empirical subsampling-root quantiles using linear interpolation."""
    if n <= 0 or not np.isfinite(point_estimate):
        raise ValueError("n must be positive and point_estimate finite")
    if roots.ndim != 1 or roots.size < 1 or not np.all(np.isfinite(roots)):
        raise ValueError("roots must be a non-empty finite one-dimensional array")
    intervals = {}
    for level in levels:
        alpha = 1.0 - level
        lower_root, upper_root = np.quantile(
            roots, [alpha / 2.0, 1.0 - alpha / 2.0], method=QUANTILE_METHOD
        )
        lo = float(point_estimate - upper_root / np.sqrt(n))
        hi = float(point_estimate - lower_root / np.sqrt(n))
        if not (np.isfinite(lo) and np.isfinite(hi) and lo <= hi):
            raise ValueError("constructed interval is non-finite or has reversed endpoints")
        intervals[f"{int(round(level * 100))}"] = (lo, hi)
    return intervals


def _wilson_interval(successes: int, trials: int) -> list[float] | None:
    if trials == 0:
        return None
    z = 1.959963984540054
    p = successes / trials
    denom = 1.0 + z * z / trials
    center = (p + z * z / (2.0 * trials)) / denom
    half = z * np.sqrt(p * (1.0 - p) / trials + z * z / (4.0 * trials * trials)) / denom
    lower = 0.0 if successes == 0 else float(max(0.0, center - half))
    upper = 1.0 if successes == trials else float(min(1.0, center + half))
    return [lower, upper]


def _summarize(hits: list[bool], widths: list[float]) -> dict:
    count = len(hits)
    successes = int(sum(hits))
    coverage = float(successes / count) if count else None
    mc_se = (
        float(np.sqrt(coverage * (1.0 - coverage) / count))
        if count and coverage is not None else None
    )
    return {
        "valid_outer_datasets": count,
        "coverage_successes": successes,
        "empirical_coverage": coverage,
        "coverage_monte_carlo_se_plugin": mc_se,
        "coverage_wilson_95pct_interval": _wilson_interval(successes, count),
        "mean_interval_width_bits": float(np.mean(widths)) if widths else None,
        "median_interval_width_bits": float(np.median(widths)) if widths else None,
    }


def run_coverage(sample_sizes: list[int], ks: list[int], rhos: list[float],
                 families: list[str], b_exponents: list[float],
                 outer_replicates: int, subsamples: int, seed: int) -> dict:
    if outer_replicates < 2:
        raise ValueError("outer_replicates must be at least 2")
    if subsamples < 20:
        raise ValueError("subsamples must be at least 20 for even a coarse tail diagnostic")
    if not sample_sizes or any(n < 4 for n in sample_sizes):
        raise ValueError("sample_sizes must be non-empty and each n must be at least 4")
    if not ks or any(k < 1 for k in ks):
        raise ValueError("ks must be non-empty and positive")
    if not rhos or any(not np.isfinite(rho) or abs(rho) >= 1 for rho in rhos):
        raise ValueError("rhos must be non-empty, finite, and have abs(rho) < 1")
    if not b_exponents or any(not (0.0 < exponent < 1.0) for exponent in b_exponents):
        raise ValueError("each b exponent must be between 0 and 1")
    allowed = {"monotone_nonlinear", "uniform_gaussian_copula"}
    if len(set(families)) != len(families) or not families or any(f not in allowed for f in families):
        raise ValueError(f"families must be unique members of {sorted(allowed)}")
    if len(set(sample_sizes)) != len(sample_sizes) or len(set(ks)) != len(ks):
        raise ValueError("sample_sizes and ks must not contain duplicates")

    root_rng = np.random.default_rng(seed)
    results = []
    levels = (0.90, 0.95)
    for family in families:
        for n in sample_sizes:
            for k in ks:
                if k >= n:
                    raise ValueError(f"require 1 <= k < n; received k={k}, n={n}")
                for rho in rhos:
                    truth = float(gaussian_mi_bits(rho))
                    for exponent in b_exponents:
                        b = int(np.floor(n ** exponent))
                        if b <= k + 1:
                            raise ValueError(f"subsample size b={b} must exceed k+1={k + 1}")
                        raw_hits = {str(int(level * 100)): [] for level in levels}
                        clipped_hits = {str(int(level * 100)): [] for level in levels}
                        raw_widths = {str(int(level * 100)): [] for level in levels}
                        clipped_widths = {str(int(level * 100)): [] for level in levels}
                        valid_full_estimates = []
                        outer_records = []
                        construction_failures = 0

                        for outer_index in range(outer_replicates):
                            outer_seed = int(root_rng.integers(0, 2**63 - 1))
                            outer_rng = np.random.default_rng(outer_seed)
                            record = {
                                "outer_replicate_index": outer_index,
                                "outer_dataset_seed": outer_seed,
                                "status": "pending",
                            }
                            try:
                                x, y = draw_control_pair(n, rho, family, outer_rng)
                                theta_n = float(ksg_mi_2d_strict(x, y, k=k))
                                record["full_sample_raw_estimate_bits"] = theta_n
                                if not np.isfinite(theta_n):
                                    raise ValueError("non-finite full-sample estimate")
                                clipped_theta_n = max(theta_n, 0.0)
                                raw_roots = np.empty(subsamples, dtype=float)
                                clipped_roots = np.empty(subsamples, dtype=float)
                                for j in range(subsamples):
                                    indices = outer_rng.choice(n, size=b, replace=False)
                                    theta_b = float(ksg_mi_2d_strict(x[indices], y[indices], k=k))
                                    if not np.isfinite(theta_b):
                                        raise ValueError(f"non-finite subset estimate at subset index {j}")
                                    clipped_b = max(theta_b, 0.0)
                                    raw_roots[j] = np.sqrt(b) * (theta_b - theta_n)
                                    clipped_roots[j] = np.sqrt(b) * (clipped_b - clipped_theta_n)
                                if not (np.all(np.isfinite(raw_roots)) and np.all(np.isfinite(clipped_roots))):
                                    raise ValueError("non-finite subsampling roots")

                                raw_intervals = _intervals(theta_n, raw_roots, n, levels)
                                clipped_intervals = _intervals(clipped_theta_n, clipped_roots, n, levels)
                                record["raw_strict_intervals_bits"] = {}
                                record["zero_clipped_diagnostic_intervals_bits"] = {}
                                record["raw_strict_coverage"] = {}
                                record["zero_clipped_diagnostic_coverage"] = {}
                                for level in levels:
                                    key = str(int(level * 100))
                                    lo, hi = raw_intervals[key]
                                    clo, chi = clipped_intervals[key]
                                    raw_hit = bool(lo <= truth <= hi)
                                    clipped_hit = bool(clo <= truth <= chi)
                                    raw_hits[key].append(raw_hit)
                                    clipped_hits[key].append(clipped_hit)
                                    raw_widths[key].append(float(hi - lo))
                                    clipped_widths[key].append(float(chi - clo))
                                    record["raw_strict_intervals_bits"][key] = [lo, hi]
                                    record["zero_clipped_diagnostic_intervals_bits"][key] = [clo, chi]
                                    record["raw_strict_coverage"][key] = raw_hit
                                    record["zero_clipped_diagnostic_coverage"][key] = clipped_hit
                                record["status"] = "valid"
                                valid_full_estimates.append(theta_n)
                            except (ValueError, FloatingPointError, OverflowError) as exc:
                                construction_failures += 1
                                record["status"] = "failed"
                                record["failure_reason"] = str(exc)
                            outer_records.append(record)

                        raw_summary = {key: _summarize(raw_hits[key], raw_widths[key]) for key in raw_hits}
                        clipped_summary = {
                            key: _summarize(clipped_hits[key], clipped_widths[key])
                            for key in clipped_hits
                        }
                        results.append({
                            "family": family,
                            "sample_size_n": n,
                            "k": k,
                            "rho": rho,
                            "true_mi_bits": truth,
                            "subsample_exponent": exponent,
                            "subsample_size_b": b,
                            "outer_replicates_requested": outer_replicates,
                            "valid_outer_datasets": len(valid_full_estimates),
                            "subsamples_per_outer_dataset": subsamples,
                            "outer_dataset_mean_raw_estimate_bits_valid_only": (
                                float(np.mean(valid_full_estimates)) if valid_full_estimates else None
                            ),
                            "outer_dataset_mean_raw_bias_bits_valid_only": (
                                float(np.mean(valid_full_estimates) - truth) if valid_full_estimates else None
                            ),
                            "interval_construction_failures": construction_failures,
                            "raw_strict_primary": raw_summary,
                            "zero_clipped_diagnostic_only": clipped_summary,
                            "outer_dataset_diagnostics": outer_records,
                        })

    return {
        "study": "empirical_subsampling_interval_coverage_screening_pilot",
        "method": (
            "For each independent outer dataset, form roots sqrt(b)*(theta_b-theta_n) "
            "from B subsets drawn without replacement; invert empirical root quantiles "
            "using sqrt(n). Coverage trials are independent outer datasets only."
        ),
        "seed": seed,
        "outer_replicates_per_condition": outer_replicates,
        "subsamples_per_outer_dataset": subsamples,
        "nominal_levels": [0.90, 0.95],
        "quantile_method": QUANTILE_METHOD,
        "quantile_diagnostics_by_level": _quantile_diagnostics(subsamples, levels),
        "families": families,
        "sample_sizes": sample_sizes,
        "k_values": ks,
        "correlations": rhos,
        "subsample_exponents": b_exponents,
        "interpretation_limits": [
            "This is a screening pilot; it does not validate nominal coverage.",
            "The Monte Carlo standard error and Wilson interval use valid independent outer datasets, not overlapping subsets.",
            "Per-outer-dataset records preserve seeds, interval endpoints, coverage flags, and failures.",
            "Clipped intervals are diagnostic only, especially at the rho=0 boundary.",
            "Independent observations only; no spatial or temporal dependence is tested.",
            "The result applies only to the specified transformed-Gaussian families and strict KSG candidate.",
            "Historical v3 code and archived outputs are not modified.",
        ],
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-sizes", type=int, nargs="+", default=[256])
    parser.add_argument("--ks", type=int, nargs="+", default=[3])
    parser.add_argument("--rhos", type=float, nargs="+", default=[0.0, 0.5])
    parser.add_argument("--families", nargs="+",
                        default=["monotone_nonlinear", "uniform_gaussian_copula"])
    parser.add_argument("--b-exponents", type=float, nargs="+", default=[0.8])
    parser.add_argument("--outer-replicates", type=int, default=10,
                        help="screening default; preregistered pilot specifies 100")
    parser.add_argument("--subsamples", type=int, default=20,
                        help="screening default; preregistered pilot specifies 200")
    parser.add_argument("--seed", type=int, default=20261113)
    parser.add_argument("--output", type=Path, default=Path("mi_subsampling_coverage_screening.json"))
    args = parser.parse_args()
    allowed = {"monotone_nonlinear", "uniform_gaussian_copula"}
    if any(family not in allowed for family in args.families):
        parser.error(f"--families must be selected from {sorted(allowed)}")
    if any(not np.isfinite(rho) or abs(rho) >= 1 for rho in args.rhos):
        parser.error("each rho must be finite and have abs(rho) < 1")
    if args.outer_replicates < 2 or args.subsamples < 20:
        parser.error("require at least 2 outer replicates and 20 subsamples")

    result = run_coverage(
        args.sample_sizes, args.ks, args.rhos, args.families,
        args.b_exponents, args.outer_replicates, args.subsamples, args.seed
    )
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"Conditions: {len(result['results'])}; outer datasets/condition: {args.outer_replicates}")
    print(f"Subsets/outer dataset: {args.subsamples}; screening does not validate coverage.")


if __name__ == "__main__":
    main()
