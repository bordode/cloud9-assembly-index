"""Independent test with a hidden linear detector background estimated from off-source borders.

The true background is used only to generate Poisson observations and score the
estimator. Reconstruction receives a fitted horizontal gradient, never the true
map. The border calibration region is declared in advance and excludes the
science-source region by design.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.stats import t

from research.sandbox.matched_exposure_acquisition import nine_phase_grid
from research.sandbox.pixel_integrated_reference import (
    gaussian_scene_subpixel_integrals,
    pixel_integrated_gaussian_frame,
)
from research.sandbox.poisson_reconstruction import (
    poisson_richardson_lucy,
    reconstruction_metrics,
)

SEEDS = tuple(range(2026111400, 2026111430))
PRIOR_SEEDS = (
    tuple(range(2026111000, 2026111030))
    + tuple(range(2026111200, 2026111230))
    + tuple(range(2026111300, 2026111330))
)
ITERATIONS = 2
MEAN_BACKGROUND_RATE = 0.5
GRADIENT_AMPLITUDES = (0.0, 0.25, 0.45)
BORDER_WIDTH = 3
SCIENCE_SHAPE = (20, 22)
PADDING_PIXELS = 4
BIN_FACTOR = 3
TOTAL_EXPOSURE = 1.0
SOURCES = np.asarray([[10.35, 11.20], [16.10, 19.65], [19.40, 8.80]])
FLUXES = [1200.0, 760.0, 430.0]
SIGMAS = [[0.72, 0.91], [1.05, 0.83], [0.88, 1.12]]
ALIGNED_PHASES = np.asarray([
    (y, x) for y in (-1.0 / 3.0, 0.0, 1.0 / 3.0)
    for x in (-1.0 / 3.0, 0.0, 1.0 / 3.0)
], dtype=float)
OFFGRID_PHASES = np.asarray([
    (y, x) for y in (-0.29, 0.0, 0.29)
    for x in (-0.23, 0.0, 0.23)
], dtype=float)
CONDITIONS = ("nine_stationary", "aligned_dithered", "offgrid_dithered")


def make_background_map(detector_shape, amplitude):
    height, width = detector_shape
    x = np.linspace(-1.0, 1.0, width, dtype=float)
    return np.broadcast_to(MEAN_BACKGROUND_RATE + amplitude * x, (height, width)).copy()


def estimate_horizontal_background(frames, frame_exposures, border_width=BORDER_WIDTH):
    """Fit non-negative linear background endpoints using border pixels only.

    Counts are pooled over frames at each detector pixel. The Poisson likelihood
    uses the known exposure schedule but does not receive the true background.
    """
    data = np.asarray(frames, dtype=float)
    exposures = np.asarray(frame_exposures, dtype=float)
    if data.ndim != 3 or data.shape[0] == 0:
        raise ValueError("frames must have shape (n_frames, height, width)")
    if exposures.shape != (data.shape[0],) or np.any(exposures <= 0):
        raise ValueError("one positive exposure is required per frame")
    if not np.all(np.isfinite(data)) or np.any(data < 0):
        raise ValueError("frames must be finite and non-negative")
    height, width = data.shape[1:]
    if border_width < 1 or 2 * border_width >= min(height, width):
        raise ValueError("border_width is invalid for detector dimensions")

    border = np.zeros((height, width), dtype=bool)
    border[:border_width, :] = True
    border[-border_width:, :] = True
    border[:, :border_width] = True
    border[:, -border_width:] = True

    x = np.linspace(-1.0, 1.0, width, dtype=float)
    x_map = np.broadcast_to(x, (height, width))
    observed = data.sum(axis=0)[border]
    total_exposure = float(exposures.sum())
    exposure_map = np.full((height, width), total_exposure, dtype=float)[border]
    coordinate = x_map[border]

    def objective(endpoints):
        left, right = endpoints
        rate = left * (1.0 - coordinate) / 2.0 + right * (1.0 + coordinate) / 2.0
        mean = np.maximum(exposure_map * rate, 1e-12)
        return float(np.sum(mean - observed * np.log(mean)))

    initial = max(float(observed.sum() / exposure_map.sum()), 1e-4)
    fit = minimize(
        objective,
        x0=np.asarray([initial, initial]),
        method="L-BFGS-B",
        bounds=((1e-8, None), (1e-8, None)),
    )
    if not fit.success or not np.all(np.isfinite(fit.x)):
        raise RuntimeError(f"background border fit failed: {fit.message}")
    left, right = map(float, fit.x)
    row = left * (1.0 - x) / 2.0 + right * (1.0 + x) / 2.0
    return np.broadcast_to(row, (height, width)).copy(), {
        "left_endpoint_rate": left,
        "right_endpoint_rate": right,
        "border_width_pixels": int(border_width),
        "calibration_pixel_count": int(border.sum()),
        "fit_success": bool(fit.success),
    }


def summarize(values):
    values = np.asarray(values, dtype=float)
    mean = float(values.mean())
    sd = float(values.std(ddof=1))
    half = float(t.ppf(0.975, len(values) - 1) * sd / np.sqrt(len(values)))
    return {"n": int(len(values)), "mean": mean, "sd": sd,
            "ci95_mean": [mean - half, mean + half]}


def trial(seed, amplitude, contamination_fraction=0.0, contamination_rate=1.0):
    detector_shape = (
        SCIENCE_SHAPE[0] + 2 * PADDING_PIXELS,
        SCIENCE_SHAPE[1] + 2 * PADDING_PIXELS,
    )
    highres_shape = (detector_shape[0] * BIN_FACTOR, detector_shape[1] * BIN_FACTOR)
    truth_background = make_background_map(detector_shape, amplitude)
    if not 0.0 <= contamination_fraction < 1.0:
        raise ValueError("contamination_fraction must be in [0, 1)")
    border_mask = np.zeros(detector_shape, dtype=bool)
    border_mask[:BORDER_WIDTH, :] = True
    border_mask[-BORDER_WIDTH:, :] = True
    border_mask[:, :BORDER_WIDTH] = True
    border_mask[:, -BORDER_WIDTH:] = True
    border_indices = np.flatnonzero(border_mask)
    n_contaminated = int(round(contamination_fraction * len(border_indices)))
    mask_rng = np.random.default_rng(seed + 700000)
    selected = mask_rng.choice(border_indices, size=n_contaminated, replace=False)
    contamination_map = np.zeros(detector_shape, dtype=float)
    contamination_map.flat[selected] = contamination_rate
    observed_background = truth_background + contamination_map
    truth = gaussian_scene_subpixel_integrals(
        highres_shape, BIN_FACTOR, SOURCES, FLUXES, SIGMAS
    )
    frame_exposure = TOTAL_EXPOSURE / 9.0
    stationary_mean = frame_exposure * pixel_integrated_gaussian_frame(
        detector_shape, SOURCES, FLUXES, SIGMAS, (0.0, 0.0)
    )
    stationary_rng = np.random.default_rng(seed)
    stationary_frames = stationary_rng.poisson(
        stationary_mean + frame_exposure * observed_background,
        size=(9,) + detector_shape,
    )

    arms = {"nine_stationary": (stationary_frames, np.zeros((9, 2)))}
    for name, phases in (("aligned_dithered", ALIGNED_PHASES),
                         ("offgrid_dithered", OFFGRID_PHASES)):
        means = np.stack([
            frame_exposure * pixel_integrated_gaussian_frame(
                detector_shape, SOURCES, FLUXES, SIGMAS, tuple(phase)
            ) + frame_exposure * observed_background
            for phase in phases
        ])
        rng = np.random.default_rng(seed + (1 if name == "aligned_dithered" else 2))
        arms[name] = (rng.poisson(means), phases)

    records = {}
    for name, (frames, phases) in arms.items():
        estimated_background, fit_info = estimate_horizontal_background(
            frames, np.full(9, frame_exposure)
        )
        estimate = poisson_richardson_lucy(
            frames, phases, np.full(9, frame_exposure),
            highres_shape, BIN_FACTOR, iterations=ITERATIONS,
            background_rate=estimated_background,
        )
        metrics = reconstruction_metrics(
            estimate, truth, BIN_FACTOR, PADDING_PIXELS,
            SCIENCE_SHAPE, SOURCES,
        )
        records[name] = {
            "relative_rmse": metrics["relative_rmse"],
            "mean_source_centroid_error_px": metrics["mean_source_centroid_error_px"],
            "mean_aperture_flux_abs_error": float(np.mean(np.abs(
                np.asarray(metrics["source_aperture_flux_ratios"]) - 1.0
            ))),
            "background_map_rmse": float(np.sqrt(np.mean(
                (estimated_background - truth_background) ** 2
            ))),
            "background_mean_abs_error": float(abs(
                estimated_background.mean() - truth_background.mean()
            )),
            "background_fit": fit_info,
            "calibration_contamination_fraction": float(contamination_fraction),
            "calibration_contamination_rate": float(contamination_rate),
            "calibration_contaminated_pixel_count": int(n_contaminated),
        }
    return records


def main():
    if set(SEEDS) & set(PRIOR_SEEDS):
        raise AssertionError("new blind-background seeds overlap prior experiments")
    records = []
    for amplitude in GRADIENT_AMPLITUDES:
        for seed in SEEDS:
            for condition, metrics in trial(seed, amplitude).items():
                records.append({
                    "seed": seed,
                    "gradient_amplitude": amplitude,
                    "condition": condition,
                    "iterations": ITERATIONS,
                    **metrics,
                })

    summary, paired = {}, {}
    metrics = (
        "relative_rmse", "mean_source_centroid_error_px",
        "mean_aperture_flux_abs_error", "background_map_rmse",
        "background_mean_abs_error",
    )
    for amplitude in GRADIENT_AMPLITUDES:
        subset = [r for r in records if r["gradient_amplitude"] == amplitude]
        by_condition = {
            c: {r["seed"]: r for r in subset if r["condition"] == c}
            for c in CONDITIONS
        }
        key = str(amplitude)
        summary[key] = {
            c: {m: summarize([v[m] for v in rows.values()]) for m in metrics}
            for c, rows in by_condition.items()
        }
        paired[key] = {}
        for label, left, right in (
            ("aligned_minus_stationary", "aligned_dithered", "nine_stationary"),
            ("offgrid_minus_stationary", "offgrid_dithered", "nine_stationary"),
            ("offgrid_minus_aligned", "offgrid_dithered", "aligned_dithered"),
        ):
            paired[key][label] = {
                m: summarize([
                    by_condition[left][s][m] - by_condition[right][s][m]
                    for s in SEEDS
                ]) for m in metrics
            }

    output = {
        "protocol": {
            "status": "independent blind-background-estimation validation",
            "seeds": list(SEEDS),
            "prior_seed_ranges": [[2026111000, 2026111029],
                                  [2026111200, 2026111229],
                                  [2026111300, 2026111329]],
            "iterations": ITERATIONS,
            "mean_background_rate": MEAN_BACKGROUND_RATE,
            "gradient_amplitudes": list(GRADIENT_AMPLITUDES),
            "true_background_definition": "0.5 + amplitude*x; x spans -1 to +1 across detector columns",
            "background_available_to_reconstruction": "estimated only from outer detector border pixels; true map is not supplied",
            "estimator": "Poisson maximum-likelihood fit of non-negative left/right endpoint rates for a horizontal linear gradient",
            "border_width_pixels": BORDER_WIDTH,
            "frames_per_arm": 9,
            "total_exposure": TOTAL_EXPOSURE,
            "noise": "independent source and background Poisson counts; no read noise",
            "primary_metric": "fixed-interior relative RMSE",
            "secondary_metrics": ["known-centre centroid error", "absolute aperture-flux error",
                                  "background-map RMSE", "background mean absolute error"],
            "limitations": [
                "calibration assumes a source-free outer detector border",
                "background model is restricted to a horizontal linear gradient",
                "no read noise, temporal drift, curved or vertical gradient, source-correlated background, or PSF mismatch",
                "off-grid shifts retain bilinear high-resolution cell interpolation",
            ],
        },
        "summary_by_gradient_amplitude": summary,
        "paired_comparisons": paired,
        "trials": records,
    }
    path = Path("dither_blind_background_estimation_validation.json")
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(path),
        "seeds": len(SEEDS),
        "gradient_amplitudes": list(GRADIENT_AMPLITUDES),
        "paired_rmse": {
            level: {
                comparison: stats["relative_rmse"]
                for comparison, stats in comparisons.items()
            } for level, comparisons in paired.items()
        },
    }, indent=2))


if __name__ == "__main__":
    main()
