#!/usr/bin/env python3
"""Cloud-9 research manifest checks and optional Git commit-signature verification.

This script reports structural checks separately from cryptographic signature
verification. It does not validate the scientific claims in the manifest.
A successful `git verify-commit` depends on the local Git/GPG trust setup and
does not, by itself, establish that a signer is an authorized researcher.
"""
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Public research metadata. The abbreviated commit reference is a pointer only;
# it is not sufficient input for cryptographic signature verification.
RESEARCH_MANIFEST = {
    "verification_target": "0.5229 AU",
    "commit_hash": "d0ecc8f",
    "resonance_vertex": "7.83 kHz",
    "dedication": ["Niki", "Nikolaos", "Apostolos"],
}


def get_sensitive_config():
    """Read optional verification settings without exposing them in reports."""
    return {
        "gpg_key_id": os.getenv("CLOUD9_GPG_KEY_ID", ""),
        "signatory": os.getenv("CLOUD9_SIGNATORY", ""),
    }


def verify_gpg_signature(commit_hash: str) -> dict:
    """Ask Git to verify a full commit hash; never treat an abbreviation as proof."""
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
        # Avoid copying OS exception details into a report; they may reveal paths.
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
                "Git/GPG trust configuration."
            ),
        }

    return {
        "status": "FAILED",
        "commit": commit_hash,
        "message": "Git could not verify the commit signature.",
    }


def validate_manifest_integrity(manifest: dict) -> tuple[bool, dict]:
    """Check manifest shape only; this does not establish scientific validity."""
    checks = {"manifest_is_mapping": isinstance(manifest, dict)}
    if not checks["manifest_is_mapping"]:
        checks.update({
            "verification_target_has_expected_format": False,
            "commit_reference_looks_like_hex": False,
            "dedication_is_non_empty_list": False,
        })
        return False, checks

    target = manifest.get("verification_target", "")
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s+AU\s*", target) if isinstance(target, str) else None
    commit_ref = manifest.get("commit_hash", "")
    dedication = manifest.get("dedication", [])

    checks.update({
        "verification_target_has_expected_format": bool(match),
        "commit_reference_looks_like_hex": bool(
            isinstance(commit_ref, str)
            and re.fullmatch(r"[0-9a-fA-F]{7,64}", commit_ref)
        ),
        "dedication_is_non_empty_list": bool(
            isinstance(dedication, list)
            and dedication
            and all(isinstance(item, str) and item.strip() for item in dedication)
        ),
    })
    return all(checks.values()), checks


def generate_integrity_report(output_path="verification_report.json"):
    """Write a structural-check report without embedding environment secrets."""
    manifest_ok, checks = validate_manifest_integrity(RESEARCH_MANIFEST)
    sensitive = get_sensitive_config()
    signature = verify_gpg_signature(RESEARCH_MANIFEST["commit_hash"])

    report = {
        "verification_time": datetime.now(timezone.utc).isoformat(),
        "manifest": RESEARCH_MANIFEST,
        "manifest_status": "STRUCTURALLY_VALID" if manifest_ok else "STRUCTURALLY_INVALID",
        "component_checks": checks,
        "signature_verification": signature,
        "scope_note": (
            "Structural checks and Git signature verification do not validate "
            "the scientific claims or independently establish signer identity."
        ),
        "verification_configuration": {
            "gpg_key_id_configured": bool(sensitive["gpg_key_id"]),
            "signatory_configured": bool(sensitive["signatory"]),
        },
    }

    path = Path(output_path)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Cloud-9 Research Manifest Check")
    print(f"Manifest status: {report['manifest_status']}")
    print(f"Commit signature: {signature['status']}")
    print(f"Report saved: {path}")
    return report


if __name__ == "__main__":
    generate_integrity_report()
