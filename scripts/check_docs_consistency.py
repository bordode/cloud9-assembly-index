"""Check selected documentation for caveats and legacy implementation overclaims."""
from pathlib import Path

CHECKS = {
    "README.md": [
        "configuration proposal",
        "not verified as implemented",
    ],
    "ETHICS_MANIFESTO.md": [
        "neither, by itself, establishes consciousness",
        "hypotheses or conceptual proposals",
    ],
    "SPECULATIVE_FRAMEWORK.md": [
        "not a validated empirical core",
        "reported historical or exploratory claims",
    ],
    "config/discovery_hooks/README.md": [
        "a config does not prove",
        "proposal-only",
    ],
}

LEGACY_OVERCLAIMS = (
    "throttles autonomous actions for flagged agents",
    "implements this via a **contaminationscorer**",
    "implements this via a **hostgravityemulator**",
    "via a **statebudgetmonitor**",
    "enforces an \"ordinary first\" policy via",
)


def check_documentation(root=Path(__file__).resolve().parents[1]):
    errors = []
    for relative_path, phrases in CHECKS.items():
        path = root / relative_path
        if not path.is_file():
            errors.append(f"{relative_path}: file missing")
            continue
        text = path.read_text(encoding="utf-8").casefold()
        for phrase in phrases:
            if phrase.casefold() not in text:
                errors.append(f"{relative_path}: missing required caveat: {phrase}")
    readme_path = root / "README.md"
    if readme_path.is_file():
        readme = readme_path.read_text(encoding="utf-8").casefold()
        for phrase in LEGACY_OVERCLAIMS:
            if phrase.casefold() in readme:
                errors.append(f"README.md: legacy overclaim phrase remains: {phrase}")
    return errors


if __name__ == "__main__":
    errors = check_documentation()
    if errors:
        print("Documentation consistency check failed:")
        print("\n".join(f"- {error}" for error in errors))
        raise SystemExit(1)
    print("Documentation consistency check passed; wording only.")
