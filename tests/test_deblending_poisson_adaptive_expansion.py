"""Tests for conditional expansion of the Poisson proposal pool."""
import unittest
import numpy as np
from research.sandbox.poisson_psf_deblending import run_poisson_psf_deblending
from research.sandbox.pixel_response_reproduction import pixel_integrated_gaussian


class AdaptiveProposalExpansionTests(unittest.TestCase):
    def _observation(self):
        return np.random.default_rng(20261901).poisson(
            pixel_integrated_gaussian(0.25, -0.15, 120.0, 1.0, 1.3, size=11)
        ).astype(float)

    def test_adaptive_policy_records_conditional_expansion(self):
        result = run_poisson_psf_deblending(
            self._observation(), exposure=1.0, max_components=3,
            max_nfev=500, proposal_policy="adaptive_top5_to10",
        )
        self.assertEqual(result["proposal_policy"], "adaptive_top5_to10")
        self.assertIn("ranks 1-5", result["adaptive_expansion_policy"])
        self.assertTrue(result["candidate_trials"])
        for trial in result["candidate_trials"]:
            diagnostics = trial["proposal_fit_diagnostics"]
            ranks = trial["proposal_ranks_evaluated"]
            self.assertEqual(len(diagnostics), trial["proposal_candidates_evaluated"])
            self.assertEqual(len(ranks), len(diagnostics))
            if trial["adaptive_expansion_triggered"]:
                top_five = [row for row in diagnostics
                            if row["proposal_rank"] <= 5 and row["optimizer_success"]]
                self.assertFalse(any(row["poisson_bic"] < trial["bic_before"]
                                     for row in top_five))
                self.assertTrue(all(rank <= 10 for rank in ranks))
            else:
                self.assertTrue(all(rank <= 5 for rank in ranks))
                self.assertTrue(any(row["optimizer_success"]
                                    and row["poisson_bic"] < trial["bic_before"]
                                    for row in diagnostics))

    def test_adaptive_policy_requires_fixed_top_five_setting(self):
        with self.assertRaises(ValueError):
            run_poisson_psf_deblending(
                self._observation(), exposure=1.0,
                proposal_policy="adaptive_top5_to10", proposal_top_k=8,
            )


if __name__ == "__main__":
    unittest.main()
