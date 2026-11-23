"""Tests for the fixed-iteration spatial-background-gradient experiment."""
import unittest

import numpy as np

from scripts.run_dither_spatial_background_gradient_validation import (
    GRADIENT_AMPLITUDES,
    GRADIENT_VALIDATION_SEEDS,
    ITERATIONS,
    make_background_map,
    summarize,
)


class DitherSpatialBackgroundGradientTests(unittest.TestCase):
    def test_gradient_validation_seeds_are_fresh(self):
        self.assertEqual(len(GRADIENT_VALIDATION_SEEDS), 30)
        self.assertTrue(set(range(2026111000, 2026111030)).isdisjoint(GRADIENT_VALIDATION_SEEDS))
        self.assertTrue(set(range(2026111200, 2026111230)).isdisjoint(GRADIENT_VALIDATION_SEEDS))

    def test_iteration_count_is_locked(self):
        self.assertEqual(ITERATIONS, (2,))

    def test_gradient_grid_is_nonnegative_and_mean_preserving(self):
        self.assertEqual(GRADIENT_AMPLITUDES, (0.0, 0.25, 0.45))
        for amplitude in GRADIENT_AMPLITUDES:
            background = make_background_map((28, 30), amplitude)
            self.assertEqual(background.shape, (28, 30))
            self.assertGreaterEqual(float(background.min()), 0.0)
            self.assertAlmostEqual(float(background.mean()), 0.5, places=12)
        self.assertAlmostEqual(float(make_background_map((28, 30), 0.45).min()), 0.05)
        self.assertAlmostEqual(float(make_background_map((28, 30), 0.45).max()), 0.95)

    def test_background_map_is_detector_fixed_and_column_varying(self):
        background = make_background_map((8, 10), 0.25)
        np.testing.assert_allclose(background[0], background[-1])
        self.assertTrue(np.all(np.diff(background[4]) > 0))

    def test_summary_reports_confidence_interval(self):
        result = summarize([1.0, 2.0, 3.0])
        self.assertEqual(result["n"], 3)
        self.assertEqual(result["mean"], 2.0)
        self.assertEqual(len(result["ci95_mean"]), 2)


if __name__ == "__main__":
    unittest.main()
