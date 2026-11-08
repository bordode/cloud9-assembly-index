"""Photon-limited non-negative reconstruction for controlled dither experiments.

The data generator uses the independent continuous Gaussian pixel-integral
reference. Reconstruction estimates a non-negative high-resolution cell-flux
image with the discrete shift-and-bin operator. These are separate code paths.

The solver is unregularized Poisson Richardson-Lucy maximum likelihood.
Iteration count is reported as an early-stopping regularizer. Read noise is
excluded from this first experiment.
"""
from __future__ import annotations

import numpy as np

from research.sandbox.dithered_stack_operator import adjoint_operator, forward_operator
from research.sandbox.matched_exposure_acquisition import nine_phase_grid
from research.sandbox.pixel_integrated_reference import (
    gaussian_scene_subpixel_integrals,
    pixel_integrated_gaussian_frame,
)


def poisson_richardson_lucy(
    frames, phases_yx, frame_exposures, highres_shape, bin_factor,
    iterations=10, epsilon=1e-12,
):
    """Reconstruct a non-negative high-resolution rate image from Poisson data.

    Each frame has mean exposure times the shift-and-bin prediction. The
    multiplicative update uses the exact discrete adjoint. No smoothness prior
    or read-noise model is included.
    """
    observations = np.asarray(frames, dtype=float)
    phases = np.asarray(phases_yx, dtype=float)
    exposures = np.asarray(frame_exposures, dtype=float)
    shape = tuple(map(int, highres_shape))
    if observations.ndim != 3 or observations.shape[0] == 0:
        raise ValueError("frames must have shape (n_frames, detector_height, detector_width)")
    if phases.shape != (observations.shape[0], 2):
        raise ValueError("phases_yx must have one (row, column) pair per frame")
    if exposures.shape != (observations.shape[0],):
        raise ValueError("frame_exposures must contain one exposure per frame")
    if not np.all(np.isfinite(observations)) or np.any(observations < 0):
        raise ValueError("Poisson observations must be finite and non-negative")
    if not np.all(np.isfinite(phases)):
        raise ValueError("phases must be finite")
    if not np.all(np.isfinite(exposures)) or np.any(exposures <= 0):
        raise ValueError("frame exposures must be finite and positive")
    if len(shape) != 2 or min(shape) <= 0:
        raise ValueError("highres_shape must contain two positive dimensions")
    if not isinstance(bin_factor, (int, np.integer)) or bin_factor <= 0:
        raise ValueError("bin_factor must be a positive integer")
    if shape[0] % bin_factor or shape[1] % bin_factor:
        raise ValueError("high-resolution shape must be divisible by bin_factor")
    if observations.shape[1:] != (shape[0] // bin_factor, shape[1] // bin_factor):
        raise ValueError("detector frame dimensions do not match highres_shape and bin_factor")
    if not isinstance(iterations, (int, np.integer)) or iterations < 1:
        raise ValueError("iterations must be a positive integer")
    if not np.isfinite(epsilon) or epsilon <= 0:
        raise ValueError("epsilon must be finite and positive")

    detector_shape = observations.shape[1:]
    sensitivity = np.zeros(shape, dtype=float)
    for phase, exposure in zip(phases, exposures):
        sensitivity += exposure * adjoint_operator(
            np.ones(detector_shape), shape, bin_factor, tuple(phase)
        )

    total_counts = float(observations.sum())
    if total_counts <= 0:
        return np.zeros(shape, dtype=float)
    estimate = np.full(
        shape, total_counts / max(float(sensitivity.sum()), epsilon), dtype=float
    )
    safe_sensitivity = np.maximum(sensitivity, epsilon)

    for _ in range(int(iterations)):
        numerator = np.zeros_like(estimate)
        for frame, phase, exposure in zip(observations, phases, exposures):
            predicted = exposure * forward_operator(estimate, bin_factor, tuple(phase))
            ratio = frame / np.maximum(predicted, epsilon)
            numerator += exposure * adjoint_operator(
                ratio, shape, bin_factor, tuple(phase)
            )
        estimate *= numerator / safe_sensitivity
        estimate = np.maximum(estimate, 0.0)
    return estimate


def reconstruction_metrics(
    reconstruction, truth, bin_factor, padding_pixels, science_shape,
    sources_yx, aperture_radius_px=2.0,
):
    """Score a fixed interior and known-source apertures, not blind detection."""
    estimate = np.asarray(reconstruction, dtype=float)
    reference = np.asarray(truth, dtype=float)
    if estimate.shape != reference.shape or estimate.ndim != 2:
        raise ValueError("reconstruction and truth must be matching 2-D arrays")
    if not isinstance(bin_factor, (int, np.integer)) or bin_factor <= 0:
        raise ValueError("bin_factor must be a positive integer")
    if not np.isfinite(aperture_radius_px) or aperture_radius_px <= 0:
        raise ValueError("aperture_radius_px must be finite and positive")

    highres_science_shape = (science_shape[0] * bin_factor, science_shape[1] * bin_factor)
    pad = int(padding_pixels) * bin_factor
    estimate_crop = estimate[pad:pad + highres_science_shape[0],
                             pad:pad + highres_science_shape[1]]
    truth_crop = reference[pad:pad + highres_science_shape[0],
                           pad:pad + highres_science_shape[1]]
    if estimate_crop.shape != highres_science_shape or truth_crop.shape != highres_science_shape:
        raise ValueError("padded reconstruction does not contain the requested science crop")
    relative_rmse = float(
        np.linalg.norm(estimate_crop - truth_crop) /
        max(float(np.linalg.norm(truth_crop)), np.finfo(float).tiny)
    )

    rows, cols = np.indices(estimate.shape)
    row_centres = (rows + 0.5) / bin_factor
    col_centres = (cols + 0.5) / bin_factor
    source_errors = []
    source_flux_ratios = []
    for centre_y, centre_x in np.asarray(sources_yx, dtype=float):
        aperture = (
            (row_centres - centre_y) ** 2 + (col_centres - centre_x) ** 2
            <= aperture_radius_px ** 2
        )
        recovered = estimate[aperture]
        expected = reference[aperture]
        recovered_flux = float(recovered.sum())
        expected_flux = float(expected.sum())
        if recovered_flux <= 0 or expected_flux <= 0:
            source_errors.append(float("nan"))
            source_flux_ratios.append(float("nan"))
            continue
        centroid_y = float((row_centres[aperture] * recovered).sum() / recovered_flux)
        centroid_x = float((col_centres[aperture] * recovered).sum() / recovered_flux)
        source_errors.append(float(np.hypot(centroid_y - centre_y, centroid_x - centre_x)))
        source_flux_ratios.append(recovered_flux / expected_flux)

    return {
        "relative_rmse": relative_rmse,
        "mean_source_centroid_error_px": float(np.nanmean(source_errors)),
        "mean_aperture_flux_ratio": float(np.nanmean(source_flux_ratios)),
        "source_centroid_errors_px": source_errors,
        "source_aperture_flux_ratios": source_flux_ratios,
        "scoring": "fixed interior RMSE; known-centre apertures, not blind source detection",
    }


def simulate_reconstruction_trial(
    sources_yx, fluxes, sigma_yx_px, science_shape=(20, 22),
    padding_pixels=4, bin_factor=3, total_exposure=1.0, seed=20261108,
    iterations=(1, 2, 3, 5, 10), dither_phases_yx=None,
):
    """Run paired photon-only long, stationary, and dithered reconstruction arms.

    The nine stationary Poisson frames are summed to form the single-long
    image. This couples the controls exactly and preserves the Poisson
    additivity identity. Dithered observations are generated independently
    from exact continuous pixel-area integrals.
    """
    if not isinstance(bin_factor, (int, np.integer)) or bin_factor <= 0:
        raise ValueError("bin_factor must be a positive integer")
    if not np.isfinite(total_exposure) or total_exposure <= 0:
        raise ValueError("total_exposure must be finite and positive")
    if not isinstance(padding_pixels, (int, np.integer)) or padding_pixels < 0:
        raise ValueError("padding_pixels must be a non-negative integer")
    if len(science_shape) != 2 or min(science_shape) <= 0:
        raise ValueError("science_shape must contain two positive dimensions")
    iteration_values = tuple(iterations)
    if not iteration_values or any(
        not isinstance(value, (int, np.integer)) or value < 1
        for value in iteration_values
    ):
        raise ValueError("iterations must be a non-empty sequence of positive integers")

    phases = np.asarray(
        nine_phase_grid() if dither_phases_yx is None else dither_phases_yx,
        dtype=float,
    )
    if phases.shape != (9, 2) or not np.all(np.isfinite(phases)):
        raise ValueError("dither_phases_yx must contain nine finite (row, column) phases")
    if np.unique(phases, axis=0).shape[0] != 9:
        raise ValueError("dither phases must be distinct")
    if np.any(np.abs(phases) > 0.5):
        raise ValueError("dither phases must lie within +/-0.5 detector pixels")
    if not np.any(np.abs(phases - np.rint(phases)) > 1e-12):
        raise ValueError("dither phases must include fractional-pixel offsets")

    detector_shape = (
        science_shape[0] + 2 * padding_pixels,
        science_shape[1] + 2 * padding_pixels,
    )
    highres_shape = (
        detector_shape[0] * bin_factor,
        detector_shape[1] * bin_factor,
    )
    source_positions = np.asarray(sources_yx, dtype=float)
    truth = gaussian_scene_subpixel_integrals(
        highres_shape, bin_factor, source_positions, fluxes, sigma_yx_px
    )
    rng = np.random.default_rng(seed)
    frame_exposure = float(total_exposure) / 9.0

    stationary_mean = frame_exposure * pixel_integrated_gaussian_frame(
        detector_shape, source_positions, fluxes, sigma_yx_px, (0.0, 0.0)
    )
    stationary_frames = rng.poisson(stationary_mean, size=(9,) + detector_shape)
    single_long = stationary_frames.sum(axis=0)

    dithered_means = np.stack([
        frame_exposure * pixel_integrated_gaussian_frame(
            detector_shape, source_positions, fluxes, sigma_yx_px, tuple(phase)
        )
        for phase in phases
    ])
    dithered_frames = rng.poisson(dithered_means)

    results = []
    for count in iteration_values:
        single_estimate = poisson_richardson_lucy(
            single_long[None, :, :], [(0.0, 0.0)], [total_exposure],
            highres_shape, bin_factor, iterations=count,
        )
        stationary_estimate = poisson_richardson_lucy(
            stationary_frames, np.zeros((9, 2)), np.full(9, frame_exposure),
            highres_shape, bin_factor, iterations=count,
        )
        dithered_estimate = poisson_richardson_lucy(
            dithered_frames, phases, np.full(9, frame_exposure),
            highres_shape, bin_factor, iterations=count,
        )
        results.append({
            "iterations": int(count),
            "single_long": reconstruction_metrics(
                single_estimate, truth, bin_factor, padding_pixels,
                science_shape, source_positions,
            ),
            "nine_stationary": reconstruction_metrics(
                stationary_estimate, truth, bin_factor, padding_pixels,
                science_shape, source_positions,
            ),
            "nine_dithered": reconstruction_metrics(
                dithered_estimate, truth, bin_factor, padding_pixels,
                science_shape, source_positions,
            ),
            "stationary_long_max_abs_difference": float(
                np.max(np.abs(single_estimate - stationary_estimate))
            ),
        })

    return {
        "results": results,
        "metadata": {
            "seed": int(seed),
            "bin_factor": int(bin_factor),
            "total_exposure": float(total_exposure),
            "frame_count_stationary": 9,
            "frame_count_dithered": 9,
            "noise": "independent Poisson photon counts; no read noise",
            "truth_generator": "continuous axis-aligned Gaussian pixel-area integrals",
            "reconstruction": "non-negative Poisson Richardson-Lucy with bilinear shift-and-bin operator",
            "regularization": "early stopping only; iteration curve reported without truth-selected optimum",
            "dither_phases_yx": phases.tolist(),
            "scoring": "fixed science interior plus known-centre source apertures",
            "limitations": [
                "controlled Gaussian scene, not a general optical PSF",
                "known source centres define aperture metrics; this is not blind detection",
                "no read noise, background, PSF mismatch, or blind lambda selection",
                "dither phases should align to the high-resolution grid for this exact cell-shift model",
            ],
        },
    }
