"""Paired exact-grid versus deliberately off-grid dither benchmark."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import t

from research.sandbox.poisson_reconstruction import simulate_reconstruction_trial


SEEDS = tuple(range(2026110900, 2026110930))
ITERATIONS = (1, 2, 3, 5, 10)
OFFGRID_PHASES = np.asarray([
    (y, x)
    for y in (-0.29, 0.0, 0.29)
    for x in (-0.23, 0.0, 0.23)
], dtype=float)
ALIGNED_PHASES = np.asarray([
    (y, x)
    for y in (-1.0 / 3.0, 0.0, 1.0 / 3.0)
    for x in (-1.0 / 3.0, 0.0, 1.0 / 3.0)
], dtype=float)
ARMS = ("single_long", "nine_stationary", "nine_dithered")
METRICS = (
    "relative_rmse",
    "mean_source_centroid_error_px",
    "mean_aperture_flux_abs_error",
)


def summarize(values):
    data = np.asarray(values, dtype=float)
    mean = float(data.mean())
    sd = float(data.std(ddof=1)) if len(data) > 1 else 0.0
    half = float(t.ppf(0.975, len(data) - 1) * sd / np.sqrt(len(data))) if len(data) > 1 else 0.0
    return {
        "n": int(len(data)),
        "mean": mean,
        "sd": sd,
        "median": float(np.median(data)),
        "ci95_mean": [mean - half, mean + half],
    }


def metric_row(row, arm):
    values = row[arm]
    ratios = np.asarray(values["source_aperture_flux_ratios"], dtype=float)
    return {
        "relative_rmse": values["relative_rmse"],
        "mean_source_centroid_error_px": values["mean_source_centroid_error_px"],
        "mean_aperture_flux_abs_error": float(np.mean(np.abs(ratios - 1.0))),
    }


def main():
    sources = np.asarray([
        [10.35, 11.20],
        [16.10, 19.65],
        [19.40, 8.80],
    ])
    fluxes = [1200.0, 760.0, 430.0]
    sigmas = [[0.72, 0.91], [1.05, 0.83], [0.88, 1.12]]
    trials = []

    for seed in SEEDS:
        common = dict(
            sources_yx=sources,
            fluxes=fluxes,
            sigma_yx_px=sigmas,
            science_shape=(20, 22),
            padding_pixels=4,
            bin_factor=3,
            total_exposure=1.0,
            seed=seed,
            iterations=ITERATIONS,
        )
        aligned = simulate_reconstruction_trial(
            **common, dither_phases_yx=ALIGNED_PHASES
        )
        offgrid = simulate_reconstruction_trial(
            **common, dither_phases_yx=OFFGRID_PHASES
        )
        for index, iteration in enumerate(ITERATIONS):
            arow = aligned["results"][index]
            orow = offgrid["results"][index]
            if arow["stationary_long_max_abs_difference"] > 2e-12:
                raise AssertionError("aligned stationary/long control failed")
            if orow["stationary_long_max_abs_difference"] > 2e-12:
                raise AssertionError("off-grid stationary/long control failed")
            for arm in ARMS:
                label = "aligned_dithered" if arm == "nine_dithered" else arm
                trials.append({
                    "seed": seed,
                    "iterations": iteration,
                    "condition": label,
                    **metric_row(arow if arm != "nine_dithered" else arow, arm),
                })
            trials.append({
                "seed": seed,
                "iterations": iteration,
                "condition": "offgrid_dithered",
                **metric_row(orow, "nine_dithered"),
            })

    summary = {}
    paired = {}
    for iteration in ITERATIONS:
        summary[str(iteration)] = {}
        by_condition = {
            condition: {
                row["seed"]: row
                for row in trials
                if row["iterations"] == iteration and row["condition"] == condition
            }
            for condition in ("single_long", "nine_stationary", "aligned_dithered", "offgrid_dithered")
        }
        for condition, values in by_condition.items():
            summary[str(iteration)][condition] = {
                metric: summarize([r[metric] for r in values.values()])
                for metric in METRICS
            }
        paired[str(iteration)] = {}
        for comparison, left, right in (
            ("offgrid_minus_stationary", "offgrid_dithered", "nine_stationary"),
            ("offgrid_minus_aligned", "offgrid_dithered", "aligned_dithered"),
            ("aligned_minus_stationary", "aligned_dithered", "nine_stationary"),
        ):
            paired[str(iteration)][comparison] = {
                metric: summarize([
                    by_condition[left][seed][metric] - by_condition[right][seed][metric]
                    for seed in SEEDS
                ])
                for metric in METRICS
            }

    output = {
        "protocol": {
            "seeds": list(SEEDS),
            "iterations": list(ITERATIONS),
            "scene": "same three-source continuous axis-aligned Gaussian scene as the first pilot",
            "science_shape_detector_pixels": [20, 22],
            "padding_detector_pixels": 4,
            "bin_factor": 3,
            "total_exposure": 1.0,
            "noise": "independent Poisson photon counts only; no read noise or background",
            "aligned_phases_yx": ALIGNED_PHASES.tolist(),
            "offgrid_phases_yx": OFFGRID_PHASES.tolist(),
            "offgrid_highres_cell_shifts": (OFFGRID_PHASES * 3.0).tolist(),
            "truth_generator": "independent continuous Gaussian detector-pixel area integrals",
            "reconstruction": "non-negative Poisson Richardson-Lucy using bilinear shift-and-bin forward model and exact discrete adjoint",
            "paired_seed_design": "same seed and stationary control for aligned and off-grid phase sets; separate dither Poisson draws",
            "metrics": "fixed-interior relative RMSE and known-centre aperture centroid/flux metrics",
            "inference": "paired per-seed differences with 95% t confidence intervals",
            "key_caveat": "off-grid data are generated from continuous Gaussian pixel integrals while reconstruction uses a bilinear cell-shift approximation; results measure this model mismatch for this scene, not universal detector performance",
        },
        "summary_by_iteration": summary,
        "paired_comparisons": paired,
        "trials": trials,
    }
    path = Path("dither_offgrid_reconstruction_benchmark.json")
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(path),
        "seeds": len(SEEDS),
        "iterations": list(ITERATIONS),
        "summary_by_iteration": summary,
        "paired_comparisons": paired,
    }, indent=2))


if __name__ == "__main__":
    main()
