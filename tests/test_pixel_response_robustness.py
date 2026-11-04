"""Regression checks for the staged pixel-response sensitivity suite."""
import math
import unittest

from research.sandbox.pixel_response_robustness import run_case


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
                    math.isfinite(value)
                    for value in result["summaries"][model].values()
                )
            )

    def test_gaussian_read_noise_case_is_recorded(self):
        result = run_case(
            noise_model="gaussian_read", noise_level=1.0, seed=20261111
        )
        self.assertEqual(result["noise_model"], "gaussian_read")
        self.assertEqual(result["noise_level"], 1.0)


if __name__ == "__main__":
    unittest.main()
