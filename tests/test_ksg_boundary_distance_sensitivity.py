"""Tests for deterministic KSG boundary-distance sensitivity cases."""
import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "audit_ksg_boundary_distance_sensitivity.py"
SPEC = importlib.util.spec_from_file_location("ksg_boundary_distance_sensitivity", MODULE_PATH)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class KSGBoundaryDistanceSensitivityTests(unittest.TestCase):
    def test_exact_and_near_boundary_points_separate_conventions(self):
        result = audit.run_distance_audit(1.0, 1e-12)
        self.assertEqual(result["target_neighbour_counts"], {
            "uninflated_strict": 1,
            "uninflated_inclusive": 2,
            "inflated_strict": 3,
            "inflated_inclusive": 4,
        })

    def test_offset_must_be_representable_at_radius(self):
        with self.assertRaises(ValueError):
            audit.run_distance_audit(1.0, 1e-20)

    def test_output_is_deterministic(self):
        self.assertEqual(audit.run_distance_audit(), audit.run_distance_audit())


if __name__ == "__main__":
    unittest.main()
