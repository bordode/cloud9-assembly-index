"""Regression checks for the staged pixel-response sensitivity suite."""
import json
import math
import unittest

from research.sandbox.pixel_response_robustness import (
    run_case,
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
        )
        self.assertEqual(result["initialization_policy"], "detector_uniform")
        for model in ("integrated", "centre"):
            self.assertIn("optimizer_success", result["summaries"][model])

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


if __name__ == "__main__":
    unittest.main()
