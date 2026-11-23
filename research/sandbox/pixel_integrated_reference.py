"""Independent analytic pixel-area reference for Gaussian source scenes.

This module deliberately does not call the bilinear shift-and-bin operator.
It integrates a continuous, axis-aligned Gaussian source model over
rectangular subpixel cells or detector-pixel footprints using Gaussian CDFs.

Coordinates are measured in detector-pixel units from the upper-left edge of
the padded array. A positive frame phase moves scene content toward increasing
row/column indices, so detector pixel (i,j) integrates the unshifted scene over
[i-phase_y, i+1-phase_y] x [j-phase_x, j+1-phase_x].
"""
from __future__ import annotations

import numpy as np
from scipy.special import ndtr


def _validate_sources(sources_yx, fluxes, sigma_yx_px):
    positions = np.asarray(sources_yx, dtype=float)
    amplitudes = np.asarray(fluxes, dtype=float)
    sigmas = np.asarray(sigma_yx_px, dtype=float)
    if positions.ndim != 2 or positions.shape[1] != 2 or positions.shape[0] == 0:
        raise ValueError("sources_yx must be a non-empty (n_sources, 2) array")
    if amplitudes.shape != (len(positions),):
        raise ValueError("fluxes must contain one value per source")
    if sigmas.shape == (2,):
        sigmas = np.broadcast_to(sigmas, (len(positions), 2)).copy()
    if sigmas.shape != (len(positions), 2):
        raise ValueError("sigma_yx_px must be (2,) or (n_sources, 2)")
    if not np.all(np.isfinite(positions)) or not np.all(np.isfinite(amplitudes)):
        raise ValueError("source positions and fluxes must be finite")
    if not np.all(np.isfinite(sigmas)) or np.any(sigmas <= 0):
        raise ValueError("Gaussian sigmas must be finite and positive")
    if np.any(amplitudes < 0):
        raise ValueError("source fluxes must be non-negative")
    return positions, amplitudes, sigmas


def _cdf_cell_masses(edges, center, sigma):
    return np.diff(ndtr((edges - center) / sigma))


def gaussian_scene_subpixel_integrals(
    highres_shape,
    bin_factor,
    sources_yx,
    fluxes,
    sigma_yx_px,
):
    """Integrate a continuous Gaussian mixture into high-resolution cells.

    Each returned cell stores the total source flux integrated over that
    subpixel cell, not a point-sampled surface brightness.
    """
    if len(highres_shape) != 2:
        raise ValueError("highres_shape must contain (height, width)")
    height, width = map(int, highres_shape)
    if height <= 0 or width <= 0:
        raise ValueError("high-resolution dimensions must be positive")
    if not isinstance(bin_factor, (int, np.integer)) or bin_factor <= 0:
        raise ValueError("bin_factor must be a positive integer")
    if height % bin_factor or width % bin_factor:
        raise ValueError("high-resolution dimensions must be divisible by bin_factor")

    positions, amplitudes, sigmas = _validate_sources(
        sources_yx, fluxes, sigma_yx_px
    )
    y_edges = np.arange(height + 1, dtype=float) / bin_factor
    x_edges = np.arange(width + 1, dtype=float) / bin_factor
    result = np.zeros((height, width), dtype=float)
    for (center_y, center_x), flux, (sigma_y, sigma_x) in zip(
        positions, amplitudes, sigmas
    ):
        y_mass = _cdf_cell_masses(y_edges, center_y, sigma_y)
        x_mass = _cdf_cell_masses(x_edges, center_x, sigma_x)
        result += flux * np.outer(y_mass, x_mass)
    return result


def pixel_integrated_gaussian_frame(
    detector_shape,
    sources_yx,
    fluxes,
    sigma_yx_px,
    phase_yx=(0.0, 0.0),
):
    """Return exact continuous-Gaussian integrals over detector pixel areas."""
    if len(detector_shape) != 2:
        raise ValueError("detector_shape must contain (height, width)")
    height, width = map(int, detector_shape)
    if height <= 0 or width <= 0:
        raise ValueError("detector dimensions must be positive")
    if len(phase_yx) != 2 or not np.all(np.isfinite(phase_yx)):
        raise ValueError("phase_yx must contain two finite values")
    phase_y, phase_x = map(float, phase_yx)
    positions, amplitudes, sigmas = _validate_sources(
        sources_yx, fluxes, sigma_yx_px
    )
    y_edges = np.arange(height + 1, dtype=float) - phase_y
    x_edges = np.arange(width + 1, dtype=float) - phase_x
    result = np.zeros((height, width), dtype=float)
    for (center_y, center_x), flux, (sigma_y, sigma_x) in zip(
        positions, amplitudes, sigmas
    ):
        y_mass = _cdf_cell_masses(y_edges, center_y, sigma_y)
        x_mass = _cdf_cell_masses(x_edges, center_x, sigma_x)
        result += flux * np.outer(y_mass, x_mass)
    return result


def crop_common_interior(frame, padding_pixels, science_shape):
    """Crop the same central science footprint from a padded detector frame."""
    values = np.asarray(frame)
    if values.ndim != 2:
        raise ValueError("frame must be a 2-D detector image")
    if len(science_shape) != 2:
        raise ValueError("science_shape must contain (height, width)")
    pad = int(padding_pixels)
    science_height, science_width = map(int, science_shape)
    if pad < 0 or science_height <= 0 or science_width <= 0:
        raise ValueError("padding must be non-negative and science dimensions positive")
    expected = (science_height + 2 * pad, science_width + 2 * pad)
    if values.shape != expected:
        raise ValueError(f"padded frame shape must be {expected}, got {values.shape}")
    return values[pad:pad + science_height, pad:pad + science_width]
