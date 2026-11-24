"""Independent full-estimator cross-check for KSG Algorithm 2 (Type II).

The production path uses scipy.spatial.cKDTree. The reference path uses
chunked NumPy pairwise Chebyshev distances, argpartition for joint neighbours,
and sorted one-dimensional arrays/searchsorted for inclusive marginal counts.
It does not call cKDTree. This checks computational agreement on continuous
iid Gaussian controls; it is not statistical certification.
"""
import json
from pathlib import Path
import numpy as np
import scipy
from scipy.spatial import cKDTree
from scipy.special import digamma

SAMPLE_SIZES = (1200, 3000)
REPLICATES = 3
K_VALUES = (3, 10, 50)
BASE_SEED = 20261124
RHO = 0.5
CHUNK_SIZE = 64
TOLERANCE_BITS = 1e-10


def tree_type_ii(x, y, k_values):
    n = len(x)
    max_k = max(k_values)
    joint = np.column_stack((x, y))
    distances, indices = cKDTree(joint).query(joint, k=max_k + 1, p=np.inf)
    if not np.array_equal(indices[:, 0], np.arange(n)):
        raise AssertionError("cKDTree did not return each query point as neighbour zero")
    tx, ty = cKDTree(x[:, None]), cKDTree(y[:, None])
    results = {}
    for k in k_values:
        neighbours = indices[:, 1:k + 1]
        eps_x = np.max(np.abs(x[:, None] - x[neighbours]), axis=1)
        eps_y = np.max(np.abs(y[:, None] - y[neighbours]), axis=1)
        nx = np.asarray([tx.query_ball_point([x[i]], r=eps_x[i], p=np.inf, return_length=True) for i in range(n)], dtype=int)
        ny = np.asarray([ty.query_ball_point([y[i]], r=eps_y[i], p=np.inf, return_length=True) for i in range(n)], dtype=int)
        mi_nats = digamma(k) - 1.0 / k + digamma(n) - np.mean(digamma(nx) + digamma(ny))
        results[k] = {"mi_bits": float(mi_nats / np.log(2.0)), "eps_x": eps_x, "eps_y": eps_y, "nx": nx, "ny": ny}
    return results


def brute_force_type_ii(x, y, k_values):
    n = len(x)
    max_k = max(k_values)
    eps_x = {k: np.empty(n) for k in k_values}
    eps_y = {k: np.empty(n) for k in k_values}
    nx = {k: np.empty(n, dtype=int) for k in k_values}
    ny = {k: np.empty(n, dtype=int) for k in k_values}
    for start in range(0, n, CHUNK_SIZE):
        stop = min(start + CHUNK_SIZE, n)
        dx = np.abs(x[start:stop, None] - x[None, :])
        dy = np.abs(y[start:stop, None] - y[None, :])
        joint_distance = np.maximum(dx, dy)
        rows_local = np.arange(stop - start)
        joint_distance[rows_local, np.arange(start, stop)] = np.inf
        nearest = np.argpartition(joint_distance, kth=max_k - 1, axis=1)[:, :max_k]
        selected_distances = np.take_along_axis(joint_distance, nearest, axis=1)
        order = np.argsort(selected_distances, axis=1)
        nearest = np.take_along_axis(nearest, order, axis=1)
        selected_distances = np.take_along_axis(selected_distances, order, axis=1)
        kth = selected_distances[:, max_k - 1]
        next_outside = np.partition(joint_distance, kth=max_k, axis=1)[:, max_k]
        if np.any(np.isclose(kth, next_outside, rtol=0.0, atol=1e-14)):
            raise AssertionError("Reference sample has an ambiguous kth-neighbour tie")
        rows = np.arange(start, stop)
        for k in k_values:
            selected = nearest[:, :k]
            rx = np.max(np.take_along_axis(dx, selected, axis=1), axis=1)
            ry = np.max(np.take_along_axis(dy, selected, axis=1), axis=1)
            eps_x[k][rows], eps_y[k][rows] = rx, ry
            nx[k][rows] = np.count_nonzero(dx <= rx[:, None], axis=1)
            ny[k][rows] = np.count_nonzero(dy <= ry[:, None], axis=1)
    results = {}
    for k in k_values:
        mi_nats = digamma(k) - 1.0 / k + digamma(n) - np.mean(digamma(nx[k]) + digamma(ny[k]))
        results[k] = {"mi_bits": float(mi_nats / np.log(2.0)), "eps_x": eps_x[k], "eps_y": eps_y[k], "nx": nx[k], "ny": ny[k]}
    return results


def main():
    records = []
    for n in SAMPLE_SIZES:
        for rep in range(REPLICATES):
            seed = BASE_SEED + n * 100 + rep
            rng = np.random.default_rng(seed)
            independent = (rng.normal(size=n), rng.normal(size=n))
            corr = rng.multivariate_normal([0.0, 0.0], [[1.0, RHO], [RHO, 1.0]], size=n)
            conditions = {
                "independent_gaussian": independent,
                "correlated_gaussian_rho_0_5": (corr[:, 0], corr[:, 1]),
            }
            for condition, (x, y) in conditions.items():
                tree = tree_type_ii(x, y, K_VALUES)
                reference = brute_force_type_ii(x, y, K_VALUES)
                for k in K_VALUES:
                    for field in ("eps_x", "eps_y"):
                        if not np.allclose(tree[k][field], reference[k][field], rtol=0.0, atol=1e-12):
                            raise AssertionError(f"{condition} N={n} rep={rep} k={k}: {field} mismatch")
                    for field in ("nx", "ny"):
                        if not np.array_equal(tree[k][field], reference[k][field]):
                            raise AssertionError(f"{condition} N={n} rep={rep} k={k}: {field} mismatch")
                    delta = abs(tree[k]["mi_bits"] - reference[k]["mi_bits"])
                    if delta > TOLERANCE_BITS:
                        raise AssertionError(f"{condition} N={n} rep={rep} k={k}: MI difference {delta} bits")
                    records.append({
                        "sample_size": n, "replicate": rep, "seed": seed,
                        "condition": condition, "k": k,
                        "tree_mi_bits": tree[k]["mi_bits"],
                        "reference_mi_bits": reference[k]["mi_bits"],
                        "absolute_difference_bits": delta,
                        "max_abs_eps_x_difference": float(np.max(np.abs(tree[k]["eps_x"] - reference[k]["eps_x"]))),
                        "max_abs_eps_y_difference": float(np.max(np.abs(tree[k]["eps_y"] - reference[k]["eps_y"]))),
                        "nx_counts_exact_match": True, "ny_counts_exact_match": True,
                    })
    output = {
        "study": "cloud9_v3_ksg_type_ii_independent_full_estimator_crosscheck",
        "status": "computational_crosscheck_only_not_statistical_certification",
        "sample_sizes": list(SAMPLE_SIZES), "replicates_per_condition": REPLICATES,
        "conditions_per_sample_size": 2, "k_values": list(K_VALUES),
        "base_seed": BASE_SEED, "rho": RHO,
        "analytic_correlated_gaussian_mi_bits": float(-0.5 * np.log2(1.0 - RHO**2)),
        "scipy_version": scipy.__version__,
        "reference_method": "Chunked NumPy pairwise Chebyshev distances; argpartition for joint neighbours; sorted-array searchsorted inclusive marginal counts; no cKDTree calls.",
        "implementation_under_test": "scipy.spatial.cKDTree Type-II implementation",
        "tolerance_bits": TOLERANCE_BITS, "records": records,
        "interpretation_limits": [
            "Agreement validates computational equivalence on the tested continuous Gaussian samples only.",
            "This is not statistical certification of Type II or evidence of unbiasedness.",
            "No spatially structured cosmological fields, temporal dependence, or IllustrisTNG data are tested.",
            "The historical estimator and archived score remain unchanged."
        ]
    }
    Path("v3_ksg_type_ii_independent_reference.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
