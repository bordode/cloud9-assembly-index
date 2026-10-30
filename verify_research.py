#!/usr/bin/env python3
"""Cloud-9 research manifest checks and optional Git commit-signature verification.

This script reports manifest structure separately from cryptographic signature
verification. It does not validate scientific claims. A successful
`git verify-commit` depends on the local Git/GPG trust setup and does not,
by itself, establish that a signer is an authorized researcher.
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
    "commit_hash": "d0ecc8f991a74a4e6d73f618e3672fd8e7164bbe",
    "resonance_vertex": "7.83 kHz",
    "dedication": ["Niki", "Nikolaos", "Apostolos"],
}


def get_sensitive_config():
    """Read optional settings; these values do not pin or authenticate a signer."""
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


def validate_manifest_structure(manifest: dict) -> tuple[bool, dict]:
    """Check field shape and format only; this does not establish scientific validity."""
    checks = {"manifest_is_mapping": isinstance(manifest, dict)}
    if not checks["manifest_is_mapping"]:
        checks.update({
            "verification_target_has_expected_format": False,
            "commit_reference_looks_like_hex": False,
            "dedication_is_non_empty_list": False,
        })
        return False, checks

    target = manifest.get("verification_target", "")
    match = (
        re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s+AU\s*", target)
        if isinstance(target, str)
        else None
    )
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


def _default_report_path() -> Path:
    """Choose a fresh default report path; callers may still supply an explicit path."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    base = Path(f"verification_report_{timestamp}.json")
    candidate = base
    suffix = 1
    while candidate.exists():
        candidate = base.with_name(f"{base.stem}_{suffix}{base.suffix}")
        suffix += 1
    return candidate


def generate_integrity_report(output_path=None):
    """Write a structural report.

    Default paths are created without overwriting prior reports. An explicitly
    supplied output_path is intentionally overwritten if it already exists.
    """
    manifest_ok, checks = validate_manifest_structure(RESEARCH_MANIFEST)
    sensitive = get_sensitive_config()
    commit_hash = RESEARCH_MANIFEST.get("commit_hash", "")
    if isinstance(commit_hash, str) and re.fullmatch(
        r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", commit_hash
    ):
        signature = verify_gpg_signature(commit_hash)
    else:
        signature = {
            "status": "NOT_ATTEMPTED",
            "commit": commit_hash if isinstance(commit_hash, str) else None,
            "message": (
                "Signature verification was not attempted because the manifest "
                "does not supply a full 40- or 64-character hexadecimal commit hash."
            ),
        }

    report = {
        "verification_time": datetime.now(timezone.utc).isoformat(),
        "manifest": RESEARCH_MANIFEST,
        "manifest_status": "STRUCTURALLY_VALID" if manifest_ok else "STRUCTURALLY_INVALID",
        "component_checks": checks,
        "signature_verification": signature,
        "scope_note": (
            "Structural checks do not validate scientific claims. Git signature "
            "verification depends on local trust configuration and does not "
            "independently establish signer identity."
        ),
        "verification_configuration": {
            "gpg_key_id_configured_informational_only": bool(sensitive["gpg_key_id"]),
            "signatory_configured_informational_only": bool(sensitive["signatory"]),
            "identity_pinned_or_authenticated": False,
        },
    }

    if output_path is None:
        path = _default_report_path()
        # Keep the original stem so repeated collisions become _1, _2, ... .
        base_path = path
        suffix = 1
        while True:
            try:
                with path.open("x", encoding="utf-8") as stream:
                    stream.write(json.dumps(report, indent=2) + "\n")
                break
            except FileExistsError:
                path = base_path.with_name(
                    f"{base_path.stem}_{suffix}{base_path.suffix}"
                )
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
