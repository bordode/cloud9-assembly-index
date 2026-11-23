#!/usr/bin/env python3
"""Known-MI calibration under nonlinear bijections and non-Gaussian marginals.

Each control starts from a bivariate Gaussian pair and applies strictly
monotone, invertible transformations separately to its coordinates. Population
mutual information is therefore unchanged exactly, while the observed
marginals and coordinate geometry change. This is a controlled stress test,
not a cosmological analysis.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
from scipy.special import ndtr

_ROOT = Path(__file__).resolve().parents[1]
_CALIBRATION_PATH = _ROOT / "scripts" / "run_mi_estimator_calibration.py"
_CALIBRATION_SPEC = importlib.util.spec_from_file_location(
    "mi_calibration_for_nongaussian", _CALIBRATION_PATH
)
if _CALIBRATION_SPEC is None or _CALIBRATION_SPEC.loader is None:
    raise ImportError(f"cannot load calibration module from {_CALIBRATION_PATH}")
_CALIBRATION = importlib.util.module_from_spec(_CALIBRATION_SPEC)
_CALIBRATION_SPEC.loader.exec_module(_CALIBRATION)

_AUDIT_PATH = _ROOT / "scripts" / "audit_ksg_boundary_conventions.py"
_AUDIT_SPEC = importlib.util.spec_from_file_location(
    "ksg_boundary_for_nongaussian", _AUDIT_PATH
)
if _AUDIT_SPEC is None or _AUDIT_SPEC.loader is None:
    raise ImportError(f"cannot load boundary audit module from {_AUDIT_PATH}")
_AUDIT = importlib.util.module_from_spec(_AUDIT_SPEC)
_AUDIT_SPEC.loader.exec_module(_AUDIT)

gaussian_mi_bits = _CALIBRATION.gaussian_mi_bits
summarize = _CALIBRATION.summarize
ksg_mi_2d_strict = _AUDIT.ksg_mi_2d_strict


def draw_control_pair(
    n: int, rho: float, family: str, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    """Draw a pair with exactly known MI under an invertible coordinate map."""
    gx, gy = _CALIBRATION.draw_pair(n, rho, rng)
    if family == "monotone_nonlinear":
        # Both maps are strictly increasing and invertible:
        # x = sinh(0.5*gx), y = exp(0.25*gy).
        x = np.sinh(0.5 * gx)
        y = np.exp(0.25 * gy)
    elif family == "uniform_gaussian_copula":
        # The normal CDF maps each Gaussian marginal to Uniform(0,1).
        # The Gaussian copula retains the same population MI.
        x = ndtr(gx)
        y = ndtr(gy)
    else:
        raise ValueError(f"unknown control family: {family}")
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError("transformed samples must remain finite")
    return x, y


def run_calibration(
    sample_sizes: list[int],
    ks: list[int],
    rhos: list[float],
    families: list[str],
    replicates: int,
    seed: int,
) -> dict:
    root_rng = np.random.default_rng(seed)
    rows = []
    for family in families:
        for n in sample_sizes:
            for k in ks:
                if k >= n:
                    raise ValueError(f"k={k} must be smaller than n={n}")
                for rho in rhos:
                    estimates = []
                    for _ in range(replicates):
                        rng = np.random.default_rng(
                            root_rng.integers(0, 2**63 - 1)
                        )
                        x, y = draw_control_pair(n, rho, family, rng)
                        estimates.append(ksg_mi_2d_strict(x, y, k=k))
                    truth = gaussian_mi_bits(rho)
                    rows.append({
                        "family": family,
                        "sample_size": n,
                        "k": k,
                        "rho": rho,
                        "replicates": replicates,
                        "estimator": "strict KSG-1 candidate; uninflated max-norm radius",
                        **summarize(estimates, truth, root_rng),
                    })
    return {
        "study": "known_mi_nonlinear_and_non_gaussian_ksg_calibration",
        "estimator": "strict KSG-1 candidate; uninflated max-norm radius and strict marginal counts",
        "units": "bits",
        "seed": seed,
        "replicates_per_condition": replicates,
        "sample_sizes": sample_sizes,
        "k_values": ks,
        "correlations": rhos,
        "families": families,
        "known_information_basis": (
            "Each sample pair is generated from a bivariate Gaussian with "
            "known MI and transformed by strictly monotone bijections. "
            "Population MI is invariant under these coordinate-wise "
            "invertible transformations."
        ),
        "limitations": [
            "Independent observations only; no spatial or temporal dependence.",
            "The controls test two specified transformed-Gaussian families, not all non-Gaussian distributions.",
            "The strict KSG-1 candidate is not thereby established as universally optimal or unbiased.",
            "The historical v3 estimator and archived outputs are not modified.",
            "Replicate summaries are calibration diagnostics, not p-values or sigma scores."
        ],
        "results": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=100)
    parser.add_argument("--sample-sizes", type=int, nargs="+",
                        default=[64, 128, 256, 512, 1200])
    parser.add_argument("--ks", type=int, nargs="+", default=[2, 3, 5, 10])
    parser.add_argument("--rhos", type=float, nargs="+",
                        default=[0.0, 0.2, 0.5, 0.8])
    parser.add_argument("--families", nargs="+",
                        default=["monotone_nonlinear", "uniform_gaussian_copula"])
    parser.add_argument("--seed", type=int, default=20261111)
    parser.add_argument("--output", type=Path,
                        default=Path("mi_nongaussian_calibration.json"))
    args = parser.parse_args()
    if args.replicates < 2:
        parser.error("--replicates must be at least 2")
    if any(n < 4 for n in args.sample_sizes):
        parser.error("sample sizes must be at least 4")
    if any(k < 1 for k in args.ks):
        parser.error("k values must be positive")
    if any(not np.isfinite(r) or abs(r) >= 1 for r in args.rhos):
        parser.error("each rho must be finite and have abs(rho) < 1")
    allowed = {"monotone_nonlinear", "uniform_gaussian_copula"}
    if not args.families or any(f not in allowed for f in args.families):
        parser.error(f"--families must be selected from {sorted(allowed)}")

    result = run_calibration(
        args.sample_sizes, args.ks, args.rhos, args.families,
        args.replicates, args.seed
    )
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"Conditions: {len(result['results'])}; replicates/condition: {args.replicates}")
    print("No p-value or sigma conversion is performed.")


if __name__ == "__main__":
    main()
