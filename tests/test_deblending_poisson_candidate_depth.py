"""Tests for the paired Poisson candidate-depth ablation."""
import unittest

from research.sandbox.deblending_poisson_candidate_depth import (
    DEPTHS, run_candidate_depth_ablation,
)


class CandidateDepthTests(unittest.TestCase):
    def test_depths_are_predeclared_and_ordered(self):
        self.assertEqual(DEPTHS, (5, 10, 25, 50))

    def test_small_paired_ablation_uses_same_seed_and_reports_cost(self):
        result = run_candidate_depth_ablation(
            trials_per_condition=1,
            seed_start=20262099,
            geometry_scales=(1.0,),
            exposures=(1.0,),
        )
        self.assertEqual(result["trial_count"], 1)
        self.assertEqual(result["records"][0]["seed"], 20262099)
        self.assertEqual(set(result["overall"]), {"5", "10", "25", "50"})
        self.assertEqual(set(result["paired_vs_top5"]), {"10", "25", "50"})
        for depth in ("5", "10", "25", "50"):
            row = result["records"][0]["depths"][depth]
            self.assertIn("matched_truth_count", row["score"])
            self.assertGreaterEqual(row["proposal_fits_evaluated"], 0)
            self.assertGreaterEqual(
                row["initial_optimizer_function_evaluations"], 0
            )
            self.assertGreaterEqual(
                row["optimizer_function_evaluations"],
                row["initial_optimizer_function_evaluations"],
            )
        self.assertEqual(
            result["fixed_detector_rules"][0],
            "Same Poisson count observation for every depth within a trial.",
        )


if __name__ == "__main__":
    unittest.main()
