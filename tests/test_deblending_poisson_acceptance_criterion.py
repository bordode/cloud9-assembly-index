"""Tests for explicit AIC/BIC acceptance criteria."""
import unittest
import numpy as np

from research.sandbox.poisson_psf_deblending import run_poisson_psf_deblending
from research.sandbox.pixel_response_reproduction import pixel_integrated_gaussian


class AcceptanceCriterionTests(unittest.TestCase):
    def _observation(self):
        rate = pixel_integrated_gaussian(
            0.25, -0.15, 120.0, 1.0, 1.3, size=11
        )
        return np.random.default_rng(20262061).poisson(rate).astype(float)

    def test_default_is_bitwise_equivalent_to_explicit_bic(self):
        obs = self._observation()
        default = run_poisson_psf_deblending(
            obs, exposure=1.0, max_components=3, max_nfev=500,
            proposal_policy="best_bic_top_k", proposal_top_k=5,
        )
        explicit = run_poisson_psf_deblending(
            obs, exposure=1.0, max_components=3, max_nfev=500,
            proposal_policy="best_bic_top_k", proposal_top_k=5,
            acceptance_criterion="bic",
        )
        self.assertEqual(default["candidates"], explicit["candidates"])
        self.assertEqual(default["poisson_bic"], explicit["poisson_bic"])
        self.assertEqual(default["candidate_trials"], explicit["candidate_trials"])

    def test_aic_and_bic_are_both_reported(self):
        result = run_poisson_psf_deblending(
            self._observation(), exposure=1.0, max_components=3,
            max_nfev=500, proposal_policy="adaptive_top5_to10",
            acceptance_criterion="aic",
        )
        self.assertEqual(result["acceptance_criterion"], "aic")
        self.assertIn("poisson_aic", result)
        self.assertIn("poisson_bic", result)
        for step in result["candidate_trials"]:
            self.assertEqual(step["acceptance_criterion"], "aic")
            self.assertIn("criterion_before", step)
            self.assertIn("criterion_after", step)
            for diagnostic in step["proposal_fit_diagnostics"]:
                self.assertIn("poisson_aic", diagnostic)
                self.assertIn("poisson_bic", diagnostic)

    def test_invalid_acceptance_criterion_is_rejected(self):
        with self.assertRaises(ValueError):
            run_poisson_psf_deblending(
                self._observation(), exposure=1.0,
                acceptance_criterion="waic",
            )


if __name__ == "__main__":
    unittest.main()
