"""Paired top-five, fixed top-ten, and adaptive Poisson proposal benchmark."""
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

METHODS = ("top5", "top10", "adaptive_top5_to10")


def _run_method(observed_rate, exposure, method):
    if method == "top5":
        policy, top_k = "best_bic_top_k", 5
    elif method == "top10":
        policy, top_k = "best_bic_top_k", 10
    else:
        policy, top_k = "adaptive_top5_to10", 5
    return run_poisson_psf_deblending(
        observed_rate,
        exposure=exposure,
        assumed_sigma_px=SIGMA_PIXELS,
        proposal_policy=policy,
        proposal_top_k=top_k,
    )


def _metrics(result, truth):
    steps = result["candidate_trials"]
    return {
        "score": _score(result["candidates"], truth),
        "selected_count": int(result["selected_source_count"]),
        "proposal_fits_evaluated": int(sum(
            step["proposal_candidates_evaluated"] for step in steps
        )),
        "optimizer_function_evaluations": int(
            result["initial_optimizer_nfev"] + sum(
                step["total_optimizer_nfev"] for step in steps
            )
        ),
        "initial_optimizer_function_evaluations": int(result["initial_optimizer_nfev"]),
        "accepted_steps": int(sum(step["accepted"] for step in steps)),
        "rejected_steps": int(sum(not step["accepted"] for step in steps)),
        "expansion_steps": int(sum(
            step.get("adaptive_expansion_triggered", False) for step in steps
        )),
        "expansion_rescued_steps": int(sum(
            step.get("adaptive_expansion_triggered", False)
            and step["accepted"]
            and step["selected_proposal_rank"] > 5
            for step in steps
        )),
        "adaptive_steps_selecting_ranks_6_to_10": int(sum(
            step.get("adaptive_expansion_triggered", False)
            and step["selected_proposal_rank"] > 5
            for step in steps
        )),
        "optimizer_success": bool(result["optimizer_success"]),
        "steps": steps,
    }


def _summary(records, method):
    rows = [record["methods"][method] for record in records]
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
        "proposal_fits_evaluated": int(sum(
            row["proposal_fits_evaluated"] for row in rows
        )),
        "optimizer_function_evaluations": int(sum(
            row["optimizer_function_evaluations"] for row in rows
        )),
        "accepted_steps": int(sum(row["accepted_steps"] for row in rows)),
        "rejected_steps": int(sum(row["rejected_steps"] for row in rows)),
        "expansion_steps": int(sum(row["expansion_steps"] for row in rows)),
        "expansion_rescued_steps": int(sum(row["expansion_rescued_steps"] for row in rows)),
    }


def _paired(records, method, baseline):
    differences = [
        record["methods"][method]["score"]["matched_truth_count"]
        - record["methods"][baseline]["score"]["matched_truth_count"]
        for record in records
    ]
    return {
        "method": method,
        "baseline": baseline,
        "better_trials": int(sum(value > 0 for value in differences)),
        "worse_trials": int(sum(value < 0 for value in differences)),
        "ties": int(sum(value == 0 for value in differences)),
        "mean_matched_source_difference": float(np.mean(differences)),
    }


def run_adaptive_expansion_benchmark(
    *, trials_per_condition=3, seed_start=20262050,
    geometry_scales=(0.8, 1.0, 1.2), exposures=(1.0, 0.1, 0.03),
):
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
                observed_counts = np.random.default_rng(seed).poisson(
                    np.clip(expected_rate * exposure, 0.0, None)
                ).astype(float)
                observed_rate = observed_counts / exposure
                methods = {}
                for method in METHODS:
                    result = _run_method(observed_rate, exposure, method)
                    methods[method] = _metrics(result, truth)
                records.append({
                    "seed": seed,
                    "trial_index": trial_index,
                    "geometry_scale": float(scale),
                    "exposure": float(exposure),
                    "observed_counts_sum": int(np.sum(observed_counts)),
                    "methods": methods,
                })
                seed += 1

    return {
        "experiment": "C9-DEBLENDING-POISSON-ADAPTIVE-EXPANSION-001",
        "status": "paired_exploratory_synthetic_benchmark",
        "data_kind": "synthetic",
        "seed_start": int(seed_start),
        "trials_per_condition": int(trials_per_condition),
        "trial_count": len(records),
        "methods": list(METHODS),
        "detector_controls": [
            "Same Poisson count observation for all three methods within each trial.",
            "Same Pearson-residual matched-filter score map and 1 px NMS.",
            "Same Poisson deviance, pixel-integrated PSF, bounds, optimizer and tolerances.",
            "Same BIC penalty, acceptance rule and stopping rule.",
            "Adaptive expansion evaluates ranks 6-10 only if no successful rank 1-5 fit lowers the current BIC.",
            "All proposal fits at a greedy step start from the same unchanged accepted scene.",
            "Truth is withheld from proposal generation, fitting and selection; used only for post-run Hungarian scoring within 1 px.",
        ],
        "overall": {method: _summary(records, method) for method in METHODS},
        "paired": {
            "adaptive_vs_top5": _paired(records, "adaptive_top5_to10", "top5"),
            "adaptive_vs_top10": _paired(records, "adaptive_top5_to10", "top10"),
            "top10_vs_top5": _paired(records, "top10", "top5"),
        },
        "records": records,
        "limitations": [
            "Exploratory 27-trial pilot: three trials per geometry/exposure cell.",
            "One fixed seven-source synthetic scene family and one PSF/noise setup.",
            "A small synthetic pilot cannot establish general detector performance.",
            "Truth-based metrics are strictly post-run evaluation and never drive selection.",
            "Results do not establish performance on real astronomical images.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--seed-start", type=int, default=20262050)
    parser.add_argument("--output", default="artifacts/deblending_poisson_adaptive_expansion.json")
    args = parser.parse_args()
    result = run_adaptive_expansion_benchmark(
        trials_per_condition=args.trials, seed_start=args.seed_start
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "experiment": result["experiment"],
        "trial_count": result["trial_count"],
        "overall": result["overall"],
        "paired": result["paired"],
        "output": str(output),
    }, indent=2))


if __name__ == "__main__":
    main()
