"""Validation tests for the exact Poisson-Gaussian latent-count EM solver."""
import unittest
import numpy as np

from research.sandbox.poisson_gaussian_reconstruction import (
    expected_latent_counts,
    poisson_gaussian_em,
)


class PoissonGaussianReconstructionTests(unittest.TestCase):
    def test_negative_observations_are_supported(self):
        y = np.array([-2.5, -0.4, 0.0, 1.2, 5.1])
        mean = np.array([0.2, 0.5, 1.0, 2.0, 4.0])
        expected = expected_latent_counts(y, mean, 1.0)
        self.assertTrue(np.all(np.isfinite(expected)))
        self.assertTrue(np.all(expected >= 0))
        self.assertTrue(np.all(expected <= 20))
        self.assertLess(expected[0], expected[-1])

    def test_zero_poisson_mean_has_zero_expected_count(self):
        result = expected_latent_counts(np.array([-1.0, 0.0, 2.0]),
                                        np.zeros(3), 1.0)
        np.testing.assert_array_equal(result, np.zeros(3))

    def test_high_signal_posterior_tracks_observation(self):
        y = np.array([20.0, 35.0, 50.0])
        mean = np.array([20.0, 35.0, 50.0])
        result = expected_latent_counts(y, mean, 0.5)
        np.testing.assert_allclose(result, y, atol=0.15)

    def test_em_returns_finite_nonnegative_image_with_negative_pixels(self):
        frames = np.array([[[-1.2, 0.3, 2.0, 1.1],
                            [0.0, 1.5, -0.7, 0.2],
                            [2.1, 0.5, 0.0, -0.3],
                            [0.2, 1.0, 0.4, 0.1]]])
        estimate = poisson_gaussian_em(
            frames, [(0.0, 0.0)], [1.0], (8, 8), 2,
            iterations=3, background_rate=0.5, read_noise_sigma=1.0,
        )
        self.assertEqual(estimate.shape, (8, 8))
        self.assertTrue(np.all(np.isfinite(estimate)))
        self.assertTrue(np.all(estimate >= 0))
        self.assertGreater(float(estimate.sum()), 0.0)

    def test_invalid_noise_scale_is_rejected(self):
        with self.assertRaises(ValueError):
            expected_latent_counts(np.array([1.0]), np.array([1.0]), 0.0)


if __name__ == "__main__":
    unittest.main()
