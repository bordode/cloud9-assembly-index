"""Paired AIC/BIC acceptance and proposal-depth benchmark."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from research.sandbox.deblending_geometry_poisson import _score
from research.sandbox.poisson_psf_deblending import run_poisson_psf_deblending
from research.sandbox.pixel_response_reproduction import (
    IMAGE_SIZE, SIGMA_PIXELS, SEVEN_SOURCE_AMPLITUDES,
    SEVEN_SOURCE_POSITIONS, _scene_model,
)

METHODS = {
    "bic_top5": ("best_bic_top_k", 5, "bic"),
    "bic_top10": ("best_bic_top_k", 10, "bic"),
    "bic_adaptive": ("adaptive_top5_to10", 5, "bic"),
    "aic_top5": ("best_bic_top_k", 5, "aic"),
    "aic_top10": ("best_bic_top_k", 10, "aic"),
    "aic_adaptive": ("adaptive_top5_to10", 5, "aic"),
}


def _run_method(rate, exposure, method):
    policy, top_k, criterion = METHODS[method]
    return run_poisson_psf_deblending(
        rate, exposure=exposure, assumed_sigma_px=SIGMA_PIXELS,
        proposal_policy=policy, proposal_top_k=top_k,
        acceptance_criterion=criterion,
    )


def _metrics(result, truth):
    steps = result["candidate_trials"]
    return {
        "score": _score(result["candidates"], truth),
        "selected_count": int(result["selected_source_count"]),
        "proposal_fits_evaluated": int(sum(s["proposal_candidates_evaluated"] for s in steps)),
        "optimizer_function_evaluations": int(result["initial_optimizer_nfev"] + sum(
            s["total_optimizer_nfev"] for s in steps
        )),
        "accepted_steps": int(sum(s["accepted"] for s in steps)),
        "rejected_steps": int(sum(not s["accepted"] for s in steps)),
        "expansion_steps": int(sum(s.get("adaptive_expansion_triggered", False) for s in steps)),
        "expansion_rescued_steps": int(sum(
            s.get("adaptive_expansion_triggered", False) and s["accepted"]
            and s["selected_proposal_rank"] > 5 for s in steps
        )),
        "poisson_deviance": float(result["poisson_deviance"]),
        "poisson_bic": float(result["poisson_bic"]),
        "poisson_aic": float(result["poisson_aic"]),
    }


def _summary(records, method):
    rows = [r["methods"][method] for r in records]
    scores = [r["score"] for r in rows]
    return {
        "trials": len(rows),
        "mean_matched_truth_sources": float(np.mean([s["matched_truth_count"] for s in scores])),
        "mean_missed_truth_sources": float(np.mean([s["missed_truth_count"] for s in scores])),
        "mean_unmatched_candidates": float(np.mean([s["unmatched_candidate_count"] for s in scores])),
        "mean_selected_candidates": float(np.mean([r["selected_count"] for r in rows])),
        "exact_seven_source_recoveries": int(sum(s["all_truth_recovered"] for s in scores)),
        "proposal_fits_evaluated": int(sum(r["proposal_fits_evaluated"] for r in rows)),
        "optimizer_function_evaluations": int(sum(r["optimizer_function_evaluations"] for r in rows)),
        "accepted_steps": int(sum(r["accepted_steps"] for r in rows)),
        "rejected_steps": int(sum(r["rejected_steps"] for r in rows)),
        "expansion_steps": int(sum(r["expansion_steps"] for r in rows)),
        "expansion_rescued_steps": int(sum(r["expansion_rescued_steps"] for r in rows)),
    }


def _paired(records, method, baseline):
    differences = [
        record["methods"][method]["score"]["matched_truth_count"]
        - record["methods"][baseline]["score"]["matched_truth_count"]
        for record in records
    ]
    extras = [
        record["methods"][method]["score"]["unmatched_candidate_count"]
        - record["methods"][baseline]["score"]["unmatched_candidate_count"]
        for record in records
    ]
    return {
        "method": method, "baseline": baseline,
        "better_trials": int(sum(x > 0 for x in differences)),
        "worse_trials": int(sum(x < 0 for x in differences)),
        "ties": int(sum(x == 0 for x in differences)),
        "mean_matched_source_difference": float(np.mean(differences)),
        "mean_unmatched_candidate_difference": float(np.mean(extras)),
    }


def run_aic_bic_acceptance_benchmark(
    *, trials_per_condition=3, seed_start=20262100,
    geometry_scales=(0.8, 1.0, 1.2), exposures=(1.0, 0.1, 0.03),
):
    if trials_per_condition < 1:
        raise ValueError("trials_per_condition must be positive")
    records, seed = [], int(seed_start)
    for scale in geometry_scales:
        for exposure in exposures:
            for trial_index in range(trials_per_condition):
                truth = SEVEN_SOURCE_POSITIONS * float(scale)
                expected = _scene_model(
                    truth, SEVEN_SOURCE_AMPLITUDES, 2.0, "integrated",
                    SIGMA_PIXELS, IMAGE_SIZE,
                )
                counts = np.random.default_rng(seed).poisson(
                    np.clip(expected * exposure, 0.0, None)
                ).astype(float)
                rate = counts / exposure
                methods = {
                    method: _metrics(_run_method(rate, exposure, method), truth)
                    for method in METHODS
                }
                records.append({
                    "seed": seed, "trial_index": trial_index,
                    "geometry_scale": float(scale), "exposure": float(exposure),
                    "observed_counts_sum": int(np.sum(counts)),
                    "methods": methods,
                })
                seed += 1

    paired = {
        "aic_top5_vs_bic_top5": _paired(records, "aic_top5", "bic_top5"),
        "aic_top10_vs_bic_top10": _paired(records, "aic_top10", "bic_top10"),
        "aic_adaptive_vs_bic_adaptive": _paired(records, "aic_adaptive", "bic_adaptive"),
        "bic_adaptive_vs_bic_top5": _paired(records, "bic_adaptive", "bic_top5"),
        "bic_top10_vs_bic_top5": _paired(records, "bic_top10", "bic_top5"),
        "aic_adaptive_vs_aic_top5": _paired(records, "aic_adaptive", "aic_top5"),
        "aic_top10_vs_aic_top5": _paired(records, "aic_top10", "aic_top5"),
    }
    return {
        "experiment": "C9-DEBLENDING-POISSON-AIC-BIC-ACCEPTANCE-001",
        "status": "paired_exploratory_synthetic_benchmark",
        "data_kind": "synthetic", "seed_start": int(seed_start),
        "trials_per_condition": int(trials_per_condition),
        "trial_count": len(records), "methods": list(METHODS),
        "detector_controls": [
            "All six methods receive the same Poisson count image within each trial.",
            "Same pixel-integrated PSF, residual score map, NMS, parameterization, bounds and optimizer tolerances.",
            "Same Poisson deviance likelihood; only the information-criterion acceptance rule and proposal depth vary.",
            "AIC = deviance + 2k; BIC = deviance + k ln(n_pixels), with k=3*source_count+1.",
            "Adaptive expansion evaluates ranks 6-10 only when no successful rank 1-5 fit lowers the selected criterion.",
            "Truth is withheld from detector decisions and used only for post-run Hungarian scoring within 1 px.",
        ],
        "overall": {method: _summary(records, method) for method in METHODS},
        "paired": paired,
        "records": records,
        "limitations": [
            "Exploratory 27-trial pilot with three trials per geometry/exposure cell.",
            "One seven-source synthetic scene family and one PSF/noise setup.",
            "Information-criterion behaviour may depend on the effective number of independent observations.",
            "Repeated observations within a fixed scene are not independent samples.",
            "No conclusions about real astronomical images follow from this synthetic benchmark.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--seed-start", type=int, default=20262100)
    parser.add_argument("--output", default="artifacts/deblending_poisson_aic_bic_acceptance.json")
    args = parser.parse_args()
    result = run_aic_bic_acceptance_benchmark(
        trials_per_condition=args.trials, seed_start=args.seed_start
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "experiment": result["experiment"], "trial_count": result["trial_count"],
        "overall": result["overall"], "paired": result["paired"],
        "output": str(output),
    }, indent=2))


if __name__ == "__main__":
    main()
