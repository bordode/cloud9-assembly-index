"""Tests for proposal fitted-scene diversity audit."""
import unittest

import numpy as np

from research.sandbox.deblending_poisson_fit_diversity import (
    _posthoc_fit_audit,
    _scene_distance,
    _summarize_posthoc_candidate_scores,
    run_diversity_audit,
)


class FitDiversityTests(unittest.TestCase):
    def test_scene_distance_is_permutation_invariant(self):
        a = [{"x_px": 0.0, "y_px": 0.0, "amplitude": 10.0},
             {"x_px": 2.0, "y_px": 0.0, "amplitude": 20.0}]
        b = [{"x_px": 2.0, "y_px": 0.0, "amplitude": 20.0},
             {"x_px": 0.0, "y_px": 0.0, "amplitude": 10.0}]
        result = _scene_distance(a, b)
        self.assertTrue(result["same_source_count"])
        self.assertAlmostEqual(result["rms_position_px"], 0.0)
        self.assertAlmostEqual(result["relative_amplitude_rms"], 0.0)

    def test_scene_distance_detects_position_change(self):
        a = [{"x_px": 0.0, "y_px": 0.0, "amplitude": 10.0}]
        b = [{"x_px": 0.1, "y_px": 0.0, "amplitude": 10.0}]
        self.assertAlmostEqual(_scene_distance(a, b)["rms_position_px"], 0.1)


    def test_posthoc_fit_audit_records_candidate_metrics_without_selection(self):
        fit = {
            "proposal_rank": 2,
            "poisson_bic": 12.5,
            "poisson_deviance": 4.5,
            "fitted_candidates": [
                {"x_px": 0.1, "y_px": 0.0, "amplitude": 10.0},
                {"x_px": 2.1, "y_px": 0.0, "amplitude": 8.0},
            ],
        }
        result = _posthoc_fit_audit(fit, np.array([[0.0, 0.0], [2.0, 0.0]]), 2)
        self.assertTrue(result["selected_by_candidate_bic"])
        self.assertEqual(result["poisson_bic"], 12.5)
        self.assertEqual(result["poisson_deviance"], 4.5)
        self.assertEqual(result["posthoc_matched_truth_count"], 2)
        self.assertAlmostEqual(result["posthoc_matched_position_rmse_px"], 0.1)

    def test_empty_posthoc_candidate_audit_is_safe(self):
        result = _posthoc_fit_audit(
            {
                "proposal_rank": 1,
                "poisson_bic": 1.0,
                "poisson_deviance": 0.5,
                "fitted_candidates": [],
            },
            np.array([[0.0, 0.0]]),
            1,
        )
        self.assertEqual(result["posthoc_matched_truth_count"], 0)
        self.assertIsNone(result["posthoc_matched_position_rmse_px"])

    def test_posthoc_summary_handles_no_successful_fits(self):
        result = _summarize_posthoc_candidate_scores([
            {"step_audits": [{"fit_audits_posthoc_only": []}]}
        ])
        self.assertEqual(result["steps_with_successful_candidate_fits"], 0)
        self.assertIsNone(result["selected_fit_mean_matched_truth"])
        self.assertIsNone(result["best_available_fit_mean_matched_truth"])

    def test_small_audit_has_expected_grid(self):
        result = run_diversity_audit(
            trials_per_condition=1, geometry_scales=(1.0,), exposures=(1.0,),
            seed_start=20261990,
        )
        self.assertEqual(result["trial_count"], 1)
        self.assertEqual(result["seed_start"], 20261990)
        self.assertIn("position_rms_px", result)
        self.assertIn("pairwise_records", result)


if __name__ == "__main__":
    unittest.main()
