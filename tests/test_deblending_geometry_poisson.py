"""Tests for the geometry/Poisson deblending stress-test harness."""
import unittest

from research.sandbox.deblending_geometry_poisson import (
    run_case,
    run_geometry_poisson_sweep,
)


class DeblendingGeometryPoissonTests(unittest.TestCase):
    def test_case_is_reproducible_and_reports_postfit_scores(self):
        first = run_case(geometry_scale=1.0, exposure=1.0, seed=20261701)
        second = run_case(geometry_scale=1.0, exposure=1.0, seed=20261701)
        self.assertEqual(first["greedy_selected_count"], second["greedy_selected_count"])
        self.assertEqual(first["greedy_score"], second["greedy_score"])
        self.assertEqual(first["joint_score"], second["joint_score"])
        self.assertEqual(first["greedy_score"]["candidate_count"],
                         first["greedy_selected_count"])
        self.assertIn("joint_optimizer_success", first)

    def test_small_sweep_has_expected_cells_and_truth_free_policy(self):
        result = run_geometry_poisson_sweep(
            trials_per_condition=1,
            geometry_scales=(0.8, 1.0),
            exposures=(1.0, 0.1),
            seed_start=20261710,
        )
        self.assertEqual(result["status"], "exploratory_synthetic_geometry_poisson_sweep")
        self.assertEqual(len(result["records"]), 4)
        self.assertEqual(len(result["aggregate"]), 4)
        self.assertIn("truth positions and source count are excluded",
                      result["candidate_generation_policy"])
        self.assertIn("likelihood-mismatch", result["likelihood_caveat"])

    def test_invalid_exposure_is_rejected(self):
        with self.assertRaises(ValueError):
            run_case(geometry_scale=1.0, exposure=0.0, seed=20261720)


if __name__ == "__main__":
    unittest.main()
