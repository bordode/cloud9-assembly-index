"""Staged robustness checks for the synthetic pixel-response comparison.

These are controlled synthetic sensitivity experiments, not astronomical-data
reconstructions and not reproductions of Aimy's original seven-star scene.
The script deliberately varies one factor at a time.
"""
from __future__ import annotations

import json

import numpy as np
from scipy.optimize import least_squares

from research.sandbox.pixel_response_reproduction import (
    IMAGE_SIZE,
    SIGMA_PIXELS,
    SEVEN_SOURCE_AMPLITUDES,
    SEVEN_SOURCE_POSITIONS,
    _scene_model,
)


def run_case(
    *,
    geometry_scale: float = 1.0,
    phase_x: float = 0.0,
    phase_y: float = 0.0,
    noise_model: str = "none",
    noise_level: float = 0.0,
    fit_sigma: float | None = None,
    seed: int = 20261106,
) -> dict:
    """Run one matched seven-source fit with one controlled perturbation."""
    if geometry_scale <= 0:
        raise ValueError("geometry_scale must be positive")
    if noise_model not in {"none", "gaussian_read", "poisson"}:
        raise ValueError("unsupported noise_model")
    if noise_level < 0:
        raise ValueError("noise_level must be non-negative")
    truth_sigma = SIGMA_PIXELS
    assumed_sigma = truth_sigma if fit_sigma is None else float(fit_sigma)
    truth_positions = SEVEN_SOURCE_POSITIONS * geometry_scale
    truth_positions = truth_positions + np.array([phase_x, phase_y])
    truth_amplitudes = SEVEN_SOURCE_AMPLITUDES.copy()
    clean = _scene_model(
        truth_positions, truth_amplitudes, 2.0, "integrated",
        truth_sigma, IMAGE_SIZE,
    )
    rng = np.random.default_rng(seed)
    if noise_model == "none":
        observed = clean.copy()
    elif noise_model == "gaussian_read":
        observed = clean + rng.normal(0.0, noise_level, clean.shape)
    else:
        observed = rng.poisson(np.clip(clean, 0.0, None)).astype(float)

    init_rng = np.random.default_rng(seed + 1)
    initial_positions = truth_positions + init_rng.normal(
        0.0, 0.12, truth_positions.shape
    )
    initial = np.concatenate([
        initial_positions.ravel(), np.log(truth_amplitudes), [2.0]
    ])
    lower = np.concatenate([
        (truth_positions - 0.5).ravel(), np.full(7, -10.0), [-np.inf]
    ])
    upper = np.concatenate([
        (truth_positions + 0.5).ravel(), np.full(7, 15.0), [np.inf]
    ])

    summaries = {}
    source_errors = {}
    for kind in ("integrated", "centre"):
        def residual(parameters: np.ndarray) -> np.ndarray:
            positions = parameters[:14].reshape(7, 2)
            amplitudes = np.exp(parameters[14:21])
            background = float(parameters[21])
            prediction = _scene_model(
                positions, amplitudes, background, kind,
                assumed_sigma, IMAGE_SIZE,
            )
            return (prediction - observed).ravel()

        result = least_squares(
            residual, initial, bounds=(lower, upper), method="trf",
            xtol=1e-10, ftol=1e-10, gtol=1e-10, max_nfev=5000,
        )
        if not result.success:
            raise RuntimeError(f"{kind} fit failed: {result.message}")
        fitted = result.x[:14].reshape(7, 2)
        signed = fitted - truth_positions
        radial = np.linalg.norm(signed, axis=1)
        summaries[kind] = {
            "mean_radial_error_px": float(radial.mean()),
            "rmse_radial_error_px": float(np.sqrt(np.mean(radial ** 2))),
            "max_radial_error_px": float(radial.max()),
            "mean_signed_x_error_px": float(signed[:, 0].mean()),
            "mean_signed_y_error_px": float(signed[:, 1].mean()),
            "least_squares_cost": float(result.cost),
        }
        source_errors[kind] = [
            {
                "source": index + 1,
                "error_x_px": float(delta[0]),
                "error_y_px": float(delta[1]),
                "radial_error_px": float(error),
            }
            for index, (delta, error) in enumerate(zip(signed, radial))
        ]

    return {
        "status": "synthetic_sensitivity_case",
        "truth_sigma_px": truth_sigma,
        "fit_sigma_px": assumed_sigma,
        "geometry_scale": geometry_scale,
        "phase_x_px": phase_x,
        "phase_y_px": phase_y,
        "noise_model": noise_model,
        "noise_level": noise_level,
        "seed": seed,
        "source_count": 7,
        "source_specific_bounds_half_width_px": 0.5,
        "summaries": summaries,
        "source_errors": source_errors,
    }


def run_robustness_sweep() -> dict:
    """Run a small one-factor-at-a-time suite; no claim of exhaustive coverage."""
    cases = []
    # Geometry and common sub-pixel phase.
    for scale in (0.8, 1.0, 1.25):
        cases.append(run_case(geometry_scale=scale, seed=20261110))
    for phase in ((0.0, 0.0), (0.25, 0.25), (-0.25, 0.25)):
        cases.append(run_case(
            phase_x=phase[0], phase_y=phase[1], seed=20261110
        ))
    # Noise is tested separately, using fixed seeds and the same observations
    # for both competing forward models within each case.
    cases.append(run_case(
        noise_model="gaussian_read", noise_level=1.0, seed=20261111
    ))
    cases.append(run_case(
        noise_model="gaussian_read", noise_level=3.0, seed=20261111
    ))
    cases.append(run_case(
        noise_model="poisson", seed=20261112
    ))
    # Both fits receive the same deliberately incorrect PSF width.
    cases.append(run_case(fit_sigma=1.2, seed=20261110))
    cases.append(run_case(fit_sigma=1.4, seed=20261110))
    return {
        "experiment": "C9-PIXEL-RESPONSE-ROBUSTNESS-001",
        "status": "synthetic_sensitivity_suite",
        "case_count": len(cases),
        "truth_forward_model": "pixel-area-integrated Gaussian, sigma 1.3 px",
        "fit_comparison": "area-integrated versus pixel-centre sampled",
        "noise_note": (
            "Gaussian read noise uses the stated standard deviation. Poisson "
            "noise samples observed counts from the positive expected pixel "
            "values; its variance is signal-dependent."
        ),
        "limitations": [
            "One seven-source base geometry and one detector size.",
            "Source-specific +/-0.5 px bounds use known source neighbourhoods.",
            "One fixed realization per noisy condition; not population statistics.",
            "Poisson and Gaussian conditions are not matched to equal SNR.",
            "PSF mismatch is applied equally to both fit models.",
            "No claim of reproducing Aimy's original experiment.",
        ],
        "cases": cases,
    }


if __name__ == "__main__":
    print(json.dumps(run_robustness_sweep(), indent=2, sort_keys=True))
