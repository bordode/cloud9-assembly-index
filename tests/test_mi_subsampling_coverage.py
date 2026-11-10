"""Tests for independent-dataset subsampling interval-coverage screening."""
import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts" / "run_mi_subsampling_coverage.py"
)
SPEC = importlib.util.spec_from_file_location("mi_subsampling_coverage", MODULE_PATH)
coverage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(coverage)


class SubsamplingCoverageTests(unittest.TestCase):
    def test_small_screen_is_reproducible_and_separates_outer_trials(self):
        args = ([64], [2], [0.0], ["monotone_nonlinear"],
                [0.7], 3, 20, 20261113)
        first = coverage.run_coverage(*args)
        second = coverage.run_coverage(*args)
        self.assertEqual(first, second)
        self.assertEqual(len(first["results"]), 1)
        row = first["results"][0]
        self.assertEqual(row["outer_replicates_requested"], 3)
        self.assertEqual(row["subsamples_per_outer_dataset"], 20)
        self.assertEqual(row["raw_strict_primary"]["90"]["valid_outer_datasets"], 3)
        self.assertIn("coverage_monte_carlo_se",
                      row["raw_strict_primary"]["95"])
        self.assertEqual(row["true_mi_bits"], 0.0)

    def test_subsample_must_exceed_k_plus_one(self):
        with self.assertRaises(ValueError):
            coverage.run_coverage(
                [16], [5], [0.0], ["monotone_nonlinear"],
                [0.5], 2, 20, 1
            )

    def test_too_few_subsamples_rejected(self):
        with self.assertRaises(ValueError):
            coverage.run_coverage(
                [64], [2], [0.0], ["monotone_nonlinear"],
                [0.7], 2, 10, 1
            )


if __name__ == "__main__":
    unittest.main()
