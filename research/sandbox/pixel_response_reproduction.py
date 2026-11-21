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
            "Single-source, noise-free synthetic pilot only. Both models "
            "recover the centroid to numerical precision across the tested "
            "phase grid (centre-model mean radial error about 4.02e-7 px). "
            "No meaningful centroid advantage is observed in this symmetric "
            "isolated-source control. This does not reproduce the reported "
            "seven-star experiment or establish performance for blended sources, "
            "noise, PSF mismatch, arbitrary image detail, or astronomical data."
        ),
    }




# A compact crowded-source control. Coordinates are in pixel units relative
# to the detector centre; fluxes are integrated source amplitudes.
SEVEN_SOURCE_POSITIONS = np.array([
    [0.00, 0.00],
    [-2.10, 0.00],
    [2.10, 0.00],
    [0.00, -2.10],
    [0.00, 2.10],
    [-1.55, -1.55],
    [1.55, 1.55],
], dtype=float)
SEVEN_SOURCE_AMPLITUDES = np.array([1000.0, 800.0, 900.0, 700.0, 850.0, 650.0, 750.0])


def _scene_model(
    positions: np.ndarray, amplitudes: np.ndarray, background: float,
    model_kind: str, sigma: float, size: int,
) -> np.ndarray:
    """Render a multi-source scene with one of the two detector models."""
    model_function = (
        pixel_integrated_gaussian if model_kind == "integrated"
        else pixel_centre_gaussian
    )
    scene = np.full((size, size), background, dtype=float)
    for (x0, y0), amplitude in zip(positions, amplitudes):
        scene += model_function(
            float(x0), float(y0), float(amplitude), 0.0, sigma, size
        )
    return scene


def run_seven_source_experiment(
    noise_sigma: float = 0.0, seed: int = 20261105,
) -> dict:
    """Fit a crowded seven-source scene with matched integrated/centre models.

    Source identities are held fixed by narrow, source-specific position bounds;
    this prevents label swapping from masquerading as localization error.
    """
    size = IMAGE_SIZE
    sigma = SIGMA_PIXELS
    truth_positions = SEVEN_SOURCE_POSITIONS.copy()
    truth_amplitudes = SEVEN_SOURCE_AMPLITUDES.copy()
    truth = _scene_model(
        truth_positions, truth_amplitudes, 2.0, "integrated", sigma, size
    )
    noise_rng = np.random.default_rng(seed)
    observed = truth + noise_rng.normal(0.0, noise_sigma, truth.shape)

    # Both fits receive exactly the same perturbed initialization and bounds.
    init_rng = np.random.default_rng(seed + 1)
    initial_positions = truth_positions + init_rng.normal(
        0.0, 0.12, truth_positions.shape
    )
    initial = np.concatenate([
        initial_positions.ravel(), np.log(truth_amplitudes), [2.0]
    ])
    lower_positions = (truth_positions - 0.5).ravel()
    upper_positions = (truth_positions + 0.5).ravel()
    lower = np.concatenate([lower_positions, np.full(7, -10.0), [-np.inf]])
    upper = np.concatenate([upper_positions, np.full(7, 15.0), [np.inf]])

    summaries = {}
    source_records = []
    for kind in ("integrated", "centre"):
        def residual(parameters: np.ndarray) -> np.ndarray:
            positions = parameters[:14].reshape(7, 2)
            amplitudes = np.exp(parameters[14:21])
            background = float(parameters[21])
            predicted = _scene_model(
                positions, amplitudes, background, kind, sigma, size
            )
            return (predicted - observed).ravel()

        result = least_squares(
            residual, initial, bounds=(lower, upper), method="trf",
            xtol=1e-12, ftol=1e-12, gtol=1e-12, max_nfev=5000,
        )
        if not result.success:
            raise RuntimeError(f"{kind} seven-source fit failed: {result.message}")
        fitted = result.x[:14].reshape(7, 2)
        errors = np.linalg.norm(fitted - truth_positions, axis=1)
        summaries[kind] = {
            "mean_radial_error_px": float(errors.mean()),
            "rmse_radial_error_px": float(np.sqrt(np.mean(errors**2))),
            "max_radial_error_px": float(errors.max()),
            "least_squares_cost": float(result.cost),
        }
        for index, (truth_xy, fitted_xy, error) in enumerate(
            zip(truth_positions, fitted, errors), start=1
        ):
            source_records.append({
                "model": kind,
                "source": index,
                "truth_x": float(truth_xy[0]),
                "truth_y": float(truth_xy[1]),
                "fit_x": float(fitted_xy[0]),
                "fit_y": float(fitted_xy[1]),
                "radial_error_px": float(error),
            })

    return {
        "experiment": "C9-PIXEL-RESPONSE-SEVEN-SOURCE-001",
        "status": "synthetic_pilot",
        "data_kind": "synthetic",
        "image_size": size,
        "source_count": 7,
        "sigma_pixels": sigma,
        "noise_model": "additive Gaussian",
        "noise_sigma": noise_sigma,
        "seed": seed,
        "truth_forward_model": "pixel-area-integrated circular Gaussian per source",
        "fit_models": ["pixel-area-integrated", "pixel-centre sampled"],
        "fitted_parameters": "14 source coordinates, 7 positive amplitudes, shared background",
        "optimizer": "scipy.optimize.least_squares; identical initialization, bounds, tolerances",
        "source_identity_control": "fixed source ordering with +/-0.5 px source-specific coordinate bounds",
        "summaries": summaries,
        "sources": source_records,
        "interpretation": (
            "Seven-source synthetic pilot only. This tests one stated geometry "
            "and does not reproduce Aimy's original scene, whose complete "
            "geometry and fitting details are unavailable in the attributed note."
        ),
    }

if __name__ == "__main__":
    print(json.dumps({
        "isolated_source": run_experiment(),
        "seven_source": run_seven_source_experiment(),
    }, indent=2, sort_keys=True))
