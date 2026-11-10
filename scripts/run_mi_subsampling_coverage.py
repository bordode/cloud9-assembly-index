#!/usr/bin/env python3
"""Empirical subsampling interval-coverage pilot for the raw strict KSG-1 candidate.

Coverage is evaluated across independent outer datasets. Subsets within an
outer dataset are used only to estimate its subsampling-root quantiles; they
are not independent coverage trials.
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


def _intervals(point_estimate: float, roots: np.ndarray, n: int,
               levels: tuple[float, ...]) -> dict[str, tuple[float, float]]:
    """Invert empirical subsampling-root quantiles for each nominal level."""
    intervals = {}
    for level in levels:
        alpha = 1.0 - level
        lower_root, upper_root = np.quantile(roots, [alpha / 2.0, 1.0 - alpha / 2.0])
        intervals[f"{int(round(level * 100))}"] = (
            float(point_estimate - upper_root / np.sqrt(n)),
            float(point_estimate - lower_root / np.sqrt(n)),
        )
    return intervals


def run_coverage(sample_sizes: list[int], ks: list[int], rhos: list[float],
                 families: list[str], b_exponents: list[float],
                 outer_replicates: int, subsamples: int, seed: int) -> dict:
    if outer_replicates < 2:
        raise ValueError("outer_replicates must be at least 2")
    if subsamples < 20:
        raise ValueError("subsamples must be at least 20 for even a coarse tail diagnostic")
    if any(not (0.0 < exponent < 1.0) for exponent in b_exponents):
        raise ValueError("each b exponent must be between 0 and 1")
    if len(set(families)) != len(families) or not families:
        raise ValueError("families must be non-empty and unique")

    root_rng = np.random.default_rng(seed)
    results = []
    levels = (0.90, 0.95)
    for family in families:
        for n in sample_sizes:
            for k in ks:
                if k < 1 or k >= n:
                    raise ValueError(f"require 1 <= k < n; received k={k}, n={n}")
                for rho in rhos:
                    truth = gaussian_mi_bits(rho)
                    for exponent in b_exponents:
                        b = int(np.floor(n ** exponent))
                        if b <= k + 1:
                            raise ValueError(
                                f"subsample size b={b} must exceed k+1={k + 1}"
                            )
                        raw_hits = {str(int(level * 100)): [] for level in levels}
                        clipped_hits = {str(int(level * 100)): [] for level in levels}
                        raw_widths = {str(int(level * 100)): [] for level in levels}
                        clipped_widths = {str(int(level * 100)): [] for level in levels}
                        full_estimates = []
                        construction_failures = 0

                        for _ in range(outer_replicates):
                            outer_rng = np.random.default_rng(
                                root_rng.integers(0, 2**63 - 1)
                            )
                            x, y = draw_control_pair(n, rho, family, outer_rng)
                            theta_n = ksg_mi_2d_strict(x, y, k=k)
                            full_estimates.append(theta_n)
                            clipped_theta_n = max(theta_n, 0.0)
                            raw_roots = np.empty(subsamples, dtype=float)
                            clipped_roots = np.empty(subsamples, dtype=float)

                            for j in range(subsamples):
                                indices = outer_rng.choice(n, size=b, replace=False)
                                theta_b = ksg_mi_2d_strict(x[indices], y[indices], k=k)
                                raw_roots[j] = np.sqrt(b) * (theta_b - theta_n)
                                clipped_roots[j] = np.sqrt(b) * (
                                    max(theta_b, 0.0) - clipped_theta_n
                                )

                            if not np.all(np.isfinite(raw_roots)):
                                construction_failures += 1
                                continue
                            raw_intervals = _intervals(theta_n, raw_roots, n, levels)
                            clipped_intervals = _intervals(
                                clipped_theta_n, clipped_roots, n, levels
                            )
                            for level in levels:
                                key = str(int(level * 100))
                                lo, hi = raw_intervals[key]
                                clo, chi = clipped_intervals[key]
                                raw_hits[key].append(bool(lo <= truth <= hi))
                                clipped_hits[key].append(bool(clo <= truth <= chi))
                                raw_widths[key].append(float(hi - lo))
                                clipped_widths[key].append(float(chi - clo))

                        def summarize(hits: list[bool], widths: list[float]) -> dict:
                            count = len(hits)
                            coverage = float(np.mean(hits)) if count else None
                            mc_se = (
                                float(np.sqrt(coverage * (1.0 - coverage) / count))
                                if count and coverage is not None else None
                            )
                            return {
                                "valid_outer_datasets": count,
                                "empirical_coverage": coverage,
                                "coverage_monte_carlo_se": mc_se,
                                "mean_interval_width_bits": (
                                    float(np.mean(widths)) if widths else None
                                ),
                                "median_interval_width_bits": (
                                    float(np.median(widths)) if widths else None
                                ),
                            }

                        raw_summary = {
                            key: summarize(raw_hits[key], raw_widths[key])
                            for key in raw_hits
                        }
                        clipped_summary = {
                            key: summarize(clipped_hits[key], clipped_widths[key])
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
                            "subsamples_per_outer_dataset": subsamples,
                            "outer_dataset_mean_raw_estimate_bits": float(np.mean(full_estimates)),
                            "outer_dataset_mean_raw_bias_bits": float(np.mean(full_estimates) - truth),
                            "interval_construction_failures": construction_failures,
                            "raw_strict_primary": raw_summary,
                            "zero_clipped_diagnostic_only": clipped_summary,
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
        "families": families,
        "sample_sizes": sample_sizes,
        "k_values": ks,
        "correlations": rhos,
        "subsample_exponents": b_exponents,
        "subsample_quantile_resolution_note": (
            "With B subsets, each two-sided tail is estimated from approximately "
            "B*alpha/2 observations; small B makes tail quantiles coarse."
        ),
        "interpretation_limits": [
            "This is a screening pilot; it does not validate nominal coverage.",
            "The Monte Carlo standard error uses independent outer datasets, not overlapping subsets.",
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
                        help="screening default; use 100 for the preregistered pilot")
    parser.add_argument("--subsamples", type=int, default=20,
                        help="screening default; use 200 or more for the preregistered pilot")
    parser.add_argument("--seed", type=int, default=20261113)
    parser.add_argument("--output", type=Path,
                        default=Path("mi_subsampling_coverage_screening.json"))
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
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"Conditions: {len(result['results'])}; outer datasets/condition: {args.outer_replicates}")
    print(f"Subsets/outer dataset: {args.subsamples}; this screening run does not validate coverage.")


if __name__ == "__main__":
    main()
