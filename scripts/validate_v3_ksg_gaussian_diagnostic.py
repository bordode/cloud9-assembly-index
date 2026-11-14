"""Diagnostic validation of the recovered KSG MI estimator.

This is a calibration study, not a certification. It compares the current
implementation with analytic Gaussian mutual information and an independence
control at sample sizes relevant to the synthetic v3 pipeline.
"""
import json
from pathlib import Path

import numpy as np

from research.validation.recovered_cloud9_null_ensemble_v3_corrected import ksg_mi_2d

SAMPLE_SIZES = (1200, 3000)
REPLICATES = 3
K = 3
CORRELATIONS = (0.0, 0.5, 0.8)
BASE_SEED = 20261114


def analytic_gaussian_mi_bits(rho):
    return float(-0.5 * np.log2(1.0 - rho**2))


def main():
    records = []
    for n in SAMPLE_SIZES:
        for rho_index, rho in enumerate(CORRELATIONS):
            estimates = []
            for replicate in range(REPLICATES):
                seed = BASE_SEED + n * 10 + rho_index * 100 + replicate
                rng = np.random.default_rng(seed)
                covariance = np.array([[1.0, rho], [rho, 1.0]])
                sample = rng.multivariate_normal([0.0, 0.0], covariance, size=n)
                estimate = ksg_mi_2d(sample[:, 0], sample[:, 1], k=K)
                if not np.isfinite(estimate):
                    raise ValueError(f"Non-finite MI estimate for n={n}, rho={rho}, rep={replicate}")
                estimates.append(float(estimate))

            expected = analytic_gaussian_mi_bits(rho)
            records.append({
                "sample_size": n,
                "k": K,
                "correlation": rho,
                "analytic_mi_bits": expected,
                "estimates_bits": estimates,
                "mean_estimate_bits": float(np.mean(estimates)),
                "median_estimate_bits": float(np.median(estimates)),
                "min_estimate_bits": float(np.min(estimates)),
                "max_estimate_bits": float(np.max(estimates)),
                "median_error_bits": float(np.median(estimates) - expected),
            })

    output = {
        "study": "recovered_v3_ksg_estimator_gaussian_diagnostic",
        "status": "diagnostic_only_not_certification",
        "base_seed": BASE_SEED,
        "replicates": REPLICATES,
        "sample_sizes": list(SAMPLE_SIZES),
        "correlations": list(CORRELATIONS),
        "metric": "mutual information in bits",
        "estimator": "recovered v3 ksg_mi_2d, unchanged",
        "records": records,
        "interpretation_limit": (
            "Synthetic Gaussian controls only. Results do not establish unbiasedness "
            "for spatially structured cosmological density fields or validate TNG."
        ),
    }
    Path("v3_ksg_gaussian_diagnostic.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
