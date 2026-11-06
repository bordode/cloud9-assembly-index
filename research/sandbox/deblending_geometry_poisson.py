"""Paired Gaussian-versus-Poisson source recovery stress test.

Both detectors receive the same Poisson-counted observation and declared PSF
width. Truth is used only to render the scene and score completed candidates.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment

from research.sandbox.iterative_psf_deblending import run_iterative_psf_deblending
from research.sandbox.poisson_psf_deblending import run_poisson_psf_deblending
from research.sandbox.pixel_response_reproduction import (
    IMAGE_SIZE,
    SIGMA_PIXELS,
    SEVEN_SOURCE_AMPLITUDES,
    SEVEN_SOURCE_POSITIONS,
    _scene_model,
)


def _score(candidates: list[dict], truth_positions: np.ndarray,
           radius_px: float = 1.0) -> dict:
    """Score a completed candidate list; never called by either detector."""
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
    """Generate one scene and compare both detectors on the same observation."""
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
    observed_counts = rng.poisson(expected_counts).astype(float)
    observed_rate = observed_counts / exposure

    # The legacy detector receives the same observed count-rate image.
    gaussian = run_iterative_psf_deblending(
        observed_rate, assumed_sigma_px=assumed_sigma_px
    )
    gaussian_joint = gaussian["joint_refit"]
    gaussian_score = (
        _score(gaussian_joint["candidates"], truth_positions)
        if gaussian_joint is not None else _score([], truth_positions)
    )

    # The Poisson detector receives the same image and the known exposure,
    # but no truth coordinates, amplitudes, or source count.
    poisson = run_poisson_psf_deblending(
        observed_rate, exposure=exposure, assumed_sigma_px=assumed_sigma_px
    )
    poisson_score = _score(poisson["candidates"], truth_positions)

    return {
        "seed": int(seed),
        "geometry_scale": float(geometry_scale),
        "exposure": float(exposure),
        "effective_counting_noise_scale": float(1.0 / np.sqrt(exposure)),
        "truth_psf_sigma_px": float(SIGMA_PIXELS),
        "assumed_psf_sigma_px": float(assumed_sigma_px),
        "observation_counts_sum": int(np.sum(observed_counts)),
        "gaussian": {
            "greedy_selected_count": int(gaussian["selected_source_count"]),
            "joint_score": gaussian_score,
            "joint_optimizer_success": (
                bool(gaussian_joint["optimizer_success"])
                if gaussian_joint is not None else False
            ),
            "joint_bic": (
                float(gaussian_joint["bic"])
                if gaussian_joint is not None else None
            ),
        },
        "poisson": {
            "selected_count": int(poisson["selected_source_count"]),
            "score": poisson_score,
            "optimizer_success": bool(poisson["optimizer_success"]),
            "poisson_deviance": float(poisson["poisson_deviance"]),
            "poisson_bic": float(poisson["poisson_bic"]),
            "candidate_trials": poisson["candidate_trials"],
        },
    }


def _summarize(records: list[dict], method: str) -> dict:
    if method == "gaussian":
        scores = [item["gaussian"]["joint_score"] for item in records]
        successes = [item["gaussian"]["joint_optimizer_success"] for item in records]
        counts = [item["gaussian"]["greedy_selected_count"] for item in records]
    else:
        scores = [item["poisson"]["score"] for item in records]
        successes = [item["poisson"]["optimizer_success"] for item in records]
        counts = [item["poisson"]["selected_count"] for item in records]
    return {
        "trials": len(records),
        "mean_matched_truth_sources": float(np.mean([
            score["matched_truth_count"] for score in scores
        ])),
        "mean_missed_truth_sources": float(np.mean([
            score["missed_truth_count"] for score in scores
        ])),
        "mean_unmatched_candidates": float(np.mean([
            score["unmatched_candidate_count"] for score in scores
        ])),
        "exact_seven_source_recoveries": int(sum(
            score["all_truth_recovered"] for score in scores
        )),
        "mean_selected_candidate_count": float(np.mean(counts)),
        "optimizer_successes": int(sum(successes)),
    }


def run_geometry_poisson_sweep(
    *, trials_per_condition: int = 10,
    geometry_scales: tuple[float, ...] = (0.8, 1.0, 1.2),
    exposures: tuple[float, ...] = (1.0, 0.1, 0.03),
    seed_start: int = 20261700,
    assumed_sigma_px: float = SIGMA_PIXELS,
) -> dict:
    """Run a paired geometry × exposure grid for both statistical methods."""
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
                "gaussian": _summarize(selected, "gaussian"),
                "poisson": _summarize(selected, "poisson"),
            }

    all_methods = {
        "gaussian": _summarize(records, "gaussian"),
        "poisson": _summarize(records, "poisson"),
    }
    return {
        "experiment": "C9-DEBLENDING-GAUSSIAN-VS-POISSON-001",
        "status": "paired_synthetic_geometry_poisson_likelihood_comparison",
        "data_kind": "synthetic",
        "truth_geometry": (
            "seven-source geometry uniformly scaled about detector centre"
        ),
        "geometry_scales": [float(value) for value in geometry_scales],
        "truth_psf_sigma_px": float(SIGMA_PIXELS),
        "assumed_psf_sigma_px": float(assumed_sigma_px),
        "noise_model": (
            "same Poisson counts for both methods: "
            "observed_counts ~ Poisson(expected_rate * exposure)"
        ),
        "exposures": [float(value) for value in exposures],
        "trials_per_condition": int(trials_per_condition),
        "methods": {
            "gaussian": (
                "legacy matched-filter proposals, Gaussian least-squares "
                "fits, profiled Gaussian BIC stopping, conditional joint refit"
            ),
            "poisson": (
                "Pearson-residual matched-filter proposals, joint Poisson "
                "deviance maximum-likelihood fits, Poisson BIC stopping"
            ),
        },
        "fair_comparison_controls": [
            "Both methods receive exactly the same count image and exposure.",
            "Both use the same declared pixel-integrated PSF family and width.",
            "Neither detector receives truth positions, amplitudes, or source count.",
            "Both are scored after detection by the same Hungarian one-to-one assignment within 1 px.",
            "Exact recovery requires seven matched truths and exactly seven candidates.",
        ],
        "aggregate": aggregate,
        "overall": all_methods,
        "records": records,
        "limitations": [
            "Synthetic point sources and one detector size only.",
            "Only uniform geometry scaling is varied; source identities and fluxes remain fixed.",
            "The Poisson detector assumes independent counts and a constant non-negative background.",
            "Both methods use greedy candidate proposals and can miss sources.",
            "Poisson BIC is an approximate model-selection criterion; finite seeds limit precision.",
            "The assumed PSF width is fixed at the declared value in this grid.",
            "Results do not establish performance on astronomical images.",
        ],
    }
