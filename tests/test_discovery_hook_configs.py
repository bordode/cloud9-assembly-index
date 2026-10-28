"""Regression tests for discovery-hook configuration state and policy.

These tests validate the declared lifecycle state. They do not prove that
external runtime components are absent or that enabled hooks are safe.
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

STATUS_TO_ENABLED = {
    "proposal_only_not_runtime_verified": False,
    "implemented_disabled_pending_activation": False,
    "implemented_enabled_runtime_verified": True,
}


class DiscoveryHookConfigTests(unittest.TestCase):
    def load_config(self, name):
        with (CONFIG_DIR / name).open(encoding="utf-8") as stream:
            return json.load(stream)

    def test_all_discovery_hook_configs_have_consistent_states(self):
        for name in CONFIG_NAMES:
            with self.subTest(config=name):
                config = self.load_config(name)
                status = config.get("implementation_status")

                self.assertIn(status, STATUS_TO_ENABLED)
                self.assertIsInstance(config.get("enabled"), bool)
                self.assertIs(
                    config["enabled"],
                    STATUS_TO_ENABLED[status],
                    "enabled flag contradicts implementation_status",
                )

    def test_consciousness_claim_flag_does_not_trigger_automatic_restriction(self):
        config = self.load_config("consciousness_claim_detector_config.json")
        policy = config["policy"]
        self.assertIs(policy["flag_for_human_review"], True)
        self.assertIs(policy["throttle_autonomous_actions_when_flagged"], False)
        self.assertIs(policy["log_to_immutable_audit"], False)
        self.assertNotIn("notify_channels", policy)

    def test_documentation_does_not_claim_hooks_are_operational(self):
        docs = (ROOT / "config" / "discovery_hooks" / "README.md").read_text(
            encoding="utf-8"
        ).casefold()
        self.assertIn("not established as operational modules", docs)
        self.assertIn("bounded repository trace", docs)


if __name__ == "__main__":
    unittest.main()
