"""Non-periodic subpixel shift-and-bin operators for controlled dither tests.

The input is a padded high-resolution array of subpixel-cell fluxes. A frame
phase is specified in detector-pixel units, converted to high-resolution cells,
applied with separable linear interpolation and zero extension, then summed
into detector pixels. The adjoint is the exact algebraic transpose of this
discrete forward operator.

This is a deliberately explicit discrete acquisition model. Linear
interpolation is not a substitute for a continuous optical PSF or an exact
pixel-response integral; those must be modelled separately in later work.
"""
from __future__ import annotations

import numpy as np


def _axis_stencil(length: int, shift: float):
    """Return source indices, weights and validity masks for output samples.

    Output index i samples the input at i - shift. Out-of-bounds samples are
    zero (non-periodic boundary); no wraparound is used.
    """
    if not np.isfinite(shift):
        raise ValueError("phase shifts must be finite")
    coordinate = np.arange(length, dtype=float) - float(shift)
    lower = np.floor(coordinate).astype(np.intp)
    fraction = coordinate - lower
    upper = lower + 1
    lower_valid = (lower >= 0) & (lower < length)
    upper_valid = (upper >= 0) & (upper < length)
    return lower, upper, 1.0 - fraction, fraction, lower_valid, upper_valid


def _weight_shape(length: int, ndim: int) -> tuple[int, ...]:
    return (length,) + (1,) * (ndim - 1)


def _shift_axis_forward(array: np.ndarray, axis: int, shift: float) -> np.ndarray:
    moved = np.moveaxis(array, axis, 0)
    lower, upper, w_lower, w_upper, valid_lower, valid_upper = _axis_stencil(
        moved.shape[0], shift
    )
    result = np.zeros_like(moved, dtype=np.result_type(moved.dtype, np.float64))
    out_lower = np.flatnonzero(valid_lower)
    out_upper = np.flatnonzero(valid_upper)
    result[out_lower] += moved[lower[out_lower]] * w_lower[out_lower].reshape(
        _weight_shape(len(out_lower), moved.ndim)
    )
    result[out_upper] += moved[upper[out_upper]] * w_upper[out_upper].reshape(
        _weight_shape(len(out_upper), moved.ndim)
    )
    return np.moveaxis(result, 0, axis)


def _shift_axis_adjoint(array: np.ndarray, axis: int, shift: float) -> np.ndarray:
    moved = np.moveaxis(array, axis, 0)
    lower, upper, w_lower, w_upper, valid_lower, valid_upper = _axis_stencil(
        moved.shape[0], shift
    )
    result = np.zeros_like(moved, dtype=np.result_type(moved.dtype, np.float64))
    out_lower = np.flatnonzero(valid_lower)
    out_upper = np.flatnonzero(valid_upper)
    np.add.at(
        result,
        lower[out_lower],
        moved[out_lower] * w_lower[out_lower].reshape(
            _weight_shape(len(out_lower), moved.ndim)
        ),
    )
    np.add.at(
        result,
        upper[out_upper],
        moved[out_upper] * w_upper[out_upper].reshape(
            _weight_shape(len(out_upper), moved.ndim)
        ),
    )
    return np.moveaxis(result, 0, axis)


def _validate_highres_shape(highres_shape: tuple[int, int], bin_factor: int) -> tuple[int, int]:
    if len(highres_shape) != 2:
        raise ValueError("highres_shape must contain (height, width)")
    height, width = (int(highres_shape[0]), int(highres_shape[1]))
    if height <= 0 or width <= 0:
        raise ValueError("high-resolution dimensions must be positive")
    if not isinstance(bin_factor, (int, np.integer)) or bin_factor <= 0:
        raise ValueError("bin_factor must be a positive integer")
    if height % bin_factor or width % bin_factor:
        raise ValueError("high-resolution dimensions must be divisible by bin_factor")
    return height, width


def forward_operator(
    highres_scene: np.ndarray,
    bin_factor: int,
    phase_yx: tuple[float, float] = (0.0, 0.0),
) -> np.ndarray:
    """Shift a padded high-resolution scene and sum subpixels into detector pixels.

    Parameters
    ----------
    highres_scene:
        2-D padded high-resolution subpixel-cell flux array.
    bin_factor:
        Number of high-resolution cells along each detector-pixel axis.
    phase_yx:
        Frame phase in detector-pixel units (row, column). Fractional values
        are allowed. Positive values move scene content toward increasing
        row/column indices. Zero extension is used at the padded-array edge.
    """
    scene = np.asarray(highres_scene, dtype=float)
    if scene.ndim != 2:
        raise ValueError("highres_scene must be a 2-D array")
    _validate_highres_shape(scene.shape, bin_factor)
    if len(phase_yx) != 2:
        raise ValueError("phase_yx must contain (row_phase, column_phase)")
    shift_y, shift_x = (
        float(phase_yx[0]) * bin_factor,
        float(phase_yx[1]) * bin_factor,
    )
    shifted = _shift_axis_forward(scene, 0, shift_y)
    shifted = _shift_axis_forward(shifted, 1, shift_x)
    height, width = scene.shape
    return shifted.reshape(
        height // bin_factor, bin_factor, width // bin_factor, bin_factor
    ).sum(axis=(1, 3))


def adjoint_operator(
    detector_frame: np.ndarray,
    highres_shape: tuple[int, int],
    bin_factor: int,
    phase_yx: tuple[float, float] = (0.0, 0.0),
) -> np.ndarray:
    """Apply the exact transpose of :func:`forward_operator`."""
    frame = np.asarray(detector_frame, dtype=float)
    height, width = _validate_highres_shape(highres_shape, bin_factor)
    expected = (height // bin_factor, width // bin_factor)
    if frame.shape != expected:
        raise ValueError(f"detector_frame shape must be {expected}, got {frame.shape}")
    if len(phase_yx) != 2:
        raise ValueError("phase_yx must contain (row_phase, column_phase)")
    shift_y, shift_x = (
        float(phase_yx[0]) * bin_factor,
        float(phase_yx[1]) * bin_factor,
    )
    expanded = np.repeat(np.repeat(frame, bin_factor, axis=0), bin_factor, axis=1)
    # Reverse the forward composition: x-shift transpose, then y-shift transpose.
    result = _shift_axis_adjoint(expanded, 1, shift_x)
    return _shift_axis_adjoint(result, 0, shift_y)


def adjoint_relative_error(
    scene: np.ndarray,
    detector_values: np.ndarray,
    bin_factor: int,
    phase_yx: tuple[float, float] = (0.0, 0.0),
) -> float:
    """Return relative inner-product mismatch |<Ax,y>-<x,A*y>| / scale."""
    predicted = forward_operator(scene, bin_factor, phase_yx)
    backprojected = adjoint_operator(detector_values, scene.shape, bin_factor, phase_yx)
    lhs = float(np.vdot(predicted, detector_values))
    rhs = float(np.vdot(scene, backprojected))
    scale = max(abs(lhs), abs(rhs), np.finfo(float).tiny)
    return abs(lhs - rhs) / scale
