"""Regression tests for the research manifest verifier.

Tests avoid importing or executing the verifier as a script and mock Git so
that no local repository or GPG configuration is required.
"""
import json
import os
import subprocess
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

    def test_manifest_structure_returns_boolean_and_checks(self):
        valid, checks = verify_research.validate_manifest_structure(
            verify_research.RESEARCH_MANIFEST
        )
        self.assertIs(valid, True)
        self.assertIs(checks["manifest_is_mapping"], True)
        self.assertTrue(all(checks.values()))

    def test_structural_format_does_not_establish_scientific_validity(self):
        manifest = {
            "verification_target": "0 AU",
            "commit_hash": "a" * 40,
            "dedication": ["Example"],
        }
        valid, checks = verify_research.validate_manifest_structure(manifest)
        self.assertIs(valid, True)
        self.assertTrue(all(checks.values()))
        # The function checks format only; it makes no scientific-validity claim.

    def test_manifest_structure_rejects_non_mapping_inputs(self):
        for manifest in (None, [], "not a manifest"):
            with self.subTest(manifest=manifest):
                valid, checks = verify_research.validate_manifest_structure(manifest)
                self.assertIs(valid, False)
                self.assertIs(checks["manifest_is_mapping"], False)
                self.assertFalse(checks["verification_target_has_expected_format"])
                self.assertFalse(checks["commit_reference_looks_like_hex"])
                self.assertFalse(checks["dedication_is_non_empty_list"])

    def test_manifest_structure_rejects_malformed_fields(self):
        valid, checks = verify_research.validate_manifest_structure({
            "verification_target": "not a measurement",
            "commit_hash": "not-a-hash",
            "dedication": [],
        })
        self.assertIs(valid, False)
        self.assertFalse(checks["verification_target_has_expected_format"])
        self.assertFalse(checks["commit_reference_looks_like_hex"])
        self.assertFalse(checks["dedication_is_non_empty_list"])

    def test_abbreviated_hash_is_not_accepted_for_direct_signature_verification(self):
        with patch("verify_research.subprocess.run") as run:
            result = verify_research.verify_gpg_signature("d0ecc8f")
        self.assertEqual(result["status"], "INVALID_INPUT")
        run.assert_not_called()

    def test_full_40_character_hash_uses_git_verify_commit_with_timeout(self):
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
            timeout=15,
        )

    def test_full_64_character_hash_is_accepted(self):
        full_hash = "b" * 64
        with patch("verify_research.subprocess.run") as run:
            run.return_value.returncode = 0
            result = verify_research.verify_gpg_signature(full_hash)
        self.assertEqual(result["status"], "VERIFIED")
        run.assert_called_once_with(
            ["git", "verify-commit", full_hash],
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )

    def test_failed_signature_does_not_claim_verification(self):
        with patch("verify_research.subprocess.run") as run:
            run.return_value.returncode = 1
            result = verify_research.verify_gpg_signature("c" * 40)
        self.assertEqual(result["status"], "FAILED")

    def test_missing_git_is_reported_as_unavailable(self):
        with patch(
            "verify_research.subprocess.run",
            side_effect=FileNotFoundError("private/path/detail"),
        ):
            result = verify_research.verify_gpg_signature("d" * 40)
        self.assertEqual(result["status"], "UNAVAILABLE")
        self.assertNotIn("private/path/detail", result["message"])

    def test_verifier_timeout_is_reported_as_unavailable(self):
        with patch(
            "verify_research.subprocess.run",
            side_effect=subprocess.TimeoutExpired("git", 15),
        ):
            result = verify_research.verify_gpg_signature("e" * 40)
        self.assertEqual(result["status"], "UNAVAILABLE")
        self.assertIn("time limit", result["message"])

    def test_other_os_launch_error_is_reported_without_path_details(self):
        with patch(
            "verify_research.subprocess.run",
            side_effect=PermissionError("private/path/detail"),
        ):
            result = verify_research.verify_gpg_signature("f" * 40)
        self.assertEqual(result["status"], "UNAVAILABLE")
        self.assertNotIn("private/path/detail", result["message"])

    def test_report_verifies_the_full_manifest_commit_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "report.json"
            with patch("verify_research.subprocess.run") as run:
                run.return_value.returncode = 0
                report = verify_research.generate_integrity_report(report_path)
            run.assert_called_once_with(
                ["git", "verify-commit", "d0ecc8f991a74a4e6d73f618e3672fd8e7164bbe"],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
            )
            serialized = report_path.read_text(encoding="utf-8")
        self.assertEqual(report["signature_verification"]["status"], "VERIFIED")
        self.assertEqual(
            report["signature_verification"]["commit"],
            "d0ecc8f991a74a4e6d73f618e3672fd8e7164bbe",
        )
        self.assertEqual(json.loads(serialized)["manifest_status"], "STRUCTURALLY_VALID")

    def test_report_does_not_include_environment_secret_values(self):
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "report.json"
            with patch.dict(os.environ, {
                "CLOUD9_GPG_KEY_ID": "TEST-SECRET-KEY-ID",
                "CLOUD9_SIGNATORY": "secret@example.invalid",
            }), patch("verify_research.subprocess.run") as run:
                run.return_value.returncode = 0
                report = verify_research.generate_integrity_report(report_path)
                run.assert_called_once()
            serialized = report_path.read_text(encoding="utf-8")
        self.assertNotIn("TEST-SECRET-KEY-ID", serialized)
        self.assertNotIn("secret@example.invalid", serialized)
        config = report["verification_configuration"]
        self.assertTrue(config["gpg_key_id_configured_informational_only"])
        self.assertTrue(config["signatory_configured_informational_only"])
        self.assertIs(config["identity_pinned_or_authenticated"], False)
        self.assertEqual(json.loads(serialized)["manifest_status"], "STRUCTURALLY_VALID")

    def test_explicit_output_path_overwrites_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "report.json"
            report_path.write_text("previous content", encoding="utf-8")
            with patch("verify_research.subprocess.run") as run:
                run.return_value.returncode = 0
                report = verify_research.generate_integrity_report(report_path)
            self.assertEqual(report["manifest_status"], "STRUCTURALLY_VALID")
            self.assertNotEqual(report_path.read_text(encoding="utf-8"), "previous content")
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["manifest_status"],
                             "STRUCTURALLY_VALID")

    def test_default_report_collision_fallback_uses_incrementing_suffixes(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory) / "verification_report_collision.json"
            first = Path(directory) / "verification_report_collision_1.json"
            second = Path(directory) / "verification_report_collision_2.json"
            base.write_text("reserved", encoding="utf-8")
            first.write_text("reserved", encoding="utf-8")
            with patch("verify_research._default_report_path", return_value=base), \
                 patch("verify_research.subprocess.run") as run:
                run.return_value.returncode = 0
                verify_research.generate_integrity_report()
            self.assertEqual(base.read_text(encoding="utf-8"), "reserved")
            self.assertEqual(first.read_text(encoding="utf-8"), "reserved")
            self.assertTrue(second.exists())
            self.assertEqual(json.loads(second.read_text(encoding="utf-8"))["manifest_status"],
                             "STRUCTURALLY_VALID")

    def test_default_reports_do_not_overwrite_previous_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("verify_research.subprocess.run") as run:
                run.return_value.returncode = 0
                with patch("verify_research._default_report_path") as default_path:
                    first = Path(directory) / "verification_report_first.json"
                    second = Path(directory) / "verification_report_second.json"
                    default_path.side_effect = [first, second]
                    verify_research.generate_integrity_report()
                    verify_research.generate_integrity_report()
                self.assertEqual(run.call_count, 2)
            reports = sorted(Path(directory).glob("verification_report_*.json"))
            self.assertEqual(len(reports), 2)
            self.assertNotEqual(reports[0].read_text(), reports[1].read_text())


    def test_default_report_path_returns_unsuffixed_base(self):
        with patch("verify_research.datetime") as mocked_datetime:
            mocked_datetime.now.return_value.strftime.return_value = "20261030T150400_123456Z"
            with patch.object(Path, "exists", return_value=True) as exists:
                path = verify_research._default_report_path()
        self.assertEqual(path, Path("verification_report_20261030T150400_123456Z.json"))
        exists.assert_not_called()



if __name__ == "__main__":
    unittest.main()
