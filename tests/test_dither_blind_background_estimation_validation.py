"""Tests for hidden-background estimation and its calibration-region contract."""
import unittest

import numpy as np

from scripts.run_dither_blind_background_estimation_validation import (
    BORDER_WIDTH,
    GRADIENT_AMPLITUDES,
    SEEDS,
    estimate_horizontal_background,
    make_background_map,
)


class BlindBackgroundEstimationTests(unittest.TestCase):
    def test_fresh_seeds_and_gradient_levels_are_locked(self):
        self.assertEqual(len(SEEDS), 30)
        self.assertEqual(len(set(SEEDS)), 30)
        self.assertEqual(GRADIENT_AMPLITUDES, (0.0, 0.25, 0.45))
        self.assertEqual(BORDER_WIDTH, 3)

    def test_estimator_recovers_noise_free_linear_map_from_border(self):
        truth = make_background_map((18, 20), 0.25)
        frames = np.broadcast_to(truth, (9, 18, 20)).copy()
        estimate, info = estimate_horizontal_background(frames, np.full(9, 1 / 9))
        np.testing.assert_allclose(estimate, truth, atol=1e-5)
        self.assertTrue(info["fit_success"])

    def test_estimator_uses_nonnegative_endpoints(self):
        rng = np.random.default_rng(20261114)
        truth = make_background_map((18, 20), 0.45)
        frames = rng.poisson(truth / 9.0, size=(9, 18, 20))
        estimate, info = estimate_horizontal_background(frames, np.full(9, 1 / 9))
        self.assertTrue(np.all(np.isfinite(estimate)))
        self.assertTrue(np.all(estimate >= 0))
        self.assertGreater(info["calibration_pixel_count"], 0)

    def test_estimator_rejects_invalid_exposures(self):
        with self.assertRaises(ValueError):
            estimate_horizontal_background(np.ones((9, 18, 20)), np.zeros(9))


if __name__ == "__main__":
    unittest.main()
