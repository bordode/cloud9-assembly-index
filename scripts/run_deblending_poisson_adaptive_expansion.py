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
    policy, top_k = {
        "top5": ("best_bic_top_k", 5),
        "top10": ("best_bic_top_k", 10),
        "adaptive_top5_to10": ("adaptive_top5_to10", 5),
    }[method]
    return run_poisson_psf_deblending(
        observed_rate, exposure=exposure, assumed_sigma_px=SIGMA_PIXELS,
        proposal_policy=policy, proposal_top_k=top_k,
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
        "initial_optimizer_function_evaluations": int(result["initial_optimizer_nfev"]),
        "accepted_steps": int(sum(s["accepted"] for s in steps)),
        "rejected_steps": int(sum(not s["accepted"] for s in steps)),
        "expansion_steps": int(sum(s.get("adaptive_expansion_triggered", False) for s in steps)),
        "expansion_rescued_steps": int(sum(
            s.get("adaptive_expansion_triggered", False) and s["accepted"]
            and s["selected_proposal_rank"] > 5 for s in steps
        )),
        "steps": steps,
    }


def _summary(records, method):
    rows = [r["methods"][method] for r in records]
    scores = [r["score"] for r in rows]
    return {
        "trials": len(rows),
        "mean_matched_truth_sources": float(np.mean([s["matched_truth_count"] for s in scores])),
        "mean_missed_truth_sources": float(np.mean([s["missed_truth_count"] for s in scores])),
        "mean_unmatched_candidates": float(np.mean([s["unmatched_candidate_count"] for s in scores])),
        "exact_seven_source_recoveries": int(sum(s["all_truth_recovered"] for s in scores)),
        "proposal_fits_evaluated": int(sum(r["proposal_fits_evaluated"] for r in rows)),
        "optimizer_function_evaluations": int(sum(r["optimizer_function_evaluations"] for r in rows)),
        "accepted_steps": int(sum(r["accepted_steps"] for r in rows)),
        "rejected_steps": int(sum(r["rejected_steps"] for r in rows)),
        "expansion_steps": int(sum(r["expansion_steps"] for r in rows)),
        "expansion_rescued_steps": int(sum(r["expansion_rescued_steps"] for r in rows)),
    }


def _paired(records, method, baseline):
    differences = [r["methods"][method]["score"]["matched_truth_count"]
                   - r["methods"][baseline]["score"]["matched_truth_count"] for r in records]
    return {
        "method": method, "baseline": baseline,
        "better_trials": int(sum(d > 0 for d in differences)),
        "worse_trials": int(sum(d < 0 for d in differences)),
        "ties": int(sum(d == 0 for d in differences)),
        "mean_matched_source_difference": float(np.mean(differences)),
    }


def run_adaptive_expansion_benchmark(
    *, trials_per_condition=3, seed_start=20262050,
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
                    "observed_counts_sum": int(np.sum(counts)), "methods": methods,
                })
                seed += 1
    return {
        "experiment": "C9-DEBLENDING-POISSON-ADAPTIVE-EXPANSION-001",
        "status": "paired_exploratory_synthetic_benchmark",
        "data_kind": "synthetic", "seed_start": int(seed_start),
        "trials_per_condition": int(trials_per_condition),
        "trial_count": len(records), "methods": list(METHODS),
        "detector_controls": [
            "Same Poisson count observation for all methods within each trial.",
            "Same residual score map, 1 px NMS, Poisson deviance, PSF, bounds and optimizer.",
            "Same BIC penalty, acceptance and stopping rules.",
            "Adaptive expands to ranks 6-10 only when no successful top-five fit lowers current BIC.",
            "Every proposal at a step is fitted against the same unchanged accepted scene.",
            "Truth is withheld from detection and used only for post-run Hungarian matching within 1 px.",
        ],
        "overall": {m: _summary(records, m) for m in METHODS},
        "paired": {
            "adaptive_vs_top5": _paired(records, "adaptive_top5_to10", "top5"),
            "adaptive_vs_top10": _paired(records, "adaptive_top5_to10", "top10"),
            "top10_vs_top5": _paired(records, "top10", "top5"),
        },
        "records": records,
        "limitations": [
            "Exploratory 27-trial pilot with three trials per geometry/exposure cell.",
            "One fixed seven-source synthetic scene family and one PSF/noise setup.",
            "Repeated source and step observations are not independent samples.",
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
        "experiment": result["experiment"], "trial_count": result["trial_count"],
        "overall": result["overall"], "paired": result["paired"],
        "output": str(output),
    }, indent=2))


if __name__ == "__main__":
    main()
