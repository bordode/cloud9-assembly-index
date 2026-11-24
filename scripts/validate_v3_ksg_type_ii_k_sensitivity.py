"""KSG Type-I/Type-II k-sensitivity study on Gaussian calibration controls.

Type II follows the separate epsilon_x / epsilon_y rectangle construction
from Kraskov et al. (2004), Eq. (9), Fig. 1(b,c), and Sec. II C.
This is a diagnostic, not estimator certification.
"""
import json
from pathlib import Path

import numpy as np
import scipy
from scipy.spatial import cKDTree
from scipy.special import digamma

SAMPLE_SIZES = (1200, 3000)
REPLICATES = 20
BASE_SEED = 20261124
RHO = 0.5


def k_grid(n):
    return sorted(set((3, 5, 10, 20, 50, 100, n // 4)))


def estimate_at_k(x, y, k, distances, indices):
    n = len(x)
    kth_radius = distances[:, k]
    tx = cKDTree(x.reshape(-1, 1))
    ty = cKDTree(y.reshape(-1, 1))

    # Algorithm 1: strict marginal counts at the joint kth-neighbour radius.
    strict_radius = np.nextafter(kth_radius, -np.inf)
    nx_i = tx.query_ball_point(
        x.reshape(-1, 1), r=strict_radius, p=np.inf, return_length=True
    )
    ny_i = ty.query_ball_point(
        y.reshape(-1, 1), r=strict_radius, p=np.inf, return_length=True
    )
    # query_ball_point includes the reference point; psi(n_x+1) with
    # self-excluded counts is exactly psi(count_including_self).
    type_i_nats = digamma(k) + digamma(n) - np.mean(
        digamma(nx_i) + digamma(ny_i)
    )

    # Algorithm 2: independent marginal widths of the rectangle enclosing
    # the k joint neighbours; X and Y maxima may be set by different points.
    neighbours = indices[:, 1 : k + 1]
    radius_x = np.max(
        np.abs(x[:, None] - x[neighbours]), axis=1
    )
    radius_y = np.max(
        np.abs(y[:, None] - y[neighbours]), axis=1
    )
    nx_ii = tx.query_ball_point(
        x.reshape(-1, 1), r=radius_x, p=np.inf, return_length=True
    )
    ny_ii = ty.query_ball_point(
        y.reshape(-1, 1), r=radius_y, p=np.inf, return_length=True
    )
    type_ii_nats = digamma(k) - 1.0 / k + digamma(n) - np.mean(
        digamma(nx_ii) + digamma(ny_ii)
    )
    return float(type_i_nats / np.log(2.0)), float(type_ii_nats / np.log(2.0))


def summarize(values):
    a = np.asarray(values, dtype=float)
    return {
        "mean_bits": float(np.mean(a)),
        "median_bits": float(np.median(a)),
        "sd_bits": float(np.std(a, ddof=1)),
        "standard_error_bits": float(np.std(a, ddof=1) / np.sqrt(len(a))),
        "q025_bits": float(np.quantile(a, 0.025)),
        "q975_bits": float(np.quantile(a, 0.975)),
        "fraction_negative": float(np.mean(a < 0.0)),
        "min_bits": float(np.min(a)),
        "max_bits": float(np.max(a)),
    }


def main():
    records = []
    for n in SAMPLE_SIZES:
        ks = k_grid(n)
        max_k = max(ks)
        values = {
            condition: {
                variant: {k: [] for k in ks}
                for variant in ("type_i", "type_ii")
            }
            for condition in ("independent_gaussian", "correlated_gaussian_rho_0_5")
        }
        for rep in range(REPLICATES):
            rng = np.random.default_rng(BASE_SEED + n * 1000 + rep)
            x = rng.normal(size=n)
            y_ind = rng.normal(size=n)
            correlated = rng.multivariate_normal(
                [0.0, 0.0], [[1.0, RHO], [RHO, 1.0]], size=n
            )
            conditions = {
                "independent_gaussian": (x, y_ind),
                "correlated_gaussian_rho_0_5": (
                    correlated[:, 0], correlated[:, 1]
                ),
            }
            for condition, (a, b) in conditions.items():
                joint = np.column_stack([a, b])
                distances, indices = cKDTree(joint).query(
                    joint, k=max_k + 1, p=np.inf
                )
                for k in ks:
                    type_i, type_ii = estimate_at_k(a, b, k, distances, indices)
                    values[condition]["type_i"][k].append(type_i)
                    values[condition]["type_ii"][k].append(type_ii)

        condition_results = {}
        for condition, variants in values.items():
            condition_results[condition] = {
                variant: {
                    str(k): summarize(samples)
                    for k, samples in k_values.items()
                }
                for variant, k_values in variants.items()
            }
        records.append({
            "sample_size": n,
            "replicates": REPLICATES,
            "k_values": ks,
            "conditions": condition_results,
        })

    output = {
        "study": "cloud9_v3_ksg_type_i_type_ii_k_sensitivity",
        "status": "diagnostic_only_not_certification",
        "base_seed": BASE_SEED,
        "sample_sizes": list(SAMPLE_SIZES),
        "replicates_per_condition": REPLICATES,
        "rho": RHO,
        "analytic_correlated_gaussian_mi_bits": float(
            -0.5 * np.log2(1.0 - RHO**2)
        ),
        "scipy_version": scipy.__version__,
        "type_ii_definition": (
            "Separate inclusive epsilon_x and epsilon_y radii are the maximum "
            "projected distances across the k joint-space neighbours; counts "
            "include self; estimator includes -1/k."
        ),
        "conditions": [
            "Independent standard normal X and Y",
            "Correlated standard normal pair with rho=0.5",
        ],
        "interpretation_limits": [
            "Twenty replicates per condition are preliminary.",
            "Large k is included to examine the paper's guidance for independence testing; these values are not automatically preferred for estimating nonzero MI.",
            "This does not validate spatially structured cosmological fields, temporal dependence, or IllustrisTNG.",
            "The historical estimator and archived score are not modified.",
        ],
        "records": records,
    }
    Path("v3_ksg_type_ii_k_sensitivity.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
