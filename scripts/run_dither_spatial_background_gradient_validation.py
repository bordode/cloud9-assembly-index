"""Independent fixed-iteration test of known detector-fixed background gradients.

The background gradient is generated independently of the source scene and is
supplied exactly to the Poisson reconstruction likelihood. This is not a test
of blind background estimation.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import t

from research.sandbox.poisson_reconstruction import simulate_reconstruction_trial


# Fresh seeds, disjoint from both earlier development and validation sets.
DEVELOPMENT_SEEDS = tuple(range(2026111000, 2026111030))
PRIOR_VALIDATION_SEEDS = tuple(range(2026111200, 2026111230))
GRADIENT_VALIDATION_SEEDS = tuple(range(2026111300, 2026111330))
ITERATIONS = (2,)
MEAN_BACKGROUND_RATE = 0.5
GRADIENT_AMPLITUDES = (0.0, 0.25, 0.45)
CONDITIONS = ("nine_stationary", "aligned_dithered", "offgrid_dithered")
METRICS = (
    "relative_rmse",
    "mean_source_centroid_error_px",
    "mean_aperture_flux_abs_error",
)
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


def make_background_map(detector_shape, amplitude):
    """Horizontal linear gradient with fixed mean and detector-fixed pattern."""
    if amplitude < 0 or amplitude >= MEAN_BACKGROUND_RATE:
        raise ValueError("gradient amplitude must be in [0, mean background rate)")
    height, width = detector_shape
    horizontal = np.linspace(-1.0, 1.0, width, dtype=float)
    return np.broadcast_to(
        MEAN_BACKGROUND_RATE + amplitude * horizontal,
        (height, width),
    ).copy()


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


def metrics_for(result):
    ratios = np.asarray(result["source_aperture_flux_ratios"], dtype=float)
    return {
        "relative_rmse": result["relative_rmse"],
        "mean_source_centroid_error_px": result["mean_source_centroid_error_px"],
        "mean_aperture_flux_abs_error": float(np.mean(np.abs(ratios - 1.0))),
    }


def main():
    if set(DEVELOPMENT_SEEDS) & set(GRADIENT_VALIDATION_SEEDS):
        raise AssertionError("gradient validation seeds overlap development seeds")
    if set(PRIOR_VALIDATION_SEEDS) & set(GRADIENT_VALIDATION_SEEDS):
        raise AssertionError("gradient validation seeds overlap prior validation seeds")

    sources = np.asarray([
        [10.35, 11.20],
        [16.10, 19.65],
        [19.40, 8.80],
    ])
    fluxes = [1200.0, 760.0, 430.0]
    sigmas = [[0.72, 0.91], [1.05, 0.83], [0.88, 1.12]]
    science_shape = (20, 22)
    padding_pixels = 4
    detector_shape = (
        science_shape[0] + 2 * padding_pixels,
        science_shape[1] + 2 * padding_pixels,
    )
    records = []

    for amplitude in GRADIENT_AMPLITUDES:
        background_map = make_background_map(detector_shape, amplitude)
        for seed in GRADIENT_VALIDATION_SEEDS:
            common = dict(
                sources_yx=sources,
                fluxes=fluxes,
                sigma_yx_px=sigmas,
                science_shape=science_shape,
                padding_pixels=padding_pixels,
                bin_factor=3,
                total_exposure=1.0,
                seed=seed,
                iterations=ITERATIONS,
                background_rate=background_map,
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

            selected = {
                "nine_stationary": arow["nine_stationary"],
                "aligned_dithered": arow["nine_dithered"],
                "offgrid_dithered": orow["nine_dithered"],
            }
            for condition, result in selected.items():
                records.append({
                    "gradient_amplitude_counts_per_pixel": amplitude,
                    "background_minimum": float(background_map.min()),
                    "background_maximum": float(background_map.max()),
                    "background_mean": float(background_map.mean()),
                    "seed": seed,
                    "iterations": 2,
                    "condition": condition,
                    **metrics_for(result),
                })

    summary = {}
    paired = {}
    for amplitude in GRADIENT_AMPLITUDES:
        key = str(amplitude)
        subset = [r for r in records if r["gradient_amplitude_counts_per_pixel"] == amplitude]
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
            ("aligned_minus_stationary", "aligned_dithered", "nine_stationary"),
            ("offgrid_minus_stationary", "offgrid_dithered", "nine_stationary"),
            ("offgrid_minus_aligned", "offgrid_dithered", "aligned_dithered"),
        ):
            paired[key][comparison] = {
                metric: summarize([
                    by_condition[left][seed][metric] - by_condition[right][seed][metric]
                    for seed in GRADIENT_VALIDATION_SEEDS
                ])
                for metric in METRICS
            }

    output = {
        "protocol": {
            "status": "independent fixed-iteration spatial-gradient validation",
            "development_seeds": list(DEVELOPMENT_SEEDS),
            "prior_uniform_background_validation_seeds": list(PRIOR_VALIDATION_SEEDS),
            "gradient_validation_seeds": list(GRADIENT_VALIDATION_SEEDS),
            "iterations": list(ITERATIONS),
            "iteration_selection": "fixed at two before this validation; no retuning",
            "mean_background_rate_counts_per_detector_pixel_per_exposure_unit": MEAN_BACKGROUND_RATE,
            "gradient_amplitudes": list(GRADIENT_AMPLITUDES),
            "gradient_axis": "horizontal detector columns only",
            "gradient_definition": "mean rate plus amplitude times a linear coordinate spanning -1 to +1 across detector columns",
            "background_assumption": "known exactly, detector-fixed, spatially varying additive Poisson background map supplied to every frame likelihood",
            "background_maps": {
                str(a): {
                    "minimum": float(make_background_map(detector_shape, a).min()),
                    "maximum": float(make_background_map(detector_shape, a).max()),
                    "mean": float(make_background_map(detector_shape, a).mean()),
                }
                for a in GRADIENT_AMPLITUDES
            },
            "science_shape_detector_pixels": list(science_shape),
            "detector_shape_pixels": list(detector_shape),
            "padding_detector_pixels": padding_pixels,
            "bin_factor": 3,
            "frames_per_arm": 9,
            "noise": "source and background Poisson counts; no read noise",
            "scene": "same three-source continuous axis-aligned Gaussian scene as prior validation",
            "paired_seed_design": "same fresh seed and same detector-fixed background map across aligned/off-grid conditions and stationary controls",
            "metrics": "fixed-interior relative RMSE and known-centre aperture centroid/flux metrics",
            "inference": "paired per-seed differences with 95% t confidence intervals",
            "limitations": [
                "background map is known exactly; blind estimation is not tested",
                "gradient is linear and horizontal only; vertical, curved, time-varying and source-correlated backgrounds are untested",
                "no read noise, dark-current drift, PSF mismatch, or blind source detection",
                "off-grid shifts remain approximated by bilinear high-resolution cell interpolation",
            ],
        },
        "summary_by_gradient_amplitude": summary,
        "paired_comparisons": paired,
        "trials": records,
    }
    path = Path("dither_spatial_background_gradient_validation.json")
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(path),
        "n_validation_seeds": len(GRADIENT_VALIDATION_SEEDS),
        "gradient_amplitudes": list(GRADIENT_AMPLITUDES),
        "fixed_iterations": list(ITERATIONS),
        "paired_rmse": {
            level: {
                comparison: stats["relative_rmse"]
                for comparison, stats in comparisons.items()
            }
            for level, comparisons in paired.items()
        },
    }, indent=2))


if __name__ == "__main__":
    main()
