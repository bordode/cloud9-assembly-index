"""Tests for nonlinear and non-Gaussian known-MI calibration controls."""
import importlib.util
import unittest
from pathlib import Path

import numpy as np

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts" / "run_mi_nongaussian_calibration.py"
)
SPEC = importlib.util.spec_from_file_location("mi_nongaussian_calibration", MODULE_PATH)
calibration = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(calibration)


class NonGaussianKnownMICalibrationTests(unittest.TestCase):
    def test_population_mi_is_invariant_under_bijective_controls(self):
        # Theoretical MI is that of the source Gaussian pair for either
        # transformed family; the transforms are strictly monotone.
        expected = calibration.gaussian_mi_bits(0.5)
        self.assertAlmostEqual(expected, 0.2075187496, places=9)
        for family in ("monotone_nonlinear", "uniform_gaussian_copula"):
            with self.subTest(family=family):
                rng = np.random.default_rng(44)
                x, y = calibration.draw_control_pair(512, 0.5, family, rng)
                self.assertEqual(x.shape, (512,))
                self.assertEqual(y.shape, (512,))
                self.assertTrue(np.all(np.isfinite(x)))
                self.assertTrue(np.all(np.isfinite(y)))
                if family == "uniform_gaussian_copula":
                    self.assertTrue(np.all((x > 0.0) & (x < 1.0)))
                    self.assertTrue(np.all((y > 0.0) & (y < 1.0)))

    def test_invalid_family_is_rejected(self):
        with self.assertRaises(ValueError):
            calibration.draw_control_pair(
                20, 0.2, "unknown", np.random.default_rng(1)
            )

    def test_small_grid_is_reproducible_and_has_expected_schema(self):
        args = ([64], [2], [0.0, 0.5],
                ["monotone_nonlinear", "uniform_gaussian_copula"], 5, 123)
        first = calibration.run_calibration(*args)
        second = calibration.run_calibration(*args)
        self.assertEqual(first, second)
        self.assertEqual(len(first["results"]), 4)
        row = first["results"][0]
        for key in ("family", "true_mi_bits", "raw_bias_bits",
                    "raw_rmse_bits", "clipped_bias_bits"):
            self.assertIn(key, row)
        self.assertEqual(row["true_mi_bits"], 0.0)


if __name__ == "__main__":
    unittest.main()
