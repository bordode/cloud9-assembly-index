"""Tests for the pre-registered independent dither validation protocol."""
import unittest

from scripts.run_dither_background_validation import (
    BACKGROUND_RATES,
    DEVELOPMENT_SEEDS,
    ITERATIONS,
    VALIDATION_SEEDS,
    summarize,
)


class DitherBackgroundValidationProtocolTests(unittest.TestCase):
    def test_validation_seeds_are_fresh_and_disjoint(self):
        self.assertEqual(len(DEVELOPMENT_SEEDS), 30)
        self.assertEqual(len(VALIDATION_SEEDS), 30)
        self.assertTrue(set(DEVELOPMENT_SEEDS).isdisjoint(VALIDATION_SEEDS))

    def test_iteration_count_is_locked_before_validation(self):
        self.assertEqual(ITERATIONS, (2,))

    def test_background_grid_matches_development_protocol(self):
        self.assertEqual(BACKGROUND_RATES, (0.0, 0.1, 0.5, 1.0, 2.0))

    def test_summary_reports_mean_and_confidence_interval(self):
        result = summarize([1.0, 2.0, 3.0])
        self.assertEqual(result["n"], 3)
        self.assertEqual(result["mean"], 2.0)
        self.assertEqual(len(result["ci95_mean"]), 2)


if __name__ == "__main__":
    unittest.main()
