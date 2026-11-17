"""Permutation-null and nonlinear stress diagnostics for recovered v3 KSG MI.

These are diagnostics, not estimator certification. The Gaussian permutation
control preserves each marginal sample exactly while destroying pairings.
The sinusoidal case is a nonlinear-dependence stress test with no analytic MI
claim; it is assessed against its own shuffled-pair control.
"""
import json
from pathlib import Path

import numpy as np

from research.validation.recovered_cloud9_null_ensemble_v3_corrected import ksg_mi_2d

SAMPLE_SIZES = (1200, 3000)
REPLICATES = 20
K = 3
BASE_SEED = 20261116


def summarize(values):
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
        "fraction_exactly_zero_after_clipping": float(np.mean(a == 0.0)),
    }


def estimate_pair(x, y):
    value = float(ksg_mi_2d(x, y, k=K))
    if not np.isfinite(value):
        raise ValueError("KSG returned a non-finite estimate")
    return value


def main():
    records = []
    for n in SAMPLE_SIZES:
        gaussian_raw, gaussian_shuffled = [], []
        nonlinear_raw, nonlinear_shuffled = [], []
        for rep in range(REPLICATES):
            seed = BASE_SEED + n * 100 + rep
            rng = np.random.default_rng(seed)

            # Correlated bivariate Gaussian: exact MI is known, but here the
            # focus is paired permutation-null behaviour.
            rho = 0.5
            cov = np.array([[1.0, rho], [rho, 1.0]])
            gaussian = rng.multivariate_normal([0.0, 0.0], cov, size=n)
            gx, gy = gaussian[:, 0], gaussian[:, 1]
            gaussian_raw.append(estimate_pair(gx, gy))
            gaussian_shuffled.append(estimate_pair(gx, rng.permutation(gy)))

            # Nonlinear sinusoidal dependence. No analytic MI is asserted:
            # compare the dependent sample with a shuffled-pair null.
            x = rng.uniform(-np.pi, np.pi, size=n)
            y = np.sin(3.0 * x) + rng.normal(0.0, 0.35, size=n)
            nonlinear_raw.append(estimate_pair(x, y))
            nonlinear_shuffled.append(estimate_pair(x, rng.permutation(y)))

        records.append({
            "sample_size": n,
            "k": K,
            "replicates": REPLICATES,
            "gaussian_rho_0_5": {
                "paired_estimates": summarize(gaussian_raw),
                "permuted_y_null": summarize(gaussian_shuffled),
                "paired_minus_null_median_bits": float(
                    np.median(gaussian_raw) - np.median(gaussian_shuffled)
                ),
                "analytic_gaussian_mi_bits": float(-0.5 * np.log2(1.0 - rho**2)),
            },
            "nonlinear_sine_stress_test": {
                "paired_estimates": summarize(nonlinear_raw),
                "permuted_y_null": summarize(nonlinear_shuffled),
                "paired_minus_null_median_bits": float(
                    np.median(nonlinear_raw) - np.median(nonlinear_shuffled)
                ),
                "analytic_mi_claimed": False,
                "relationship": "X~Uniform(-pi,pi); Y=sin(3X)+Normal(0,0.35)",
            },
        })

    output = {
        "study": "recovered_v3_ksg_permutation_and_nonlinear_diagnostics",
        "status": "diagnostic_only_not_certification",
        "base_seed": BASE_SEED,
        "sample_sizes": list(SAMPLE_SIZES),
        "replicates_per_condition": REPLICATES,
        "k": K,
        "metric": "mutual information in bits",
        "estimator": "recovered v3 ksg_mi_2d, unchanged",
        "permutation_design": (
            "Within each replicate, Y is independently permuted; X and Y "
            "marginal samples are preserved exactly while pairings are destroyed."
        ),
        "clipping_note": (
            "The recovered estimator clips negative raw KSG values to zero. "
            "The reported zero fraction is therefore a property of the clipped "
            "output, not evidence that the underlying estimator is unbiased."
        ),
        "records": records,
        "interpretation_limits": [
            "Permutation controls test dependence detection under these iid synthetic samples only.",
            "The sinusoidal case is a nonlinear stress test, not a known-MI calibration target.",
            "No result establishes accuracy for spatially structured cosmological fields, dependent samples, or TNG.",
            "Twenty replicates provide a preliminary distribution, not a definitive uncertainty characterization.",
        ],
    }
    Path("v3_ksg_permutation_nonlinear_diagnostic.json").write_text(
        json.dumps(output, indent=2) + "\\n", encoding="utf-8"
    )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
