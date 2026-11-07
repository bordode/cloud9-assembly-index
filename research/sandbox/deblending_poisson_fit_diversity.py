"""Post-detection audit of fitted-scene diversity among top-five proposals."""
from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment

from research.sandbox.deblending_poisson_proposal_bic import run_case
from research.sandbox.deblending_geometry_poisson import _score
from research.sandbox.pixel_response_reproduction import SEVEN_SOURCE_POSITIONS


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
                for step in steps:
                    fits = [x for x in step["proposal_fit_diagnostics"] if x["optimizer_success"]]
                    selected_rank = step["selected_proposal_rank"]
                    fit_audits = [{
                        "proposal_rank": fit["proposal_rank"],
                        "selected_by_bic": fit["proposal_rank"] == selected_rank,
                        "posthoc_truth_score": _score(fit["fitted_candidates"], truth),
                    } for fit in fits]
                    comparisons = []
                    for i in range(len(fits)):
                        for j in range(i + 1, len(fits)):
                            dist = _scene_distance(fits[i]["fitted_candidates"], fits[j]["fitted_candidates"])
                            if not dist["same_source_count"]:
                                continue
                            row = {
                                "seed": case["seed"], "step": step["step"],
                                "rank_a": fits[i]["proposal_rank"], "rank_b": fits[j]["proposal_rank"],
                                "matched_truth_a_posthoc": fit_audits[i]["posthoc_truth_score"]["matched_truth_count"],
                                "matched_truth_b_posthoc": fit_audits[j]["posthoc_truth_score"]["matched_truth_count"],
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
                        "pairwise_comparisons": comparisons,
                    })
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
        "posthoc_candidate_score_audit": {
            "selected_fit_comparisons": int(sum(
                1 for r in records for s in r["step_audits"]
                if s["fit_audits_posthoc_only"]
            )),
            "selected_fit_mean_matched_truth": float(np.mean([
                next(x["posthoc_truth_score"]["matched_truth_count"]
                     for x in s["fit_audits_posthoc_only"] if x["selected_by_bic"])
                for r in records for s in r["step_audits"]
                if any(x["selected_by_bic"] for x in s["fit_audits_posthoc_only"])
            ])),
            "best_available_fit_mean_matched_truth": float(np.mean([
                max(x["posthoc_truth_score"]["matched_truth_count"]
                    for x in s["fit_audits_posthoc_only"])
                for r in records for s in r["step_audits"] if s["fit_audits_posthoc_only"]
            ])),
            "steps_where_selected_fit_matches_best_posthoc_score": int(sum(
                next(x["posthoc_truth_score"]["matched_truth_count"]
                     for x in s["fit_audits_posthoc_only"] if x["selected_by_bic"])
                == max(x["posthoc_truth_score"]["matched_truth_count"]
                       for x in s["fit_audits_posthoc_only"])
                for r in records for s in r["step_audits"] if s["fit_audits_posthoc_only"]
            )),
            "warning": "Truth-based scores are computed strictly after all fits and BIC selection; they are audit labels only and never influence fitting or selection."
        },
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
