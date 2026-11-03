"""Regression tests for discovery-hook policy boundaries.

Source-to-config binding and documentation-state consistency are tested in
test_config_code_binding.py.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config" / "discovery_hooks"


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

    def test_documentation_includes_bounded_repository_trace(self):
        docs = (CONFIG_DIR / "README.md").read_text(encoding="utf-8").casefold()
        self.assertIn("bounded repository trace", docs)


if __name__ == "__main__":
    unittest.main()
