"""Matched-exposure acquisition simulations for controlled dither experiments.

The input scene is a padded high-resolution array of expected detected
photo-electrons per unit exposure in each subpixel cell. The existing
shift-and-bin operator maps that rate scene to detector-pixel rates.

Three arms are simulated:
* one long exposure (one detector readout);
* nine stationary exposures, each E/9 (nine readouts);
* nine phase-dithered exposures, each E/9 (nine readouts).

Photon counts are independent Poisson draws per exposure/frame. Optional
read noise is independent Gaussian noise per detector pixel per readout, with
the same per-read standard deviation in both nine-frame arms. Thus, after
summing frames, the nine-frame arms incur nine read-noise contributions while
the single-long arm incurs one. This difference is intentional and reported.

This is a controlled discrete bilinear shift-and-bin simulation, not a
continuous optical PSF or exact pixel-response integral.
"""
from __future__ import annotations

import numpy as np

from research.sandbox.dithered_stack_operator import (
    forward_operator,
    forward_stack,
)

N_FRAMES = 9
ZERO_PHASE = (0.0, 0.0)


def nine_phase_grid() -> tuple[tuple[float, float], ...]:
    """Return a 3x3 grid of distinct fractional detector-pixel phases."""
    offsets = (-1.0 / 3.0, 0.0, 1.0 / 3.0)
    return tuple((row, col) for row in offsets for col in offsets)


def _validate_phases(phases_yx) -> np.ndarray:
    phases = np.asarray(phases_yx, dtype=float)
    if phases.shape != (N_FRAMES, 2):
        raise ValueError("dither_phases_yx must contain exactly nine (row, column) phases")
    if not np.all(np.isfinite(phases)):
        raise ValueError("dither phases must be finite")
    if np.any(np.abs(phases) > 0.5):
        raise ValueError("dither phases must lie within +/-0.5 detector pixels")
    if np.unique(phases, axis=0).shape[0] != N_FRAMES:
        raise ValueError("the nine dither phases must be distinct")
    if not np.any(np.abs(phases - np.rint(phases)) > 1e-12):
        raise ValueError("the dither sequence must include fractional-pixel offsets")
    return phases


def _draw_noisy_frames(expected_counts: np.ndarray, rng: np.random.Generator,
                       read_noise_sigma: float) -> np.ndarray:
    """Draw independent Poisson counts and optional independent read noise."""
    counts = rng.poisson(expected_counts).astype(float)
    if read_noise_sigma:
        counts += rng.normal(0.0, read_noise_sigma, size=counts.shape)
    return counts


def simulate_matched_exposure_arms(
    highres_scene: np.ndarray,
    bin_factor: int,
    total_exposure: float,
    dither_phases_yx=None,
    rng: np.random.Generator | int | None = None,
    read_noise_sigma: float = 0.0,
) -> dict:
    """Simulate single-long, nine-stationary, and nine-dithered observations.

    Parameters
    ----------
    highres_scene:
        Non-negative 2-D padded rate image. Each cell contains expected
        detected photo-electrons per unit exposure in that subpixel cell.
    bin_factor:
        High-resolution cells per detector pixel along each axis.
    total_exposure:
        Total exposure E, in arbitrary but consistent exposure units.
    dither_phases_yx:
        Exactly nine distinct (row, column) phases in detector-pixel units.
        Defaults to a 3x3 grid at offsets -1/3, 0, +1/3 pixels.
    rng:
        NumPy Generator, integer seed, or None. Reusing the same integer seed
        reproduces the complete three-arm experiment.
    read_noise_sigma:
        Gaussian read-noise standard deviation in electrons per pixel per
        readout. Zero gives the photon-noise-only primary model.

    Returns
    -------
    dict
        Observations, expected counts, and metadata. Stack axes are
        (frame, detector_row, detector_column). No frames are summed.
    """
    scene = np.asarray(highres_scene, dtype=float)
    if scene.ndim != 2 or scene.size == 0:
        raise ValueError("highres_scene must be a non-empty 2-D array")
    if not np.all(np.isfinite(scene)) or np.any(scene < 0):
        raise ValueError("highres_scene must contain finite non-negative rates")
    if not np.isfinite(total_exposure) or total_exposure <= 0:
        raise ValueError("total_exposure must be finite and positive")
    if not np.isfinite(read_noise_sigma) or read_noise_sigma < 0:
        raise ValueError("read_noise_sigma must be finite and non-negative")

    phases = _validate_phases(
        nine_phase_grid() if dither_phases_yx is None else dither_phases_yx
    )
    generator = rng if isinstance(rng, np.random.Generator) else np.random.default_rng(rng)
    frame_exposure = float(total_exposure) / N_FRAMES

    stationary_rate = forward_operator(scene, bin_factor, ZERO_PHASE)
    dithered_rate = forward_stack(scene, bin_factor, phases)
    expected_single = float(total_exposure) * stationary_rate
    expected_stationary = np.broadcast_to(
        frame_exposure * stationary_rate, (N_FRAMES,) + stationary_rate.shape
    ).copy()
    expected_dithered = frame_exposure * dithered_rate

    single_long = _draw_noisy_frames(expected_single, generator, read_noise_sigma)
    stationary_stack = _draw_noisy_frames(
        expected_stationary, generator, read_noise_sigma
    )
    dithered_stack = _draw_noisy_frames(
        expected_dithered, generator, read_noise_sigma
    )

    return {
        "single_long": single_long,
        "stationary_stack": stationary_stack,
        "dithered_stack": dithered_stack,
        "expected_single_long": expected_single,
        "expected_stationary_stack": expected_stationary,
        "expected_dithered_stack": expected_dithered,
        "metadata": {
            "total_exposure": float(total_exposure),
            "frame_exposure": frame_exposure,
            "frame_count_single": 1,
            "frame_count_stationary": N_FRAMES,
            "frame_count_dithered": N_FRAMES,
            "read_noise_sigma_per_readout": float(read_noise_sigma),
            "read_noise_readouts": {
                "single_long": 1,
                "stationary_stack": N_FRAMES,
                "dithered_stack": N_FRAMES,
            },
            "photon_noise": "independent Poisson draw for every pixel in every frame",
            "read_noise": "independent Gaussian draw per pixel per readout",
            "phase_units": "detector pixels; (row, column)",
            "forward_model": "non-periodic bilinear shift followed by block-sum integration",
        },
    }
