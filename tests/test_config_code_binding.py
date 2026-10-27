"""Static binding checks for discovery-hook configuration.

These tests inspect source without importing or activating hook code. Parked
proposals may remain disabled whether or not implementation work exists; an
enabled hook must at least point to parseable source defining its configured
class. Runtime loading and integration remain separate requirements.
"""
import ast
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config" / "discovery_hooks"
PARKED = "proposal_only_not_runtime_verified"


def configs():
    return sorted(CONFIG_DIR.glob("*_config.json"))


def module_source_path(module_name):
    """Resolve a dotted module name to a Python source file without importing it."""
    if not isinstance(module_name, str) or not module_name:
        return None
    parts = module_name.split(".")
    if any(not part.isidentifier() for part in parts):
        return None
    module_file = ROOT.joinpath(*parts).with_suffix(".py")
    package_file = ROOT.joinpath(*parts, "__init__.py")
    if module_file.is_file():
        return module_file
    if package_file.is_file():
        return package_file
    return None


def source_defines_class(source_path, class_name):
    """Return False for absent, malformed, or class-mismatched source."""
    if not isinstance(class_name, str) or not class_name.isidentifier():
        return False
    try:
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    except (OSError, SyntaxError, UnicodeError):
        return False
    return any(
        isinstance(node, ast.ClassDef) and node.name == class_name
        for node in ast.walk(tree)
    )


class ConfigCodeBindingTests(unittest.TestCase):
    def test_every_config_has_explicit_status_and_valid_enabled_binding(self):
        paths = configs()
        self.assertTrue(paths, f"No discovery-hook configs found in {CONFIG_DIR}")

        for path in paths:
            with self.subTest(config=path.name):
                config = json.loads(path.read_text(encoding="utf-8"))
                module_name = config.get("module")
                class_name = config.get("class")
                enabled = config.get("enabled")
                status = config.get("implementation_status")

                self.assertTrue(
                    isinstance(module_name, str) and module_name,
                    f"{path.name}: missing module name",
                )
                self.assertTrue(
                    isinstance(class_name, str) and class_name,
                    f"{path.name}: missing class name",
                )
                self.assertIsInstance(enabled, bool, f"{path.name}: enabled must be boolean")

                if enabled is False:
                    self.assertEqual(
                        status,
                        PARKED,
                        f"{path.name}: disabled config must be explicitly marked {PARKED}",
                    )
                    continue

                self.assertNotEqual(
                    status,
                    PARKED,
                    f"{path.name}: enabled config is still labelled {PARKED}",
                )
                source_path = module_source_path(module_name)
                self.assertIsNotNone(
                    source_path,
                    f"{path.name}: enabled but no source file resolves for module {module_name}",
                )
                self.assertTrue(
                    source_defines_class(source_path, class_name),
                    f"{path.name}: enabled but {module_name} does not define class {class_name}",
                )

    def test_documentation_matches_whether_all_hooks_are_parked(self):
        readme = (CONFIG_DIR / "README.md").read_text(encoding="utf-8").casefold()
        loaded = [json.loads(path.read_text(encoding="utf-8")) for path in configs()]
        all_parked = all(
            config.get("enabled") is False
            and config.get("implementation_status") == PARKED
            for config in loaded
        )

        self.assertIn("bounded repository trace", readme)
        if all_parked:
            self.assertIn("not established as operational modules", readme)
        else:
            self.assertNotIn("all five are marked", readme)
            self.assertIn("requirements before activation", readme)


if __name__ == "__main__":
    unittest.main()
