"""Synthetic pilot comparing pixel-integrated and pixel-centre Gaussian models.

This is a controlled parameter-estimation experiment, not an astronomical-data
reconstruction and not a reproduction of Aimy's seven-source result.

Run:
    python research/sandbox/pixel_response_reproduction.py
"""
from __future__ import annotations

import json
from math import erf, sqrt

import numpy as np
from scipy.optimize import least_squares


IMAGE_SIZE = 21
SIGMA_PIXELS = 1.3
PHASES = np.linspace(-0.4, 0.4, 5)
NOISE_SIGMA = 0.0
SEED = 20261104


def _normal_cdf(x: np.ndarray) -> np.ndarray:
    """Standard-normal CDF using the scalar math.erf implementation."""
    return 0.5 * (1.0 + np.vectorize(erf)(x / sqrt(2.0)))


def pixel_integrated_gaussian(
    x0: float, y0: float, amplitude: float, background: float,
    sigma: float, size: int = IMAGE_SIZE,
) -> np.ndarray:
    """Expected pixel counts for a circular Gaussian integrated over squares."""
    coords = np.arange(size, dtype=float) - (size - 1) / 2
    x_lo = (coords - 0.5 - x0) / sigma
    x_hi = (coords + 0.5 - x0) / sigma
    y_lo = (coords - 0.5 - y0) / sigma
    y_hi = (coords + 0.5 - y0) / sigma
    px = _normal_cdf(x_hi) - _normal_cdf(x_lo)
    py = _normal_cdf(y_hi) - _normal_cdf(y_lo)
    return background + amplitude * np.outer(py, px)


def pixel_centre_gaussian(
    x0: float, y0: float, amplitude: float, background: float,
    sigma: float, size: int = IMAGE_SIZE,
) -> np.ndarray:
    """Gaussian intensity evaluated at pixel centres (not area integrated)."""
    coords = np.arange(size, dtype=float) - (size - 1) / 2
    xx, yy = np.meshgrid(coords, coords)
    radius2 = (xx - x0) ** 2 + (yy - y0) ** 2
    return background + amplitude * np.exp(-radius2 / (2.0 * sigma**2))


def fit_position(data: np.ndarray, model_kind: str, sigma: float) -> tuple[float, float]:
    """Fit x, y, positive amplitude, and background with identical least squares."""
    model = pixel_integrated_gaussian if model_kind == "integrated" else pixel_centre_gaussian

    def residual(parameters: np.ndarray) -> np.ndarray:
        x0, y0, log_amplitude, background = parameters
        predicted = model(x0, y0, np.exp(log_amplitude), background, sigma)
        return (predicted - data).ravel()

    initial = np.array([0.0, 0.0, np.log(max(float(data.max()), 1e-6)), 0.0])
    result = least_squares(
        residual,
        initial,
        bounds=([-0.5, -0.5, -20.0, -np.inf], [0.5, 0.5, 20.0, np.inf]),
        method="trf",
        xtol=1e-12,
        ftol=1e-12,
        gtol=1e-12,
        max_nfev=2000,
    )
    if not result.success:
        raise RuntimeError(f"{model_kind} fit did not converge: {result.message}")
    return float(result.x[0]), float(result.x[1])


def run_experiment(noise_sigma: float = NOISE_SIGMA, seed: int = SEED) -> dict:
    """Compare both models over a 5x5 sub-pixel phase grid."""
    rng = np.random.default_rng(seed)
    records = []
    centre = (IMAGE_SIZE - 1) / 2
    for y_phase in PHASES:
        for x_phase in PHASES:
            truth_x, truth_y = float(x_phase), float(y_phase)
            clean = pixel_integrated_gaussian(
                truth_x, truth_y, amplitude=1000.0, background=2.0,
                sigma=SIGMA_PIXELS,
            )
            observed = clean + rng.normal(0.0, noise_sigma, clean.shape)
            for kind in ("integrated", "centre"):
                fit_x, fit_y = fit_position(observed, kind, SIGMA_PIXELS)
                dx, dy = fit_x - truth_x, fit_y - truth_y
                records.append({
                    "phase_x": truth_x,
                    "phase_y": truth_y,
                    "model": kind,
                    "fit_x": fit_x,
                    "fit_y": fit_y,
                    "error_x": dx,
                    "error_y": dy,
                    "radial_error_px": float(np.hypot(dx, dy)),
                })

    summaries = {}
    for kind in ("integrated", "centre"):
        errors = np.array([
            row["radial_error_px"] for row in records if row["model"] == kind
        ])
        summaries[kind] = {
            "mean_radial_error_px": float(errors.mean()),
            "rmse_radial_error_px": float(np.sqrt(np.mean(errors**2))),
            "max_radial_error_px": float(errors.max()),
        }
    return {
        "experiment": "C9-PIXEL-RESPONSE-PILOT-001",
        "status": "synthetic_pilot",
        "data_kind": "synthetic",
        "image_size": IMAGE_SIZE,
        "psf": "circular Gaussian",
        "sigma_pixels": SIGMA_PIXELS,
        "noise_sigma": noise_sigma,
        "seed": seed,
        "phase_grid_count": len(PHASES) ** 2,
        "truth_forward_model": "pixel-area-integrated Gaussian",
        "fit_models": ["pixel-area-integrated Gaussian", "pixel-centre Gaussian"],
        "optimizer": "scipy.optimize.least_squares; identical bounds and tolerances",
        "summaries": summaries,
        "records": records,
        "interpretation": (
            "Single-source synthetic pilot only. It does not reproduce the "
            "reported seven-star experiment and is not evidence about arbitrary "
            "image-detail recovery or astronomical observations."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(run_experiment(), indent=2, sort_keys=True))
