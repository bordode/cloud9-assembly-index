"""Tests for the paired Gaussian/Poisson deblending benchmark."""
import unittest

import numpy as np

from research.sandbox.deblending_geometry_poisson import (
    run_case,
    run_geometry_poisson_sweep,
)
from research.sandbox.poisson_psf_deblending import run_poisson_psf_deblending
from research.sandbox.pixel_response_reproduction import pixel_integrated_gaussian


class DeblendingGeometryPoissonTests(unittest.TestCase):
    def test_poisson_detector_is_reproducible_and_reports_likelihood(self):
        expected = pixel_integrated_gaussian(
            0.4, -0.3, 120.0, 1.5, 1.3, size=9
        )
        rng = np.random.default_rng(20261731)
        counts = rng.poisson(expected)
        rate = counts.astype(float)
        first = run_poisson_psf_deblending(
            rate, exposure=1.0, max_components=2, max_nfev=500
        )
        second = run_poisson_psf_deblending(
            rate, exposure=1.0, max_components=2, max_nfev=500
        )
        self.assertEqual(first["selected_source_count"], second["selected_source_count"])
        self.assertEqual(first["candidates"], second["candidates"])
        self.assertEqual(first["poisson_bic"], second["poisson_bic"])
        self.assertEqual(first["method"], "joint_poisson_deviance_mle_with_poisson_bic")
        self.assertIn("Poisson-deviance", first["fitting_policy"])

    def test_paired_case_uses_same_seed_and_reports_both_methods(self):
        result = run_case(
            geometry_scale=1.0, exposure=1.0, seed=20261732,
        )
        self.assertIn("gaussian", result)
        self.assertIn("poisson", result)
        self.assertIsInstance(
            result["gaussian"]["joint_score"]["candidate_count"], int
        )
        self.assertEqual(result["poisson"]["score"]["candidate_count"],
                         result["poisson"]["selected_count"])
        self.assertEqual(result["observation_counts_sum"],
                         int(result["observation_counts_sum"]))

    def test_small_sweep_has_expected_cells_and_shared_observation_policy(self):
        result = run_geometry_poisson_sweep(
            trials_per_condition=1,
            geometry_scales=(1.0,),
            exposures=(1.0,),
            seed_start=20261740,
        )
        self.assertEqual(result["status"],
                         "paired_synthetic_geometry_poisson_likelihood_comparison")
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(len(result["aggregate"]), 1)
        self.assertEqual(result["overall"]["gaussian"]["trials"], 1)
        self.assertEqual(result["overall"]["poisson"]["trials"], 1)
        self.assertIn("same count image", " ".join(result["fair_comparison_controls"]))

    def test_invalid_exposure_is_rejected(self):
        with self.assertRaises(ValueError):
            run_poisson_psf_deblending(np.ones((9, 9)), exposure=0.0)


if __name__ == "__main__":
    unittest.main()
