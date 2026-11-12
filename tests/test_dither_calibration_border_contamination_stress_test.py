"""Tests for the calibration-border contamination stress test."""
import unittest

from scripts.run_dither_blind_background_estimation_validation import trial
from scripts.run_dither_calibration_border_contamination_stress_test import (
    CONTAMINATION_FRACTIONS,
    CONTAMINATION_RATE,
    GRADIENT_AMPLITUDE,
    SEEDS,
)


class CalibrationBorderContaminationTests(unittest.TestCase):
    def test_locked_stress_design(self):
        self.assertEqual(len(SEEDS), 30)
        self.assertEqual(SEEDS[0], 2026111500)
        self.assertEqual(SEEDS[-1], 2026111529)
        self.assertEqual(CONTAMINATION_FRACTIONS, (0.0, 0.05, 0.15))
        self.assertEqual(GRADIENT_AMPLITUDE, 0.25)
        self.assertEqual(CONTAMINATION_RATE, 1.0)

    def test_contamination_is_deterministic_and_shared_across_arms(self):
        first = trial(SEEDS[0], GRADIENT_AMPLITUDE, 0.15, CONTAMINATION_RATE)
        second = trial(SEEDS[0], GRADIENT_AMPLITUDE, 0.15, CONTAMINATION_RATE)
        self.assertEqual(first, second)
        counts = {
            values["calibration_contaminated_pixel_count"]
            for values in first.values()
        }
        self.assertEqual(len(counts), 1)
        self.assertGreater(next(iter(counts)), 0)

    def test_clean_condition_has_no_contaminated_border_pixels(self):
        result = trial(SEEDS[0], GRADIENT_AMPLITUDE, 0.0, CONTAMINATION_RATE)
        self.assertTrue(all(
            values["calibration_contaminated_pixel_count"] == 0
            for values in result.values()
        ))


if __name__ == "__main__":
    unittest.main()
