"""Tests for the predeclared Poisson deterministic multi-start experiment."""
import unittest

import numpy as np

from research.sandbox.deblending_poisson_multistart import (
    MULTISTART_OFFSETS,
    run_case,
)
from research.sandbox.poisson_psf_deblending import run_poisson_psf_deblending
from research.sandbox.pixel_response_reproduction import pixel_integrated_gaussian


class PoissonMultiStartTests(unittest.TestCase):
    def test_default_single_start_matches_explicit_zero_offset(self):
        counts = np.random.default_rng(20261801).poisson(
            pixel_integrated_gaussian(0.2, -0.1, 80.0, 1.0, 1.3, size=9)
        ).astype(float)
        default = run_poisson_psf_deblending(
            counts, exposure=1.0, max_components=2, max_nfev=500
        )
        explicit = run_poisson_psf_deblending(
            counts, exposure=1.0, max_components=2, max_nfev=500,
            proposal_start_offsets=((0.0, 0.0),),
        )
        self.assertEqual(default["selected_source_count"],
                         explicit["selected_source_count"])
        self.assertEqual(default["candidates"], explicit["candidates"])
        self.assertEqual(default["poisson_bic"], explicit["poisson_bic"])

    def test_multistart_records_all_initializations(self):
        counts = np.random.default_rng(20261802).poisson(
            pixel_integrated_gaussian(0.3, -0.2, 100.0, 1.0, 1.3, size=9)
        ).astype(float)
        result = run_poisson_psf_deblending(
            counts, exposure=1.0, max_components=1, max_nfev=500,
            proposal_start_offsets=MULTISTART_OFFSETS,
        )
        self.assertTrue(
            result["candidate_trials"],
            "the diagnostic fixture must exercise at least one proposal",
        )
        trial = result["candidate_trials"][0]
        self.assertEqual(trial["initialization_starts_tried"], 9)
        self.assertEqual(len(trial["winning_start_offset_px"]), 2)
        self.assertGreaterEqual(trial["successful_initialization_starts"], 1)
        self.assertLessEqual(trial["successful_initialization_starts"], 9)

    def test_three_way_case_uses_common_observation(self):
        result = run_case(geometry_scale=1.0, exposure=1.0, seed=20261803)
        self.assertEqual(result["gaussian"]["score"]["candidate_count"],
                         result["gaussian"]["selected_count"])
        self.assertEqual(result["poisson_single"]["score"]["candidate_count"],
                         result["poisson_single"]["selected_count"])
        self.assertEqual(result["poisson_multistart"]["score"]["candidate_count"],
                         result["poisson_multistart"]["selected_count"])
        self.assertEqual(result["seed"], 20261803)


if __name__ == "__main__":
    unittest.main()
