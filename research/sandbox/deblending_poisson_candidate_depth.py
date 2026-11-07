"""Paired candidate-depth ablation for the Poisson residual proposal pool."""
from __future__ import annotations

import numpy as np

from research.sandbox.deblending_geometry_poisson import _score
from research.sandbox.poisson_psf_deblending import run_poisson_psf_deblending
from research.sandbox.pixel_response_reproduction import (
    IMAGE_SIZE, SIGMA_PIXELS, SEVEN_SOURCE_AMPLITUDES,
    SEVEN_SOURCE_POSITIONS, _scene_model,
)

DEPTHS = (5, 10, 25, 50)


def _summarize(records: list[dict], depth: int) -> dict:
    rows = [item["depths"][str(depth)] for item in records]
    scores = [row["score"] for row in rows]
    return {
        "trials": len(rows),
        "mean_matched_truth_sources": float(np.mean(
            [score["matched_truth_count"] for score in scores]
        )),
        "mean_missed_truth_sources": float(np.mean(
            [score["missed_truth_count"] for score in scores]
        )),
        "mean_unmatched_candidates": float(np.mean(
            [score["unmatched_candidate_count"] for score in scores]
        )),
        "exact_seven_source_recoveries": int(sum(
            score["all_truth_recovered"] for score in scores
        )),
        "mean_selected_candidate_count": float(np.mean(
            [row["selected_count"] for row in rows]
        )),
        "proposal_fits_evaluated": int(sum(
            row["proposal_fits_evaluated"] for row in rows
        )),
        "optimizer_function_evaluations": int(sum(
            row["optimizer_function_evaluations"] for row in rows
        )),
        "accepted_steps": int(sum(row["accepted_steps"] for row in rows)),
        "rejected_steps": int(sum(row["rejected_steps"] for row in rows)),
    }


def _paired(records: list[dict], depth: int, baseline: int = 5) -> dict:
    differences = [
        item["depths"][str(depth)]["score"]["matched_truth_count"]
        - item["depths"][str(baseline)]["score"]["matched_truth_count"]
        for item in records
    ]
    return {
        "depth": depth,
        "baseline_depth": baseline,
        "better_trials": int(sum(value > 0 for value in differences)),
        "worse_trials": int(sum(value < 0 for value in differences)),
        "ties": int(sum(value == 0 for value in differences)),
        "mean_matched_source_difference": float(np.mean(differences)),
        "exact_recovery_depth": int(sum(
            item["depths"][str(depth)]["score"]["all_truth_recovered"]
            for item in records
        )),
        "exact_recovery_baseline": int(sum(
            item["depths"][str(baseline)]["score"]["all_truth_recovered"]
            for item in records
        )),
    }


def run_candidate_depth_ablation(
    *, trials_per_condition: int = 3, seed_start: int = 20262000,
    geometry_scales=(0.8, 1.0, 1.2), exposures=(1.0, 0.1, 0.03),
) -> dict:
    """Compare top-5/10/25/50 on identical synthetic count observations.

    Truth is used only after each depth's detector run for scoring. The
    proposal score, 1 px NMS, Poisson objective, optimizer, BIC penalty,
    acceptance and stopping rules remain unchanged.
    """
    if trials_per_condition < 1:
        raise ValueError("trials_per_condition must be positive")
    records = []
    seed = int(seed_start)
    for scale in geometry_scales:
        for exposure in exposures:
            for trial_index in range(trials_per_condition):
                truth = SEVEN_SOURCE_POSITIONS * float(scale)
                expected_rate = _scene_model(
                    truth, SEVEN_SOURCE_AMPLITUDES, 2.0, "integrated",
                    SIGMA_PIXELS, IMAGE_SIZE,
                )
                rng = np.random.default_rng(seed)
                observed_counts = rng.poisson(
                    np.clip(expected_rate * exposure, 0.0, None)
                ).astype(float)
                observed_rate = observed_counts / exposure
                depth_rows = {}
                for depth in DEPTHS:
                    result = run_poisson_psf_deblending(
                        observed_rate, exposure=exposure,
                        assumed_sigma_px=SIGMA_PIXELS,
                        proposal_policy="best_bic_top_k",
                        proposal_top_k=depth,
                    )
                    steps = result["candidate_trials"]
                    depth_rows[str(depth)] = {
                        "selected_count": int(result["selected_source_count"]),
                        "score": _score(result["candidates"], truth),
                        "proposal_fits_evaluated": int(sum(
                            step["proposal_candidates_evaluated"] for step in steps
                        )),
                        "optimizer_function_evaluations": int(sum(
                            step["total_optimizer_nfev"] for step in steps
                        )),
                        "accepted_steps": int(sum(step["accepted"] for step in steps)),
                        "rejected_steps": int(sum(not step["accepted"] for step in steps)),
                        "optimizer_success": bool(result["optimizer_success"]),
                    }
                records.append({
                    "seed": seed,
                    "trial_index": trial_index,
                    "geometry_scale": float(scale),
                    "exposure": float(exposure),
                    "observed_counts_sum": int(np.sum(observed_counts)),
                    "depths": depth_rows,
                })
                seed += 1

    return {
        "experiment": "C9-DEBLENDING-POISSON-CANDIDATE-DEPTH-001",
        "status": "paired_exploratory_synthetic_ablation",
        "data_kind": "synthetic",
        "seed_start": int(seed_start),
        "trials_per_condition": int(trials_per_condition),
        "trial_count": len(records),
        "proposal_depths": list(DEPTHS),
        "nonmaximum_suppression_radius_px": 1.0,
        "fixed_detector_rules": [
            "Same Poisson count observation for every depth within a trial.",
            "Same residual score map and observation-only ranked proposals.",
            "Same 1 px non-maximum-suppression radius.",
            "Same Poisson deviance, parameterization, bounds, optimizer tolerances and BIC penalty.",
            "Same BIC candidate selection, acceptance and stopping rules.",
            "No truth information enters proposals, fitting, or selection.",
            "Truth is used only after each run for Hungarian source matching within 1 px.",
        ],
        "overall": {str(depth): _summarize(records, depth) for depth in DEPTHS},
        "paired_vs_top5": {
            str(depth): _paired(records, depth) for depth in DEPTHS if depth != 5
        },
        "by_condition": {
            f"geometry={scale},exposure={exposure}": {
                str(depth): _summarize([
                    row for row in records
                    if row["geometry_scale"] == scale and row["exposure"] == exposure
                ], depth)
                for depth in DEPTHS
            }
            for scale in geometry_scales for exposure in exposures
        },
        "records": records,
        "limitations": [
            "Exploratory 27-trial pilot: three trials per geometry/exposure cell.",
            "One fixed seven-source synthetic scene family and one PSF/noise setup.",
            "Deeper pools increase optimizer cost and may select different local fits.",
            "A proposal peak near truth is not proof of source identifiability.",
            "Results do not establish performance on real astronomical images.",
        ],
    }
