"""Stress-test border-calibrated background estimation under contaminated calibration pixels."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from scripts.run_dither_blind_background_estimation_validation import (
    CONDITIONS,
    GRADIENT_AMPLITUDES,
    SEEDS as BASE_SEEDS,
    summarize,
    trial,
)

SEEDS = tuple(range(2026111500, 2026111530))
PRIOR_SEED_RANGES = (
    (2026111000, 2026111029),
    (2026111200, 2026111229),
    (2026111300, 2026111329),
    (2026111400, 2026111429),
)
GRADIENT_AMPLITUDE = 0.25
CONTAMINATION_FRACTIONS = (0.0, 0.05, 0.15)
CONTAMINATION_RATE = 1.0
ITERATIONS = 2
METRICS = (
    "relative_rmse",
    "mean_source_centroid_error_px",
    "mean_aperture_flux_abs_error",
    "background_map_rmse",
    "background_mean_abs_error",
)


def main():
    if any(set(SEEDS) & set(range(start, end + 1)) for start, end in PRIOR_SEED_RANGES):
        raise AssertionError("stress-test seeds overlap prior experiments")
    if GRADIENT_AMPLITUDE not in GRADIENT_AMPLITUDES:
        raise AssertionError("stress-test gradient must be a previously validated level")
    if len(SEEDS) != 30 or len(set(SEEDS)) != 30:
        raise AssertionError("expected 30 unique fresh paired seeds")

    records = []
    for fraction in CONTAMINATION_FRACTIONS:
        for seed in SEEDS:
            for condition, values in trial(
                seed, GRADIENT_AMPLITUDE, fraction, CONTAMINATION_RATE
            ).items():
                records.append({
                    "seed": seed,
                    "gradient_amplitude": GRADIENT_AMPLITUDE,
                    "contamination_fraction": fraction,
                    "contamination_rate": CONTAMINATION_RATE,
                    "condition": condition,
                    "iterations": ITERATIONS,
                    **values,
                })

    summary, paired = {}, {}
    for fraction in CONTAMINATION_FRACTIONS:
        subset = [r for r in records if r["contamination_fraction"] == fraction]
        by_condition = {
            condition: {r["seed"]: r for r in subset if r["condition"] == condition}
            for condition in CONDITIONS
        }
        key = str(fraction)
        summary[key] = {
            condition: {
                metric: summarize([row[metric] for row in values.values()])
                for metric in METRICS
            }
            for condition, values in by_condition.items()
        }
        paired[key] = {}
        for label, left, right in (
            ("aligned_minus_stationary", "aligned_dithered", "nine_stationary"),
            ("offgrid_minus_stationary", "offgrid_dithered", "nine_stationary"),
            ("offgrid_minus_aligned", "offgrid_dithered", "aligned_dithered"),
        ):
            paired[key][label] = {
                metric: summarize([
                    by_condition[left][seed][metric] - by_condition[right][seed][metric]
                    for seed in SEEDS
                ])
                for metric in METRICS
            }

    output = {
        "protocol": {
            "status": "pre-registered calibration-border contamination stress test",
            "seeds": list(SEEDS),
            "prior_seed_ranges_inclusive": [list(x) for x in PRIOR_SEED_RANGES],
            "gradient_amplitude": GRADIENT_AMPLITUDE,
            "contamination_fractions": list(CONTAMINATION_FRACTIONS),
            "contamination_rate": CONTAMINATION_RATE,
            "contamination_model": "additional Poisson background rate on a deterministic, seed-specific subset of outer-border calibration pixels; same mask across acquisition arms",
            "estimator_awareness": "estimator is not told which calibration pixels are contaminated",
            "iterations": ITERATIONS,
            "frames_per_arm": 9,
            "total_exposure": 1.0,
            "primary_metric": "fixed-interior relative RMSE",
            "secondary_metrics": list(METRICS[1:]),
            "trial_count": len(records),
            "limitations": [
                "contamination is restricted to outer calibration border pixels",
                "horizontal linear background model remains correctly specified apart from contaminated calibration observations",
                "no temporal drift, read noise, PSF mismatch, or general detector systematics",
            ],
        },
        "summary_by_contamination_fraction": summary,
        "paired_comparisons": paired,
        "trials": records,
    }
    path = Path("dither_calibration_border_contamination_stress_test.json")
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(path),
        "seeds": len(SEEDS),
        "contamination_fractions": list(CONTAMINATION_FRACTIONS),
        "paired_relative_rmse": {
            level: {
                comparison: stats["relative_rmse"]
                for comparison, stats in comparisons.items()
            }
            for level, comparisons in paired.items()
        },
    }, indent=2))


if __name__ == "__main__":
    main()
