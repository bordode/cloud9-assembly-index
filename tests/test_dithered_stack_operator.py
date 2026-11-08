"""Tests for the non-periodic dither shift-and-bin operator."""
import unittest

import numpy as np

from research.sandbox.dithered_stack_operator import (
    adjoint_operator,
    adjoint_relative_error,
    forward_operator,
)


def explicit_bilinear_reference(scene, bin_factor, phase_yx):
    """Small, slow reference implementation independent of the axis helpers."""
    shift_y, shift_x = (phase_yx[0] * bin_factor, phase_yx[1] * bin_factor)
    height, width = scene.shape
    shifted = np.zeros_like(scene, dtype=float)
    for out_y in range(height):
        source_y = out_y - shift_y
        y0 = int(np.floor(source_y))
        fy = source_y - y0
        for out_x in range(width):
            source_x = out_x - shift_x
            x0 = int(np.floor(source_x))
            fx = source_x - x0
            for iy, wy in ((y0, 1.0 - fy), (y0 + 1, fy)):
                for ix, wx in ((x0, 1.0 - fx), (x0 + 1, fx)):
                    if 0 <= iy < height and 0 <= ix < width:
                        shifted[out_y, out_x] += scene[iy, ix] * wy * wx
    return shifted.reshape(
        height // bin_factor, bin_factor, width // bin_factor, bin_factor
    ).sum(axis=(1, 3))


class DitheredStackOperatorTests(unittest.TestCase):
    def test_zero_phase_is_exact_block_sum(self):
        scene = np.arange(8 * 12, dtype=float).reshape(8, 12)
        observed = forward_operator(scene, bin_factor=2)
        expected = scene.reshape(4, 2, 6, 2).sum(axis=(1, 3))
        np.testing.assert_allclose(observed, expected, rtol=0, atol=0)

    def test_fractional_phase_matches_explicit_bilinear_reference(self):
        rng = np.random.default_rng(20261108)
        scene = rng.normal(size=(12, 16))
        for phase in ((0.25, -0.375), (-0.4, 0.2), (0.5, 0.5)):
            with self.subTest(phase=phase):
                actual = forward_operator(scene, 2, phase)
                expected = explicit_bilinear_reference(scene, 2, phase)
                np.testing.assert_allclose(actual, expected, rtol=2e-15, atol=2e-15)

    def test_fractional_phase_adjoint_identity(self):
        rng = np.random.default_rng(20261108)
        scene = rng.normal(size=(24, 30))
        detector = rng.normal(size=(12, 15))
        for phase in ((0.25, -0.375), (-0.4, 0.2), (0.0, 0.0), (0.5, 0.5)):
            with self.subTest(phase=phase):
                error = adjoint_relative_error(scene, detector, 2, phase)
                self.assertLess(error, 2e-14)

    def test_adjoint_shape(self):
        detector = np.ones((6, 8))
        result = adjoint_operator(detector, (12, 16), 2, (0.25, -0.125))
        self.assertEqual(result.shape, (12, 16))

    def test_nonperiodic_boundary_does_not_wrap(self):
        scene = np.zeros((8, 8), dtype=float)
        scene[0, 0] = 1.0
        shifted = forward_operator(scene, bin_factor=2, phase_yx=(-1.0, 0.0))
        # A negative row phase moves the scene toward the upper boundary;
        # zero extension discards flux that leaves the padded field.
        self.assertGreaterEqual(float(shifted.sum()), 0.0)
        self.assertLess(float(shifted.sum()), 1.0)

    def test_invalid_shapes_and_phases_rejected(self):
        with self.assertRaises(ValueError):
            forward_operator(np.ones((7, 8)), 2)
        with self.assertRaises(ValueError):
            forward_operator(np.ones((8, 8)), 0)
        with self.assertRaises(ValueError):
            forward_operator(np.ones((8, 8)), 2, (float("nan"), 0.0))


if __name__ == "__main__":
    unittest.main()
