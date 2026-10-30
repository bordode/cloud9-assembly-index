#!/usr/bin/env python3
"""Cloud-9 manifest structure checks and optional Git commit-signature verification.

This tool checks metadata shape and, only when explicitly supplied, asks Git to
verify a commit signature. It does not validate scientific claims, prove the
provenance of research data, or independently establish signer identity.
"""
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# This manifest describes the verifier's scope, not a scientific result.
# Historical +0.5229 AU language was withdrawn in ETHICS.md; 7.83 Hz remains
# a conceptual reference only. Neither belongs in a cryptographic target list.
RESEARCH_MANIFEST = {
    "manifest_scope": "software_integrity_only",
    "scientific_claims_status": "not_assessed",
    "dedication": ["Niki", "Nikolaos", "Apostolos"],
}


def get_sensitive_config():
    """Read optional settings; these values do not pin or authenticate a signer."""
    return {
        "gpg_key_id": os.getenv("CLOUD9_GPG_KEY_ID", ""),
        "signatory": os.getenv("CLOUD9_SIGNATORY", ""),
    }


def verify_gpg_signature(commit_hash: str) -> dict:
    """Ask Git to verify a full commit hash under the current local trust setup."""
    if not isinstance(commit_hash, str) or not re.fullmatch(
        r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", commit_hash
    ):
        return {
            "status": "INVALID_INPUT",
            "commit": commit_hash if isinstance(commit_hash, str) else None,
            "message": "Provide a full 40- or 64-character hexadecimal commit hash.",
        }

    try:
        result = subprocess.run(
            ["git", "verify-commit", commit_hash],
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
    except FileNotFoundError:
        return {
            "status": "UNAVAILABLE",
            "commit": commit_hash,
            "message": "Git executable was not found.",
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "UNAVAILABLE",
            "commit": commit_hash,
            "message": "Git signature verification exceeded the time limit.",
        }
    except OSError:
        return {
            "status": "UNAVAILABLE",
            "commit": commit_hash,
            "message": "Git signature verification could not be started.",
        }

    if result.returncode == 0:
        return {
            "status": "VERIFIED",
            "commit": commit_hash,
            "message": (
                "Git accepted the commit signature under the current local "
                "Git/GPG trust configuration. This does not establish signer "
                "authorization or research-data provenance."
            ),
        }

    return {
        "status": "FAILED",
        "commit": commit_hash,
        "message": "Git could not verify the commit signature.",
    }


def validate_manifest_structure(manifest: dict) -> tuple[bool, dict]:
    """Check metadata shape and allowed scope labels only; no scientific validation."""
    checks = {"manifest_is_mapping": isinstance(manifest, dict)}
    if not checks["manifest_is_mapping"]:
        checks.update({
            "scope_is_software_integrity_only": False,
            "scientific_claims_are_not_assessed": False,
            "dedication_is_non_empty_list": False,
            "contains_no_scientific_verification_target": False,
        })
        return False, checks

    dedication = manifest.get("dedication", [])
    checks.update({
        "scope_is_software_integrity_only": (
            manifest.get("manifest_scope") == "software_integrity_only"
        ),
        "scientific_claims_are_not_assessed": (
            manifest.get("scientific_claims_status") == "not_assessed"
        ),
        "dedication_is_non_empty_list": bool(
            isinstance(dedication, list)
            and dedication
            and all(isinstance(item, str) and item.strip() for item in dedication)
        ),
        "contains_no_scientific_verification_target": not any(
            key in manifest
            for key in ("verification_target", "resonance_vertex", "assembly_score")
        ),
    })
    return all(checks.values()), checks


def _default_report_path() -> Path:
    """Return an unsuffixed timestamped path; exclusive creation handles collisions."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    return Path(f"verification_report_{timestamp}.json")


def generate_integrity_report(output_path=None, commit_hash=None):
    """Write a structural report and optionally verify an explicitly supplied commit.

    Default report paths are created without overwriting prior reports. An
    explicitly supplied output_path is intentionally overwritten if it exists.
    Signature verification is NOT attempted unless commit_hash is supplied.
    """
    manifest_ok, checks = validate_manifest_structure(RESEARCH_MANIFEST)
    sensitive = get_sensitive_config()
    if commit_hash is None:
        signature = {
            "status": "NOT_ATTEMPTED",
            "commit": None,
            "message": (
                "No commit was supplied. The manifest intentionally does not "
                "pin a commit as scientific evidence."
            ),
        }
    else:
        signature = verify_gpg_signature(commit_hash)

    report = {
        "verification_time": datetime.now(timezone.utc).isoformat(),
        "manifest": RESEARCH_MANIFEST,
        "manifest_status": "STRUCTURALLY_VALID" if manifest_ok else "STRUCTURALLY_INVALID",
        "component_checks": checks,
        "signature_verification": signature,
        "scope_note": (
            "Structural checks do not validate scientific claims or research-data "
            "provenance. Git signature verification depends on local trust "
            "configuration and does not independently establish signer identity "
            "or authorization."
        ),
        "verification_configuration": {
            "gpg_key_id_configured_informational_only": bool(sensitive["gpg_key_id"]),
            "signatory_configured_informational_only": bool(sensitive["signatory"]),
            "identity_pinned_or_authenticated": False,
        },
    }

    if output_path is None:
        base_path = _default_report_path()
        suffix = 0
        while True:
            path = (
                base_path
                if suffix == 0
                else base_path.with_name(f"{base_path.stem}_{suffix}{base_path.suffix}")
            )
            try:
                with path.open("x", encoding="utf-8") as stream:
                    stream.write(json.dumps(report, indent=2) + "\n")
                break
            except FileExistsError:
                suffix += 1
    else:
        path = Path(output_path)
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Cloud-9 Research Manifest Check")
    print(f"Manifest status: {report['manifest_status']}")
    print(f"Commit signature: {signature['status']}")
    print(f"Report saved: {path}")
    return report


if __name__ == "__main__":
    generate_integrity_report()
