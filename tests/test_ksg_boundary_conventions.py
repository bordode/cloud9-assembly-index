"""Tests for the paired KSG boundary-convention audit."""
import importlib.util
import unittest
from pathlib import Path

import numpy as np

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "audit_ksg_boundary_conventions.py"
SPEC = importlib.util.spec_from_file_location("ksg_boundary_audit", MODULE_PATH)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class KSGBoundaryConventionTests(unittest.TestCase):
    def test_strict_counts_exclude_points_exactly_on_radius(self):
        values = np.array([0.0, 1.0, -1.0])
        radii = np.array([1.0, 1.0, 1.0])
        counts = audit.strict_marginal_counts(values, radii)
        self.assertEqual(counts.tolist(), [0, 0, 0])

    def test_zero_radius_requires_explicit_tie_policy(self):
        with self.assertRaises(ValueError):
            audit.strict_marginal_counts(np.array([0.0, 0.0]), np.array([0.0, 0.0]))

    def test_strict_counts_include_points_inside_radius(self):
        values = np.array([0.0, 0.5, -0.5, 2.0])
        radii = np.ones(4)
        counts = audit.strict_marginal_counts(values, radii)
        self.assertEqual(counts.tolist(), [2, 1, 1, 0])

    def test_strict_estimator_is_finite_and_reproducible(self):
        rng1 = np.random.default_rng(2026)
        rng2 = np.random.default_rng(2026)
        x1, y1 = audit.draw_pair(128, 0.5, rng1)
        x2, y2 = audit.draw_pair(128, 0.5, rng2)
        first = audit.ksg_mi_2d_strict(x1, y1, k=3)
        second = audit.ksg_mi_2d_strict(x2, y2, k=3)
        self.assertTrue(np.isfinite(first))
        self.assertAlmostEqual(first, second)

    def test_comparison_schema_and_reproducibility(self):
        first = audit.run_comparison([64], [2], [0.0, 0.5], 5, 123)
        second = audit.run_comparison([64], [2], [0.0, 0.5], 5, 123)
        self.assertEqual(first, second)
        self.assertEqual(len(first["results"]), 2)
        row = first["results"][0]
        for key in (
            "legacy_inclusive_bias_bits", "strict_bias_bits",
            "paired_strict_minus_legacy_mean_bits",
        ):
            self.assertIn(key, row)


if __name__ == "__main__":
    unittest.main()
