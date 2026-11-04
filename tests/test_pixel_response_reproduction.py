"""Tests for the controlled synthetic pixel-response pilot."""
import unittest

from research.sandbox.pixel_response_reproduction import (
    run_experiment,
    run_seven_source_experiment,
)


class PixelResponsePilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_experiment(noise_sigma=0.0, seed=20261104)

    def test_experiment_is_explicitly_synthetic_and_scoped(self):
        self.assertEqual(self.result["data_kind"], "synthetic")
        self.assertEqual(self.result["status"], "synthetic_pilot")
        self.assertEqual(self.result["phase_grid_count"], 25)
        self.assertIn("does not reproduce", self.result["interpretation"])

    def test_integrated_model_recovers_identifiable_noise_free_positions(self):
        summary = self.result["summaries"]
        self.assertLess(summary["integrated"]["max_radial_error_px"], 1e-6)

    def test_isolated_symmetric_source_has_no_material_centroid_bias(self):
        summary = self.result["summaries"]
        # A symmetric isolated source is a null control: both models should
        # localize its centre accurately even if their pixel predictions differ.
        self.assertLess(summary["centre"]["max_radial_error_px"], 1e-5)
        self.assertLess(summary["integrated"]["max_radial_error_px"], 1e-6)

    def test_seven_source_scene_exposes_centre_sampling_position_bias(self):
        result = run_seven_source_experiment(noise_sigma=0.0, seed=20261105)
        self.assertEqual(result["source_count"], 7)
        self.assertEqual(result["data_kind"], "synthetic")
        integrated = result["summaries"]["integrated"]
        centre = result["summaries"]["centre"]
        self.assertLess(integrated["max_radial_error_px"], 1e-6)
        self.assertGreater(centre["mean_radial_error_px"], 0.04)
        self.assertLess(centre["mean_radial_error_px"], 0.08)
        self.assertIn("does not reproduce Aimy", result["interpretation"])


if __name__ == "__main__":
    unittest.main()
