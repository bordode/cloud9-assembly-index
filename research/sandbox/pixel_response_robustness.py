"""Staged robustness checks for the synthetic pixel-response comparison.

These are controlled synthetic sensitivity experiments, not astronomical-data
reconstructions and not reproductions of Aimy's original seven-star scene.
The script deliberately varies one factor at a time.
"""
from __future__ import annotations

import json

import numpy as np
from scipy.optimize import least_squares, linear_sum_assignment
from scipy.ndimage import gaussian_filter, maximum_filter

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
    initialization_seed: int | None = None,
    position_bound_half_width: float | None = 0.5,
    initialization_policy: str = "truth_jitter",
    detector_bounds: bool = False,
) -> dict:
    """Run one matched seven-source fit with one controlled perturbation."""
    if geometry_scale <= 0:
        raise ValueError("geometry_scale must be positive")
    if noise_model not in {"none", "gaussian_read", "poisson"}:
        raise ValueError("unsupported noise_model")
    if noise_level < 0:
        raise ValueError("noise_level must be non-negative")
    if noise_model == "gaussian_read" and noise_level <= 0:
        raise ValueError("Gaussian read-noise standard deviation must be positive")
    if position_bound_half_width is not None and position_bound_half_width <= 0:
        raise ValueError("position_bound_half_width must be positive or None")
    if initialization_policy not in {"truth_jitter", "detector_uniform"}:
        raise ValueError("unsupported initialization_policy")
    if detector_bounds and position_bound_half_width is not None:
        raise ValueError(
            "detector_bounds cannot be combined with truth-centred bounds"
        )
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

    init_seed = seed + 1 if initialization_seed is None else initialization_seed
    init_rng = np.random.default_rng(init_seed)
    if initialization_policy == "truth_jitter":
        initial_positions = truth_positions + init_rng.normal(
            0.0, 0.12, truth_positions.shape
        )
    else:
        # Deliberately do not seed from known source coordinates. The seven
        # components start independently across the detector field.
        half_field = (IMAGE_SIZE - 1) / 2 - 1.0
        initial_positions = init_rng.uniform(
            -half_field, half_field, size=truth_positions.shape
        )
    initial = np.concatenate([
        initial_positions.ravel(), np.log(truth_amplitudes), [2.0]
    ])
    if detector_bounds:
        # Physical field-of-view bounds use detector geometry only, never
        # the hidden true source coordinates.
        half_field = (IMAGE_SIZE - 1) / 2
        lower_positions = np.full(14, -half_field)
        upper_positions = np.full(14, half_field)
    elif position_bound_half_width is None:
        lower_positions = np.full(14, -np.inf)
        upper_positions = np.full(14, np.inf)
    else:
        lower_positions = (truth_positions - position_bound_half_width).ravel()
        upper_positions = (truth_positions + position_bound_half_width).ravel()
    lower = np.concatenate([lower_positions, np.full(7, -10.0), [-np.inf]])
    upper = np.concatenate([upper_positions, np.full(7, 15.0), [np.inf]])
    if noise_model == "poisson":
        lower[-1] = 0.0

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
            if noise_model == "poisson":
                # Signed square-root Poisson deviance residuals implement the
                # Poisson likelihood for both competing forward models.
                expected = np.clip(prediction, 1e-12, None)
                counts = np.clip(observed, 0.0, None)
                term = expected - counts
                positive = counts > 0
                term[positive] += counts[positive] * np.log(
                    counts[positive] / expected[positive]
                )
                return (np.sign(prediction - observed)
                        * np.sqrt(2.0 * np.maximum(term, 0.0))).ravel()
            if noise_model == "gaussian_read":
                return ((prediction - observed) / noise_level).ravel()
            return (prediction - observed).ravel()

        result = least_squares(
            residual, initial, bounds=(lower, upper), method="trf",
            xtol=1e-10, ftol=1e-10, gtol=1e-10, max_nfev=5000,
        )
        fitted_raw = result.x[:14].reshape(7, 2)
        # Match fitted positions to truth by minimum total Euclidean distance.
        # This makes label switching visible instead of treating array order
        # as physical source identity.
        distances = np.linalg.norm(
            truth_positions[:, None, :] - fitted_raw[None, :, :], axis=2
        )
        truth_indices, fitted_indices = linear_sum_assignment(distances)
        fitted = fitted_raw[fitted_indices]
        signed = fitted - truth_positions[truth_indices]
        radial = np.linalg.norm(signed, axis=1)
        position_bound_hits = 0
        if detector_bounds or position_bound_half_width is not None:
            lower_xy = lower_positions.reshape(7, 2)
            upper_xy = upper_positions.reshape(7, 2)
            tol = 1e-5
            position_bound_hits = int(np.count_nonzero(
                np.isclose(fitted_raw, lower_xy, atol=tol, rtol=0.0)
                | np.isclose(fitted_raw, upper_xy, atol=tol, rtol=0.0)
            ))
        summaries[kind] = {
            "mean_radial_error_px": float(radial.mean()),
            "rmse_radial_error_px": float(np.sqrt(np.mean(radial ** 2))),
            "max_radial_error_px": float(radial.max()),
            "mean_signed_x_error_px": float(signed[:, 0].mean()),
            "mean_signed_y_error_px": float(signed[:, 1].mean()),
            "least_squares_cost": float(result.cost),
            "optimizer_success": bool(result.success),
            "optimizer_message": str(result.message),
            "optimizer_status": int(result.status),
            "nfev": int(result.nfev),
            "position_bound_hits": position_bound_hits,
            "max_abs_fitted_coordinate_px": float(np.max(np.abs(fitted_raw))),
            "assignment_total_distance_px": float(distances[truth_indices, fitted_indices].sum()),
            "assignment_permutation": [int(i) for i in fitted_indices],
            "assignment_swaps": int(sum(i != j for i, j in enumerate(fitted_indices))),
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
        "initialization_seed": init_seed,
        "initialization_policy": initialization_policy,
        "source_count": 7,
        "position_bound_half_width_px": position_bound_half_width,
        "position_bounds_policy": (
            "physical detector-field bounds" if detector_bounds
            else ("unbounded" if position_bound_half_width is None
                  else "truth-centred diagnostic bounds")
        ),
        "detector_bounds_enabled": detector_bounds,
        "summaries": summaries,
        "source_errors": source_errors,
    }


def run_repeated_noise_trials(
    *,
    noise_model: str,
    noise_level: float = 0.0,
    trials: int = 20,
    seed_start: int = 20261200,
    initialization_seed: int = 20261199,
) -> dict:
    """Estimate repeatability across noise draws with a fixed initialization.

    The same noise realization is fitted by both forward models within each
    trial. The initial parameter vector is held fixed across trials, isolating
    variability due to the generated observation noise.
    """
    if noise_model not in {"gaussian_read", "poisson"}:
        raise ValueError("repeated trials require gaussian_read or poisson")
    if trials < 2:
        raise ValueError("at least two trials are required")
    if noise_model == "gaussian_read" and noise_level <= 0:
        raise ValueError("Gaussian read-noise standard deviation must be positive")

    results = [
        run_case(
            noise_model=noise_model,
            noise_level=noise_level,
            seed=seed_start + index,
            initialization_seed=initialization_seed,
        )
        for index in range(trials)
    ]
    metrics = (
        "mean_radial_error_px",
        "rmse_radial_error_px",
        "max_radial_error_px",
        "mean_signed_x_error_px",
        "mean_signed_y_error_px",
    )
    aggregate = {}
    for model in ("integrated", "centre"):
        aggregate[model] = {}
        for metric in metrics:
            values = np.asarray(
                [item["summaries"][model][metric] for item in results],
                dtype=float,
            )
            aggregate[model][metric] = {
                "mean_across_trials": float(values.mean()),
                "std_across_trials": float(values.std(ddof=1)),
                "min_across_trials": float(values.min()),
                "max_across_trials": float(values.max()),
            }

    return {
        "experiment": "C9-PIXEL-RESPONSE-REPEATED-NOISE-001",
        "status": "synthetic_repeated_noise_trials",
        "noise_model": noise_model,
        "noise_level": noise_level,
        "trial_count": trials,
        "seed_start": seed_start,
        "initialization_seed_fixed": initialization_seed,
        "initialization_policy": (
            "Same initial parameter vector in every trial; only the noise "
            "realization changes."
        ),
        "paired_model_policy": (
            "Both forward models fit the same observed image in each trial."
        ),
        "aggregate_metrics": aggregate,
        "trial_results": results,
        "limitations": [
            "Single seven-source geometry and detector size.",
            "Known source neighbourhoods constrain each fitted position to +/-0.5 px.",
            "Fixed initialization does not test sensitivity to optimizer starts.",
            "Finite trial count; results are specific to this synthetic setup.",
            "Gaussian and Poisson conditions are not matched to equal SNR.",
        ],
    }


def run_initialization_trials(
    *,
    noise_model: str = "gaussian_read",
    noise_level: float = 1.0,
    trials: int = 10,
    observation_seed: int = 20261300,
    initialization_seed_start: int = 20261310,
) -> dict:
    """Vary optimizer starts while holding the observed image fixed."""
    if noise_model not in {"gaussian_read", "poisson", "none"}:
        raise ValueError("unsupported noise_model")
    if trials < 2:
        raise ValueError("at least two trials are required")
    if noise_model == "gaussian_read" and noise_level <= 0:
        raise ValueError("Gaussian read-noise standard deviation must be positive")

    results = [
        run_case(
            noise_model=noise_model,
            noise_level=noise_level,
            seed=observation_seed,
            initialization_seed=initialization_seed_start + index,
        )
        for index in range(trials)
    ]
    aggregate = {}
    for model in ("integrated", "centre"):
        values = np.asarray(
            [item["summaries"][model]["rmse_radial_error_px"]
             for item in results],
            dtype=float,
        )
        aggregate[model] = {
            "mean_rmse_across_starts_px": float(values.mean()),
            "std_rmse_across_starts_px": float(values.std(ddof=1)),
            "min_rmse_across_starts_px": float(values.min()),
            "max_rmse_across_starts_px": float(values.max()),
        }

    return {
        "experiment": "C9-PIXEL-RESPONSE-INITIALIZATION-001",
        "status": "synthetic_initialization_sensitivity",
        "noise_model": noise_model,
        "noise_level": noise_level,
        "observation_seed_fixed": observation_seed,
        "initialization_seed_start": initialization_seed_start,
        "trial_count": trials,
        "observation_policy": (
            "Same generated observation in every trial; only starting "
            "positions vary."
        ),
        "aggregate_metrics": aggregate,
        "trial_results": results,
        "limitations": [
            "Single synthetic scene and one fixed observation.",
            "Source-specific +/-0.5 px truth-centred bounds remain in force.",
            "Starting positions vary, but the optimizer is not tested outside "
            "the known source neighbourhoods.",
            "Finite number of starts; not a global-optimum proof.",
        ],
    }



def run_position_bound_sweep(
    *,
    noise_model: str = "gaussian_read",
    noise_level: float = 1.0,
    starts_per_bound: int = 3,
    observation_seed: int = 20261400,
    initialization_seed_start: int = 20261410,
    initialization_policy: str = "truth_jitter",
) -> dict:
    """Execute paired fits across widening bounds and independent starts.

    Failed optimizer terminations remain in the output. This is a synthetic
    fixed-seven-component localization study, not blind source detection.
    """
    if starts_per_bound < 1:
        raise ValueError("starts_per_bound must be at least one")
    if noise_model == "gaussian_read" and noise_level <= 0:
        raise ValueError("Gaussian read-noise standard deviation must be positive")
    widths = (0.5, 1.0, 2.0, None)
    records = []
    for width_index, width in enumerate(widths):
        for start_index in range(starts_per_bound):
            result = run_case(
                noise_model=noise_model,
                noise_level=noise_level,
                seed=observation_seed,
                initialization_seed=initialization_seed_start + start_index,
                position_bound_half_width=width,
                initialization_policy=initialization_policy,
            )
            records.append({
                "bound_half_width_px": width,
                "start_index": start_index,
                "initialization_seed": initialization_seed_start + start_index,
                "result": result,
            })
    aggregate = {}
    for width in widths:
        selected = [r["result"] for r in records if r["bound_half_width_px"] == width]
        aggregate[str(width)] = {}
        for model in ("integrated", "centre"):
            summaries = [r["summaries"][model] for r in selected]
            values = np.asarray([x["rmse_radial_error_px"] for x in summaries])
            aggregate[str(width)][model] = {
                "runs": len(summaries),
                "optimizer_successes": int(sum(x["optimizer_success"] for x in summaries)),
                "optimizer_failures": int(sum(not x["optimizer_success"] for x in summaries)),
                "mean_rmse_px": float(values.mean()),
                "std_rmse_px": float(values.std(ddof=1)) if len(values) > 1 else 0.0,
                "max_source_swaps": int(max(x["assignment_swaps"] for x in summaries)),
                "total_position_bound_hits": int(sum(x["position_bound_hits"] for x in summaries)),
                "max_nfev": int(max(x["nfev"] for x in summaries)),
            }
    return {
        "experiment": "C9-PIXEL-RESPONSE-POSITION-BOUNDS-001",
        "status": "synthetic_position_bound_sweep",
        "data_kind": "synthetic",
        "noise_model": noise_model,
        "noise_level": noise_level,
        "observation_seed_fixed": observation_seed,
        "starts_per_bound": starts_per_bound,
        "initialization_policy": initialization_policy,
        "bound_widths_px": list(widths),
        "paired_fit_policy": "Both models receive identical observation and initialization for every run.",
        "source_assignment": "Hungarian minimum-total-distance assignment against seven known truth sources.",
        "limitations": [
            "Fixed seven-component model; no source birth/death or false-positive detection.",
            "Hungarian assignment forces a one-to-one match and cannot alone diagnose missing or duplicated components.",
            "truth_jitter starts remain informed by known source coordinates; detector_uniform starts are more independent but are not a complete blind-detection pipeline.",
            "One fixed synthetic geometry, PSF, and observation realization.",
        ],
        "aggregate": aggregate,
        "runs": records,
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


def run_image_peak_detection(
    *,
    noise_model: str = "none",
    noise_level: float = 0.0,
    seed: int = 20261500,
    smoothing_sigma_px: float = 0.8,
    threshold_fractions: tuple[float, ...] = (0.05, 0.10, 0.20),
    minimum_separation_px: float = 1.25,
) -> dict:
    """Detect candidate peaks from the observation without using source truth.

    Truth coordinates are used only after detection to score candidate
    coverage. The detector does not force a seven-candidate output and does
    not run the seven-component fitter when the candidate count is wrong.
    """
    if noise_model not in {"none", "gaussian_read", "poisson"}:
        raise ValueError("unsupported noise_model")
    if noise_level < 0:
        raise ValueError("noise_level must be non-negative")
    if noise_model == "gaussian_read" and noise_level <= 0:
        raise ValueError("Gaussian read-noise standard deviation must be positive")
    if smoothing_sigma_px < 0:
        raise ValueError("smoothing_sigma_px must be non-negative")
    if minimum_separation_px <= 0:
        raise ValueError("minimum_separation_px must be positive")
    if not threshold_fractions or any(
        fraction <= 0 or fraction >= 1 for fraction in threshold_fractions
    ):
        raise ValueError("threshold fractions must lie strictly between 0 and 1")

    truth_positions = SEVEN_SOURCE_POSITIONS.copy()
    clean = _scene_model(
        truth_positions, SEVEN_SOURCE_AMPLITUDES.copy(), 2.0, "integrated",
        SIGMA_PIXELS, IMAGE_SIZE,
    )
    rng = np.random.default_rng(seed)
    if noise_model == "none":
        observed = clean.copy()
    elif noise_model == "gaussian_read":
        observed = clean + rng.normal(0.0, noise_level, clean.shape)
    else:
        observed = rng.poisson(np.clip(clean, 0.0, None)).astype(float)

    filtered = (
        gaussian_filter(observed, smoothing_sigma_px)
        if smoothing_sigma_px > 0 else observed.copy()
    )
    background = float(np.percentile(filtered, 20))
    dynamic_range = float(filtered.max() - background)
    if not np.isfinite(dynamic_range) or dynamic_range <= 0:
        raise ValueError("observation has no positive detectable dynamic range")

    threshold_results = []
    for fraction in threshold_fractions:
        threshold = background + fraction * dynamic_range
        local_max = filtered == maximum_filter(filtered, size=3, mode="nearest")
        coordinates = np.argwhere(local_max & (filtered >= threshold))
        ranked = sorted(
            ((float(filtered[y, x]), float(x), float(y)) for y, x in coordinates),
            reverse=True,
        )
        selected = []
        for intensity, x, y in ranked:
            if all(
                np.hypot(x - candidate["x_px"], y - candidate["y_px"])
                >= minimum_separation_px
                for candidate in selected
            ):
                selected.append({
                    "x_px": x,
                    "y_px": y,
                    "filtered_intensity": intensity,
                })

        if selected:
            # Detection coordinates are array indices (origin at the
            # upper-left); the synthetic source model uses detector-centred
            # coordinates. Convert before comparing with truth.
            detector_centre = (IMAGE_SIZE - 1) / 2
            candidate_xy = np.asarray(
                [[item["x_px"] - detector_centre,
                  item["y_px"] - detector_centre] for item in selected],
                dtype=float,
            )
            distances = np.linalg.norm(
                truth_positions[:, None, :] - candidate_xy[None, :, :], axis=2
            )
            truth_idx, candidate_idx = linear_sum_assignment(distances)
            matched = [
                {
                    "truth_source": int(t + 1),
                    "candidate_index": int(c),
                    "distance_px": float(distances[t, c]),
                }
                for t, c in zip(truth_idx, candidate_idx)
                if distances[t, c] <= 1.0
            ]
            covered_truth = {item["truth_source"] for item in matched}
            matched_candidates = {item["candidate_index"] for item in matched}
        else:
            matched = []
            covered_truth = set()
            matched_candidates = set()

        threshold_results.append({
            "threshold_fraction_of_dynamic_range": float(fraction),
            "absolute_threshold": float(threshold),
            "candidate_count": len(selected),
            "candidates": selected,
            "truth_matches_within_1px": matched,
            "matched_truth_count": len(covered_truth),
            "missed_truth_sources": [
                index + 1 for index in range(len(truth_positions))
                if index + 1 not in covered_truth
            ],
            "unmatched_candidate_indices": [
                index for index in range(len(selected))
                if index not in matched_candidates
            ],
            "fit_readiness": (
                "candidate_count_is_seven_but_fit_not_yet_run"
                if len(selected) == 7
                else "not_ready_candidate_count_differs_from_seven"
            ),
        })

    return {
        "experiment": "C9-PIXEL-RESPONSE-IMAGE-PEAK-DETECTION-001",
        "status": "synthetic_observation_only_candidate_detection",
        "data_kind": "synthetic",
        "noise_model": noise_model,
        "noise_level": noise_level,
        "observation_seed": seed,
        "smoothing_sigma_px": smoothing_sigma_px,
        "minimum_separation_px": minimum_separation_px,
        "threshold_policy": "Fractions of observed filtered dynamic range; no truth-derived threshold.",
        "initialization_policy": "Candidate coordinates come only from local maxima in the observed image.",
        "truth_use_policy": "Truth coordinates are used only after detection for evaluation, never for candidate generation.",
        "source_count_expected_for_evaluation_only": 7,
        "threshold_results": threshold_results,
        "limitations": [
            "Synthetic seven-source geometry only; not astronomical-image validation.",
            "Candidate detection is not yet a complete source birth/death fitting pipeline.",
            "Exactly seven candidates does not prove correct source identities or reliable fit initialization.",
            "One observation per noise condition; no repeated-noise population estimate.",
            "The 1 px matching radius is an explicit diagnostic convention, not a physical detection guarantee.",
        ],
    }



def run_peak_detection_sensitivity_sweep(
    *,
    smoothing_sigmas_px: tuple[float, ...] = (0.0, 0.4, 0.8, 1.2, 1.6),
    minimum_separations_px: tuple[float, ...] = (0.5, 0.75, 1.0, 1.25, 1.5, 2.0),
    threshold_fractions: tuple[float, ...] = (0.01, 0.025, 0.05, 0.10, 0.20),
    noise_model: str = "none",
    noise_level: float = 0.0,
    seed: int = 20261500,
) -> dict:
    """Map detector behaviour over declared smoothing/separation/threshold grids.

    Every candidate list is generated from the observation alone. Truth is
    used only by run_image_peak_detection after candidate generation to score
    coverage. This is a detector-configuration diagnostic, not a fit.
    """
    if not smoothing_sigmas_px or any(value < 0 for value in smoothing_sigmas_px):
        raise ValueError("smoothing sigmas must be a non-empty non-negative grid")
    if not minimum_separations_px or any(value <= 0 for value in minimum_separations_px):
        raise ValueError("minimum separations must be a non-empty positive grid")
    if not threshold_fractions:
        raise ValueError("threshold grid must not be empty")

    records = []
    for smoothing_sigma in smoothing_sigmas_px:
        for separation in minimum_separations_px:
            result = run_image_peak_detection(
                noise_model=noise_model,
                noise_level=noise_level,
                seed=seed,
                smoothing_sigma_px=smoothing_sigma,
                threshold_fractions=threshold_fractions,
                minimum_separation_px=separation,
            )
            for threshold_result in result["threshold_results"]:
                records.append({
                    "smoothing_sigma_px": float(smoothing_sigma),
                    "minimum_separation_px": float(separation),
                    "threshold_fraction": threshold_result[
                        "threshold_fraction_of_dynamic_range"
                    ],
                    "candidate_count": threshold_result["candidate_count"],
                    "matched_truth_count": threshold_result["matched_truth_count"],
                    "missed_truth_count": len(
                        threshold_result["missed_truth_sources"]
                    ),
                    "unmatched_candidate_count": len(
                        threshold_result["unmatched_candidate_indices"]
                    ),
                    "fit_readiness": threshold_result["fit_readiness"],
                })

    return {
        "experiment": "C9-PIXEL-RESPONSE-PEAK-DETECTION-SENSITIVITY-001",
        "status": "synthetic_peak_detection_sensitivity_sweep",
        "data_kind": "synthetic",
        "noise_model": noise_model,
        "noise_level": noise_level,
        "observation_seed": seed,
        "smoothing_sigmas_px": list(smoothing_sigmas_px),
        "minimum_separations_px": list(minimum_separations_px),
        "threshold_fractions": list(threshold_fractions),
        "configuration_count": len(smoothing_sigmas_px) * len(minimum_separations_px),
        "scored_configuration_count": len(records),
        "candidate_generation_policy": (
            "Observed-image local maxima only; truth is excluded from candidate generation."
        ),
        "scoring_policy": (
            "Hungarian one-to-one assignment with a declared 1 px matching radius."
        ),
        "records": records,
        "limitations": [
            "Single synthetic seven-source scene and one observation seed per noise condition.",
            "Grid results are configuration diagnostics, not estimates of population detection performance.",
            "The one-to-one 1 px scoring rule is a diagnostic convention.",
            "No source fitting is attempted, even when seven candidates are found.",
            "A good candidate count does not establish correct source identity or unbiased positions.",
        ],
    }
