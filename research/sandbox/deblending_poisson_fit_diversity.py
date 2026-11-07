"""Post-detection audit of fitted-scene diversity among top-five proposals."""
from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment

from research.sandbox.deblending_poisson_proposal_bic import run_case
from research.sandbox.deblending_geometry_poisson import _score
from research.sandbox.pixel_response_reproduction import (
    SEVEN_SOURCE_AMPLITUDES, SEVEN_SOURCE_POSITIONS, SIGMA_PIXELS,
)


def _posthoc_fit_audit(fit: dict, truth: np.ndarray, selected_rank: int) -> dict:
    """Attach truth-based localization metrics after candidate-BIC selection."""
    score = _score(fit["fitted_candidates"], truth)
    errors = np.asarray(score["matched_radial_errors_px"], dtype=float)
    rmse = float(np.sqrt(np.mean(errors ** 2))) if errors.size else None
    return {
        "proposal_rank": int(fit["proposal_rank"]),
        "selected_by_candidate_bic": int(fit["proposal_rank"]) == int(selected_rank),
        "poisson_bic": float(fit["poisson_bic"]),
        "poisson_deviance": float(fit["poisson_deviance"]),
        "posthoc_matched_truth_count": int(score["matched_truth_count"]),
        "posthoc_matched_position_rmse_px": rmse,
        "posthoc_truth_score": score,
    }



def _posthoc_source_audit(
    fitted_candidates: list[dict],
    truth: np.ndarray,
    truth_amplitudes: np.ndarray,
    sigma_px: float,
    match_radius_px: float = 1.0,
) -> list[dict]:
    """Describe source-level localization, crowding and assignment ambiguity.

    This diagnostic is evaluation-only. It is called after a candidate fit and
    candidate-BIC selection; none of its outputs enter detector decisions.
    """
    truth = np.asarray(truth, dtype=float).reshape((-1, 2))
    amplitudes = np.asarray(truth_amplitudes, dtype=float).reshape((-1,))
    if len(amplitudes) != len(truth):
        raise ValueError("truth_amplitudes must have one value per truth position")
    if sigma_px <= 0 or match_radius_px <= 0:
        raise ValueError("sigma_px and match_radius_px must be positive")

    if len(truth) > 1:
        truth_distances = np.linalg.norm(
            truth[:, None, :] - truth[None, :, :], axis=2
        )
        np.fill_diagonal(truth_distances, np.inf)
        nearest_separation = np.min(truth_distances, axis=1)
        neighbours_within_two_sigma = np.sum(
            truth_distances <= 2.0 * sigma_px, axis=1
        )
    else:
        nearest_separation = np.full(len(truth), np.inf)
        neighbours_within_two_sigma = np.zeros(len(truth), dtype=int)

    if fitted_candidates:
        candidate_xy = np.asarray(
            [[item["x_px"], item["y_px"]] for item in fitted_candidates],
            dtype=float,
        ).reshape((-1, 2))
        distances = np.linalg.norm(
            truth[:, None, :] - candidate_xy[None, :, :], axis=2
        )
        truth_indices, candidate_indices = linear_sum_assignment(distances)
        assignments = {
            int(t): (int(c), float(distances[t, c]))
            for t, c in zip(truth_indices, candidate_indices)
        }
    else:
        candidate_xy = np.empty((0, 2), dtype=float)
        distances = np.empty((len(truth), 0), dtype=float)
        assignments = {}

    flux_order = np.argsort(-amplitudes, kind="stable")
    flux_ranks = np.empty(len(amplitudes), dtype=int)
    flux_ranks[flux_order] = np.arange(1, len(amplitudes) + 1)

    rows = []
    for index, truth_xy in enumerate(truth):
        assignment = assignments.get(index)
        assigned_candidate_index = assignment[0] if assignment else None
        assigned_distance = assignment[1] if assignment else None
        matched = assigned_distance is not None and assigned_distance <= match_radius_px
        if distances.shape[1] >= 2:
            nearest_two = np.sort(distances[index])[:2]
            candidate_margin = float(nearest_two[1] - nearest_two[0])
        elif distances.shape[1] == 1:
            candidate_margin = None
        else:
            candidate_margin = None
        separation = float(nearest_separation[index])
        separation_sigma = separation / sigma_px
        if separation_sigma < 1.5:
            crowding_band = "close_lt_1_5_sigma"
        elif separation_sigma < 2.5:
            crowding_band = "intermediate_1_5_to_2_5_sigma"
        else:
            crowding_band = "separated_ge_2_5_sigma"
        rank = int(flux_ranks[index])
        bright_cutoff = max(1, int(np.ceil(len(amplitudes) / 3.0)))
        middle_cutoff = max(bright_cutoff + 1, int(np.ceil(2.0 * len(amplitudes) / 3.0)))
        flux_band = "brightest_third" if rank <= bright_cutoff else (
            "middle_third" if rank <= middle_cutoff else "faintest_third"
        )
        rows.append({
            "truth_source_index": int(index),
            "truth_amplitude": float(amplitudes[index]),
            "truth_flux_rank_brightest_first": rank,
            "flux_band": flux_band,
            "nearest_truth_separation_px": separation,
            "nearest_truth_separation_sigma": float(separation_sigma),
            "truth_neighbours_within_2_sigma": int(neighbours_within_two_sigma[index]),
            "crowding_band": crowding_band,
            "assigned_candidate_index": assigned_candidate_index,
            "posthoc_assignment_distance_px": assigned_distance,
            "matched_within_1_px_posthoc": bool(matched),
            "nearest_candidate_margin_px": candidate_margin,
        })
    return rows


def _summarize_source_localization(records: list[dict]) -> dict:
    """Aggregate source-level localization, retaining misses in denominators."""
    rows = [
        source
        for record in records
        for step in record["step_audits"]
        for fit in step["fit_audits_posthoc_only"]
        for source in fit.get("source_audits_posthoc_only", [])
    ]
    groups = {}
    for dimension in ("crowding_band", "flux_band"):
        labels = sorted({row[dimension] for row in rows})
        groups[dimension] = {}
        for label in labels:
            selected = [row for row in rows if row[dimension] == label]
            matched = [
                row["posthoc_assignment_distance_px"]
                for row in selected
                if row["matched_within_1_px_posthoc"]
            ]
            unmatched = [
                row for row in selected
                if not row["matched_within_1_px_posthoc"]
            ]
            unmatched_assigned = [
                row["posthoc_assignment_distance_px"]
                for row in unmatched
                if row["posthoc_assignment_distance_px"] is not None
            ]
            groups[dimension][label] = {
                "source_observations": len(selected),
                "matched_within_1_px": len(matched),
                "unmatched": len(unmatched),
                "match_fraction": (
                    float(len(matched) / len(selected)) if selected else None
                ),
                "median_matched_error_px": (
                    float(np.median(matched)) if matched else None
                ),
                "p90_matched_error_px": (
                    float(np.percentile(matched, 90)) if matched else None
                ),
                "unmatched_with_assigned_candidate": len(unmatched_assigned),
                "unmatched_without_assigned_candidate": (
                    len(unmatched) - len(unmatched_assigned)
                ),
                "median_unmatched_assigned_distance_px": (
                    float(np.median(unmatched_assigned))
                    if unmatched_assigned else None
                ),
            }
    matched_total = sum(
        bool(row["matched_within_1_px_posthoc"]) for row in rows
    )
    unmatched_total = len(rows) - matched_total
    return {
        "source_observation_count": len(rows),
        "matched_within_1_px": int(matched_total),
        "unmatched": int(unmatched_total),
        "match_fraction": (
            float(matched_total / len(rows)) if rows else None
        ),
        "grouped_results": groups,
        "warning": (
            "These are repeated post-hoc source observations across candidate "
            "fits, not independent astronomical sources or trials. Unmatched "
            "truth sources remain in each group's denominator. Group "
            "differences are descriptive and are not detector selection rules."
        ),
    }


def _truth_assignment_distances(
    fitted_candidates: list[dict], truth: np.ndarray
) -> dict[int, float | None]:
    """Return one-to-one post-hoc truth-to-candidate assignment distances."""
    truth = np.asarray(truth, dtype=float).reshape((-1, 2))
    if not fitted_candidates:
        return {index: None for index in range(len(truth))}
    candidate_xy = np.asarray(
        [[item["x_px"], item["y_px"]] for item in fitted_candidates],
        dtype=float,
    ).reshape((-1, 2))
    distances = np.linalg.norm(
        truth[:, None, :] - candidate_xy[None, :, :], axis=2
    )
    truth_indices, candidate_indices = linear_sum_assignment(distances)
    assigned = {
        int(t): float(distances[t, candidate])
        for t, candidate in zip(truth_indices, candidate_indices)
    }
    return {index: assigned.get(index) for index in range(len(truth))}


def _audit_missed_source_path(
    current_candidates: list[dict],
    truth: np.ndarray,
    proposal_pool: list[dict],
    fit_diagnostics: list[dict],
    selected_rank: int,
    accepted: bool,
    ranked_score_peaks: list[dict] | None = None,
    match_radius_px: float = 1.0,
) -> list[dict]:
    """Trace each currently missed truth source through proposal, fit and BIC.

    This is post-hoc only. Truth labels never enter proposal generation,
    optimization, candidate-BIC selection, or the acceptance decision.
    """
    truth = np.asarray(truth, dtype=float).reshape((-1, 2))
    current_distances = _truth_assignment_distances(current_candidates, truth)
    proposal_xy = np.asarray(
        [[item["x_px"], item["y_px"]] for item in proposal_pool], dtype=float
    ).reshape((-1, 2)) if proposal_pool else np.empty((0, 2), dtype=float)
    successful = [
        item for item in fit_diagnostics if item["optimizer_success"]
    ]
    selected_fit = next(
        (item for item in successful
         if int(item["proposal_rank"]) == int(selected_rank)),
        None,
    )
    fit_distances = {
        int(item["proposal_rank"]): _truth_assignment_distances(
            item["fitted_candidates"], truth
        )
        for item in successful
    }
    rows = []
    for truth_index, truth_xy in enumerate(truth):
        current_distance = current_distances[truth_index]
        if current_distance is not None and current_distance <= match_radius_px:
            continue
        proposal_distance = (
            float(np.min(np.linalg.norm(proposal_xy - truth_xy, axis=1)))
            if len(proposal_xy) else None
        )
        nearby_proposal = (
            proposal_distance is not None
            and proposal_distance <= match_radius_px
        )
        peak_distances = [
            (
                float(np.hypot(item["x_px"] - truth_xy[0],
                               item["y_px"] - truth_xy[1])),
                int(item["rank"]),
            )
            for item in (ranked_score_peaks or [])
        ]
        nearest_peak_distance, nearest_peak_rank = (
            min(peak_distances, key=lambda item: (item[0], item[1]))
            if peak_distances else (None, None)
        )
        nearby_top50_peak = (
            nearest_peak_distance is not None
            and nearest_peak_distance <= match_radius_px
        )
        recovering_ranks = [
            rank for rank, distances in fit_distances.items()
            if distances[truth_index] is not None
            and distances[truth_index] <= match_radius_px
        ]
        selected_distance = (
            fit_distances.get(int(selected_rank), {}).get(truth_index)
            if int(selected_rank) in fit_distances else None
        )
        selected_recovers = (
            selected_distance is not None
            and selected_distance <= match_radius_px
        )
        if not recovering_ranks and not nearby_proposal:
            stage = "proposal_generation_gap"
        elif not recovering_ranks:
            stage = "fit_recovery_gap"
        elif selected_recovers and accepted:
            stage = "recovered_by_selected_fit"
        elif selected_recovers and not accepted:
            stage = "selected_fit_rejected_by_bic"
        elif recovering_ranks and not selected_recovers:
            stage = "bic_candidate_selection_gap"
        else:
            stage = "fit_recovery_gap"
        rows.append({
            "truth_source_index": int(truth_index),
            "current_scene_assignment_distance_px_posthoc": current_distance,
            "nearest_proposal_distance_px_posthoc": proposal_distance,
            "nearby_proposal_within_1_px_posthoc": bool(nearby_proposal),
            "nearest_ranked_score_peak_distance_px_posthoc": nearest_peak_distance,
            "nearest_ranked_score_peak_rank_posthoc": nearest_peak_rank,
            "nearby_ranked_score_peak_within_1_px_posthoc": bool(nearby_top50_peak),
            "successful_fit_ranks_recovering_source_posthoc": recovering_ranks,
            "selected_fit_assignment_distance_px_posthoc": selected_distance,
            "selected_fit_recovers_source_posthoc": bool(selected_recovers),
            "step_accepted_by_bic": bool(accepted),
            "stage": stage,
        })
    return rows


def _summarize_ranked_peak_coverage(records: list[dict]) -> dict:
    """Summarize how far down the ranked residual peaks missed truths appear."""
    rows = [
        source
        for record in records
        for step in record["step_audits"]
        for source in step.get("missed_source_path_posthoc_only", [])
    ]
    proposal_gaps = [row for row in rows if row["stage"] == "proposal_generation_gap"]
    bands = {
        "ranks_1_to_5": 0,
        "ranks_6_to_10": 0,
        "ranks_11_to_25": 0,
        "ranks_26_to_50": 0,
        "no_peak_within_1_px_top50": 0,
    }
    for row in proposal_gaps:
        rank = row["nearest_ranked_score_peak_rank_posthoc"]
        distance = row["nearest_ranked_score_peak_distance_px_posthoc"]
        if distance is None or distance > 1.0 or rank is None:
            bands["no_peak_within_1_px_top50"] += 1
        elif rank <= 5:
            bands["ranks_1_to_5"] += 1
        elif rank <= 10:
            bands["ranks_6_to_10"] += 1
        elif rank <= 25:
            bands["ranks_11_to_25"] += 1
        else:
            bands["ranks_26_to_50"] += 1
    return {
        "proposal_generation_gap_observations": len(proposal_gaps),
        "nearest_ranked_peak_bands_within_1_px": bands,
        "warning": (
            "This is a post-hoc coordinate-proximity audit of the top 50 "
            "observation-derived score-map peaks after 1 px non-maximum "
            "suppression. It does not prove source identifiability or alter "
            "the detector. Repeated source/step observations are correlated."
        ),
    }


def _summarize_source_path(records: list[dict]) -> dict:
    """Count post-hoc missed-source pathways across the replay."""
    rows = [
        source
        for record in records
        for step in record["step_audits"]
        for source in step.get("missed_source_path_posthoc_only", [])
    ]
    stages = (
        "proposal_generation_gap",
        "fit_recovery_gap",
        "bic_candidate_selection_gap",
        "selected_fit_rejected_by_bic",
        "recovered_by_selected_fit",
    )
    counts = {stage: sum(row["stage"] == stage for row in rows)
              for stage in stages}
    return {
        "missed_source_step_observations": len(rows),
        "stage_counts": counts,
        "warning": (
            "These are repeated post-hoc source/step observations within a "
            "fixed synthetic scene, not independent sources or trials. A "
            "nearby proposal is defined by coordinate proximity within 1 px; "
            "a fit recovery uses one-to-one Hungarian assignment within 1 px. "
            "All truth-based labels are diagnostic only and never affect the "
            "observation-only detector."
        ),
    }


def _scene_distance(left: list[dict], right: list[dict]) -> dict:
    if len(left) != len(right):
        return {"same_source_count": False, "rms_position_px": None,
                "max_position_px": None, "relative_amplitude_rms": None}
    if not left:
        return {"same_source_count": True, "rms_position_px": 0.0,
                "max_position_px": 0.0, "relative_amplitude_rms": 0.0}
    a = np.array([[v["x_px"], v["y_px"]] for v in left], dtype=float)
    b = np.array([[v["x_px"], v["y_px"]] for v in right], dtype=float)
    rows, cols = linear_sum_assignment(np.linalg.norm(a[:, None, :] - b[None, :, :], axis=2))
    delta = np.linalg.norm(a[rows] - b[cols], axis=1)
    amp_a = np.array([left[i]["amplitude"] for i in rows], dtype=float)
    amp_b = np.array([right[i]["amplitude"] for i in cols], dtype=float)
    scale = np.maximum((np.abs(amp_a) + np.abs(amp_b)) / 2.0, 1e-12)
    return {
        "same_source_count": True,
        "rms_position_px": float(np.sqrt(np.mean(delta ** 2))),
        "max_position_px": float(np.max(delta)),
        "relative_amplitude_rms": float(np.sqrt(np.mean(((amp_a - amp_b) / scale) ** 2))),
    }


def _summarize_posthoc_candidate_scores(records: list[dict]) -> dict:
    """Summarize truth-only diagnostics; tolerate steps with no successful fits."""
    steps = [
        step
        for record in records
        for step in record["step_audits"]
        if step["fit_audits_posthoc_only"]
    ]
    selected = [
        next((fit for fit in step["fit_audits_posthoc_only"]
              if fit["selected_by_candidate_bic"]), None)
        for step in steps
    ]
    selected = [fit for fit in selected if fit is not None]
    best_counts = [
        max(fit["posthoc_matched_truth_count"]
            for fit in step["fit_audits_posthoc_only"])
        for step in steps
    ]
    selected_counts = [fit["posthoc_matched_truth_count"] for fit in selected]
    return {
        "steps_with_successful_candidate_fits": len(steps),
        "selected_fit_comparisons": len(selected),
        "steps_missing_selected_fit_record": len(steps) - len(selected),
        "selected_fit_mean_matched_truth": (
            float(np.mean(selected_counts)) if selected_counts else None
        ),
        "best_available_fit_mean_matched_truth": (
            float(np.mean(best_counts)) if best_counts else None
        ),
        "steps_where_selected_fit_matches_best_posthoc_score": (
            int(sum(a == b for a, b in zip(selected_counts, best_counts)))
            if len(selected_counts) == len(best_counts) else None
        ),
        "warning": (
            "Truth-based scores and localization errors are computed strictly "
            "after all fits and candidate-BIC selection; they are audit labels "
            "only and never influence fitting, proposal generation, or selection."
        ),
    }


def run_diversity_audit(*, trials_per_condition: int = 10,
                        geometry_scales=(0.8, 1.0, 1.2),
                        exposures=(1.0, 0.1, 0.03),
                        seed_start: int = 20261900) -> dict:
    records, pair_rows, seed = [], [], int(seed_start)
    for scale in geometry_scales:
        for exposure in exposures:
            for index in range(trials_per_condition):
                case = run_case(geometry_scale=float(scale), exposure=float(exposure), seed=seed)
                seed += 1
                method = case["poisson_topk_bic"]
                steps = method["candidate_trials"]
                step_audits = []
                truth = SEVEN_SOURCE_POSITIONS * float(scale)
                current_scene = []
                for step in steps:
                    fits = [x for x in step["proposal_fit_diagnostics"] if x["optimizer_success"]]
                    selected_rank = step["selected_proposal_rank"]
                    path_audits = _audit_missed_source_path(
                        current_scene, truth, step.get("proposal_pool", []),
                        step["proposal_fit_diagnostics"], selected_rank,
                        step["accepted"],
                        ranked_score_peaks=step.get("ranked_score_peaks_diagnostic_only", []),
                    )
                    fit_audits = [
                        _posthoc_fit_audit(fit, truth, selected_rank)
                        for fit in fits
                    ]
                    for fit_audit, fit in zip(fit_audits, fits):
                        fit_audit["source_audits_posthoc_only"] = _posthoc_source_audit(
                            fit["fitted_candidates"], truth,
                            SEVEN_SOURCE_AMPLITUDES, SIGMA_PIXELS,
                        )
                    comparisons = []
                    for i in range(len(fits)):
                        for j in range(i + 1, len(fits)):
                            dist = _scene_distance(fits[i]["fitted_candidates"], fits[j]["fitted_candidates"])
                            if not dist["same_source_count"]:
                                continue
                            row = {
                                "seed": case["seed"], "step": step["step"],
                                "rank_a": fits[i]["proposal_rank"], "rank_b": fits[j]["proposal_rank"],
                                "matched_truth_a_posthoc": fit_audits[i]["posthoc_matched_truth_count"],
                                "matched_truth_b_posthoc": fit_audits[j]["posthoc_matched_truth_count"],
                                "bic_abs_difference": abs(fits[i]["poisson_bic"] - fits[j]["poisson_bic"]),
                                "deviance_abs_difference": abs(fits[i]["poisson_deviance"] - fits[j]["poisson_deviance"]),
                                "background_abs_difference": abs(fits[i]["fitted_background_rate"] - fits[j]["fitted_background_rate"]),
                                **dist,
                            }
                            comparisons.append(row)
                            pair_rows.append(row)
                    step_audits.append({
                        "step": step["step"],
                        "selected_proposal_rank": selected_rank,
                        "successful_fits": len(fits),
                        "fit_audits_posthoc_only": fit_audits,
                        "missed_source_path_posthoc_only": path_audits,
                        "pairwise_comparisons": comparisons,
                    })
                    if step["accepted"]:
                        selected_scene_fit = next(
                            (item for item in step["proposal_fit_diagnostics"]
                             if item["optimizer_success"]
                             and int(item["proposal_rank"]) == int(selected_rank)),
                            None,
                        )
                        if selected_scene_fit is not None:
                            current_scene = selected_scene_fit["fitted_candidates"]
                records.append({
                    "seed": case["seed"], "geometry_scale": float(scale),
                    "exposure": float(exposure),
                    "selected_count": method["selected_count"],
                    "score": method["score"],
                    "step_audits": step_audits,
                    "optimizer_function_evaluations": sum(
                        s["total_optimizer_nfev"] for s in steps
                    ),
                })

    distances = np.array([x["rms_position_px"] for x in pair_rows], dtype=float)
    bic = np.array([x["bic_abs_difference"] for x in pair_rows], dtype=float)
    if len(distances) > 1 and np.std(distances) > 0 and np.std(bic) > 0:
        correlation = float(np.corrcoef(distances, bic)[0, 1])
    else:
        correlation = None
    return {
        "experiment": "C9-DEBLENDING-POISSON-FIT-DIVERSITY-001",
        "status": "post_detection_scene_configuration_audit",
        "seed_start": int(seed_start), "trial_count": len(records),
        "geometry_scales": list(map(float, geometry_scales)),
        "exposures": list(map(float, exposures)),
        "pairwise_comparison_count": len(pair_rows),
        "steps_with_multiple_successful_fits": sum(
            s["successful_fits"] > 1
            for r in records for s in r["step_audits"]
        ),
        "position_rms_px": {
            "median": float(np.median(distances)) if len(distances) else None,
            "p90": float(np.percentile(distances, 90)) if len(distances) else None,
            "max": float(np.max(distances)) if len(distances) else None,
            "fraction_le_1e_3": float(np.mean(distances <= 1e-3)) if len(distances) else None,
            "fraction_le_1e_2": float(np.mean(distances <= 1e-2)) if len(distances) else None,
            "fraction_gt_0_05": float(np.mean(distances > 0.05)) if len(distances) else None,
        },
        "bic_difference": {
            "median": float(np.median(bic)) if len(bic) else None,
            "p90": float(np.percentile(bic, 90)) if len(bic) else None,
            "max": float(np.max(bic)) if len(bic) else None,
            "correlation_with_position_rms": correlation,
        },
        "relative_amplitude_rms_median": float(np.median([
            x["relative_amplitude_rms"] for x in pair_rows
        ])) if pair_rows else None,
        "background_abs_difference_median": float(np.median([
            x["background_abs_difference"] for x in pair_rows
        ])) if pair_rows else None,
        "total_optimizer_function_evaluations": int(sum(
            r["optimizer_function_evaluations"] for r in records
        )),
        "posthoc_candidate_score_audit": _summarize_posthoc_candidate_scores(records),
        "posthoc_source_localization_audit": _summarize_source_localization(records),
        "posthoc_missed_source_path_audit": _summarize_source_path(records),
        "posthoc_ranked_score_peak_coverage": _summarize_ranked_peak_coverage(records),
        "pairwise_records": pair_rows,
        "records": records,
        "limitations": [
            "This is a replay/audit of the PR #37 synthetic benchmark, not an independent recovery benchmark.",
            "Hungarian coordinate matching is diagnostic and can be ambiguous for weak or coincident sources.",
            "Similarity thresholds are descriptive numerical bins, not scientific equivalence criteria.",
            "Truth is not used for candidate selection; it is not required for this fit-diversity calculation.",
            "Synthetic scenes do not establish real-image performance.",
        ],
    }
