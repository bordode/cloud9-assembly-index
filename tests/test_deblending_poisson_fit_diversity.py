"""Tests for proposal fitted-scene diversity audit."""
import unittest

from research.sandbox.deblending_poisson_fit_diversity import _scene_distance, run_diversity_audit


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
