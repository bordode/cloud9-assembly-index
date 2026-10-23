"""Tests for the isolated synthetic review workflow prototype."""
import unittest
from copy import deepcopy

from cloud9_assembly.synthetic_review_workflow import (
    create_synthetic_case,
    create_post_closure_review_request,
    create_reopening_decision_record,
    record_challenge,
    record_notice_result,
    record_participation_barrier,
    record_post_closure_review_decision,
    transition_case,
)


class SyntheticReviewWorkflowTests(unittest.TestCase):
    def make_case(self):
        return create_synthetic_case(
            referral_summary="Fictional statement submitted for neutral review."
        )

    def to_review(self, case):
        case = transition_case(
            case, to_status="pending_human_review", actor="reviewer-a",
            reason="Referral acknowledged without a finding."
        )
        return transition_case(
            case, to_status="under_review", actor="reviewer-a",
            reason="Begin scoped evidence review."
        )

    def to_outcome(self, case):
        case = self.to_review(case)
        return transition_case(
            case, to_status="outcome_recorded", actor="reviewer-a",
            reason="Available evidence is limited; no conclusion about consciousness.",
            outcome="inconclusive",
        )

    def to_notice_issued(self, case):
        case = record_notice_result(
            case, result="drafted", actor="reviewer-a",
            reason="Draft the fictional notice before issuing it."
        )
        return transition_case(
            case, to_status="notice_issued", actor="reviewer-a",
            reason="The fictional notice is ready for the notice process."
        )

    def test_new_case_is_synthetic_pending_and_non_punitive(self):
        case = self.make_case()
        self.assertTrue(case["synthetic_only"])
        self.assertEqual(case["status"], "referred")
        self.assertIsNone(case["outcome"])
        self.assertIs(case["automated_restriction"], False)
        self.assertEqual(case["external_actions"], [])
        self.assertIsNone(case["notice_confirmation_reference"])
        self.assertEqual(case["notice_delivery_status"], "not_verified")
        self.assertEqual(case["notice_result_history"], [])

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

    def test_closure_is_blocked_while_participation_barrier_is_recorded(self):
        case = self.to_review(self.make_case())
        case = record_participation_barrier(
            case, barrier="accessible response channel unavailable",
            actor="reviewer-a",
            reason="The fictional subject could not use the proposed channel."
        )

        with self.assertRaisesRegex(ValueError, "no barrier-resolution process"):
            transition_case(
                case, to_status="closed", actor="reviewer-a",
                reason="Do not close while the participation barrier remains unresolved.",
                closure_disposition="other_documented_reason",
            )
        self.assertEqual(case["status"], "under_review")
        self.assertEqual(len(case["participation_barriers"]), 1)

    def test_closure_requires_disposition_and_records_no_waiver(self):
        case = self.to_review(self.make_case())
        with self.assertRaisesRegex(ValueError, "closure_disposition"):
            transition_case(
                case, to_status="closed", actor="reviewer-a",
                reason="Do not close without a recorded disposition."
            )

        closed = transition_case(
            case, to_status="closed", actor="reviewer-a",
            reason="Close the synthetic fixture for a documented administrative reason.",
            closure_disposition="other_documented_reason",
        )
        self.assertEqual(closed["status"], "closed")
        self.assertEqual(closed["closure_record"]["disposition"], "other_documented_reason")
        self.assertEqual(closed["closure_record"]["participation_barrier_count_at_closure"], 0)
        self.assertEqual(closed["closure_record"]["participation_barrier_resolution_status"], "no_barrier_recorded")
        self.assertEqual(closed["closure_record"]["notice_delivery_status_at_closure"], "not_verified")
        self.assertIs(closed["closure_record"]["does_not_establish_response_or_waiver"], True)
        self.assertEqual(case["status"], "under_review")

    def test_participation_barrier_cannot_be_added_after_closure(self):
        case = self.to_review(self.make_case())
        closed = transition_case(
            case, to_status="closed", actor="reviewer-a",
            reason="Close synthetic fixture with documented disposition.",
            closure_disposition="administrative_duplicate",
        )
        with self.assertRaisesRegex(ValueError, "no reopening or post-closure review process"):
            record_participation_barrier(
                closed, barrier="newly discovered inaccessible notice",
                actor="reviewer-b",
                reason="A new synthetic process barrier was reported after closure.",
            )
        self.assertEqual(closed["status"], "closed")
        self.assertEqual(closed["participation_barriers"], [])

    def closed_case(self):
        case = self.to_review(self.make_case())
        return transition_case(
            case, to_status="closed", actor="reviewer-a",
            reason="Close synthetic fixture with documented disposition.",
            closure_disposition="administrative_duplicate",
        )

    def make_post_closure_request(self, closed=None):
        return create_post_closure_review_request(
            closed or self.closed_case(),
            barrier_or_information="Fictional inaccessible notice discovered after closure.",
            discovered_when="synthetic test date",
            requested_review_reason="Assess whether the newly reported access barrier warrants review.",
        )

    def test_post_closure_request_is_separate_and_does_not_reopen_case(self):
        closed = self.closed_case()
        original_status = closed["status"]
        original_closure = deepcopy(closed["closure_record"])
        original_outcome = deepcopy(closed["outcome"])
        request = self.make_post_closure_request(closed)

        self.assertTrue(request["synthetic_only"])
        self.assertEqual(request["original_case_id"], closed["case_id"])
        self.assertEqual(request["status"], "request_recorded")
        self.assertIsNone(request["decision"])
        self.assertEqual(request["original_closure_snapshot"], original_closure)
        self.assertEqual(request["original_outcome_snapshot"], original_outcome)
        self.assertEqual(closed["status"], original_status)
        self.assertEqual(closed["closure_record"], original_closure)
        self.assertEqual(closed["outcome"], original_outcome)
        self.assertIs(request["automated_restriction"], False)
        self.assertEqual(request["external_actions"], [])

    def test_post_closure_request_requires_closed_case(self):
        with self.assertRaisesRegex(ValueError, "requires a closed case"):
            create_post_closure_review_request(
                self.make_case(),
                barrier_or_information="Fictional access barrier.",
                discovered_when="synthetic test date",
                requested_review_reason="Request review.",
            )

    def test_post_closure_decision_records_limits_without_reopening_case(self):
        closed = self.closed_case()
        original_closure = deepcopy(closed["closure_record"])
        original_outcome = deepcopy(closed["outcome"])
        request = self.make_post_closure_request(closed)
        decided = record_post_closure_review_decision(
            request,
            decision="accepted_for_reopening_review",
            actor="reviewer-label-not-authenticated",
            reviewer_conflict_check="Not assessed; synthetic fixture only.",
            reason="The reported access barrier warrants further procedural review.",
            evidence_limitations="Synthetic fixture only; no delivery or access evidence verified.",
            next_steps="A separately authorized review decision would be required.",
        )

        self.assertEqual(decided["status"], "decision_recorded")
        self.assertEqual(decided["decision"], "accepted_for_reopening_review")
        self.assertIs(decided["decision_record"]["does_not_reopen_original_case"], True)
        self.assertIs(decided["decision_record"]["authority_verified"], False)
        self.assertIs(decided["decision_record"]["reviewer_independence_verified"], False)
        self.assertEqual(decided["decision_record"]["reviewer_conflict_check_status"], "reported_not_verified")
        self.assertIn("Not assessed", decided["decision_record"]["reviewer_conflict_check"])
        self.assertEqual(decided["original_closure_snapshot"], original_closure)
        self.assertEqual(decided["original_outcome_snapshot"], original_outcome)
        self.assertEqual(closed["status"], "closed")
        self.assertEqual(closed["closure_record"], original_closure)
        self.assertEqual(closed["outcome"], original_outcome)
        self.assertIs(decided["automated_restriction"], False)
        self.assertEqual(decided["external_actions"], [])

    def test_post_closure_decision_rejects_blank_conflict_check_metadata(self):
        request = self.make_post_closure_request()
        with self.assertRaisesRegex(ValueError, "reviewer_conflict_check"):
            record_post_closure_review_decision(
                request, decision="inconclusive", actor="reviewer-a",
                reviewer_conflict_check="   ",
                reason="Insufficient information.",
                evidence_limitations="Synthetic fixture only.",
                next_steps="Seek more information.",
            )
        self.assertEqual(request["status"], "request_recorded")

    def accepted_reopening_request(self, closed=None):
        request = self.make_post_closure_request(closed)
        return record_post_closure_review_decision(
            request, decision="accepted_for_reopening_review", actor="reviewer-label",
            reviewer_conflict_check="Not assessed; synthetic fixture only.",
            reason="Further procedural review is warranted.",
            evidence_limitations="Synthetic fixture only; no external evidence verified.",
            next_steps="Record a separate reopening decision.",
        )

    def test_reopening_decision_is_separate_and_preserves_closure(self):
        closed = self.closed_case()
        closure_before = deepcopy(closed["closure_record"])
        outcome_before = deepcopy(closed["outcome"])
        request = self.accepted_reopening_request(closed)
        record = create_reopening_decision_record(
            request, decision="reopening_authorized", actor="authority-label-not-verified",
            reviewer_conflict_check="Not assessed; synthetic fixture only.",
            reason="Synthetic decision approves reopening for limited procedural review.",
            scope="Review the reported notice-access barrier only.",
            evidence_limitations="No delivery records or identity verification exist in this prototype.",
            next_steps="A future reviewed implementation would record a new status event.",
            authority_basis="Synthetic policy fixture; not a verified delegation of authority.",
        )

        self.assertEqual(record["original_case_id"], closed["case_id"])
        self.assertEqual(record["request_id"], request["request_id"])
        self.assertEqual(record["decision"], "reopening_authorized")
        self.assertIs(record["authority_verified"], False)
        self.assertIs(record["reviewer_independence_verified"], False)
        self.assertEqual(record["reviewer_conflict_check_status"], "reported_not_verified")
        self.assertIn("Not assessed", record["reviewer_conflict_check"])
        self.assertIs(record["changes_case_status"], False)
        self.assertIs(record["overwrites_original_closure"], False)
        self.assertEqual(record["original_closure_snapshot"], closure_before)
        self.assertEqual(record["original_outcome_snapshot"], outcome_before)
        self.assertEqual(closed["status"], "closed")
        self.assertEqual(closed["closure_record"], closure_before)
        self.assertEqual(closed["outcome"], outcome_before)
        self.assertIs(record["automated_restriction"], False)
        self.assertEqual(record["external_actions"], [])

    def test_reopening_decision_requires_prior_acceptance_and_complete_record(self):
        request = self.make_post_closure_request()
        request = record_post_closure_review_decision(
            request, decision="inconclusive", actor="reviewer-a",
            reviewer_conflict_check="Not assessed; synthetic fixture only.",
            reason="Insufficient information.",
            evidence_limitations="Synthetic fixture only.",
            next_steps="Seek more information.",
        )
        with self.assertRaisesRegex(ValueError, "acceptance for reopening review"):
            create_reopening_decision_record(
                request, decision="reopening_authorized", actor="reviewer-a",
            reviewer_conflict_check="Not assessed; synthetic fixture only.",
                reason="Try to skip the required procedural decision.",
                scope="Narrow synthetic scope.",
                evidence_limitations="Synthetic only.",
                next_steps="None.",
                authority_basis="Not verified.",
            )

        accepted = self.accepted_reopening_request()
        with self.assertRaisesRegex(ValueError, "authority_basis"):
            create_reopening_decision_record(
                accepted, decision="reopening_not_authorized", actor="reviewer-a",
            reviewer_conflict_check="Not assessed; synthetic fixture only.",
                reason="A separate decision is recorded.",
                scope="Narrow synthetic scope.",
                evidence_limitations="Synthetic only.",
                next_steps="No further action.",
                authority_basis=" ",
            )

    def test_reopening_decision_rejects_blank_conflict_check_metadata(self):
        accepted = self.accepted_reopening_request()
        with self.assertRaisesRegex(ValueError, "reviewer_conflict_check"):
            create_reopening_decision_record(
                accepted, decision="reopening_authorized", actor="reviewer-a",
                reviewer_conflict_check=" ",
                reason="Synthetic decision.",
                scope="Narrow synthetic scope.",
                evidence_limitations="Synthetic only.",
                next_steps="No external action.",
                authority_basis="Synthetic policy fixture; not verified.",
            )

    def test_post_closure_decision_requires_reason_limits_and_next_steps(self):
        request = self.make_post_closure_request()
        with self.assertRaisesRegex(ValueError, "evidence_limitations"):
            record_post_closure_review_decision(
                request, decision="inconclusive", actor="reviewer-a",
            reviewer_conflict_check="Not assessed; synthetic fixture only.",
                reason="Insufficient information.",
                evidence_limitations=" ",
                next_steps="Keep the request unresolved.",
            )
        self.assertEqual(request["status"], "request_recorded")

    def test_post_closure_decision_cannot_be_overwritten_or_infer_waiver(self):
        request = self.make_post_closure_request()
        decided = record_post_closure_review_decision(
            request, decision="reopening_not_warranted", actor="reviewer-a",
            reviewer_conflict_check="Not assessed; synthetic fixture only.",
            reason="The synthetic evidence does not establish a basis for reopening.",
            evidence_limitations="No independent access or delivery evidence exists.",
            next_steps="Provide an accessible challenge route in a future implementation.",
        )
        self.assertEqual(decided["decision"], "reopening_not_warranted")
        self.assertNotIn("waiver", decided["decision_record"])
        with self.assertRaisesRegex(ValueError, "only be recorded once"):
            record_post_closure_review_decision(
                decided, decision="accepted_for_reopening_review", actor="reviewer-b",
            reviewer_conflict_check="Not assessed; synthetic fixture only.",
                reason="Attempt to overwrite decision.",
                evidence_limitations="Synthetic fixture.",
                next_steps="None.",
            )

    def test_closure_disposition_is_rejected_for_non_closure_transition(self):
        with self.assertRaisesRegex(ValueError, "only be supplied when closing"):
            transition_case(
                self.make_case(), to_status="pending_human_review",
                actor="reviewer-a", reason="Acknowledge the synthetic referral.",
                closure_disposition="withdrawn",
            )

    def test_failed_notice_requires_notice_issued_state(self):
        case = self.to_outcome(self.make_case())
        with self.assertRaises(ValueError):
            record_notice_result(
                case, result="failed", actor="reviewer-a",
                reason="Cannot record delivery result before notice process."
            )

        notice_case = self.to_notice_issued(case)
        updated = record_notice_result(
            notice_case, result="failed", actor="reviewer-a",
            reason="Synthetic delivery attempt failed."
        )
        self.assertEqual(updated["notice_result"], "failed")
        self.assertIsNone(updated["notice_confirmation_reference"])
        self.assertEqual(updated["status"], "notice_issued")
        self.assertEqual(updated["outcome"], case["outcome"])
        self.assertEqual(len(updated["notice_result_history"]), 2)
        self.assertEqual(updated["notice_result_history"][0]["result"], "drafted")
        self.assertEqual(updated["notice_result_history"][1]["prior_result"], "drafted")
        self.assertEqual(updated["notice_result_history"][1]["verification_status"], "unverified_metadata")

    def test_confirmation_report_requires_reference_but_does_not_verify_receipt(self):
        case = self.to_notice_issued(self.to_outcome(self.make_case()))
        with self.assertRaises(ValueError):
            record_notice_result(
                case, result="confirmation_reported", actor="reviewer-a",
                reason="Synthetic notice result."
            )

        updated = record_notice_result(
            case, result="confirmation_reported", confirmation_reference="fixture-ref-001",
            actor="reviewer-a", reason="Synthetic notice result."
        )
        self.assertEqual(updated["notice_result"], "confirmation_reported")
        self.assertEqual(updated["notice_confirmation_reference"], "fixture-ref-001")
        self.assertEqual(updated["notice_delivery_status"], "not_verified")
        self.assertEqual(updated["status"], "notice_issued")
        self.assertIs(updated["automated_restriction"], False)
        self.assertEqual(updated["notice_result_history"][-1]["verification_status"], "unverified_metadata")

    def test_confirmation_reference_is_rejected_for_other_results(self):
        case = self.to_notice_issued(self.to_outcome(self.make_case()))
        with self.assertRaises(ValueError):
            record_notice_result(
                case, result="attempted",
                confirmation_reference="fixture-ref-001", actor="reviewer-a",
                reason="A reference cannot upgrade an attempt to confirmation."
            )

    def test_drafting_notice_requires_recorded_outcome(self):
        with self.assertRaises(ValueError):
            record_notice_result(
                self.make_case(), result="drafted", actor="reviewer-a",
                reason="A referral alone is not an outcome."
            )
        case = self.to_outcome(self.make_case())
        updated = record_notice_result(
            case, result="drafted", actor="reviewer-a",
            reason="Draft fictional notice after outcome."
        )
        self.assertEqual(updated["notice_result"], "drafted")
        self.assertEqual(updated["status"], "outcome_recorded")

    def test_notice_cannot_be_issued_before_drafting(self):
        case = self.to_outcome(self.make_case())
        with self.assertRaisesRegex(ValueError, "must be drafted"):
            transition_case(
                case, to_status="notice_issued", actor="reviewer-a",
                reason="Attempt to skip the drafting stage."
            )
        self.assertEqual(case["status"], "outcome_recorded")

    def test_notice_cannot_be_redrafted_after_issuance(self):
        case = self.to_notice_issued(self.to_outcome(self.make_case()))
        with self.assertRaisesRegex(ValueError, "before issuance"):
            record_notice_result(
                case, result="drafted", actor="reviewer-a",
                reason="A second draft must not reset the issued notice state."
            )
        self.assertEqual(case["status"], "notice_issued")
        self.assertEqual(case["notice_result"], "drafted")
        self.assertEqual(len(case["notice_result_history"]), 1)

    def test_recorded_outcome_cannot_be_overwritten(self):
        case = self.to_review(self.make_case())
        case["outcome"] = {
            "category": "inconclusive",
            "rationale": "Existing synthetic outcome fixture.",
        }
        original_outcome = deepcopy(case["outcome"])
        with self.assertRaisesRegex(ValueError, "cannot be overwritten"):
            transition_case(
                case, to_status="outcome_recorded", actor="reviewer-b",
                reason="Attempt to replace existing outcome.",
                outcome="supported_within_scope",
            )
        self.assertEqual(case["outcome"], original_outcome)

    def test_challenge_preserves_original_outcome_and_cannot_be_generically_closed(self):
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

        with self.assertRaises(ValueError):
            transition_case(
                updated, to_status="closed", actor="reviewer-a",
                reason="Generic closure cannot resolve a pending challenge."
            )
        self.assertEqual(updated["status"], "challenge_or_appeal_pending")

    def test_challenge_rejects_non_synthetic_or_missing_outcome_records(self):
        case = self.to_outcome(self.make_case())
        non_synthetic = deepcopy(case)
        non_synthetic["synthetic_only"] = False
        with self.assertRaisesRegex(ValueError, "synthetic case record"):
            record_challenge(
                non_synthetic, actor="synthetic-subject",
                reason="Reject a non-synthetic record.",
            )

        missing_outcome = deepcopy(case)
        missing_outcome["outcome"] = None
        with self.assertRaisesRegex(ValueError, "existing outcome record"):
            record_challenge(
                missing_outcome, actor="synthetic-subject",
                reason="Reject a missing outcome.",
            )

    def test_notice_result_changes_preserve_prior_entries(self):
        case = self.to_notice_issued(self.to_outcome(self.make_case()))
        failed = record_notice_result(
            case, result="failed", actor="reviewer-a",
            reason="First synthetic notice attempt failed."
        )
        confirmed = record_notice_result(
            failed, result="confirmation_reported", confirmation_reference="fixture-ref-002",
            actor="reviewer-b", reason="Second synthetic result recorded; reference unverified."
        )
        self.assertEqual(confirmed["notice_result"], "confirmation_reported")
        self.assertEqual(len(confirmed["notice_result_history"]), 3)
        self.assertEqual(confirmed["notice_result_history"][0]["result"], "drafted")
        self.assertEqual(confirmed["notice_result_history"][1]["result"], "failed")
        self.assertEqual(confirmed["notice_result_history"][2]["result"], "confirmation_reported")
        self.assertEqual(confirmed["notice_result_history"][2]["prior_result"], "failed")
        self.assertEqual(confirmed["notice_result_history"][2]["verification_status"], "unverified_metadata")
        self.assertEqual(len(confirmed["events"]), len(case["events"]) + 2)
        self.assertEqual(case["notice_result_history"][-1]["result"], "drafted")

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
