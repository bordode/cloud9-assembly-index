"""Tests for top-k Poisson residual proposals selected by unchanged BIC."""
import unittest

import numpy as np

from research.sandbox.poisson_psf_deblending import run_poisson_psf_deblending
from research.sandbox.pixel_response_reproduction import pixel_integrated_gaussian


class PoissonProposalBicTests(unittest.TestCase):
    def _observation(self):
        return np.random.default_rng(20261901).poisson(
            pixel_integrated_gaussian(0.25, -0.15, 120.0, 1.0, 1.3, size=11)
        ).astype(float)

    def test_default_policy_matches_explicit_top_score(self):
        data = self._observation()
        default = run_poisson_psf_deblending(
            data, exposure=1.0, max_components=2, max_nfev=500
        )
        explicit = run_poisson_psf_deblending(
            data, exposure=1.0, max_components=2, max_nfev=500,
            proposal_policy="top_score",
        )
        self.assertEqual(default["selected_source_count"], explicit["selected_source_count"])
        self.assertEqual(default["candidates"], explicit["candidates"])
        self.assertEqual(default["poisson_bic"], explicit["poisson_bic"])

    def test_topk_policy_records_ranked_pool_and_bic_choice(self):
        result = run_poisson_psf_deblending(
            self._observation(), exposure=1.0, max_components=2, max_nfev=500,
            proposal_policy="best_bic_top_k", proposal_top_k=5,
        )
        self.assertEqual(result["proposal_policy"], "best_bic_top_k")
        self.assertTrue(
            result["candidate_trials"],
            "the test fixture must exercise a proposal step",
        )
        trial = result["candidate_trials"][0]
        self.assertGreaterEqual(len(trial["proposal_pool"]), 2)
        self.assertLessEqual(len(trial["proposal_pool"]), 5)
        self.assertGreaterEqual(trial["selected_proposal_rank"], 1)
        self.assertLessEqual(trial["selected_proposal_rank"], len(trial["proposal_pool"]))
        self.assertEqual(
            trial["proposal_candidates_evaluated"],
            len(trial["proposal_pool"]),
        )
        self.assertEqual(
            len(trial["proposal_fit_diagnostics"]),
            len(trial["proposal_pool"]),
        )
        self.assertTrue(all(
            "poisson_bic" in item and "poisson_deviance" in item
            for item in trial["proposal_fit_diagnostics"]
        ))
        self.assertAlmostEqual(
            trial["bic_improvement"],
            trial["bic_before"] - trial["bic_after"],
        )

    def test_invalid_policy_and_top_k_rejected(self):
        with self.assertRaises(ValueError):
            run_poisson_psf_deblending(
                self._observation(), exposure=1.0, proposal_policy="oracle"
            )
        with self.assertRaises(ValueError):
            run_poisson_psf_deblending(
                self._observation(), exposure=1.0,
                proposal_policy="best_bic_top_k", proposal_top_k=0,
            )


if __name__ == "__main__":
    unittest.main()
