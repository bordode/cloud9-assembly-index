"""Tests for the standalone known-MI calibration harness."""
import importlib.util
import unittest
from pathlib import Path

import numpy as np

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_mi_estimator_calibration.py"
SPEC = importlib.util.spec_from_file_location("mi_calibration", MODULE_PATH)
mi_calibration = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mi_calibration)


class KnownMICalibrationTests(unittest.TestCase):
    def test_gaussian_mi_known_values(self):
        self.assertAlmostEqual(mi_calibration.gaussian_mi_bits(0.0), 0.0)
        self.assertAlmostEqual(mi_calibration.gaussian_mi_bits(0.5), 0.2075187496)
        self.assertAlmostEqual(mi_calibration.gaussian_mi_bits(-0.5), 0.2075187496)

    def test_gaussian_mi_rejects_invalid_correlation(self):
        for rho in (1.0, -1.0, float("nan")):
            with self.subTest(rho=rho):
                with self.assertRaises(ValueError):
                    mi_calibration.gaussian_mi_bits(rho)

    def test_raw_estimator_is_finite_and_reproducible(self):
        rng1 = np.random.default_rng(17)
        rng2 = np.random.default_rng(17)
        x1, y1 = mi_calibration.draw_pair(128, 0.5, rng1)
        x2, y2 = mi_calibration.draw_pair(128, 0.5, rng2)
        first = mi_calibration.ksg_mi_2d_raw(x1, y1, k=3)
        second = mi_calibration.ksg_mi_2d_raw(x2, y2, k=3)
        self.assertTrue(np.isfinite(first))
        self.assertAlmostEqual(first, second)

    def test_estimator_validates_inputs(self):
        with self.assertRaises(ValueError):
            mi_calibration.ksg_mi_2d_raw(np.arange(10), np.arange(9), k=2)
        with self.assertRaises(ValueError):
            mi_calibration.ksg_mi_2d_raw(np.arange(10), np.arange(10), k=10)
        with self.assertRaises(ValueError):
            mi_calibration.ksg_mi_2d_raw([1, 2, np.nan], [1, 2, 3], k=1)

    def test_small_calibration_output_schema_and_reproducibility(self):
        first = mi_calibration.run_calibration([64], [2], [0.0, 0.5], 5, 123)
        second = mi_calibration.run_calibration([64], [2], [0.0, 0.5], 5, 123)
        self.assertEqual(first, second)
        self.assertEqual(len(first["results"]), 2)
        row = first["results"][0]
        for key in (
            "true_mi_bits", "raw_bias_bits", "raw_rmse_bits",
            "clipped_bias_bits", "raw_fraction_below_zero",
            "clipped_fraction_equal_zero",
        ):
            self.assertIn(key, row)
        self.assertEqual(row["condition"], "independent_gaussian")
        self.assertEqual(row["true_mi_bits"], 0.0)


if __name__ == "__main__":
    unittest.main()
