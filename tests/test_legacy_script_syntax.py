"""Syntax regression checks for legacy Python scripts.

These checks compile source without importing modules or executing script code.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LegacyScriptSyntaxTests(unittest.TestCase):
    def test_cloud9_full_is_parseable_python(self):
        path = ROOT / "cloud9_full.py"
        source = path.read_text(encoding="utf-8")
        try:
            compile(source, str(path), "exec")
        except SyntaxError as exc:
            self.fail(f"{path.name} has invalid Python syntax: {exc}")


if __name__ == "__main__":
    unittest.main()
