"""Tests for the factorial KSG radius/count-convention audit."""
import importlib.util
import unittest
from pathlib import Path

import numpy as np

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "audit_ksg_boundary_factorial.py"
SPEC = importlib.util.spec_from_file_location("ksg_boundary_factorial", MODULE_PATH)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class KSGBoundaryFactorialTests(unittest.TestCase):
    def test_inclusive_and_strict_counts_differ_at_boundary(self):
        values = np.array([0.0, 1.0, -1.0, 0.5])
        radii = np.ones(4)
        strict = audit.strict_marginal_counts(values, radii)
        inclusive = audit.inclusive_marginal_counts(values, radii)
        self.assertEqual(strict.tolist(), [1, 1, 1, 1])
        self.assertEqual(inclusive.tolist(), [3, 2, 2, 2])

    def test_four_factorial_variants_are_finite(self):
        rng = np.random.default_rng(22)
        x, y = audit.draw_pair(128, 0.5, rng)
        vals = [
            audit.ksg_mi_factorial(x, y, 3, offset, rule)
            for offset in (0.0, 1e-12)
            for rule in ("strict", "inclusive")
        ]
        self.assertEqual(len(vals), 4)
        self.assertTrue(np.all(np.isfinite(vals)))

    def test_small_factorial_grid_is_reproducible(self):
        args = ([64], [2], [0.0, 0.5], 5, 123, 1e-12)
        first = audit.run_factorial(*args)
        second = audit.run_factorial(*args)
        self.assertEqual(first, second)
        self.assertEqual(len(first["results"]), 2)
        row = first["results"][0]
        self.assertEqual(len(row["variants"]), 4)
        self.assertIn("radius_by_count_interaction", row["paired_factorial_effects_bits"])

    def test_invalid_offset_is_rejected(self):
        with self.assertRaises(ValueError):
            audit.run_factorial([64], [2], [0.0], 5, 1, 0.0)


if __name__ == "__main__":
    unittest.main()
