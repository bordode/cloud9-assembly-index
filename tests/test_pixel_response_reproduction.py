"""Tests for the controlled synthetic pixel-response pilot."""
import unittest

from research.sandbox.pixel_response_reproduction import run_experiment


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

    def test_centre_model_is_evaluated_on_identical_data(self):
        summary = self.result["summaries"]
        self.assertGreater(
            summary["centre"]["mean_radial_error_px"],
            summary["integrated"]["mean_radial_error_px"],
        )


if __name__ == "__main__":
    unittest.main()
