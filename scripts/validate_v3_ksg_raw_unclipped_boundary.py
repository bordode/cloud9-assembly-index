"""Raw KSG and radius-boundary convention diagnostics.

This file deliberately does not modify the recovered historical estimator.
It reconstructs its unclipped expression and contrasts its current inclusive
radius query with a strict-below-kth-radius count for diagnostic purposes.
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


def raw_ksg(x, y, strict_boundary=False):
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    n = len(x)
    if n < K + 2:
        return 0.0, {"boundary_count_changes": 0, "mean_nx": 0.0, "mean_ny": 0.0}

    joint = np.column_stack([x, y])
    joint_tree = cKDTree(joint)
    x_tree = cKDTree(x.reshape(-1, 1))
    y_tree = cKDTree(y.reshape(-1, 1))
    distances, _ = joint_tree.query(joint, k=K + 1, p=np.inf)
    kth = distances[:, K]

    if strict_boundary:
        radii = np.nextafter(kth, -np.inf)
    else:
        radii = kth + 1e-12

    nx = np.asarray([
        x_tree.query_ball_point([x[i]], r=radii[i], p=np.inf, return_length=True) - 1
        for i in range(n)
    ], dtype=int)
    ny = np.asarray([
        y_tree.query_ball_point([y[i]], r=radii[i], p=np.inf, return_length=True) - 1
        for i in range(n)
    ], dtype=int)

    # Exact recovered-v3 digamma expression, but without max(0, ...).
    raw_nats = digamma(K) - np.mean(digamma(nx + 1) + digamma(ny + 1)) + digamma(n)
    diagnostics = {
        "boundary_count_changes": int(np.sum(nx != 0) * 0 + np.sum(ny != 0) * 0),
        "mean_nx": float(np.mean(nx)),
        "mean_ny": float(np.mean(ny)),
    }
    return float(raw_nats / np.log(2.0)), diagnostics


def summary(values):
    a = np.asarray(values, dtype=float)
    return {
        "count": int(a.size),
        "mean_bits": float(np.mean(a)),
        "median_bits": float(np.median(a)),
        "sd_bits": float(np.std(a, ddof=1)),
        "q025_bits": float(np.quantile(a, 0.025)),
        "q975_bits": float(np.quantile(a, 0.975)),
        "min_bits": float(np.min(a)),
        "max_bits": float(np.max(a)),
        "fraction_negative_raw": float(np.mean(a < 0.0)),
        "fraction_exactly_zero_raw": float(np.mean(a == 0.0)),
    }


def main():
    records = []
    for n in SAMPLE_SIZES:
        conditions = {
            "gaussian_rho_0_5": {"x": [], "y": []},
            "gaussian_rho_0_5_shuffled": {"x": [], "y": []},
            "sinusoidal_nonlinear": {"x": [], "y": []},
            "sinusoidal_nonlinear_shuffled": {"x": [], "y": []},
        }
        for rep in range(REPLICATES):
            seed = BASE_SEED + n * 100 + rep
            rng = np.random.default_rng(seed)
            rho = 0.5
            cov = np.array([[1.0, rho], [rho, 1.0]])
            gaussian = rng.multivariate_normal([0.0, 0.0], cov, size=n)
            gx, gy = gaussian[:, 0], gaussian[:, 1]
            x = rng.uniform(-np.pi, np.pi, size=n)
            y = np.sin(3.0 * x) + rng.normal(0.0, 0.35, size=n)

            conditions["gaussian_rho_0_5"]["x"].append(gx)
            conditions["gaussian_rho_0_5"]["y"].append(gy)
            conditions["gaussian_rho_0_5_shuffled"]["x"].append(gx)
            conditions["gaussian_rho_0_5_shuffled"]["y"].append(rng.permutation(gy))
            conditions["sinusoidal_nonlinear"]["x"].append(x)
            conditions["sinusoidal_nonlinear"]["y"].append(y)
            conditions["sinusoidal_nonlinear_shuffled"]["x"].append(x)
            conditions["sinusoidal_nonlinear_shuffled"]["y"].append(rng.permutation(y))

        condition_results = {}
        for name, samples in conditions.items():
            current_raw, strict_raw, historical_clipped = [], [], []
            current_mean_nx, current_mean_ny = [], []
            strict_mean_nx, strict_mean_ny = [], []
            boundary_changed_replicates = 0
            for x, y in zip(samples["x"], samples["y"]):
                raw_current, diag_current = raw_ksg(x, y, strict_boundary=False)
                raw_strict, diag_strict = raw_ksg(x, y, strict_boundary=True)
                clipped = float(ksg_mi_2d(x, y, k=K))
                if not np.isclose(clipped, max(0.0, raw_current), atol=1e-12, rtol=0.0):
                    raise AssertionError("Reconstructed raw expression does not match historical clipped output")
                current_raw.append(raw_current)
                strict_raw.append(raw_strict)
                historical_clipped.append(clipped)
                current_mean_nx.append(diag_current["mean_nx"])
                current_mean_ny.append(diag_current["mean_ny"])
                strict_mean_nx.append(diag_strict["mean_nx"])
                strict_mean_ny.append(diag_strict["mean_ny"])
                if raw_current != raw_strict:
                    boundary_changed_replicates += 1

            condition_results[name] = {
                "historical_clipped_output": summary(historical_clipped),
                "reconstructed_unclipped_current_radius": summary(current_raw),
                "strict_below_kth_radius_unclipped": summary(strict_raw),
                "mean_marginal_neighbour_counts_current_radius": {
                    "nx": float(np.mean(current_mean_nx)),
                    "ny": float(np.mean(current_mean_ny)),
                },
                "mean_marginal_neighbour_counts_strict_radius": {
                    "nx": float(np.mean(strict_mean_nx)),
                    "ny": float(np.mean(strict_mean_ny)),
                },
                "replicates_where_strict_and_current_estimate_differ": boundary_changed_replicates,
            }

        records.append({
            "sample_size": n,
            "k": K,
            "replicates": REPLICATES,
            "conditions": condition_results,
        })

    output = {
        "study": "recovered_v3_ksg_raw_unclipped_and_radius_boundary_diagnostic",
        "status": "diagnostic_only_not_certification",
        "base_seed": BASE_SEED,
        "sample_sizes": list(SAMPLE_SIZES),
        "replicates_per_condition": REPLICATES,
        "k": K,
        "metric": "mutual information in bits",
        "scipy_version": scipy.__version__,
        "historical_source_modified": False,
        "method": (
            "Reconstruct the recovered-v3 digamma expression without nonnegative clipping. "
            "Compare current radius kth_distance+1e-12 with strict radius nextafter(kth_distance,-infinity)."
        ),
        "conditions": [
            "Gaussian rho=0.5 paired",
            "same Gaussian marginal samples with Y independently permuted",
            "sinusoidal nonlinear paired stress test",
            "same sinusoidal marginal samples with Y independently permuted",
        ],
        "interpretation_limits": [
            "The raw helper is a diagnostic reconstruction, not a replacement estimator.",
            "The strict-radius variant is a convention sensitivity check, not asserted to be the correct KSG convention.",
            "No result validates the estimator for spatially structured cosmological fields or TNG.",
            "Twenty replicates are preliminary and do not establish a complete bias or uncertainty characterization.",
        ],
        "records": records,
    }
    Path("v3_ksg_raw_unclipped_boundary_diagnostic.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
