"""Regression tests for the research manifest verifier.

Tests avoid importing or executing the verifier as a script and mock Git so
that no local repository or GPG configuration is required.
"""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import verify_research


class VerifyResearchTests(unittest.TestCase):
    def test_file_is_plain_parseable_python(self):
        path = Path(verify_research.__file__)
        source = path.read_text(encoding="utf-8")
        self.assertFalse(source.lstrip().startswith("```"))
        compile(source, str(path), "exec")

    def test_manifest_validation_returns_boolean_and_checks(self):
        valid, checks = verify_research.validate_manifest_integrity(
            verify_research.RESEARCH_MANIFEST
        )
        self.assertIs(valid, True)
        self.assertTrue(all(checks.values()))

    def test_manifest_validation_rejects_malformed_fields(self):
        valid, checks = verify_research.validate_manifest_integrity({
            "verification_target": "not a measurement",
            "commit_hash": "not-a-hash",
            "dedication": [],
        })
        self.assertIs(valid, False)
        self.assertFalse(checks["verification_target_has_expected_format"])
        self.assertFalse(checks["commit_reference_looks_like_hex"])
        self.assertFalse(checks["dedication_is_non_empty_list"])

    def test_abbreviated_hash_is_not_accepted_for_signature_verification(self):
        with patch("verify_research.subprocess.run") as run:
            result = verify_research.verify_gpg_signature("d0ecc8f")
        self.assertEqual(result["status"], "INVALID_INPUT")
        run.assert_not_called()

    def test_full_hash_uses_git_verify_commit(self):
        full_hash = "a" * 40
        with patch("verify_research.subprocess.run") as run:
            run.return_value.returncode = 0
            result = verify_research.verify_gpg_signature(full_hash)
        self.assertEqual(result["status"], "VERIFIED")
        run.assert_called_once_with(
            ["git", "verify-commit", full_hash],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_failed_signature_does_not_claim_verification(self):
        with patch("verify_research.subprocess.run") as run:
            run.return_value.returncode = 1
            result = verify_research.verify_gpg_signature("b" * 40)
        self.assertEqual(result["status"], "FAILED")

    def test_report_does_not_include_environment_secret_values(self):
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "report.json"
            with patch.dict(os.environ, {
                "CLOUD9_GPG_KEY_ID": "TEST-SECRET-KEY-ID",
                "CLOUD9_SIGNATORY": "secret@example.invalid",
            }), patch("verify_research.subprocess.run") as run:
                run.return_value.returncode = 1
                report = verify_research.generate_integrity_report(report_path)
            serialized = report_path.read_text(encoding="utf-8")
        self.assertNotIn("TEST-SECRET-KEY-ID", serialized)
        self.assertNotIn("secret@example.invalid", serialized)
        self.assertTrue(report["verification_configuration"]["gpg_key_id_configured"])
        self.assertEqual(json.loads(serialized)["manifest_status"], "STRUCTURALLY_VALID")


if __name__ == "__main__":
    unittest.main()
