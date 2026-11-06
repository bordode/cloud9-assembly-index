"""Regression checks for the staged pixel-response sensitivity suite."""
import json
import math
import unittest

import numpy as np
from scipy.optimize import linear_sum_assignment

from research.sandbox.iterative_psf_deblending import run_iterative_psf_deblending
from research.sandbox.pixel_response_reproduction import (
    IMAGE_SIZE, SIGMA_PIXELS, SEVEN_SOURCE_AMPLITUDES,
    SEVEN_SOURCE_POSITIONS, _scene_model,
)
from research.sandbox.pixel_response_robustness import (
    run_case,
    run_image_peak_detection,
    run_peak_detection_sensitivity_sweep,
    run_initialization_trials,
    run_repeated_noise_trials,
    run_position_bound_sweep,
)


class PixelResponseRobustnessTests(unittest.TestCase):
    def test_case_records_matched_fit_conditions_and_sourcewise_errors(self):
        result = run_case(
            geometry_scale=1.0,
            phase_x=0.25,
            phase_y=-0.25,
            noise_model="none",
            seed=20261110,
        )
        self.assertEqual(result["status"], "synthetic_sensitivity_case")
        self.assertEqual(result["source_count"], 7)
        self.assertEqual(result["truth_sigma_px"], 1.3)
        self.assertEqual(result["fit_sigma_px"], 1.3)
        self.assertEqual(len(result["source_errors"]["integrated"]), 7)
        self.assertEqual(len(result["source_errors"]["centre"]), 7)
        self.assertIn("mean_signed_x_error_px", result["summaries"]["centre"])

    def test_unbounded_position_fit_reports_source_assignment(self):
        result = run_case(
            noise_model="none", seed=20261110,
            initialization_seed=20261111,
            position_bound_half_width=None,
        )
        self.assertIsNone(result["position_bound_half_width_px"])
        for model in ("integrated", "centre"):
            summary = result["summaries"][model]
            self.assertEqual(len(summary["assignment_permutation"]), 7)
            self.assertGreaterEqual(summary["assignment_swaps"], 0)
            self.assertEqual(summary["position_bound_hits"], 0)
            self.assertTrue(math.isfinite(summary["assignment_total_distance_px"]))

    def test_detector_uniform_initialization_is_recorded(self):
        result = run_case(
            noise_model="none", seed=20261110,
            initialization_seed=20261111,
            position_bound_half_width=None,
            initialization_policy="detector_uniform",
            detector_bounds=True,
        )
        self.assertEqual(result["initialization_policy"], "detector_uniform")
        self.assertTrue(result["detector_bounds_enabled"])
        self.assertEqual(result["position_bounds_policy"], "physical detector-field bounds")
        for model in ("integrated", "centre"):
            self.assertIn("optimizer_success", result["summaries"][model])

    def test_detector_uniform_start_is_confined_to_physical_field(self):
        records = []
        for start_index in range(3):
            result = run_case(
                noise_model="none", seed=20261450,
                initialization_seed=20261451 + start_index,
                position_bound_half_width=None,
                initialization_policy="detector_uniform",
                detector_bounds=True,
            )
            records.append({
                model: {
                    "optimizer_success": result["summaries"][model]["optimizer_success"],
                    "nfev": result["summaries"][model]["nfev"],
                    "rmse_radial_error_px": result["summaries"][model]["rmse_radial_error_px"],
                    "assignment_swaps": result["summaries"][model]["assignment_swaps"],
                    "assignment_total_distance_px": result["summaries"][model]["assignment_total_distance_px"],
                    "max_abs_fitted_coordinate_px": result["summaries"][model]["max_abs_fitted_coordinate_px"],
                }
                for model in ("integrated", "centre")
            })
        print("DETECTOR_UNIFORM_START_RESULT=" + json.dumps(records, sort_keys=True))
        self.assertEqual(len(records), 3)
        for record in records:
            for model in ("integrated", "centre"):
                self.assertIn("optimizer_success", record[model])
                self.assertLessEqual(record[model]["max_abs_fitted_coordinate_px"], 12.0 + 1e-8)

    def test_detector_bounds_cannot_be_combined_with_truth_centred_bounds(self):
        with self.assertRaises(ValueError):
            run_case(detector_bounds=True, position_bound_half_width=0.5)

    def test_position_bound_width_is_validated(self):
        with self.assertRaises(ValueError):
            run_case(position_bound_half_width=0.0)

    def test_position_bound_sweep_preserves_all_paired_runs(self):
        result = run_position_bound_sweep(
            noise_model="none", starts_per_bound=3,
            observation_seed=20261420,
            initialization_seed_start=20261430,
        )
        self.assertEqual(result["bound_widths_px"], [0.5, 1.0, 2.0, None])
        self.assertEqual(len(result["runs"]), 12)
        self.assertEqual(result["status"], "synthetic_position_bound_sweep")
        print("POSITION_BOUND_SWEEP_RESULT=" + json.dumps(result["aggregate"], sort_keys=True))
        for width in ("0.5", "1.0", "2.0", "None"):
            for model in ("integrated", "centre"):
                self.assertEqual(result["aggregate"][width][model]["runs"], 3)
                self.assertGreaterEqual(
                    result["aggregate"][width][model]["optimizer_successes"], 0
                )

    def test_psf_mismatch_is_explicit(self):
        result = run_case(fit_sigma=1.2, seed=20261110)
        self.assertEqual(result["truth_sigma_px"], 1.3)
        self.assertEqual(result["fit_sigma_px"], 1.2)

    def test_noise_model_is_validated(self):
        with self.assertRaises(ValueError):
            run_case(noise_model="unknown")
        with self.assertRaises(ValueError):
            run_case(noise_model="gaussian_read", noise_level=0.0)

    def test_poisson_case_uses_finite_deviance_fit_results(self):
        result = run_case(noise_model="poisson", seed=20261112)
        for model in ("integrated", "centre"):
            self.assertTrue(
                all(
                    math.isfinite(result["summaries"][model][metric])
                    for metric in (
                        "mean_radial_error_px",
                        "rmse_radial_error_px",
                        "max_radial_error_px",
                        "mean_signed_x_error_px",
                        "mean_signed_y_error_px",
                        "least_squares_cost",
                        "assignment_total_distance_px",
                    )
                )
            )

    def test_gaussian_read_noise_case_is_recorded(self):
        result = run_case(
            noise_model="gaussian_read", noise_level=1.0, seed=20261111
        )
        self.assertEqual(result["noise_model"], "gaussian_read")
        self.assertEqual(result["noise_level"], 1.0)

    def test_initialization_trials_hold_observation_seed_fixed(self):
        result = run_initialization_trials(
            noise_model="gaussian_read",
            noise_level=1.0,
            trials=3,
            observation_seed=20261320,
            initialization_seed_start=20261330,
        )
        self.assertEqual(result["trial_count"], 3)
        self.assertEqual(
            {item["seed"] for item in result["trial_results"]},
            {20261320},
        )
        self.assertEqual(
            [item["initialization_seed"] for item in result["trial_results"]],
            [20261330, 20261331, 20261332],
        )
        for model in ("integrated", "centre"):
            self.assertTrue(
                math.isfinite(
                    result["aggregate_metrics"][model][
                        "mean_rmse_across_starts_px"
                    ]
                )
            )

    def test_repeated_noise_trials_hold_initialization_fixed(self):
        result = run_repeated_noise_trials(
            noise_model="gaussian_read",
            noise_level=1.0,
            trials=3,
            seed_start=20261210,
            initialization_seed=20261209,
        )
        self.assertEqual(result["trial_count"], 3)
        self.assertEqual(
            {item["initialization_seed"] for item in result["trial_results"]},
            {20261209},
        )
        self.assertEqual(
            [item["seed"] for item in result["trial_results"]],
            [20261210, 20261211, 20261212],
        )
        for model in ("integrated", "centre"):
            self.assertTrue(
                math.isfinite(
                    result["aggregate_metrics"][model][
                        "rmse_radial_error_px"
                    ]["mean_across_trials"]
                )
            )


    def test_image_peak_candidates_are_observation_derived_and_not_forced_to_seven(self):
        result = run_image_peak_detection(
            noise_model="none",
            seed=20261500,
            threshold_fractions=(0.05, 0.10, 0.20),
        )
        self.assertEqual(
            result["status"], "synthetic_observation_only_candidate_detection"
        )
        self.assertIn("observation_seed", result)
        self.assertIn("truth_use_policy", result)
        self.assertIn("never for candidate generation", result["truth_use_policy"])
        self.assertEqual(len(result["threshold_results"]), 3)
        for threshold_result in result["threshold_results"]:
            self.assertEqual(
                threshold_result["candidate_count"],
                len(threshold_result["candidates"]),
            )
            self.assertLessEqual(threshold_result["matched_truth_count"], 7)
            # Candidate coordinates must be converted from image-array
            # indices to the detector-centred coordinate frame used by truth.
            self.assertEqual(threshold_result["matched_truth_count"], 1)
            self.assertEqual(
                threshold_result["matched_truth_count"]
                + len(threshold_result["missed_truth_sources"]),
                7,
            )
            self.assertIn(
                threshold_result["fit_readiness"],
                {
                    "candidate_count_is_seven_but_fit_not_yet_run",
                    "not_ready_candidate_count_differs_from_seven",
                },
            )
        print(
            "IMAGE_PEAK_DETECTION_RESULT="
            + json.dumps(result["threshold_results"], sort_keys=True)
        )


    def test_peak_detection_sensitivity_sweep_records_full_grid(self):
        result = run_peak_detection_sensitivity_sweep(
            noise_model="none",
            seed=20261500,
        )
        self.assertEqual(result["status"], "synthetic_peak_detection_sensitivity_sweep")
        self.assertEqual(result["configuration_count"], 30)
        self.assertEqual(result["scored_configuration_count"], 150)
        self.assertEqual(len(result["records"]), 150)
        self.assertIn("truth is excluded", result["candidate_generation_policy"])
        for record in result["records"]:
            self.assertLessEqual(record["matched_truth_count"], 7)
            self.assertEqual(
                record["matched_truth_count"] + record["missed_truth_count"], 7
            )
            self.assertGreaterEqual(record["unmatched_candidate_count"], 0)
        print(
            "PEAK_DETECTION_SENSITIVITY_RESULT="
            + json.dumps(result, sort_keys=True)
        )

    def test_image_peak_detection_rejects_invalid_thresholds(self):
        with self.assertRaises(ValueError):
            run_image_peak_detection(threshold_fractions=(0.0, 0.1))


    def test_iterative_deblender_uses_observation_and_bic_without_forcing_count(self):
        observation = _scene_model(
            SEVEN_SOURCE_POSITIONS, SEVEN_SOURCE_AMPLITUDES,
            2.0, "integrated", SIGMA_PIXELS, IMAGE_SIZE,
        )
        result = run_iterative_psf_deblending(
            observation, assumed_sigma_px=SIGMA_PIXELS, max_components=12,
        )
        self.assertEqual(
            result["status"], "observation_only_iterative_psf_deblending"
        )
        self.assertEqual(result["selected_source_count"], len(result["selected_candidates"]))
        self.assertLessEqual(result["selected_source_count"], 12)
        self.assertIn("no truth positions", result["candidate_generation_policy"])
        self.assertGreaterEqual(len(result["candidate_trials"]), 1)
        for accepted in result["candidate_trials"]:
            if accepted["accepted"]:
                self.assertLess(accepted["bic_after"], accepted["bic_before"])
        self.assertTrue(np.all(np.isfinite(result["residual"])))
        def score_candidates(candidates):
            candidate_xy = np.asarray(
                [[item["x_px"], item["y_px"]] for item in candidates],
                dtype=float,
            ).reshape((-1, 2))
            distances = (
                np.linalg.norm(
                    SEVEN_SOURCE_POSITIONS[:, None, :] - candidate_xy[None, :, :],
                    axis=2,
                )
                if len(candidates) else np.empty((7, 0))
            )
            if len(candidates):
                truth_idx, candidate_idx = linear_sum_assignment(distances)
                matched = [
                    float(distances[t, candidate_idx[i]])
                    for i, t in enumerate(truth_idx)
                    if distances[t, candidate_idx[i]] <= 1.0
                ]
            else:
                matched = []
            return {
                "candidate_count": len(candidates),
                "matched_truth_count_within_1px": len(matched),
                "missed_truth_count": 7 - len(matched),
                "unmatched_candidate_count": len(candidates) - len(matched),
                "matched_radial_errors_px": matched,
            }

        greedy_score = score_candidates(result["selected_candidates"])
        joint = result["joint_refit"]
        self.assertIsNotNone(joint)
        self.assertTrue(np.all(np.isfinite(joint["residual"])))
        joint_score = score_candidates(joint["candidates"])
        print("ITERATIVE_PSF_DEBLENDING_RESULT=" + json.dumps({
            "greedy": greedy_score,
            "joint_refit": joint_score,
            "joint_optimizer_success": joint["optimizer_success"],
            "joint_rss": joint["rss"],
            "joint_bic": joint["bic"],
            "greedy_candidates": result["selected_candidates"],
            "joint_candidates": joint["candidates"],
            "trial_bic_sequence": [
                {"bic_before": item["bic_before"],
                 "bic_after": item["bic_after"],
                 "accepted": item["accepted"]}
                for item in result["candidate_trials"]
            ],
        }, sort_keys=True))

    def test_iterative_deblender_is_deterministic_for_fixed_observation(self):
        observation = _scene_model(
            SEVEN_SOURCE_POSITIONS, SEVEN_SOURCE_AMPLITUDES,
            2.0, "integrated", SIGMA_PIXELS, IMAGE_SIZE,
        )
        first = run_iterative_psf_deblending(observation, max_components=5)
        second = run_iterative_psf_deblending(observation, max_components=5)
        self.assertEqual(first["selected_candidates"], second["selected_candidates"])
        self.assertEqual(first["selected_source_count"], second["selected_source_count"])
        self.assertEqual(first["final_bic"], second["final_bic"])

    def test_iterative_deblender_validates_observation(self):
        with self.assertRaises(ValueError):
            run_iterative_psf_deblending(np.zeros((4, 4)))
        with self.assertRaises(ValueError):
            run_iterative_psf_deblending(np.zeros((7, 7)), assumed_sigma_px=0.0)


if __name__ == "__main__":
    unittest.main()
