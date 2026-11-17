"""Convention-aware cross-check of recovered v3 KSG against scikit-learn.

scikit-learn's mutual_info_regression uses a continuous-continuous
nearest-neighbour MI estimator related to KSG. It is an independent
implementation, but not assumed to be an identical estimator convention.
The script compares both implementations on identical deterministic samples.
"""
import json
from pathlib import Path

import numpy as np
import sklearn
from sklearn.feature_selection import mutual_info_regression

from research.validation.recovered_cloud9_null_ensemble_v3_corrected import ksg_mi_2d

SAMPLE_SIZES = (1200, 3000)
REPLICATES = 20
K = 3
BASE_SEED = 20261117


def sklearn_mi_bits(x, y, seed):
    # sklearn returns nats; convert to bits for a like-unit comparison.
    value_nats = mutual_info_regression(
        np.asarray(x).reshape(-1, 1),
        np.asarray(y),
        discrete_features=False,
        n_neighbors=K,
        copy=True,
        random_state=seed,
    )[0]
    return float(value_nats / np.log(2.0))


def summary(values):
    a = np.asarray(values, dtype=float)
    return {
        "mean_bits": float(np.mean(a)),
        "median_bits": float(np.median(a)),
        "sd_bits": float(np.std(a, ddof=1)),
        "q025_bits": float(np.quantile(a, 0.025)),
        "q975_bits": float(np.quantile(a, 0.975)),
        "min_bits": float(np.min(a)),
        "max_bits": float(np.max(a)),
    }


def main():
    records = []
    for n in SAMPLE_SIZES:
        conditions = {
            "gaussian_rho_0_5": {"recovered": [], "sklearn": []},
            "gaussian_rho_0_5_shuffled": {"recovered": [], "sklearn": []},
            "sinusoidal_nonlinear": {"recovered": [], "sklearn": []},
            "sinusoidal_nonlinear_shuffled": {"recovered": [], "sklearn": []},
        }
        for rep in range(REPLICATES):
            seed = BASE_SEED + n * 100 + rep
            rng = np.random.default_rng(seed)

            rho = 0.5
            cov = np.array([[1.0, rho], [rho, 1.0]])
            g = rng.multivariate_normal([0.0, 0.0], cov, size=n)
            gx, gy = g[:, 0], g[:, 1]
            gy_shuffled = rng.permutation(gy)

            x = rng.uniform(-np.pi, np.pi, size=n)
            y = np.sin(3.0 * x) + rng.normal(0.0, 0.35, size=n)
            y_shuffled = rng.permutation(y)

            samples = {
                "gaussian_rho_0_5": (gx, gy),
                "gaussian_rho_0_5_shuffled": (gx, gy_shuffled),
                "sinusoidal_nonlinear": (x, y),
                "sinusoidal_nonlinear_shuffled": (x, y_shuffled),
            }
            for name, (a, b) in samples.items():
                conditions[name]["recovered"].append(float(ksg_mi_2d(a, b, k=K)))
                conditions[name]["sklearn"].append(sklearn_mi_bits(a, b, seed + rep))

        record = {"sample_size": n, "k": K, "replicates": REPLICATES, "conditions": {}}
        for name, values in conditions.items():
            recovered = np.asarray(values["recovered"])
            reference = np.asarray(values["sklearn"])
            record["conditions"][name] = {
                "recovered_v3": summary(recovered),
                "sklearn_reference": summary(reference),
                "paired_difference_recovered_minus_sklearn": summary(recovered - reference),
            }
        records.append(record)

    output = {
        "study": "recovered_v3_ksg_vs_sklearn_reference",
        "status": "diagnostic_only_not_certification",
        "base_seed": BASE_SEED,
        "sample_sizes": list(SAMPLE_SIZES),
        "replicates_per_condition": REPLICATES,
        "k": K,
        "scikit_learn_version": sklearn.__version__,
        "reference": (
            "sklearn.feature_selection.mutual_info_regression, continuous "
            "features, n_neighbors=3; output converted from nats to bits"
        ),
        "reference_caveat": (
            "This is a separate maintained nearest-neighbour MI implementation "
            "related to KSG, not assumed to be convention-identical to recovered v3."
        ),
        "analytic_gaussian_mi_rho_0_5_bits": float(-0.5 * np.log2(1.0 - 0.5**2)),
        "records": records,
        "interpretation_limits": [
            "Differences may reflect estimator convention, radius boundary handling, noise regularization, or finite-sample behaviour.",
            "The comparison is an implementation cross-check, not proof that either estimator is ground truth.",
            "The sinusoidal case has no analytic MI value asserted.",
            "No result establishes validity for spatially structured cosmological fields or TNG.",
        ],
    }
    Path("v3_ksg_reference_crosscheck.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
