"""Independent, pre-registered validation of dither gains with known Poisson background.

This validation uses fresh seeds and a fixed two-iteration reconstruction setting.
It does not retune the iteration count or estimate the background from the data.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import t

from research.sandbox.poisson_reconstruction import simulate_reconstruction_trial


# Frozen before the validation run; disjoint from development seeds 2026111000–2026111029.
DEVELOPMENT_SEEDS = tuple(range(2026111000, 2026111030))
VALIDATION_SEEDS = tuple(range(2026111200, 2026111230))
ITERATIONS = (2,)
BACKGROUND_RATES = (0.0, 0.1, 0.5, 1.0, 2.0)
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
CONDITIONS = ("nine_stationary", "aligned_dithered", "offgrid_dithered")
METRICS = (
    "relative_rmse",
    "mean_source_centroid_error_px",
    "mean_aperture_flux_abs_error",
)


def summarize(values):
    data = np.asarray(values, dtype=float)
    mean = float(data.mean())
    sd = float(data.std(ddof=1))
    half = float(t.ppf(0.975, len(data) - 1) * sd / np.sqrt(len(data)))
    return {
        "n": int(len(data)),
        "mean": mean,
        "sd": sd,
        "median": float(np.median(data)),
        "ci95_mean": [mean - half, mean + half],
    }


def metric_row(result, arm):
    values = result["nine_dithered"] if arm in ("aligned_dithered", "offgrid_dithered") else result[arm]
    ratios = np.asarray(values["source_aperture_flux_ratios"], dtype=float)
    return {
        "relative_rmse": values["relative_rmse"],
        "mean_source_centroid_error_px": values["mean_source_centroid_error_px"],
        "mean_aperture_flux_abs_error": float(np.mean(np.abs(ratios - 1.0))),
    }


def main():
    if set(DEVELOPMENT_SEEDS) & set(VALIDATION_SEEDS):
        raise AssertionError("validation seeds must be disjoint from development seeds")

    sources = np.asarray([
        [10.35, 11.20],
        [16.10, 19.65],
        [19.40, 8.80],
    ])
    fluxes = [1200.0, 760.0, 430.0]
    sigmas = [[0.72, 0.91], [1.05, 0.83], [0.88, 1.12]]
    records = []

    for background_rate in BACKGROUND_RATES:
        for seed in VALIDATION_SEEDS:
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
                background_rate=background_rate,
            )
            aligned = simulate_reconstruction_trial(
                **common, dither_phases_yx=ALIGNED_PHASES
            )
            offgrid = simulate_reconstruction_trial(
                **common, dither_phases_yx=OFFGRID_PHASES
            )
            arow = aligned["results"][0]
            orow = offgrid["results"][0]
            if arow["stationary_long_max_abs_difference"] > 2e-12:
                raise AssertionError("aligned stationary/long control failed")
            if orow["stationary_long_max_abs_difference"] > 2e-12:
                raise AssertionError("off-grid stationary/long control failed")

            for condition in CONDITIONS:
                source = orow if condition == "offgrid_dithered" else arow
                ratios = np.asarray(
                    source["nine_dithered" if condition != "nine_stationary" else "nine_stationary"]["source_aperture_flux_ratios"],
                    dtype=float,
                )
                metrics = (
                    metric_row(source, condition)
                    if condition != "offgrid_dithered"
                    else metric_row(orow, condition)
                )
                if condition == "nine_stationary":
                    metrics = {
                        "relative_rmse": source["nine_stationary"]["relative_rmse"],
                        "mean_source_centroid_error_px": source["nine_stationary"]["mean_source_centroid_error_px"],
                        "mean_aperture_flux_abs_error": float(np.mean(np.abs(ratios - 1.0))),
                    }
                records.append({
                    "background_rate": background_rate,
                    "seed": seed,
                    "iterations": 2,
                    "condition": condition,
                    **metrics,
                })

    summary = {}
    paired = {}
    for background_rate in BACKGROUND_RATES:
        key = str(background_rate)
        subset = [r for r in records if r["background_rate"] == background_rate]
        by_condition = {
            condition: {r["seed"]: r for r in subset if r["condition"] == condition}
            for condition in CONDITIONS
        }
        summary[key] = {
            condition: {
                metric: summarize([row[metric] for row in values.values()])
                for metric in METRICS
            }
            for condition, values in by_condition.items()
        }
        paired[key] = {}
        for comparison, left, right in (
            ("offgrid_minus_stationary", "offgrid_dithered", "nine_stationary"),
            ("aligned_minus_stationary", "aligned_dithered", "nine_stationary"),
            ("offgrid_minus_aligned", "offgrid_dithered", "aligned_dithered"),
        ):
            paired[key][comparison] = {
                metric: summarize([
                    by_condition[left][seed][metric] - by_condition[right][seed][metric]
                    for seed in VALIDATION_SEEDS
                ])
                for metric in METRICS
            }

    output = {
        "protocol": {
            "status": "pre-registered independent validation",
            "development_seeds": list(DEVELOPMENT_SEEDS),
            "validation_seeds": list(VALIDATION_SEEDS),
            "iterations": list(ITERATIONS),
            "iteration_selection": "fixed at two before validation; no retuning on validation results",
            "background_rates_counts_per_detector_pixel_per_exposure_unit": list(BACKGROUND_RATES),
            "background_assumption": "known, spatially uniform, additive Poisson background; supplied exactly to the reconstruction likelihood",
            "background_expected_counts_per_frame_pixel": [rate / 9.0 for rate in BACKGROUND_RATES],
            "total_exposure": 1.0,
            "science_shape_detector_pixels": [20, 22],
            "padding_detector_pixels": 4,
            "detector_shape_pixels": [28, 30],
            "bin_factor": 3,
            "frames_per_arm": 9,
            "noise": "source and background Poisson counts; no read noise",
            "scene": "same three-source continuous axis-aligned Gaussian scene as development benchmark",
            "aligned_phases_yx": ALIGNED_PHASES.tolist(),
            "offgrid_phases_yx": OFFGRID_PHASES.tolist(),
            "truth_generator": "independent continuous Gaussian detector-pixel area integrals",
            "reconstruction": "Poisson Richardson-Lucy with known additive background and bilinear shift-and-bin source model",
            "paired_seed_design": "same fresh seed across aligned/off-grid conditions at each background level; identical stationary controls",
            "metrics": "fixed-interior relative RMSE and known-centre aperture centroid/flux metrics",
            "inference": "paired per-seed differences with 95% t confidence intervals",
            "limitations": [
                "background is known exactly; blind background estimation is not tested",
                "background is spatially uniform and temporally constant",
                "off-grid shifts remain approximated by bilinear high-resolution cell interpolation",
                "no read noise, background gradients, dark-current drift, PSF mismatch, or blind source detection",
                "iteration count was fixed from development evidence and not selected on validation data",
            ],
        },
        "summary_by_background": summary,
        "paired_comparisons": paired,
        "trials": records,
    }
    path = Path("dither_background_independent_validation.json")
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(path),
        "n_validation_seeds": len(VALIDATION_SEEDS),
        "background_rates": list(BACKGROUND_RATES),
        "fixed_iterations": list(ITERATIONS),
        "paired_rmse": {
            bg: {
                comparison: stats["relative_rmse"]
                for comparison, stats in comparisons.items()
            }
            for bg, comparisons in paired.items()
        },
    }, indent=2))


if __name__ == "__main__":
    main()
