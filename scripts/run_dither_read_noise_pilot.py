"""Paired pilot for known-background Poisson-Gaussian dither reconstruction."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import t

from research.sandbox.pixel_integrated_reference import (
    gaussian_scene_subpixel_integrals,
    pixel_integrated_gaussian_frame,
)
from research.sandbox.poisson_reconstruction import reconstruction_metrics
from research.sandbox.poisson_gaussian_reconstruction import poisson_gaussian_em

SEEDS = tuple(range(2026111200, 2026111212))
READ_NOISE_SIGMAS = (0.5, 1.0, 2.0)
BACKGROUND_RATE = 0.5
ITERATIONS = (1, 2, 3, 5)
ALIGNED_PHASES = np.asarray([
    (y, x) for y in (-1/3, 0.0, 1/3) for x in (-1/3, 0.0, 1/3)
], dtype=float)
OFFGRID_PHASES = np.asarray([
    (y, x) for y in (-0.29, 0.0, 0.29) for x in (-0.23, 0.0, 0.23)
], dtype=float)


def stats(values):
    x = np.asarray(values, dtype=float)
    mean = float(x.mean())
    half = float(t.ppf(0.975, len(x)-1) * x.std(ddof=1) / np.sqrt(len(x)))
    return {"n": int(len(x)), "mean": mean, "ci95_mean": [mean-half, mean+half]}


def acquire(rng, phases, sources, fluxes, sigmas, detector_shape, exposure, read_sigma):
    means = np.stack([
        exposure * (
            pixel_integrated_gaussian_frame(
                detector_shape, sources, fluxes, sigmas, tuple(phase)
            ) + BACKGROUND_RATE
        )
        for phase in phases
    ])
    photons = rng.poisson(means)
    return photons + rng.normal(0.0, read_sigma, size=photons.shape)


def main():
    science_shape = (20, 22)
    padding = 4
    detector_shape = (28, 30)
    bin_factor = 3
    highres_shape = (detector_shape[0]*bin_factor, detector_shape[1]*bin_factor)
    sources = np.asarray([[10.35, 11.20], [16.10, 19.65], [19.40, 8.80]])
    fluxes = [1200.0, 760.0, 430.0]
    sigmas = [[0.72, 0.91], [1.05, 0.83], [0.88, 1.12]]
    truth = gaussian_scene_subpixel_integrals(
        highres_shape, bin_factor, sources, fluxes, sigmas
    )
    exposure = 1.0 / 9.0
    records = []

    for seed in SEEDS:
        # A common stationary acquisition is reused in both paired phase comparisons.
        for read_sigma in READ_NOISE_SIGMAS:
            stationary_rng = np.random.default_rng(seed + int(read_sigma*100000))
            stationary = acquire(
                stationary_rng, np.zeros((9, 2)), sources, fluxes, sigmas,
                detector_shape, exposure, read_sigma,
            )
            arms = {"nine_stationary": (stationary, np.zeros((9, 2)))}
            for name, phases, offset in (
                ("aligned_dithered", ALIGNED_PHASES, 1000000),
                ("offgrid_dithered", OFFGRID_PHASES, 2000000),
            ):
                rng = np.random.default_rng(seed + int(read_sigma*100000) + offset)
                arms[name] = (
                    acquire(rng, phases, sources, fluxes, sigmas,
                            detector_shape, exposure, read_sigma),
                    phases,
                )

            for arm, (frames, phases) in arms.items():
                for count in ITERATIONS:
                    estimate = poisson_gaussian_em(
                        frames, phases, np.full(9, exposure), highres_shape,
                        bin_factor, iterations=count, background_rate=BACKGROUND_RATE,
                        read_noise_sigma=read_sigma,
                    )
                    metric = reconstruction_metrics(
                        estimate, truth, bin_factor, padding, science_shape, sources
                    )
                    records.append({
                        "seed": seed,
                        "read_noise_sigma": read_sigma,
                        "iterations": count,
                        "condition": arm,
                        "relative_rmse": metric["relative_rmse"],
                        "centroid_error_px": metric["mean_source_centroid_error_px"],
                        "aperture_flux_abs_error": float(np.mean(np.abs(
                            np.asarray(metric["source_aperture_flux_ratios"]) - 1.0
                        ))),
                    })

    summary = {}
    paired = {}
    for sigma in READ_NOISE_SIGMAS:
        summary[str(sigma)] = {}
        paired[str(sigma)] = {}
        for iteration in ITERATIONS:
            subset = [r for r in records if r["read_noise_sigma"] == sigma
                      and r["iterations"] == iteration]
            by_arm = {
                arm: {r["seed"]: r for r in subset if r["condition"] == arm}
                for arm in ("nine_stationary", "aligned_dithered", "offgrid_dithered")
            }
            summary[str(sigma)][str(iteration)] = {
                arm: stats([r["relative_rmse"] for r in rows.values()])
                for arm, rows in by_arm.items()
            }
            paired[str(sigma)][str(iteration)] = {}
            for arm in ("aligned_dithered", "offgrid_dithered"):
                paired[str(sigma)][str(iteration)][arm + "_minus_stationary_rmse"] = stats([
                    by_arm[arm][seed]["relative_rmse"]
                    - by_arm["nine_stationary"][seed]["relative_rmse"]
                    for seed in SEEDS
                ])

    output = {
        "protocol": {
            "seeds": list(SEEDS),
            "read_noise_sigma_electrons_per_read": list(READ_NOISE_SIGMAS),
            "known_uniform_poisson_background_rate": BACKGROUND_RATE,
            "total_exposure": 1.0,
            "frames_per_arm": 9,
            "frame_exposure": exposure,
            "iterations": list(ITERATIONS),
            "noise_model": "independent Poisson source plus known uniform Poisson background, followed by independent zero-mean Gaussian read noise per pixel per frame",
            "truth": "continuous axis-aligned Gaussian detector-pixel integrals",
            "reconstruction": "exact discrete Poisson-Gaussian latent-count EM with known background and bilinear shift-and-bin source operator",
            "comparison": "nine stationary, nine aligned-dither, nine off-grid-dither; common stationary observations reused within each seed/read-noise level",
            "limitations": [
                "12-seed pilot; estimates are preliminary",
                "read noise is independent, homoscedastic and Gaussian",
                "background is known exactly and spatially uniform",
                "controlled Gaussian scene; no realistic optical PSF or detector effects",
                "known-centre aperture metrics are not blind source detection",
                "iteration checkpoints are descriptive, not an independently calibrated stopping rule",
            ],
        },
        "summary_by_read_noise_and_iteration": summary,
        "paired_rmse_differences": paired,
        "trials": records,
    }
    Path("dither_read_noise_pilot.json").write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\\n", encoding="utf-8"
    )
    print(json.dumps({"output": "dither_read_noise_pilot.json",
                      "seeds": len(SEEDS), "read_noise_sigmas": list(READ_NOISE_SIGMAS),
                      "iterations": list(ITERATIONS),
                      "paired_rmse_differences": paired}, indent=2))


if __name__ == "__main__":
    main()
