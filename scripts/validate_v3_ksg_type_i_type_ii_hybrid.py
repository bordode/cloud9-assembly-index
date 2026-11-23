"""Compare complete KSG Algorithm 1, Algorithm 2, and recovered hybrid conventions.

The recovered historical source is imported read-only and never modified.
This diagnostic makes the boundary/count convention and formula explicit.
"""
import json
from pathlib import Path

import numpy as np
import scipy
from scipy.spatial import cKDTree
from scipy.special import digamma

from research.validation.recovered_cloud9_null_ensemble_v3_corrected import ksg_mi_2d

SAMPLE_SIZES = (1200, 3000)
REPLICATES = 20
K = 3
BASE_SEED = 20261117


def counts(x, y, radius_mode):
    n = len(x)
    joint = np.column_stack([x, y])
    distances, _ = cKDTree(joint).query(joint, k=K + 1, p=np.inf)
    kth = distances[:, K]
    if radius_mode == "strict":
        radii = np.nextafter(kth, -np.inf)
    elif radius_mode == "inclusive":
        radii = kth
    elif radius_mode == "historical_inclusive_epsilon":
        radii = kth + 1e-12
    else:
        raise ValueError(radius_mode)

    tx = cKDTree(np.asarray(x).reshape(-1, 1))
    ty = cKDTree(np.asarray(y).reshape(-1, 1))
    nx = np.asarray([
        tx.query_ball_point([x[i]], r=radii[i], p=np.inf, return_length=True)
        for i in range(n)
    ], dtype=int)
    ny = np.asarray([
        ty.query_ball_point([y[i]], r=radii[i], p=np.inf, return_length=True)
        for i in range(n)
    ], dtype=int)
    return nx, ny


def estimate(x, y, variant):
    n = len(x)
    if variant == "ksg_type_i":
        # Algorithm 1: strict marginal counts exclude self; use psi(n_x+1).
        nx, ny = counts(x, y, "strict")
        value_nats = digamma(K) + digamma(n) - np.mean(digamma(nx) + digamma(ny))
        # nx,ny here include no self; psi(nx) would be wrong for Type I.
        # Re-express the strict counts explicitly as neighbour counts excluding self.
        value_nats = digamma(K) + digamma(n) - np.mean(
            digamma(nx) + digamma(ny)
        )
        # The query counts include self even at strict radius; remove self
        # before applying the Type-I +1 convention.
        value_nats = digamma(K) + digamma(n) - np.mean(
            digamma((nx - 1) + 1) + digamma((ny - 1) + 1)
        )
    elif variant == "ksg_type_ii":
        # Algorithm 2: inclusive counts include self; subtract 1/k.
        nx, ny = counts(x, y, "inclusive")
        value_nats = digamma(K) - 1.0 / K + digamma(n) - np.mean(
            digamma(nx) + digamma(ny)
        )
    elif variant == "recovered_hybrid":
        # Historical implementation: inclusive counts plus epsilon,
        # but Type-I digamma expression and no Type-II -1/k correction.
        nx, ny = counts(x, y, "historical_inclusive_epsilon")
        value_nats = digamma(K) + digamma(n) - np.mean(
            digamma(nx) + digamma(ny)
        )
        historical = float(ksg_mi_2d(x, y, k=K))
        if not np.isclose(historical, max(0.0, value_nats / np.log(2.0)), atol=1e-12, rtol=0.0):
            raise AssertionError("Hybrid reconstruction does not match recovered historical output")
    else:
        raise ValueError(variant)
    return float(value_nats / np.log(2.0))


def summarize(values):
    a = np.asarray(values, dtype=float)
    return {
        "mean_bits": float(np.mean(a)),
        "median_bits": float(np.median(a)),
        "sd_bits": float(np.std(a, ddof=1)),
        "q025_bits": float(np.quantile(a, 0.025)),
        "q975_bits": float(np.quantile(a, 0.975)),
        "fraction_negative": float(np.mean(a < 0.0)),
        "min_bits": float(np.min(a)),
        "max_bits": float(np.max(a)),
    }


def main():
    records = []
    for n in SAMPLE_SIZES:
        samples = {
            "gaussian_rho_0_5": {v: [] for v in ("ksg_type_i", "ksg_type_ii", "recovered_hybrid")},
            "gaussian_rho_0_5_shuffled": {v: [] for v in ("ksg_type_i", "ksg_type_ii", "recovered_hybrid")},
            "sinusoidal_nonlinear": {v: [] for v in ("ksg_type_i", "ksg_type_ii", "recovered_hybrid")},
            "sinusoidal_nonlinear_shuffled": {v: [] for v in ("ksg_type_i", "ksg_type_ii", "recovered_hybrid")},
        }
        for rep in range(REPLICATES):
            rng = np.random.default_rng(BASE_SEED + n * 100 + rep)
            rho = 0.5
            gaussian = rng.multivariate_normal([0.0, 0.0], [[1.0, rho], [rho, 1.0]], size=n)
            gx, gy = gaussian[:, 0], gaussian[:, 1]
            x = rng.uniform(-np.pi, np.pi, size=n)
            y = np.sin(3.0 * x) + rng.normal(0.0, 0.35, size=n)
            conditions = {
                "gaussian_rho_0_5": (gx, gy),
                "gaussian_rho_0_5_shuffled": (gx, rng.permutation(gy)),
                "sinusoidal_nonlinear": (x, y),
                "sinusoidal_nonlinear_shuffled": (x, rng.permutation(y)),
            }
            for name, (a, b) in conditions.items():
                for variant in samples[name]:
                    samples[name][variant].append(estimate(a, b, variant))

        condition_results = {}
        for name, variants in samples.items():
            condition_results[name] = {
                variant: summarize(values) for variant, values in variants.items()
            }
        records.append({
            "sample_size": n,
            "k": K,
            "replicates": REPLICATES,
            "analytic_gaussian_rho_0_5_bits": float(-0.5 * np.log2(1.0 - 0.5**2)),
            "conditions": condition_results,
        })

    output = {
        "study": "recovered_v3_ksg_type_i_type_ii_and_hybrid_convention_comparison",
        "status": "diagnostic_only_not_certification",
        "base_seed": BASE_SEED,
        "sample_sizes": list(SAMPLE_SIZES),
        "replicates_per_condition": REPLICATES,
        "k": K,
        "scipy_version": scipy.__version__,
        "historical_source_modified": False,
        "definitions": {
            "ksg_type_i": "Strict marginal radius < kth joint distance; counts exclude self; psi(nx+1)+psi(ny+1); no -1/k term.",
            "ksg_type_ii": "Inclusive marginal radius <= kth joint distance; counts include self; psi(nx)+psi(ny); includes -1/k term.",
            "recovered_hybrid": "Inclusive kth_distance+1e-12 counts; psi(inclusive_nx)+psi(inclusive_ny); omits Type-II -1/k correction.",
        },
        "conditions": [
            "Gaussian rho=0.5 paired",
            "same Gaussian marginal samples with Y independently permuted",
            "sinusoidal nonlinear paired stress test",
            "same sinusoidal marginal samples with Y independently permuted",
        ],
        "interpretation_limits": [
            "This compares published estimator conventions and the recovered hybrid; it does not establish which variant best fits the cosmological application.",
            "The sinusoidal construction has no analytic MI value asserted.",
            "Twenty replicates are preliminary.",
            "No result validates spatially structured cosmological fields or TNG.",
        ],
        "records": records,
    }
    Path("v3_ksg_type_i_type_ii_hybrid_comparison.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
