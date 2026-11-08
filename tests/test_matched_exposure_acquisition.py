"""Tests for matched-exposure Poisson/read-noise acquisition arms."""
import unittest

import numpy as np

from research.sandbox.matched_exposure_acquisition import (
    nine_phase_grid,
    simulate_matched_exposure_arms,
)


class MatchedExposureAcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.scene = np.zeros((24, 24), dtype=float)
        self.scene[8:16, 8:16] = 2.0
        self.scene[10:14, 10:14] = 5.0

    def test_expected_counts_match_exposure_accounting(self):
        result = simulate_matched_exposure_arms(
            self.scene, 2, total_exposure=90.0, rng=1234
        )
        np.testing.assert_allclose(
            result["expected_single_long"],
            90.0 * result["expected_stationary_stack"][0],
            rtol=0,
            atol=0,
        )
        np.testing.assert_allclose(
            result["expected_stationary_stack"],
            np.broadcast_to(
                result["expected_stationary_stack"][0],
                result["expected_stationary_stack"].shape,
            ),
            rtol=0,
            atol=0,
        )
        self.assertEqual(result["stationary_stack"].shape, (9, 12, 12))
        self.assertEqual(result["dithered_stack"].shape, (9, 12, 12))
        self.assertEqual(result["single_long"].shape, (12, 12))
        self.assertEqual(result["metadata"]["frame_exposure"], 10.0)

    def test_photon_only_draws_are_nonnegative_integer_counts(self):
        result = simulate_matched_exposure_arms(
            self.scene, 2, 90.0, rng=42, read_noise_sigma=0.0
        )
        for key in ("single_long", "stationary_stack", "dithered_stack"):
            values = result[key]
            self.assertTrue(np.all(values >= 0))
            np.testing.assert_array_equal(values, np.floor(values))

    def test_seed_reproduces_all_three_arms(self):
        first = simulate_matched_exposure_arms(self.scene, 2, 90.0, rng=20261108)
        second = simulate_matched_exposure_arms(self.scene, 2, 90.0, rng=20261108)
        for key in ("single_long", "stationary_stack", "dithered_stack"):
            np.testing.assert_array_equal(first[key], second[key])

    def test_read_noise_is_per_readout_and_can_make_counts_negative(self):
        zero_scene = np.zeros((8, 8), dtype=float)
        result = simulate_matched_exposure_arms(
            zero_scene,
            2,
            9.0,
            rng=8,
            read_noise_sigma=5.0,
        )
        self.assertEqual(result["metadata"]["read_noise_readouts"]["single_long"], 1)
        self.assertEqual(result["metadata"]["read_noise_readouts"]["stationary_stack"], 9)
        self.assertEqual(result["metadata"]["read_noise_readouts"]["dithered_stack"], 9)
        self.assertTrue(np.any(result["single_long"] < 0))
        self.assertTrue(np.any(result["stationary_stack"] < 0))

    def test_default_phase_grid_is_nine_distinct_fractional_phases(self):
        phases = np.asarray(nine_phase_grid())
        self.assertEqual(phases.shape, (9, 2))
        self.assertEqual(np.unique(phases, axis=0).shape[0], 9)
        self.assertTrue(np.any(np.abs(phases - np.rint(phases)) > 1e-12))

    def test_invalid_scene_exposure_noise_and_phases_rejected(self):
        with self.assertRaises(ValueError):
            simulate_matched_exposure_arms(-np.ones((8, 8)), 2, 9.0)
        with self.assertRaises(ValueError):
            simulate_matched_exposure_arms(self.scene, 2, 0.0)
        with self.assertRaises(ValueError):
            simulate_matched_exposure_arms(self.scene, 2, 9.0, read_noise_sigma=-1.0)
        with self.assertRaises(ValueError):
            simulate_matched_exposure_arms(
                self.scene, 2, 9.0, dither_phases_yx=((0.0, 0.0),)
            )
        repeated = [(0.0, 0.0)] * 9
        with self.assertRaises(ValueError):
            simulate_matched_exposure_arms(
                self.scene, 2, 9.0, dither_phases_yx=repeated
            )


if __name__ == "__main__":
    unittest.main()
