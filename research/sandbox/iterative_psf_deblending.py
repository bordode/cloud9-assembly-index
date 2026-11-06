"""Observation-only iterative PSF subtraction for controlled point-source tests.

This is a deliberately simple greedy detector. It does not know the true
source count, positions, or amplitudes. Truth scoring belongs outside this
module, after candidate generation.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import least_squares
from scipy.signal import correlate2d

from research.sandbox.pixel_response_reproduction import (
    IMAGE_SIZE,
    SIGMA_PIXELS,
    pixel_integrated_gaussian,
)


def _psf_template(
    x_px: float, y_px: float, sigma_px: float, size: int
) -> np.ndarray:
    """Return a unit-amplitude, zero-background pixel-integrated PSF."""
    return pixel_integrated_gaussian(
        x_px, y_px, 1.0, 0.0, sigma_px, size=size
    )


def _profiled_bic(rss: float, pixel_count: int, parameter_count: int) -> float:
    """Gaussian BIC with residual variance profiled from the current RSS."""
    floor = np.finfo(float).tiny
    return float(
        pixel_count * np.log(max(rss / pixel_count, floor))
        + parameter_count * np.log(pixel_count)
    )


def run_iterative_psf_deblending(
    observation: np.ndarray,
    *,
    assumed_sigma_px: float = SIGMA_PIXELS,
    background_estimate: float | None = None,
    max_components: int = 12,
    detector_half_width_px: float | None = None,
) -> dict:
    """Greedily detect, fit, and subtract sources using observation data only.

    Candidate proposals use a normalized matched-filter score. Each proposal
    is refined by fitting one integrated Gaussian to the current residual.
    A component is retained only when the profiled Gaussian BIC decreases.
    The known source count and all truth coordinates/amplitudes are excluded.
    """
    data = np.asarray(observation, dtype=float)
    if data.ndim != 2 or data.shape[0] != data.shape[1] or data.shape[0] < 5:
        raise ValueError("observation must be a square 2-D array of size >= 5")
    if not np.all(np.isfinite(data)):
        raise ValueError("observation must contain only finite values")
    if assumed_sigma_px <= 0:
        raise ValueError("assumed_sigma_px must be positive")
    if max_components < 1:
        raise ValueError("max_components must be positive")

    size = data.shape[0]
    centre = (size - 1) / 2.0
    half_width = (
        (size - 1) / 2.0
        if detector_half_width_px is None
        else float(detector_half_width_px)
    )
    if half_width <= 0 or half_width > centre:
        raise ValueError("detector_half_width_px must lie in (0, detector half-field]")

    background = (
        float(np.median(data))
        if background_estimate is None
        else float(background_estimate)
    )
    if not np.isfinite(background):
        raise ValueError("background estimate must be finite")

    residual = data - background
    initial_rss = float(np.sum(residual**2))
    pixel_count = int(data.size)
    accepted: list[dict] = []
    trials: list[dict] = []
    current_rss = initial_rss
    current_bic = _profiled_bic(current_rss, pixel_count, 0)
    template = _psf_template(0.0, 0.0, assumed_sigma_px, size)
    template_norm = float(np.sum(template**2))
    if template_norm <= 0:
        raise ValueError("PSF template has zero energy")

    for step in range(max_components):
        # The Gaussian PSF is symmetric, so correlation and convolution
        # have the same orientation. Normalize by template energy.
        correlation = correlate2d(
            residual, template, mode="same", boundary="fill", fillvalue=0.0
        )
        score = correlation / np.sqrt(template_norm)
        row, col = np.unravel_index(int(np.argmax(score)), score.shape)
        start_x = float(col - centre)
        start_y = float(row - centre)
        start_score = float(score[row, col])

        def single_source_residual(parameters: np.ndarray) -> np.ndarray:
            x0, y0, log_amplitude = parameters
            model = _psf_template(
                float(x0), float(y0), assumed_sigma_px, size
            ) * float(np.exp(log_amplitude))
            return (model - residual).ravel()

        initial_amplitude = max(
            float(correlation[row, col] / template_norm), 1e-8
        )
        fit = least_squares(
            single_source_residual,
            np.array([start_x, start_y, np.log(initial_amplitude)]),
            bounds=(
                [-half_width, -half_width, -30.0],
                [half_width, half_width, 30.0],
            ),
            method="trf",
            xtol=1e-10,
            ftol=1e-10,
            gtol=1e-10,
            max_nfev=1500,
        )
        fit_x, fit_y = float(fit.x[0]), float(fit.x[1])
        fit_amplitude = float(np.exp(fit.x[2]))
        component = _psf_template(
            fit_x, fit_y, assumed_sigma_px, size
        ) * fit_amplitude
        proposed_residual = residual - component
        proposed_rss = float(np.sum(proposed_residual**2))
        proposed_bic = _profiled_bic(
            proposed_rss, pixel_count, 3 * (len(accepted) + 1)
        )
        accepted_component = bool(fit.success and proposed_bic < current_bic)
        trial = {
            "step": step + 1,
            "matched_filter_start_x_px": start_x,
            "matched_filter_start_y_px": start_y,
            "matched_filter_score": start_score,
            "fit_x_px": fit_x,
            "fit_y_px": fit_y,
            "fit_amplitude": fit_amplitude,
            "optimizer_success": bool(fit.success),
            "optimizer_nfev": int(fit.nfev),
            "rss_before": current_rss,
            "rss_after": proposed_rss,
            "bic_before": current_bic,
            "bic_after": proposed_bic,
            "accepted": accepted_component,
        }
        trials.append(trial)
        if not accepted_component:
            break
        accepted.append({
            "x_px": fit_x,
            "y_px": fit_y,
            "amplitude": fit_amplitude,
            "step": step + 1,
        })
        residual = proposed_residual
        current_rss = proposed_rss
        current_bic = proposed_bic

    return {
        "experiment": "C9-PIXEL-RESPONSE-ITERATIVE-PSF-DEBLENDING-001",
        "status": "observation_only_iterative_psf_deblending",
        "data_kind": "synthetic_or_user_supplied_observation",
        "image_shape": [int(size), int(size)],
        "assumed_psf_sigma_px": float(assumed_sigma_px),
        "background_estimate": background,
        "background_policy": (
            "median of observation" if background_estimate is None
            else "explicit caller-supplied value"
        ),
        "candidate_generation_policy": (
            "normalized matched filtering of current observation residual; "
            "no truth positions, amplitudes, or source count"
        ),
        "stopping_policy": (
            "retain a fitted component only when profiled Gaussian BIC "
            "decreases; stop at first rejected component or max_components"
        ),
        "max_components": int(max_components),
        "initial_rss": initial_rss,
        "final_rss": current_rss,
        "final_bic": current_bic,
        "selected_source_count": len(accepted),
        "selected_candidates": accepted,
        "candidate_trials": trials,
        "residual": residual,
        "limitations": [
            "Greedy sequential subtraction; accepted components are not jointly refitted.",
            "Assumes a known PSF family and supplied/assumed PSF width.",
            "Uses a constant median background unless one is supplied.",
            "Profiled Gaussian BIC is a provisional stopping criterion; correlated residuals and model mismatch can invalidate its nominal interpretation.",
            "A candidate count is not proof of correct source identities.",
            "Synthetic point-source test only; not validated on astronomical data.",
        ],
    }
