"""Three-way comparison of Gaussian, single-peak Poisson, and top-five/BIC Poisson."""
from __future__ import annotations

import numpy as np

from research.sandbox.deblending_geometry_poisson import _score
from research.sandbox.iterative_psf_deblending import run_iterative_psf_deblending
from research.sandbox.poisson_psf_deblending import run_poisson_psf_deblending
from research.sandbox.pixel_response_reproduction import (
    IMAGE_SIZE, SIGMA_PIXELS, SEVEN_SOURCE_AMPLITUDES,
    SEVEN_SOURCE_POSITIONS, _scene_model,
)


def _proposal_truth_audit(trials: list[dict], truth: np.ndarray) -> list[dict]:
    """Post-hoc only: label proposal coordinates by proximity to hidden truth."""
    audited = []
    for trial in trials:
        pool = trial.get("proposal_pool", [])
        labels = []
        for proposal in pool:
            distances = np.linalg.norm(
                truth - np.array([proposal["x_px"], proposal["y_px"]]), axis=1
            )
            nearest = int(np.argmin(distances))
            labels.append({
                "rank": proposal["rank"],
                "nearest_truth_index_posthoc": nearest,
                "nearest_truth_distance_px_posthoc": float(distances[nearest]),
                "within_one_pixel_posthoc": bool(distances[nearest] <= 1.0),
            })
        audited.append({
            "step": trial["step"],
            "accepted": trial["accepted"],
            "bic_improvement": trial["bic_improvement"],
            "selected_proposal_rank": trial["selected_proposal_rank"],
            "proposal_pool_posthoc_truth_audit": labels,
        })
    return audited


def run_case(*, geometry_scale: float, exposure: float, seed: int,
             proposal_top_k: int = 5) -> dict:
    truth = SEVEN_SOURCE_POSITIONS * float(geometry_scale)
    expected_rate = _scene_model(
        truth, SEVEN_SOURCE_AMPLITUDES, 2.0, "integrated",
        SIGMA_PIXELS, IMAGE_SIZE,
    )
    rng = np.random.default_rng(seed)
    observed_counts = rng.poisson(
        np.clip(expected_rate * exposure, 0.0, None)
    ).astype(float)
    observed_rate = observed_counts / exposure

    gaussian = run_iterative_psf_deblending(
        observed_rate, assumed_sigma_px=SIGMA_PIXELS
    )
    gj = gaussian["joint_refit"]
    gc = gj["candidates"] if gj is not None else []
    gaussian_record = {
        "selected_count": int(gaussian["selected_source_count"]),
        "score": _score(gc, truth),
        "optimizer_success": bool(gj["optimizer_success"]) if gj else False,
    }

    single = run_poisson_psf_deblending(
        observed_rate, exposure=exposure, assumed_sigma_px=SIGMA_PIXELS,
        proposal_policy="top_score",
    )
    topk = run_poisson_psf_deblending(
        observed_rate, exposure=exposure, assumed_sigma_px=SIGMA_PIXELS,
        proposal_policy="best_bic_top_k", proposal_top_k=proposal_top_k,
    )
    return {
        "seed": int(seed),
        "geometry_scale": float(geometry_scale),
        "exposure": float(exposure),
        "observation_counts_sum": int(np.sum(observed_counts)),
        "gaussian": gaussian_record,
        "poisson_single": {
            "selected_count": int(single["selected_source_count"]),
            "score": _score(single["candidates"], truth),
            "optimizer_success": bool(single["optimizer_success"]),
            "candidate_trials": single["candidate_trials"],
        },
        "poisson_topk_bic": {
            "selected_count": int(topk["selected_source_count"]),
            "score": _score(topk["candidates"], truth),
            "optimizer_success": bool(topk["optimizer_success"]),
            "candidate_trials": topk["candidate_trials"],
            "posthoc_proposal_truth_audit": _proposal_truth_audit(
                topk["candidate_trials"], truth
            ),
        },
    }


def _summary(records: list[dict], method: str) -> dict:
    scores = [item[method]["score"] for item in records]
    return {
        "trials": len(records),
        "mean_matched_truth_sources": float(np.mean(
            [s["matched_truth_count"] for s in scores]
        )),
        "mean_missed_truth_sources": float(np.mean(
            [s["missed_truth_count"] for s in scores]
        )),
        "mean_unmatched_candidates": float(np.mean(
            [s["unmatched_candidate_count"] for s in scores]
        )),
        "mean_selected_candidate_count": float(np.mean(
            [item[method]["selected_count"] for item in records]
        )),
        "exact_seven_source_recoveries": int(sum(
            s["all_truth_recovered"] for s in scores
        )),
        "optimizer_successes": int(sum(
            item[method]["optimizer_success"] for item in records
        )),
    }


def _paired(records: list[dict], left: str, right: str) -> dict:
    differences = [
        item[left]["score"]["matched_truth_count"]
        - item[right]["score"]["matched_truth_count"]
        for item in records
    ]
    return {
        "left_matched_more": int(sum(x > 0 for x in differences)),
        "right_matched_more": int(sum(x < 0 for x in differences)),
        "ties": int(sum(x == 0 for x in differences)),
        "mean_matched_difference_left_minus_right": float(np.mean(differences)),
        "exact_recovery_left": int(sum(
            item[left]["score"]["all_truth_recovered"] for item in records
        )),
        "exact_recovery_right": int(sum(
            item[right]["score"]["all_truth_recovered"] for item in records
        )),
    }


def run_proposal_bic_sweep(*, trials_per_condition: int = 10,
                           seed_start: int = 20261900,
                           proposal_top_k: int = 5) -> dict:
    if trials_per_condition < 1 or proposal_top_k < 2:
        raise ValueError("trials_per_condition must be positive and proposal_top_k >= 2")
    records = []
    seed = int(seed_start)
    for scale in (0.8, 1.0, 1.2):
        for exposure in (1.0, 0.1, 0.03):
            for index in range(trials_per_condition):
                record = run_case(
                    geometry_scale=scale, exposure=exposure, seed=seed,
                    proposal_top_k=proposal_top_k,
                )
                record["trial_index"] = index
                records.append(record)
                seed += 1

    methods = ("gaussian", "poisson_single", "poisson_topk_bic")
    overall = {name: _summary(records, name) for name in methods}
    by_condition = {}
    for scale in (0.8, 1.0, 1.2):
        for exposure in (1.0, 0.1, 0.03):
            cell = [r for r in records
                    if r["geometry_scale"] == scale and r["exposure"] == exposure]
            by_condition[f"geometry={scale},exposure={exposure}"] = {
                name: _summary(cell, name) for name in methods
            }

    candidate_steps = [
        trial for record in records
        for trial in record["poisson_topk_bic"]["candidate_trials"]
    ]
    return {
        "experiment": "C9-DEBLENDING-POISSON-PROPOSAL-BIC-001",
        "status": "predeclared_three_way_synthetic_comparison",
        "data_kind": "synthetic",
        "seed_start": int(seed_start),
        "trials_per_condition": int(trials_per_condition),
        "proposal_top_k": int(proposal_top_k),
        "nonmaximum_suppression_radius_px": 1.0,
        "trial_count": len(records),
        "methods": {
            "gaussian": "Existing observation-only Gaussian baseline.",
            "poisson_single": "Existing Poisson detector; single highest residual proposal; unchanged likelihood and BIC.",
            "poisson_topk_bic": "Fit up to five spatially separated residual proposals and choose successful fit with lowest unchanged Poisson BIC.",
        },
        "anti_peeking_controls": [
            "All methods receive the same Poisson count observation.",
            "No detector receives truth positions, amplitudes, or source count.",
            "Truth is used only after detection for Hungarian scoring within 1 px.",
            "Fresh seed range is disjoint from earlier PR #35 and PR #36 experiments.",
            "No BIC penalty tuning or truth-guided proposal selection is performed.",
        ],
        "overall": overall,
        "by_condition": by_condition,
        "paired_topk_vs_single": _paired(records, "poisson_topk_bic", "poisson_single"),
        "paired_topk_vs_gaussian": _paired(records, "poisson_topk_bic", "gaussian"),
        "candidate_diagnostics": {
            "proposal_steps": len(candidate_steps),
            "proposal_fits_evaluated": int(sum(
                t["proposal_candidates_evaluated"] for t in candidate_steps
            )),
            "optimizer_function_evaluations": int(sum(
                t["total_optimizer_nfev"] for t in candidate_steps
            )),
            "accepted_steps": int(sum(t["accepted"] for t in candidate_steps)),
            "rejected_steps": int(sum(not t["accepted"] for t in candidate_steps)),
            "posthoc_truth_near_proposal_count": int(sum(
                label["within_one_pixel_posthoc"]
                for t in candidate_steps
                for label in _proposal_truth_audit([t], np.zeros((0, 2)))[0]["proposal_pool_posthoc_truth_audit"]
            )) if False else None,
        },
        "records": records,
        "limitations": [
            "Synthetic point sources, one detector size, fixed PSF family and fluxes.",
            "Top-five selection increases optimizer work and is not a free improvement.",
            "Proposal candidates are spatially separated local peaks, not a complete enumeration of all possible source positions.",
            "Greedy source addition and the unchanged approximate BIC stopping rule remain.",
            "Post-hoc proposal/truth proximity is diagnostic only and cannot guide detection.",
            "Results do not establish performance on real astronomical images.",
        ],
    }
