"""Run the paired photon-only dither reconstruction benchmark."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import t

from research.sandbox.poisson_reconstruction import simulate_reconstruction_trial


SEEDS = tuple(range(2026110800, 2026110830))
ITERATIONS = (1, 2, 3, 5, 10)
ARMS = ("single_long", "nine_stationary", "nine_dithered")
METRICS = (
    "relative_rmse",
    "mean_source_centroid_error_px",
    "mean_aperture_flux_ratio",
)


def summarize(values):
    data = np.asarray(values, dtype=float)
    mean = float(data.mean())
    sd = float(data.std(ddof=1)) if len(data) > 1 else 0.0
    half_width = float(t.ppf(0.975, len(data) - 1) * sd / np.sqrt(len(data))) if len(data) > 1 else 0.0
    return {
        "n": int(len(data)),
        "mean": mean,
        "sd": sd,
        "median": float(np.median(data)),
        "ci95_mean": [mean - half_width, mean + half_width],
    }


def main():
    source_positions = np.array([
        [10.35, 11.20],
        [16.10, 19.65],
        [19.40, 8.80],
    ])
    fluxes = [1200.0, 760.0, 430.0]
    sigmas = [[0.72, 0.91], [1.05, 0.83], [0.88, 1.12]]

    trials = []
    for seed in SEEDS:
        trial = simulate_reconstruction_trial(
            sources_yx=source_positions,
            fluxes=fluxes,
            sigma_yx_px=sigmas,
            science_shape=(20, 22),
            padding_pixels=4,
            bin_factor=3,
            total_exposure=1.0,
            seed=seed,
            iterations=ITERATIONS,
        )
        for row in trial["results"]:
            for arm in ARMS:
                metrics = row[arm]
                trials.append({
                    "seed": seed,
                    "iterations": row["iterations"],
                    "arm": arm,
                    **metrics,
                    "mean_aperture_flux_abs_error": float(
                        np.mean(np.abs(np.asarray(
                            metrics["source_aperture_flux_ratios"], dtype=float
                        ) - 1.0))
                    ),
                    "stationary_long_max_abs_difference": row[
                        "stationary_long_max_abs_difference"
                    ],
                })

    summary = {}
    paired = {}
    for iteration in ITERATIONS:
        summary[str(iteration)] = {}
        by_seed = {
            arm: {
                row["seed"]: row
                for row in trials
                if row["iterations"] == iteration and row["arm"] == arm
            }
            for arm in ARMS
        }
        for arm in ARMS:
            summary[str(iteration)][arm] = {
                metric: summarize([row[metric] for row in by_seed[arm].values()])
                for metric in METRICS
            }
            summary[str(iteration)][arm]["mean_aperture_flux_abs_error"] = summarize([
                row["mean_aperture_flux_abs_error"] for row in by_seed[arm].values()
            ])
        paired[str(iteration)] = {}
        for metric in METRICS + ("mean_aperture_flux_abs_error",):
            differences = [
                by_seed["nine_dithered"][seed][metric]
                - by_seed["nine_stationary"][seed][metric]
                for seed in SEEDS
            ] if metric != "mean_aperture_flux_abs_error" else [
                by_seed["nine_dithered"][seed][metric]
                - by_seed["nine_stationary"][seed][metric]
                for seed in SEEDS
            ]
            paired[str(iteration)][metric] = summarize(differences)
        paired[str(iteration)]["stationary_vs_long_max_abs_difference"] = max(
            row["stationary_long_max_abs_difference"]
            for row in by_seed["nine_stationary"].values()
        )

    output = {
        "protocol": {
            "seeds": list(SEEDS),
            "iterations": list(ITERATIONS),
            "scene": "three axis-aligned Gaussian sources; fixed 20x22 science crop; four detector-pixel guard",
            "bin_factor": 3,
            "total_exposure": 1.0,
            "noise": "Poisson only; no read noise or background",
            "arms": "single-long and nine-stationary share exactly the same summed stationary photon counts; nine-dithered has nine independently drawn phase-specific frames",
            "reconstruction": "Poisson Richardson-Lucy; non-negative high-resolution cell-flux image; fixed iteration curve",
            "phase_grid": "3x3 row/column offsets -1/3, 0, +1/3 detector pixels; aligned to the 3x high-resolution grid",
            "metrics": "fixed-interior relative RMSE; known-centre radius-2-pixel centroid and aperture-flux metrics",
            "inference": "paired dither-minus-stationary differences with 95% t confidence intervals",
        },
        "summary_by_iteration": summary,
        "paired_dither_minus_stationary": paired,
        "trials": trials,
    }
    path = Path("dither_reconstruction_benchmark.json")
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "n_trials": len(SEEDS), "iterations": list(ITERATIONS), "paired": paired}, indent=2))


if __name__ == "__main__":
    main()
