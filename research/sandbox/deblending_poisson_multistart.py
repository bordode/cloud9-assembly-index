"""Three-way Gaussian / Poisson single-start / Poisson multi-start comparison."""
from __future__ import annotations

import numpy as np

from research.sandbox.deblending_geometry_poisson import _score, _summarize
from research.sandbox.iterative_psf_deblending import run_iterative_psf_deblending
from research.sandbox.poisson_psf_deblending import run_poisson_psf_deblending
from research.sandbox.pixel_response_reproduction import (
    IMAGE_SIZE,
    SIGMA_PIXELS,
    SEVEN_SOURCE_AMPLITUDES,
    SEVEN_SOURCE_POSITIONS,
    _scene_model,
)

MULTISTART_OFFSETS = (
    (0.0, 0.0),
    (0.35, 0.0), (-0.35, 0.0),
    (0.0, 0.35), (0.0, -0.35),
    (0.35, 0.35), (0.35, -0.35),
    (-0.35, 0.35), (-0.35, -0.35),
)


def run_case(*, geometry_scale: float, exposure: float, seed: int) -> dict:
    truth_positions = SEVEN_SOURCE_POSITIONS * float(geometry_scale)
    expected_rate = _scene_model(
        truth_positions, SEVEN_SOURCE_AMPLITUDES, 2.0, "integrated",
        SIGMA_PIXELS, IMAGE_SIZE,
    )
    rng = np.random.default_rng(seed)
    expected_counts = np.clip(expected_rate * exposure, 0.0, None)
    observed_counts = rng.poisson(expected_counts).astype(float)
    observed_rate = observed_counts / exposure

    gaussian = run_iterative_psf_deblending(
        observed_rate, assumed_sigma_px=SIGMA_PIXELS
    )
    gaussian_joint = gaussian["joint_refit"]
    gaussian_candidates = (
        gaussian_joint["candidates"] if gaussian_joint is not None else []
    )
    gaussian_score = _score(gaussian_candidates, truth_positions)

    single = run_poisson_psf_deblending(
        observed_rate, exposure=exposure, assumed_sigma_px=SIGMA_PIXELS
    )
    multi = run_poisson_psf_deblending(
        observed_rate, exposure=exposure, assumed_sigma_px=SIGMA_PIXELS,
        proposal_start_offsets=MULTISTART_OFFSETS,
    )
    return {
        "seed": int(seed),
        "geometry_scale": float(geometry_scale),
        "exposure": float(exposure),
        "observation_counts_sum": int(np.sum(observed_counts)),
        "gaussian": {
            "selected_count": int(gaussian["selected_source_count"]),
            "score": gaussian_score,
            "optimizer_success": (
                bool(gaussian_joint["optimizer_success"])
                if gaussian_joint is not None else False
            ),
        },
        "poisson_single": {
            "selected_count": int(single["selected_source_count"]),
            "score": _score(single["candidates"], truth_positions),
            "optimizer_success": bool(single["optimizer_success"]),
            "poisson_deviance": float(single["poisson_deviance"]),
            "poisson_bic": float(single["poisson_bic"]),
            "candidate_trials": single["candidate_trials"],
        },
        "poisson_multistart": {
            "selected_count": int(multi["selected_source_count"]),
            "score": _score(multi["candidates"], truth_positions),
            "optimizer_success": bool(multi["optimizer_success"]),
            "poisson_deviance": float(multi["poisson_deviance"]),
            "poisson_bic": float(multi["poisson_bic"]),
            "candidate_trials": multi["candidate_trials"],
        },
    }


def _summary(records: list[dict], method: str) -> dict:
    scores = [record[method]["score"] for record in records]
    return {
        "trials": len(records),
        "mean_matched_truth_sources": float(np.mean(
            [score["matched_truth_count"] for score in scores]
        )),
        "mean_missed_truth_sources": float(np.mean(
            [score["missed_truth_count"] for score in scores]
        )),
        "mean_unmatched_candidates": float(np.mean(
            [score["unmatched_candidate_count"] for score in scores]
        )),
        "mean_selected_candidate_count": float(np.mean(
            [record[method]["selected_count"] for record in records]
        )),
        "exact_seven_source_recoveries": int(sum(
            score["all_truth_recovered"] for score in scores
        )),
        "optimizer_successes": int(sum(
            record[method]["optimizer_success"] for record in records
        )),
    }


def run_multistart_sweep(
    *,
    trials_per_condition: int = 10,
    geometry_scales: tuple[float, ...] = (0.8, 1.0, 1.2),
    exposures: tuple[float, ...] = (1.0, 0.1, 0.03),
    seed_start: int = 20261800,
) -> dict:
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
                    geometry_scale=float(scale), exposure=float(exposure), seed=seed
                )
                record["trial_index"] = int(trial_index)
                records.append(record)
                seed += 1

    methods = ("gaussian", "poisson_single", "poisson_multistart")
    overall = {method: _summary(records, method) for method in methods}
    paired = {
        "multistart_matched_more_than_single": 0,
        "single_matched_more_than_multistart": 0,
        "ties": 0,
        "mean_matched_difference_multistart_minus_single": 0.0,
        "exact_recovery_changed_single_to_multi": 0,
    }
    differences = []
    for record in records:
        single = record["poisson_single"]["score"]
        multi = record["poisson_multistart"]["score"]
        difference = multi["matched_truth_count"] - single["matched_truth_count"]
        differences.append(difference)
        if difference > 0:
            paired["multistart_matched_more_than_single"] += 1
        elif difference < 0:
            paired["single_matched_more_than_multistart"] += 1
        else:
            paired["ties"] += 1
        if multi["all_truth_recovered"] != single["all_truth_recovered"]:
            paired["exact_recovery_changed_single_to_multi"] += 1
    paired["mean_matched_difference_multistart_minus_single"] = float(
        np.mean(differences)
    )

    return {
        "experiment": "C9-DEBLENDING-POISSON-MULTISTART-001",
        "status": "predeclared_three_way_synthetic_comparison",
        "data_kind": "synthetic",
        "seed_start": int(seed_start),
        "trials_per_condition": int(trials_per_condition),
        "geometry_scales": [float(value) for value in geometry_scales],
        "exposures": [float(value) for value in exposures],
        "trial_count": len(records),
        "multistart_offsets_px": [list(offset) for offset in MULTISTART_OFFSETS],
        "methods": {
            "gaussian": "Existing observation-only Gaussian baseline.",
            "poisson_single": "Existing Poisson detector with its unchanged single proposal initialization.",
            "poisson_multistart": (
                "Same Poisson detector and proposal sequence; nine deterministic "
                "new-source initial positions; choose successful fit with lowest "
                "Poisson deviance before applying the unchanged Poisson BIC rule."
            ),
        },
        "anti_peeking_controls": [
            "All three methods receive the same observed count-rate image in each trial.",
            "No detector receives truth positions, amplitudes, or source count.",
            "Truth is used only after detection for the same Hungarian one-to-one scoring within 1 px.",
            "The seed range is disjoint from the PR #35 comparison.",
            "No BIC penalty tuning or truth-guided seed selection is performed.",
        ],
        "overall": overall,
        "paired_poisson_comparison": paired,
        "records": records,
        "limitations": [
            "Synthetic point sources, fixed PSF family/width, detector size, fluxes, and background.",
            "Only one deterministic nine-start offset grid is tested.",
            "Both Poisson methods retain greedy proposals and the same approximate BIC selection rule.",
            "Results do not establish performance on real astronomical images.",
        ],
    }
