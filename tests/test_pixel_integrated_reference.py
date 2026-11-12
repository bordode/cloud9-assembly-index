"""Independent analytic validation of the dither shift-and-bin model."""
import unittest

import numpy as np

from research.sandbox.dithered_stack_operator import forward_operator
from research.sandbox.pixel_integrated_reference import (
    crop_common_interior,
    gaussian_scene_subpixel_integrals,
    pixel_integrated_gaussian_frame,
)


class PixelIntegratedReferenceTests(unittest.TestCase):
    def setUp(self):
        self.science_shape = (20, 22)
        self.padding = 4
        self.detector_shape = (
            self.science_shape[0] + 2 * self.padding,
            self.science_shape[1] + 2 * self.padding,
        )
        self.sources = np.array([
            [self.padding + 6.35, self.padding + 7.20],
            [self.padding + 12.10, self.padding + 15.65],
            [self.padding + 15.40, self.padding + 4.80],
        ])
        self.fluxes = np.array([1200.0, 760.0, 430.0])
        self.sigmas = np.array([[0.72, 0.91], [1.05, 0.83], [0.88, 1.12]])

    def _comparison(self, bin_factor, phase):
        highres = gaussian_scene_subpixel_integrals(
            (self.detector_shape[0] * bin_factor,
             self.detector_shape[1] * bin_factor),
            bin_factor,
            self.sources,
            self.fluxes,
            self.sigmas,
        )
        approximate = forward_operator(highres, bin_factor, phase)
        exact = pixel_integrated_gaussian_frame(
            self.detector_shape,
            self.sources,
            self.fluxes,
            self.sigmas,
            phase,
        )
        approximate = crop_common_interior(
            approximate, self.padding, self.science_shape
        )
        exact = crop_common_interior(exact, self.padding, self.science_shape)
        relative_rmse = np.linalg.norm(approximate - exact) / np.linalg.norm(exact)
        return relative_rmse, approximate, exact

    def test_zero_phase_block_sum_matches_exact_pixel_integrals(self):
        error, approximate, exact = self._comparison(4, (0.0, 0.0))
        self.assertLess(error, 2e-13)
        np.testing.assert_allclose(approximate, exact, rtol=2e-13, atol=2e-13)

    def test_grid_aligned_fractional_phases_match_exact_integrals(self):
        # At bin_factor=3, +/-1/3 detector-pixel offsets are exactly one
        # high-resolution cell, so the shift is a discrete cell permutation.
        for phase in (
            (-1.0 / 3.0, -1.0 / 3.0),
            (-1.0 / 3.0, 0.0),
            (0.0, 1.0 / 3.0),
            (1.0 / 3.0, 1.0 / 3.0),
        ):
            with self.subTest(phase=phase):
                error, approximate, exact = self._comparison(3, phase)
                self.assertLess(error, 3e-13)
                np.testing.assert_allclose(
                    approximate, exact, rtol=3e-13, atol=3e-13
                )

    def test_off_grid_phase_error_decreases_with_supersampling(self):
        phase = (0.23, -0.17)
        errors = [self._comparison(factor, phase)[0] for factor in (2, 4, 8, 16)]
        self.assertLess(errors[1], errors[0])
        self.assertLess(errors[2], errors[1])
        self.assertLess(errors[3], errors[2])
        self.assertLess(errors[3], 1e-3)

    def test_common_interior_crop_is_fixed_and_validated(self):
        padded = np.arange(self.detector_shape[0] * self.detector_shape[1]).reshape(
            self.detector_shape
        )
        cropped = crop_common_interior(
            padded, self.padding, self.science_shape
        )
        self.assertEqual(cropped.shape, self.science_shape)
        np.testing.assert_array_equal(
            cropped,
            padded[
                self.padding:self.padding + self.science_shape[0],
                self.padding:self.padding + self.science_shape[1],
            ],
        )
        with self.assertRaises(ValueError):
            crop_common_interior(padded[:-1], self.padding, self.science_shape)


    def test_padding_extension_does_not_change_fixed_interior(self):
        phase = (0.23, -0.17)
        interior_results = []
        for padding in (4, 8):
            detector_shape = (
                self.science_shape[0] + 2 * padding,
                self.science_shape[1] + 2 * padding,
            )
            sources = self.sources - self.padding + padding
            highres = gaussian_scene_subpixel_integrals(
                (detector_shape[0] * 4, detector_shape[1] * 4),
                4,
                sources,
                self.fluxes,
                self.sigmas,
            )
            frame = forward_operator(highres, 4, phase)
            interior_results.append(
                crop_common_interior(frame, padding, self.science_shape)
            )
        np.testing.assert_allclose(
            interior_results[0], interior_results[1], rtol=1e-11, atol=1e-10
        )

    def test_invalid_source_parameters_rejected(self):
        with self.assertRaises(ValueError):
            gaussian_scene_subpixel_integrals(
                (16, 16), 2, [[4.0, 4.0]], [100.0], [0.0, 1.0]
            )
        with self.assertRaises(ValueError):
            pixel_integrated_gaussian_frame(
                (8, 8), [[4.0, 4.0]], [-1.0], [1.0, 1.0]
            )


if __name__ == "__main__":
    unittest.main()
