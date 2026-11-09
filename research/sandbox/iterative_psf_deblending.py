"""Observation-only iterative PSF subtraction for controlled point-source tests.

This is a deliberately simple greedy detector. It does not know the true
source count, positions, or amplitudes. Truth scoring belongs outside this
module, after candidate generation.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import least_squares, linear_sum_assignment
from scipy.signal import correlate2d

from research.sandbox.pixel_response_reproduction import (
    IMAGE_SIZE,
    SIGMA_PIXELS,
    pixel_integrated_gaussian,
    SEVEN_SOURCE_AMPLITUDES,
    SEVEN_SOURCE_POSITIONS,
    _scene_model,
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

    # Conditional joint refit: this cannot change the BIC-selected count.
    # It tests whether the greedy locations can be jointly disentangled once
    # all retained components are allowed to move together.
    joint_refit = None
    if accepted:
        joint_initial = np.concatenate([
            np.asarray([
                value
                for item in accepted
                for value in (item["x_px"], item["y_px"])
            ], dtype=float),
            np.log(np.asarray([item["amplitude"] for item in accepted], dtype=float)),
        ])
        component_count = len(accepted)

        def joint_residual(parameters: np.ndarray) -> np.ndarray:
            positions = parameters[:2 * component_count].reshape(component_count, 2)
            amplitudes = np.exp(parameters[2 * component_count:])
            prediction = np.zeros_like(data, dtype=float)
            for (x0, y0), amplitude in zip(positions, amplitudes):
                prediction += _psf_template(
                    float(x0), float(y0), assumed_sigma_px, size
                ) * float(amplitude)
            return (prediction - (data - background)).ravel()

        joint_lower = np.concatenate([
            np.full(2 * component_count, -half_width),
            np.full(component_count, -30.0),
        ])
        joint_upper = np.concatenate([
            np.full(2 * component_count, half_width),
            np.full(component_count, 30.0),
        ])
        joint_fit = least_squares(
            joint_residual,
            joint_initial,
            bounds=(joint_lower, joint_upper),
            method="trf",
            xtol=1e-10,
            ftol=1e-10,
            gtol=1e-10,
            max_nfev=5000,
        )
        joint_positions = joint_fit.x[:2 * component_count].reshape(
            component_count, 2
        )
        joint_amplitudes = np.exp(joint_fit.x[2 * component_count:])
        joint_resid_image = joint_residual(joint_fit.x).reshape(data.shape)
        joint_rss = float(np.sum(joint_resid_image**2))
        joint_refit = {
            "optimizer_success": bool(joint_fit.success),
            "optimizer_message": str(joint_fit.message),
            "nfev": int(joint_fit.nfev),
            "rss": joint_rss,
            "bic": _profiled_bic(
                joint_rss, pixel_count, 3 * component_count
            ),
            "candidates": [
                {
                    "x_px": float(position[0]),
                    "y_px": float(position[1]),
                    "amplitude": float(amplitude),
                }
                for position, amplitude in zip(
                    joint_positions, joint_amplitudes
                )
            ],
            "residual": joint_resid_image,
            "interpretation_limit": (
                "Conditional refinement of the greedy-selected component "
                "count; it does not reconsider source birth/death or prove "
                "that the selected count is correct."
            ),
        }

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
        "joint_refit": joint_refit,
        "residual": residual,
        "limitations": [
            "Greedy sequential subtraction; the optional joint refit is conditional on the greedy-selected component count and cannot add or remove sources.",
            "Assumes a known PSF family and supplied/assumed PSF width.",
            "Uses a constant median background unless one is supplied.",
            "Profiled Gaussian BIC is a provisional stopping criterion; correlated residuals and model mismatch can invalidate its nominal interpretation.",
            "A candidate count is not proof of correct source identities.",
            "Synthetic point-source test only; not validated on astronomical data.",
        ],
    }


def _score_candidate_positions(candidates: list[dict], radius_px: float = 1.0) -> dict:
    """Score candidate positions against truth; call only after detection."""
    if not candidates:
        return {
            "candidate_count": 0,
            "matched_truth_count": 0,
            "missed_truth_count": int(len(SEVEN_SOURCE_POSITIONS)),
            "unmatched_candidate_count": 0,
            "matched_radial_errors_px": [],
        }
    candidate_xy = np.asarray(
        [[item["x_px"], item["y_px"]] for item in candidates], dtype=float
    )
    distances = np.linalg.norm(
        SEVEN_SOURCE_POSITIONS[:, None, :] - candidate_xy[None, :, :], axis=2
    )
    truth_indices, candidate_indices = linear_sum_assignment(distances)
    matched_errors = [
        float(distances[t, c])
        for t, c in zip(truth_indices, candidate_indices)
        if distances[t, c] <= radius_px
    ]
    return {
        "candidate_count": len(candidates),
        "matched_truth_count": len(matched_errors),
        "missed_truth_count": int(len(SEVEN_SOURCE_POSITIONS) - len(matched_errors)),
        "unmatched_candidate_count": int(len(candidates) - len(matched_errors)),
        "matched_radial_errors_px": matched_errors,
    }


def run_deblending_robustness_sweep(
    *,
    trials_per_condition: int = 3,
    gaussian_noise_levels: tuple[float, ...] = (0.0, 1.0, 3.0),
    assumed_sigma_widths_px: tuple[float, ...] = (1.1, 1.3, 1.5),
    seed_start: int = 20261600,
) -> dict:
    """Score greedy and conditional-joint deblending across noise and PSF widths.

    The generator uses one declared synthetic geometry. Candidate generation
    receives only each noisy observation and the assumed PSF width. Truth is
    used only by the scoring helper after the detector and joint fit finish.
    """
    if trials_per_condition < 1:
        raise ValueError("trials_per_condition must be positive")
    if not gaussian_noise_levels or any(level < 0 for level in gaussian_noise_levels):
        raise ValueError("Gaussian noise levels must be a non-empty non-negative grid")
    if not assumed_sigma_widths_px or any(
        width <= 0 for width in assumed_sigma_widths_px
    ):
        raise ValueError("assumed PSF widths must be a non-empty positive grid")

    clean = _scene_model(
        SEVEN_SOURCE_POSITIONS, SEVEN_SOURCE_AMPLITUDES,
        2.0, "integrated", SIGMA_PIXELS, IMAGE_SIZE,
    )
    records = []
    seed = seed_start
    for noise_sigma in gaussian_noise_levels:
        for assumed_sigma in assumed_sigma_widths_px:
            for trial_index in range(trials_per_condition):
                rng = np.random.default_rng(seed)
                observed = (
                    clean.copy() if noise_sigma == 0
                    else clean + rng.normal(0.0, noise_sigma, clean.shape)
                )
                result = run_iterative_psf_deblending(
                    observed, assumed_sigma_px=assumed_sigma
                )
                greedy_score = _score_candidate_positions(
                    result["selected_candidates"]
                )
                joint = result["joint_refit"]
                joint_score = (
                    _score_candidate_positions(joint["candidates"])
                    if joint is not None else None
                )
                records.append({
                    "seed": seed,
                    "trial_index": trial_index,
                    "gaussian_read_noise_sigma": float(noise_sigma),
                    "truth_psf_sigma_px": float(SIGMA_PIXELS),
                    "assumed_psf_sigma_px": float(assumed_sigma),
                    "greedy_bic_selected_count": result["selected_source_count"],
                    "greedy_score": greedy_score,
                    "joint_refit_score": joint_score,
                    "joint_refit_optimizer_success": (
                        bool(joint["optimizer_success"]) if joint is not None else False
                    ),
                    "joint_refit_bic": (
                        float(joint["bic"]) if joint is not None else None
                    ),
                })
                seed += 1

    grouped = {}
    for noise_sigma in gaussian_noise_levels:
        for assumed_sigma in assumed_sigma_widths_px:
            selected = [
                item for item in records
                if item["gaussian_read_noise_sigma"] == float(noise_sigma)
                and item["assumed_psf_sigma_px"] == float(assumed_sigma)
            ]
            grouped[f"noise={noise_sigma},sigma={assumed_sigma}"] = {
                "trials": len(selected),
                "greedy_mean_matched": float(np.mean([
                    item["greedy_score"]["matched_truth_count"] for item in selected
                ])),
                "joint_mean_matched": float(np.mean([
                    item["joint_refit_score"]["matched_truth_count"]
                    if item["joint_refit_score"] is not None else 0
                    for item in selected
                ])),
                "joint_all_seven_recovery_trials": int(sum(
                    item["joint_refit_score"] is not None
                    and item["joint_refit_score"]["matched_truth_count"] == 7
                    and item["joint_refit_score"]["unmatched_candidate_count"] == 0
                    for item in selected
                )),
                "joint_optimizer_successes": int(sum(
                    item["joint_refit_optimizer_success"] for item in selected
                )),
            }

    return {
        "experiment": "C9-PIXEL-RESPONSE-DEBLENDING-ROBUSTNESS-001",
        "status": "synthetic_deblending_noise_and_psf_width_sweep",
        "data_kind": "synthetic",
        "truth_geometry": "fixed seven-source 21x21 crowded scene",
        "truth_psf_sigma_px": float(SIGMA_PIXELS),
        "noise_model": "additive Gaussian read noise",
        "trials_per_condition": int(trials_per_condition),
        "gaussian_noise_levels": list(gaussian_noise_levels),
        "assumed_sigma_widths_px": list(assumed_sigma_widths_px),
        "candidate_generation_policy": (
            "observation-only matched filtering and BIC; no truth positions, "
            "amplitudes, or source count are passed to the detector"
        ),
        "truth_scoring_policy": (
            "Hungarian one-to-one assignment within 1 px, applied after "
            "greedy detection and conditional joint refinement"
        ),
        "joint_refit_policy": (
            "refits the BIC-selected component count; it cannot add or remove "
            "components and is not an independent source-count selector"
        ),
        "aggregate": grouped,
        "records": records,
        "limitations": [
            "One synthetic geometry and detector size.",
            "Gaussian read noise only; Poisson counting noise is not included.",
            "Finite trial count; increase to at least 20 seeds per condition for a stronger estimate.",
            "No source-separation or geometry variation in this sweep.",
            "The BIC noise model is provisional and residuals may be correlated.",
            "Synthetic point-source evidence only; not astronomical-image validation.",
        ],
    }
