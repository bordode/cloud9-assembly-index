"""Tests for independent-dataset subsampling interval-coverage screening."""
import importlib.util
import unittest
from pathlib import Path

import numpy as np

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_mi_subsampling_coverage.py"
SPEC = importlib.util.spec_from_file_location("mi_subsampling_coverage", MODULE_PATH)
coverage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(coverage)


class SubsamplingCoverageTests(unittest.TestCase):
    def test_small_screen_is_reproducible_and_preserves_outer_diagnostics(self):
        args = ([64], [2], [0.0], ["monotone_nonlinear"], [0.7], 3, 20, 20261113)
        first = coverage.run_coverage(*args)
        second = coverage.run_coverage(*args)
        self.assertEqual(first, second)
        self.assertEqual(len(first["results"]), 1)
        row = first["results"][0]
        self.assertEqual(row["outer_replicates_requested"], 3)
        self.assertEqual(row["subsamples_per_outer_dataset"], 20)
        self.assertEqual(row["valid_outer_datasets"], 3)
        self.assertEqual(row["raw_strict_primary"]["90"]["valid_outer_datasets"], 3)
        self.assertIn("coverage_monte_carlo_se_plugin", row["raw_strict_primary"]["95"])
        wilson = row["raw_strict_primary"]["95"]["coverage_wilson_95pct_interval"]
        self.assertLess(wilson[0], wilson[1])
        self.assertGreaterEqual(wilson[0], 0.0)
        self.assertLessEqual(wilson[1], 1.0)
        self.assertEqual(row["true_mi_bits"], 0.0)
        records = row["outer_dataset_diagnostics"]
        self.assertEqual([r["outer_replicate_index"] for r in records], [0, 1, 2])
        self.assertEqual(len({r["outer_dataset_seed"] for r in records}), 3)
        self.assertTrue(all(r["status"] == "valid" for r in records))
        self.assertIn("90", records[0]["raw_strict_intervals_bits"])
        self.assertIn("95", records[0]["raw_strict_coverage"])

    def test_quantile_resolution_is_reported_and_coarse_at_screening_b(self):
        diag = coverage._quantile_diagnostics(20, (0.90, 0.95))
        self.assertAlmostEqual(diag["90"]["expected_subsets_per_tail"], 1.0)
        self.assertAlmostEqual(diag["95"]["expected_subsets_per_tail"], 0.5)
        self.assertAlmostEqual(
            diag["95"]["lower_linear_order_statistic_position_zero_based"], 0.475
        )
        self.assertEqual(coverage.QUANTILE_METHOD, "linear")

    def test_interval_quantiles_are_finite_ordered_and_deterministic(self):
        roots = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
        a = coverage._intervals(0.5, roots, 100, (0.90, 0.95))
        b = coverage._intervals(0.5, roots, 100, (0.90, 0.95))
        self.assertEqual(a, b)
        for lo, hi in a.values():
            self.assertTrue(np.isfinite(lo) and np.isfinite(hi))
            self.assertLessEqual(lo, hi)

    def test_wilson_interval_remains_informative_at_extremes(self):
        self.assertEqual(coverage._wilson_interval(0, 10)[0], 0.0)
        self.assertEqual(coverage._wilson_interval(10, 10)[1], 1.0)
        self.assertGreater(coverage._wilson_interval(0, 10)[1], 0.0)
        self.assertLess(coverage._wilson_interval(10, 10)[0], 1.0)
        self.assertIsNone(coverage._wilson_interval(0, 0))

    def test_failed_dataset_is_not_included_in_valid_estimate_denominator(self):
        # Patch the estimator for this test only: one outer dataset gets a non-finite subset.
        original = coverage.ksg_mi_2d_strict
        calls = {"count": 0}

        def injected(x, y, k):
            calls["count"] += 1
            if calls["count"] == 2:
                return float("nan")
            return original(x, y, k)

        coverage.ksg_mi_2d_strict = injected
        try:
            result = coverage.run_coverage(
                [64], [2], [0.0], ["monotone_nonlinear"], [0.7], 2, 20, 20261113
            )
        finally:
            coverage.ksg_mi_2d_strict = original
        row = result["results"][0]
        self.assertEqual(row["valid_outer_datasets"], 1)
        self.assertEqual(row["interval_construction_failures"], 1)
        self.assertEqual(len(row["outer_dataset_diagnostics"]), 2)
        self.assertEqual(row["outer_dataset_diagnostics"][0]["status"], "failed")
        self.assertEqual(row["raw_strict_primary"]["90"]["valid_outer_datasets"], 1)

    def test_invalid_inputs_rejected(self):
        with self.assertRaises(ValueError):
            coverage.run_coverage([], [2], [0.0], ["monotone_nonlinear"], [0.7], 2, 20, 1)
        with self.assertRaises(ValueError):
            coverage.run_coverage([64], [2], [1.0], ["monotone_nonlinear"], [0.7], 2, 20, 1)
        with self.assertRaises(ValueError):
            coverage.run_coverage([64], [2], [0.0], ["bad_family"], [0.7], 2, 20, 1)

    def test_subsample_must_exceed_k_plus_one(self):
        with self.assertRaises(ValueError):
            coverage.run_coverage([16], [5], [0.0], ["monotone_nonlinear"], [0.5], 2, 20, 1)

    def test_too_few_subsamples_rejected(self):
        with self.assertRaises(ValueError):
            coverage.run_coverage([64], [2], [0.0], ["monotone_nonlinear"], [0.7], 2, 10, 1)


if __name__ == "__main__":
    unittest.main()
