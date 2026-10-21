import tempfile
import unittest
from pathlib import Path

from scripts.check_docs_consistency import CHECKS, check_documentation


class DocumentationConsistencyTests(unittest.TestCase):
    def test_current_selected_documents_meet_wording_rules(self):
        self.assertEqual(check_documentation(), [])

    def test_check_detects_missing_caveat_and_legacy_overclaim(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for relative_path, rules in CHECKS.items():
                path = root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("neutral text", encoding="utf-8")
            readme = root / "README.md"
            readme.write_text(
                "throttles autonomous actions for flagged agents",
                encoding="utf-8",
            )
            errors = check_documentation(root)
            self.assertTrue(any("legacy overclaim phrase remains" in e for e in errors))
            self.assertTrue(any("missing required caveat" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
