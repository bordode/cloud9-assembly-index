"""Poisson-likelihood source-count selection for pixel-integrated PSF scenes.

Unlike the legacy Gaussian-BIC detector, this detector fits the complete
candidate scene by minimizing Poisson deviance at every proposed source count.
Truth positions and source count are never supplied to the detector.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import least_squares
from scipy.signal import correlate2d

from research.sandbox.pixel_response_reproduction import (
    SIGMA_PIXELS,
    pixel_integrated_gaussian,
)


def _template(x: float, y: float, sigma: float, size: int) -> np.ndarray:
    return pixel_integrated_gaussian(x, y, 1.0, 0.0, sigma, size)


def _poisson_deviance_residual(observed_counts: np.ndarray,
                               expected_counts: np.ndarray) -> np.ndarray:
    """Signed square-root Poisson deviance residuals."""
    mu = np.maximum(np.asarray(expected_counts, dtype=float), 1e-12)
    y = np.asarray(observed_counts, dtype=float)
    term = mu - y
    positive = y > 0
    term[positive] += y[positive] * np.log(y[positive] / mu[positive])
    deviance = np.maximum(2.0 * term, 0.0)
    return (np.sign(mu - y) * np.sqrt(deviance)).ravel()


def run_poisson_psf_deblending(
    observation_rate: np.ndarray,
    *,
    exposure: float,
    assumed_sigma_px: float = SIGMA_PIXELS,
    max_components: int = 12,
    detector_half_width_px: float | None = None,
    max_nfev: int = 2500,
    proposal_start_offsets: tuple[tuple[float, float], ...] = ((0.0, 0.0),),
) -> dict:
    """Detect sources and select count using Poisson likelihood/BIC.

    observation_rate is the observed count image divided by exposure.
    Multiplying it by exposure recovers the integer Poisson observations.
    The model is a constant non-negative background plus pixel-integrated
    Gaussian sources. Each candidate addition triggers a joint Poisson MLE
    refit of all retained sources and the background.
    """
    data = np.asarray(observation_rate, dtype=float)
    if data.ndim != 2 or data.shape[0] != data.shape[1] or data.shape[0] < 5:
        raise ValueError("observation_rate must be a square 2-D array of size >= 5")
    if not np.all(np.isfinite(data)) or np.any(data < 0):
        raise ValueError("observation_rate must be finite and non-negative")
    if not np.isfinite(exposure) or exposure <= 0:
        raise ValueError("exposure must be finite and positive")
    if not np.isfinite(assumed_sigma_px) or assumed_sigma_px <= 0:
        raise ValueError("assumed_sigma_px must be finite and positive")
    if max_components < 1:
        raise ValueError("max_components must be positive")
    offsets = tuple((float(dx), float(dy)) for dx, dy in proposal_start_offsets)
    if not offsets or not np.all(np.isfinite(np.asarray(offsets, dtype=float))):
        raise ValueError("proposal_start_offsets must be a non-empty finite sequence")

    size = data.shape[0]
    centre = (size - 1) / 2.0
    half_width = centre if detector_half_width_px is None else float(detector_half_width_px)
    if not np.isfinite(half_width) or half_width <= 0 or half_width > centre:
        raise ValueError("detector_half_width_px must lie in (0, detector half-field]")

    observed_counts = data * float(exposure)
    pixel_count = int(data.size)
    initial_background = max(float(np.mean(data)), 1e-8)
    accepted: list[dict] = []
    trials: list[dict] = []
    current_background = initial_background

    def fit_scene(starts: list[tuple[float, float, float]]) -> dict:
        count = len(starts)
        initial = []
        lower = []
        upper = []
        for x0, y0, amplitude in starts:
            initial.extend([x0, y0, np.log(max(amplitude, 1e-8))])
            lower.extend([-half_width, -half_width, -30.0])
            upper.extend([half_width, half_width, 30.0])
        initial.append(np.log(current_background))
        lower.append(-30.0)
        upper.append(30.0)

        def decode(parameters: np.ndarray):
            packed = parameters[:3 * count].reshape(count, 3)
            xy = packed[:, :2]
            amplitudes = np.exp(packed[:, 2])
            background = float(np.exp(parameters[3 * count]))
            return xy, amplitudes, background

        def predicted_rate(parameters: np.ndarray) -> np.ndarray:
            xy, amplitudes, background = decode(parameters)
            prediction = np.full(data.shape, background, dtype=float)
            for (x0, y0), amplitude in zip(xy, amplitudes):
                prediction += _template(
                    float(x0), float(y0), assumed_sigma_px, size
                ) * float(amplitude)
            return prediction

        def residual(parameters: np.ndarray) -> np.ndarray:
            return _poisson_deviance_residual(
                observed_counts, exposure * predicted_rate(parameters)
            )

        result = least_squares(
            residual,
            np.asarray(initial, dtype=float),
            bounds=(np.asarray(lower), np.asarray(upper)),
            method="trf",
            x_scale="jac",
            xtol=1e-9,
            ftol=1e-9,
            gtol=1e-9,
            max_nfev=max_nfev,
        )
        deviance = float(np.sum(residual(result.x) ** 2))
        parameter_count = 3 * count + 1
        bic = deviance + parameter_count * np.log(pixel_count)
        xy, amplitudes, background = decode(result.x)
        candidates = [
            {"x_px": float(position[0]), "y_px": float(position[1]),
             "amplitude": float(amplitude)}
            for position, amplitude in zip(xy, amplitudes)
        ]
        return {
            "success": bool(result.success),
            "message": str(result.message),
            "nfev": int(result.nfev),
            "deviance": deviance,
            "bic": float(bic),
            "background": background,
            "candidates": candidates,
            "prediction_rate": predicted_rate(result.x),
        }

    current_fit = fit_scene([])
    current_background = current_fit["background"]
    current_bic = current_fit["bic"]
    current_prediction = current_fit["prediction_rate"]

    for step in range(max_components):
        expected_counts = np.maximum(exposure * current_prediction, 1e-8)
        pearson = (observed_counts - expected_counts) / np.sqrt(expected_counts)
        template = _template(0.0, 0.0, assumed_sigma_px, size)
        norm = float(np.sqrt(np.sum(template ** 2)))
        score = correlate2d(pearson, template, mode="same", boundary="fill")
        score = score / max(norm, 1e-12)

        yy, xx = np.indices(score.shape)
        for item in accepted:
            distance = np.hypot(xx - (item["x_px"] + centre),
                                yy - (item["y_px"] + centre))
            score[distance < 0.8] = -np.inf
        row, col = np.unravel_index(int(np.argmax(score)), score.shape)
        proposal_x = float(col - centre)
        proposal_y = float(row - centre)
        proposal_score = float(score[row, col])
        if not np.isfinite(proposal_score) or proposal_score <= 0:
            break

        amplitude_start = max(
            float(np.sum((data - current_prediction) * template)
                  / max(np.sum(template ** 2), 1e-12)),
            1e-6,
        )
        starts = [
            (item["x_px"], item["y_px"], item["amplitude"])
            for item in accepted
        ]
        fit_attempts = []
        for offset_x, offset_y in offsets:
            candidate_starts = list(starts)
            candidate_starts.append((
                float(np.clip(proposal_x + offset_x, -half_width, half_width)),
                float(np.clip(proposal_y + offset_y, -half_width, half_width)),
                amplitude_start,
            ))
            fit_attempts.append({
                "offset": [offset_x, offset_y],
                "fit": fit_scene(candidate_starts),
            })
        successful_attempts = [
            item for item in fit_attempts if item["fit"]["success"]
        ]
        if successful_attempts:
            winning_attempt = min(
                successful_attempts, key=lambda item: item["fit"]["deviance"]
            )
            proposed_fit = winning_attempt["fit"]
            winning_offset = winning_attempt["offset"]
        else:
            proposed_fit = fit_attempts[0]["fit"]
            winning_offset = fit_attempts[0]["offset"]
        attempt_deviances = [
            float(item["fit"]["deviance"]) for item in fit_attempts
        ]
        accepted_candidate = bool(
            successful_attempts and proposed_fit["bic"] < current_bic
        )
        trial_record = {
            "step": step + 1,
            "proposal_x_px": proposal_x,
            "proposal_y_px": proposal_y,
            "proposal_score": proposal_score,
            "optimizer_success": proposed_fit["success"],
            "optimizer_nfev": proposed_fit["nfev"],
            "deviance_before": current_fit["deviance"],
            "deviance_after": proposed_fit["deviance"],
            "bic_before": current_bic,
            "bic_after": proposed_fit["bic"],
            "accepted": accepted_candidate,
        }
        if len(offsets) > 1:
            trial_record.update({
                "initialization_starts_tried": len(offsets),
                "winning_start_offset_px": winning_offset,
                "successful_initialization_starts": len(successful_attempts),
                "start_deviance_min": float(min(attempt_deviances)),
                "start_deviance_max": float(max(attempt_deviances)),
                "start_deviance_range": float(max(attempt_deviances) - min(attempt_deviances)),
            })
        trials.append(trial_record)
        if not accepted_candidate:
            break

        accepted = proposed_fit["candidates"]
        current_fit = proposed_fit
        current_background = proposed_fit["background"]
        current_bic = proposed_fit["bic"]
        current_prediction = proposed_fit["prediction_rate"]

    return {
        "method": "joint_poisson_deviance_mle_with_poisson_bic",
        "exposure": float(exposure),
        "assumed_psf_sigma_px": float(assumed_sigma_px),
        "selected_source_count": len(accepted),
        "candidates": accepted,
        "optimizer_success": bool(current_fit["success"]),
        "optimizer_message": current_fit["message"],
        "optimizer_nfev": current_fit["nfev"],
        "poisson_deviance": current_fit["deviance"],
        "poisson_bic": current_fit["bic"],
        "background_rate": current_fit["background"],
        "candidate_trials": trials,
        "candidate_generation_policy": (
            "Pearson-residual matched-filter proposals from the observation; "
            "truth positions, amplitudes, and source count are excluded"
        ),
        "fitting_policy": (
            "joint Poisson-deviance maximum-likelihood refit of all retained "
            "pixel-integrated PSFs and shared non-negative background after "
            "each proposed source"
        ),
        "stopping_policy": (
            "accept a candidate only when Poisson BIC decreases; stop at first "
            "rejected candidate or max_components"
        ),
        "limitations": [
            "Synthetic or supplied count-rate image with known exposure.",
            "Assumes independent Poisson pixels and a known PSF family/width.",
            "Uses a constant non-negative background.",
            "Greedy proposal order can miss sources; BIC is an approximate model-selection criterion.",
            "One detector size and point-source family in the current benchmark.",
        ],
    }
