"""Geometry and photon-counting stress tests for observation-only PSF deblending.

This module is an exploratory synthetic benchmark. The detector receives only
the noisy image and declared PSF width; truth positions are used only to render
the scene and to score completed detections afterward.

Important: the detector's current stopping rule profiles a Gaussian residual
variance. Poisson observations therefore test robustness under likelihood
mismatch; this module does not claim a Poisson-optimal detector.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment

from research.sandbox.iterative_psf_deblending import (
    run_iterative_psf_deblending,
)
from research.sandbox.pixel_response_reproduction import (
    IMAGE_SIZE,
    SIGMA_PIXELS,
    SEVEN_SOURCE_AMPLITUDES,
    SEVEN_SOURCE_POSITIONS,
    _scene_model,
)


def _score(candidates: list[dict], truth_positions: np.ndarray,
           radius_px: float = 1.0) -> dict:
    """Score a completed candidate list; never called by the detector."""
    candidate_xy = np.asarray(
        [[item["x_px"], item["y_px"]] for item in candidates], dtype=float
    ).reshape((-1, 2))
    if len(candidate_xy) == 0:
        matched = []
    else:
        distances = np.linalg.norm(
            truth_positions[:, None, :] - candidate_xy[None, :, :], axis=2
        )
        truth_idx, candidate_idx = linear_sum_assignment(distances)
        matched = [
            float(distances[t, c])
            for t, c in zip(truth_idx, candidate_idx)
            if distances[t, c] <= radius_px
        ]
    matched_count = len(matched)
    return {
        "candidate_count": int(len(candidates)),
        "matched_truth_count": matched_count,
        "missed_truth_count": int(len(truth_positions) - matched_count),
        "unmatched_candidate_count": int(len(candidates) - matched_count),
        "matched_radial_errors_px": matched,
        "all_truth_recovered": bool(
            matched_count == len(truth_positions)
            and len(candidates) == len(truth_positions)
        ),
    }


def run_case(*, geometry_scale: float, exposure: float, seed: int,
             assumed_sigma_px: float = SIGMA_PIXELS) -> dict:
    """Generate one Poisson-counted scene, detect blindly, then score."""
    if geometry_scale <= 0:
        raise ValueError("geometry_scale must be positive")
    if exposure <= 0:
        raise ValueError("exposure must be positive")
    if assumed_sigma_px <= 0:
        raise ValueError("assumed_sigma_px must be positive")

    truth_positions = SEVEN_SOURCE_POSITIONS * float(geometry_scale)
    clean_expected_rate = _scene_model(
        truth_positions, SEVEN_SOURCE_AMPLITUDES, 2.0, "integrated",
        SIGMA_PIXELS, IMAGE_SIZE,
    )
    rng = np.random.default_rng(seed)
    expected_counts = np.clip(clean_expected_rate * exposure, 0.0, None)
    observed = rng.poisson(expected_counts).astype(float) / exposure

    # No truth coordinates, amplitudes, or source count enter this call.
    detected = run_iterative_psf_deblending(
        observed, assumed_sigma_px=assumed_sigma_px
    )
    greedy_score = _score(detected["selected_candidates"], truth_positions)
    joint = detected["joint_refit"]
    joint_score = (
        _score(joint["candidates"], truth_positions) if joint is not None else None
    )
    return {
        "seed": int(seed),
        "geometry_scale": float(geometry_scale),
        "exposure": float(exposure),
        "effective_counting_noise_scale": float(1.0 / np.sqrt(exposure)),
        "truth_psf_sigma_px": float(SIGMA_PIXELS),
        "assumed_psf_sigma_px": float(assumed_sigma_px),
        "greedy_selected_count": int(detected["selected_source_count"]),
        "greedy_score": greedy_score,
        "joint_score": joint_score,
        "joint_optimizer_success": (
            bool(joint["optimizer_success"]) if joint is not None else False
        ),
        "joint_bic": float(joint["bic"]) if joint is not None else None,
    }


def run_geometry_poisson_sweep(
    *, trials_per_condition: int = 10,
    geometry_scales: tuple[float, ...] = (0.8, 1.0, 1.2),
    exposures: tuple[float, ...] = (1.0, 0.1, 0.03),
    seed_start: int = 20261700,
    assumed_sigma_px: float = SIGMA_PIXELS,
) -> dict:
    """Run a predeclared geometry × Poisson-exposure grid."""
    if trials_per_condition < 1:
        raise ValueError("trials_per_condition must be positive")
    if not geometry_scales or any(value <= 0 for value in geometry_scales):
        raise ValueError("geometry_scales must be non-empty and positive")
    if not exposures or any(value <= 0 for value in exposures):
        raise ValueError("exposures must be non-empty and positive")

    records = []
    seed = int(seed_start)
    for scale in geometry_scales:
        for exposure in exposures:
            for trial_index in range(trials_per_condition):
                record = run_case(
                    geometry_scale=float(scale),
                    exposure=float(exposure),
                    seed=seed,
                    assumed_sigma_px=assumed_sigma_px,
                )
                record["trial_index"] = int(trial_index)
                records.append(record)
                seed += 1

    aggregate = {}
    for scale in geometry_scales:
        for exposure in exposures:
            selected = [
                item for item in records
                if item["geometry_scale"] == float(scale)
                and item["exposure"] == float(exposure)
            ]
            aggregate[f"geometry={scale},exposure={exposure}"] = {
                "trials": len(selected),
                "mean_greedy_matched": float(np.mean([
                    item["greedy_score"]["matched_truth_count"]
                    for item in selected
                ])),
                "mean_joint_matched": float(np.mean([
                    item["joint_score"]["matched_truth_count"]
                    if item["joint_score"] is not None else 0
                    for item in selected
                ])),
                "joint_all_seven_trials": int(sum(
                    item["joint_score"] is not None
                    and item["joint_score"]["all_truth_recovered"]
                    for item in selected
                )),
                "joint_optimizer_successes": int(sum(
                    item["joint_optimizer_success"] for item in selected
                )),
                "mean_joint_unmatched_candidates": float(np.mean([
                    item["joint_score"]["unmatched_candidate_count"]
                    if item["joint_score"] is not None else 7
                    for item in selected
                ])),
            }

    return {
        "experiment": "C9-DEBLENDING-GEOMETRY-POISSON-001",
        "status": "exploratory_synthetic_geometry_poisson_sweep",
        "data_kind": "synthetic",
        "truth_geometry": (
            "seven-source geometry uniformly scaled about detector centre"
        ),
        "geometry_scales": [float(value) for value in geometry_scales],
        "truth_psf_sigma_px": float(SIGMA_PIXELS),
        "assumed_psf_sigma_px": float(assumed_sigma_px),
        "noise_model": (
            "Poisson counts: observed = Poisson(expected_rate * exposure) "
            "/ exposure"
        ),
        "exposures": [float(value) for value in exposures],
        "trials_per_condition": int(trials_per_condition),
        "candidate_generation_policy": (
            "detector receives only the noisy observation and assumed PSF "
            "width; truth positions and source count are excluded"
        ),
        "scoring_policy": (
            "post-fit Hungarian one-to-one assignment within 1 px; exact "
            "seven-source recovery also requires no unmatched candidates"
        ),
        "likelihood_caveat": (
            "The current detector uses a profiled Gaussian BIC stopping rule "
            "on Poisson-counted data. This is an intentional likelihood-"
            "mismatch stress test, not a Poisson-optimal inference method."
        ),
        "aggregate": aggregate,
        "records": records,
        "limitations": [
            "Synthetic point sources and one detector size only.",
            "Only uniform geometry scaling is varied; source identities and fluxes remain fixed.",
            "The Gaussian BIC is not the Poisson likelihood and may mis-rank candidate counts.",
            "The assumed PSF width is fixed at the declared value in this grid.",
            "Finite seeds; results do not establish astronomical-image performance.",
        ],
    }
