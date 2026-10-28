"""Check that discovery-hook configuration agrees with repository code.

These checks establish configuration/code consistency, not scientific validity,
production integration, or operational safety.

States:
- proposal_only_not_runtime_verified: disabled; named module must not resolve.
- implemented_disabled_pending_activation: disabled; module and class exist.
- implemented_enabled_runtime_verified: enabled; module and class exist, and
  a non-test source file references the config (a weak temporary check).
"""
import importlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config" / "discovery_hooks"

PARKED = "proposal_only_not_runtime_verified"
IMPLEMENTED_DISABLED = "implemented_disabled_pending_activation"
ENABLED_STATUS = "implemented_enabled_runtime_verified"

STATUS_TO_ENABLED = {
    PARKED: False,
    IMPLEMENTED_DISABLED: False,
    ENABLED_STATUS: True,
}


def configs():
    return sorted(CONFIG_DIR.glob("*_config.json"))


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def locate(module_name):
    """Locate a module without importing the target itself.

    Dotted-name lookup may still import its parent package.
    """
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ImportError, ValueError):
        return False


def non_test_references(path):
    """Find non-test Python files mentioning this config filename.

    This is only a weak placeholder for a real loader integration test.
    """
    found = []
    for source in ROOT.rglob("*.py"):
        if "tests" in source.parts or not source.is_file():
            continue
        try:
            content = source.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if path.name in content:
            found.append(source)
    return found


class ConfigCodeBindingTests(unittest.TestCase):
    def test_at_least_one_config_is_discovered(self):
        self.assertTrue(CONFIG_DIR.is_dir(), f"Missing {CONFIG_DIR}")
        self.assertTrue(configs(), f"No hook configs found in {CONFIG_DIR}")

    def test_every_config_has_consistent_state(self):
        for path in configs():
            with self.subTest(config=path.name):
                config = load(path)
                self.assertTrue(config.get("module"), "module missing")
                self.assertTrue(config.get("class"), "class missing")
                self.assertIsInstance(config.get("enabled"), bool)

                status = config.get("implementation_status")
                self.assertIn(
                    status,
                    STATUS_TO_ENABLED,
                    f"Unknown implementation_status: {status!r}",
                )
                self.assertIs(
                    config["enabled"],
                    STATUS_TO_ENABLED[status],
                    "enabled flag contradicts implementation_status",
                )

    def test_parked_configs_do_not_resolve_to_modules(self):
        for path in configs():
            config = load(path)
            if config.get("implementation_status") != PARKED:
                continue
            with self.subTest(config=path.name):
                self.assertIs(config["enabled"], False)
                self.assertFalse(
                    locate(config["module"]),
                    f"{path.name}: module resolves; review whether its "
                    "status should be implemented-disabled instead.",
                )

    def test_implemented_configs_import_and_expose_the_named_class(self):
        for path in configs():
            config = load(path)
            if config.get("implementation_status") not in (
                IMPLEMENTED_DISABLED,
                ENABLED_STATUS,
            ):
                continue
            with self.subTest(config=path.name):
                self.assertTrue(
                    locate(config["module"]),
                    f"{path.name}: module does not resolve",
                )
                try:
                    module = importlib.import_module(config["module"])
                except Exception as exc:
                    self.fail(
                        f"{path.name}: module import failed "
                        f"({type(exc).__name__}: {exc})"
                    )
                self.assertTrue(
                    hasattr(module, config["class"]),
                    f"{path.name}: class {config['class']!r} missing",
                )

    def test_enabled_configs_have_a_non_test_reference(self):
        # Weak placeholder only: a filename mention does not prove the loader
        # instantiates the class or passes configuration into it. Replace this
        # with a test of the actual loader entry point when one exists.
        for path in configs():
            config = load(path)
            if config.get("implementation_status") != ENABLED_STATUS:
                continue
            with self.subTest(config=path.name):
                self.assertTrue(
                    non_test_references(path),
                    f"{path.name}: no non-test source reference found",
                )


if __name__ == "__main__":
    unittest.main()
