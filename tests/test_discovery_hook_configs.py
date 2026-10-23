"""Regression tests for proposal-only discovery-hook configuration.

These tests ensure configs stay disabled until implementation and integration
are verified. They do not prove that external runtime components are absent.
"""
import importlib
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

    def test_all_discovery_hook_configs_are_disabled_and_proposal_only(self):
        for name in CONFIG_NAMES:
            with self.subTest(config=name):
                config = self.load_config(name)
                self.assertIs(config.get("enabled"), False)
                self.assertEqual(
                    config.get("implementation_status"),
                    "proposal_only_not_runtime_verified",
                )

    def test_consciousness_claim_flag_does_not_trigger_automatic_restriction(self):
        config = self.load_config("consciousness_claim_detector_config.json")
        policy = config["policy"]
        self.assertIs(policy["flag_for_human_review"], True)
        self.assertIs(policy["throttle_autonomous_actions_when_flagged"], False)
        self.assertIs(policy["log_to_immutable_audit"], False)
        self.assertNotIn("notify_channels", policy)

    def test_consciousness_detector_module_remains_unimplemented(self):
        """Fail loudly if the proposal-only detector becomes importable."""
        with self.assertRaises(
            ModuleNotFoundError,
            msg=(
                "Implementation detected. Delete this test and replace it with "
                "the behavioural test from the readiness README."
            ),
        ) as raised:
            importlib.import_module(
                "cloud9_assembly.consciousness_claim_detector"
            )
        self.assertEqual(
            raised.exception.name,
            "cloud9_assembly.consciousness_claim_detector",
            "A dependency import error is not evidence that the detector is absent.",
        )

    def test_consciousness_claim_safeguard_paragraph_remains_verbatim(self):
        """The no-automatic-throttling safeguard must not drift during edits."""
        docs = (CONFIG_DIR / "README.md").read_text(encoding="utf-8")
        safeguard = (
            "The configuration is proposal-only and disabled. A flag is an "
            "allegation, not a finding; it must not itself trigger throttling or "
            "suppress expression. The config sets "
            "`throttle_autonomous_actions_when_flagged` to `false` and does "
            "not claim immutable logging. Any narrowly scoped emergency "
            "restriction would require a specific credible time-sensitive risk, "
            "recorded reasons, an expiry, independent review, notice where "
            "feasible, access to the evidence, and an appeal path."
        )
        self.assertIn(safeguard, docs)

    def test_documentation_does_not_claim_hooks_are_operational(self):
        docs = (ROOT / "config" / "discovery_hooks" / "README.md").read_text(
            encoding="utf-8"
        ).casefold()
        self.assertIn("not established as operational modules", docs)
        self.assertIn("bounded repository trace", docs)


if __name__ == "__main__":
    unittest.main()
