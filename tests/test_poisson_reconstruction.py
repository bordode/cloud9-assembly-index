"""Tests for the photon-limited reconstruction control experiment."""
import unittest

import numpy as np

from research.sandbox.poisson_reconstruction import (
    poisson_richardson_lucy,
    simulate_reconstruction_trial,
)


class PoissonReconstructionTests(unittest.TestCase):
    def test_single_long_and_stationary_stack_are_equivalent(self):
        result = simulate_reconstruction_trial(
            sources_yx=[[6.35, 7.20], [11.10, 12.65]],
            fluxes=[900.0, 650.0],
            sigma_yx_px=[[0.8, 0.9], [1.0, 0.85]],
            science_shape=(12, 14),
            padding_pixels=3,
            bin_factor=3,
            seed=20261108,
            iterations=(1, 2),
        )
        for row in result["results"]:
            self.assertLess(row["stationary_long_max_abs_difference"], 2e-12)
            self.assertAlmostEqual(
                row["single_long"]["relative_rmse"],
                row["nine_stationary"]["relative_rmse"],
                places=12,
            )

    def test_dither_reconstruction_is_finite_and_nonnegative(self):
        result = simulate_reconstruction_trial(
            sources_yx=[[6.35, 7.20], [11.10, 12.65]],
            fluxes=[900.0, 650.0],
            sigma_yx_px=[[0.8, 0.9], [1.0, 0.85]],
            science_shape=(12, 14),
            padding_pixels=3,
            bin_factor=3,
            seed=17,
            iterations=(2,),
        )
        row = result["results"][0]
        self.assertTrue(np.isfinite(row["nine_dithered"]["relative_rmse"]))
        self.assertTrue(np.isfinite(row["nine_dithered"]["mean_source_centroid_error_px"]))
        self.assertTrue(np.isfinite(row["nine_dithered"]["mean_aperture_flux_ratio"]))

    def test_offgrid_dither_phases_are_supported_and_reproducible(self):
        phases = [
            (y, x)
            for y in (-0.29, 0.0, 0.29)
            for x in (-0.23, 0.0, 0.23)
        ]
        result = simulate_reconstruction_trial(
            sources_yx=[[6.35, 7.20], [11.10, 12.65]],
            fluxes=[900.0, 650.0],
            sigma_yx_px=[[0.8, 0.9], [1.0, 0.85]],
            science_shape=(12, 14),
            padding_pixels=3,
            bin_factor=3,
            seed=23,
            iterations=(2,),
            dither_phases_yx=phases,
        )
        self.assertEqual(result["metadata"]["dither_phases_yx"], [list(p) for p in phases])
        self.assertLess(result["results"][0]["stationary_long_max_abs_difference"], 2e-12)
        self.assertTrue(np.isfinite(result["results"][0]["nine_dithered"]["relative_rmse"]))

    def test_known_uniform_background_preserves_long_stationary_control(self):
        result = simulate_reconstruction_trial(
            sources_yx=[[6.35, 7.20], [11.10, 12.65]],
            fluxes=[900.0, 650.0],
            sigma_yx_px=[[0.8, 0.9], [1.0, 0.85]],
            science_shape=(12, 14),
            padding_pixels=3,
            bin_factor=3,
            seed=29,
            iterations=(1, 2),
            background_rate=0.5,
        )
        for row in result["results"]:
            self.assertLess(row["stationary_long_max_abs_difference"], 2e-12)
            self.assertAlmostEqual(
                row["single_long"]["relative_rmse"],
                row["nine_stationary"]["relative_rmse"],
                places=12,
            )
        self.assertEqual(
            result["metadata"]["background_rate_counts_per_detector_pixel_per_exposure_unit"],
            0.5,
        )

    def test_known_spatial_background_map_preserves_stationary_control(self):
        background = np.broadcast_to(
            np.linspace(0.1, 0.9, 20, dtype=float), (18, 20)
        ).copy()
        result = simulate_reconstruction_trial(
            sources_yx=[[6.35, 7.20], [11.10, 12.65]],
            fluxes=[900.0, 650.0],
            sigma_yx_px=[[0.8, 0.9], [1.0, 0.85]],
            science_shape=(12, 14),
            padding_pixels=3,
            bin_factor=3,
            seed=31,
            iterations=(2,),
            background_rate=background,
        )
        self.assertLess(result["results"][0]["stationary_long_max_abs_difference"], 2e-12)
        self.assertIsNone(
            result["metadata"]["background_rate_counts_per_detector_pixel_per_exposure_unit"]
        )
        self.assertEqual(result["metadata"]["background_map_summary"]["shape"], [18, 20])
        self.assertAlmostEqual(result["metadata"]["background_map_summary"]["mean"], 0.5)

    def test_background_map_with_wrong_detector_shape_is_rejected(self):
        with self.assertRaises(ValueError):
            simulate_reconstruction_trial(
                sources_yx=[[6.35, 7.20]],
                fluxes=[900.0],
                sigma_yx_px=[[0.8, 0.9]],
                science_shape=(12, 14),
                padding_pixels=3,
                bin_factor=3,
                iterations=(1,),
                background_rate=np.ones((4, 4)),
            )

    def test_negative_background_rate_is_rejected(self):
        with self.assertRaises(ValueError):
            simulate_reconstruction_trial(
                sources_yx=[[6.35, 7.20]],
                fluxes=[900.0],
                sigma_yx_px=[[0.8, 0.9]],
                science_shape=(12, 14),
                padding_pixels=3,
                bin_factor=3,
                iterations=(1,),
                background_rate=-0.1,
            )

    def test_solver_rejects_invalid_data_and_iteration_count(self):
        with self.assertRaises(ValueError):
            poisson_richardson_lucy(
                np.ones((1, 4, 4)), [(0.0, 0.0)], [1.0],
                (8, 8), 2, iterations=0,
            )
        with self.assertRaises(ValueError):
            poisson_richardson_lucy(
                -np.ones((1, 4, 4)), [(0.0, 0.0)], [1.0],
                (8, 8), 2,
            )


if __name__ == "__main__":
    unittest.main()
