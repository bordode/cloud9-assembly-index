"""Regression tests for proposal-only discovery-hook configuration.

These tests protect the policy boundaries and keep documentation aligned with
the current implementation status. Source-to-config binding is tested in
test_config_code_binding.py.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config" / "discovery_hooks"
CONFIG_NAMES = (
    "consciousness_claim_detector_config.json",
    "contamination_scorer_config.json",
    "host_gravity_emulator_config.json",
    "state_budget_monitor_config.json",
    "mundane_mechanism_catalog_config.json",
)


class DiscoveryHookConfigTests(unittest.TestCase):
    def load_config(self, name):
        with (CONFIG_DIR / name).open(encoding="utf-8") as stream:
            return json.load(stream)

    def test_consciousness_claim_flag_does_not_trigger_automatic_restriction(self):
        config = self.load_config("consciousness_claim_detector_config.json")
        policy = config["policy"]
        self.assertIs(policy["flag_for_human_review"], True)
        self.assertIs(policy["throttle_autonomous_actions_when_flagged"], False)
        self.assertIs(policy["log_to_immutable_audit"], False)
        self.assertNotIn("notify_channels", policy)

    def test_documentation_does_not_claim_hooks_are_operational(self):
        docs = (CONFIG_DIR / "README.md").read_text(encoding="utf-8").casefold()
        self.assertIn("not established as operational modules", docs)
        self.assertIn("bounded repository trace", docs)


if __name__ == "__main__":
    unittest.main()
