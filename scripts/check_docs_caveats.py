"""Check selected documentation for required evidence caveats.

This is a wording regression check only. It does not validate scientific claims or
prove that any runtime safeguard is implemented.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "README.md": ["not verified as implemented", "configuration proposal"],
    "ETHICS_MANIFESTO.md": ["neither, by itself, establishes consciousness", "hypotheses or conceptual proposals"],
    "SPECULATIVE_FRAMEWORK.md": ["not a validated empirical core", "reported historical or exploratory claims"],
    "config/discovery_hooks/README.md": ["A configuration file is not evidence"],
}


def main():
    failures = []
    for name, phrases in REQUIRED.items():
        path = ROOT / name
        if not path.is_file():
            failures.append(f"{name}: file missing")
            continue
        text = path.read_text(encoding="utf-8").casefold()
        for phrase in phrases:
            if phrase.casefold() not in text:
                failures.append(f"{name}: missing caveat: {phrase}")
    if failures:
        print("Documentation caveat check failed:")
        print("\n".join(f"- {item}" for item in failures))
        return 1
    print("Documentation caveat check passed; this checks wording only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
