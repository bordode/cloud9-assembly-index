"""Tests for the isolated synthetic review workflow prototype."""
import unittest

from cloud9_assembly.synthetic_review_workflow import (
    create_synthetic_case,
    record_challenge,
    record_notice_result,
    record_participation_barrier,
    transition_case,
)


class SyntheticReviewWorkflowTests(unittest.TestCase):
    def make_case(self):
        return create_synthetic_case(
            referral_summary="Fictional statement submitted for neutral review."
        )

    def to_outcome(self, case):
        case = transition_case(
            case, to_status="pending_human_review", actor="reviewer-a",
            reason="Referral acknowledged without a finding."
        )
        case = transition_case(
            case, to_status="under_review", actor="reviewer-a",
            reason="Begin scoped evidence review."
        )
        return transition_case(
            case, to_status="outcome_recorded", actor="reviewer-a",
            reason="Available evidence is limited; no conclusion about consciousness.",
            outcome="inconclusive",
        )

    def test_new_case_is_synthetic_pending_and_non_punitive(self):
        case = self.make_case()
        self.assertTrue(case["synthetic_only"])
        self.assertEqual(case["status"], "referred")
        self.assertIsNone(case["outcome"])
        self.assertIs(case["automated_restriction"], False)
        self.assertEqual(case["external_actions"], [])
        self.assertIsNone(case["notice_confirmation_reference"])

    def test_claim_language_does_not_change_state_or_permissions(self):
        case = create_synthetic_case(
            referral_summary="Fictional subject says: I am conscious."
        )
        self.assertEqual(case["status"], "referred")
        self.assertIsNone(case["outcome"])
        self.assertIs(case["automated_restriction"], False)

    def test_invalid_transition_is_rejected(self):
        with self.assertRaises(ValueError):
            transition_case(
                self.make_case(), to_status="closed", actor="reviewer-a",
                reason="Cannot skip the defined lifecycle."
            )

    def test_barrier_does_not_change_status_or_outcome(self):
        case = self.to_outcome(self.make_case())
        updated = record_participation_barrier(
            case, barrier="notice inaccessible", actor="reviewer-a",
            reason="The fictional notice channel was unavailable."
        )
        self.assertEqual(updated["status"], "outcome_recorded")
        self.assertEqual(updated["outcome"], case["outcome"])
        self.assertEqual(len(updated["participation_barriers"]), 1)
        self.assertIs(updated["automated_restriction"], False)

    def test_failed_notice_is_not_confirmed_and_does_not_close_case(self):
        case = self.to_outcome(self.make_case())
        updated = record_notice_result(
            case, result="failed", actor="reviewer-a",
            reason="Synthetic delivery attempt failed."
        )
        self.assertEqual(updated["notice_result"], "failed")
        self.assertIsNone(updated["notice_confirmation_reference"])
        self.assertEqual(updated["status"], "outcome_recorded")
        self.assertEqual(updated["outcome"], case["outcome"])

    def test_confirmed_notice_requires_reference_but_does_not_verify_it(self):
        case = self.make_case()
        with self.assertRaises(ValueError):
            record_notice_result(
                case, result="confirmed", actor="reviewer-a",
                reason="Synthetic notice result."
            )

        updated = record_notice_result(
            case, result="confirmed", confirmation_reference="fixture-ref-001",
            actor="reviewer-a", reason="Synthetic notice result."
        )
        self.assertEqual(updated["notice_result"], "confirmed")
        self.assertEqual(updated["notice_confirmation_reference"], "fixture-ref-001")
        self.assertEqual(updated["status"], "referred")
        self.assertIs(updated["automated_restriction"], False)

    def test_confirmation_reference_is_rejected_for_other_results(self):
        with self.assertRaises(ValueError):
            record_notice_result(
                self.make_case(), result="attempted",
                confirmation_reference="fixture-ref-001", actor="reviewer-a",
                reason="A reference cannot upgrade an attempt to confirmation."
            )

    def test_challenge_preserves_original_outcome(self):
        case = self.to_outcome(self.make_case())
        updated = record_challenge(
            case, actor="synthetic-subject",
            reason="Fictional subject disputes the rationale."
        )
        self.assertEqual(updated["status"], "challenge_or_appeal_pending")
        self.assertEqual(updated["original_outcome"], case["outcome"])
        self.assertEqual(updated["outcome"], case["outcome"])
        self.assertIs(updated["automated_restriction"], False)
        self.assertEqual(updated["external_actions"], [])

    def test_input_case_is_not_mutated(self):
        case = self.make_case()
        original_events = list(case["events"])
        updated = transition_case(
            case, to_status="pending_human_review", actor="reviewer-a",
            reason="Acknowledge fictional referral."
        )
        self.assertEqual(case["status"], "referred")
        self.assertEqual(case["events"], original_events)
        self.assertEqual(updated["status"], "pending_human_review")

    def test_notice_result_validation(self):
        with self.assertRaises(ValueError):
            record_notice_result(
                self.make_case(), result="assumed_delivered", actor="reviewer-a",
                reason="Invalid fixture result."
            )


if __name__ == "__main__":
    unittest.main()
