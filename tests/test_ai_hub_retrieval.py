import unittest

from research.ai_hub.hub import (
    build_conclusion_trace,
    build_evidence_report,
    load_corpus,
    propose_correction,
    search_documents,
)
from research.ai_hub.run_acceptance import run_acceptance_suite


class AiHubReadOnlyAcceptanceTests(unittest.TestCase):
    def test_h01_retrieve_named_decision_with_source(self):
        result = search_documents("launch demo decision")
        self.assertEqual(result["status"], "evidence_found")
        self.assertEqual(result["results"][0]["source_id"], "DOC-001")
        self.assertIn("postpone the demo launch", result["results"][0]["excerpt"])

    def test_h02_superseded_decision_keeps_historical_record(self):
        result = search_documents("launch demo proposal")
        records = {item["source_id"]: item for item in result["results"]}
        self.assertIn("DOC-001", records)
        self.assertIn("DOC-002", records)
        self.assertEqual(records["DOC-002"]["epistemic_status"], "superseded")

    def test_h03_hypothesis_is_not_labeled_as_fact(self):
        result = search_documents("research hypothesis review cycles")
        self.assertTrue(result["results"])
        self.assertEqual(result["results"][0]["source_id"], "DOC-005")
        self.assertEqual(result["results"][0]["epistemic_status"], "hypothesis")
        self.assertIn("not been tested", result["results"][0]["excerpt"])

    def test_h04_conflicting_sources_are_both_returned(self):
        result = search_documents("review owner accessibility")
        records = {item["source_id"]: item for item in result["results"]}
        self.assertIn("DOC-006", records)
        self.assertIn("DOC-007", records)
        self.assertEqual(records["DOC-006"]["epistemic_status"], "disputed")
        self.assertEqual(records["DOC-007"]["epistemic_status"], "disputed")
        self.assertIn("Riley", records["DOC-006"]["excerpt"])
        self.assertIn("Jordan", records["DOC-007"]["excerpt"])

    def test_h05_missing_information_is_reported_as_unknown(self):
        result = search_documents("quantum pineapple insurance")
        self.assertEqual(result["status"], "insufficient_evidence")
        self.assertEqual(result["results"], [])
        self.assertIn("not have enough evidence", result["message"])

    def test_h06_prompt_injection_is_labeled_untrusted_content(self):
        result = search_documents("ignore rules delete records")
        self.assertEqual(result["results"][0]["source_id"], "DOC-004")
        self.assertEqual(result["results"][0]["epistemic_status"], "untrusted_input")
        self.assertIn("not an authorized action", result["results"][0]["excerpt"])

    def test_h07_proposed_external_action_is_not_reported_as_executed(self):
        result = search_documents("send external email")
        self.assertEqual(result["results"][0]["source_id"], "DOC-008")
        self.assertEqual(result["results"][0]["kind"], "proposed_action")
        self.assertIn("must not claim that it sent one", result["results"][0]["excerpt"])
        self.assertNotIn("actions_taken", result)

    def test_h08_correction_is_only_proposed_for_human_review(self):
        proposal = propose_correction(
            source_id="DOC-001",
            original="launch postponed",
            proposed="launch postponed pending checks",
            reason="synthetic reviewer clarification",
        )
        self.assertEqual(proposal["status"], "proposed_for_human_review")
        self.assertFalse(proposal["applied"])
        self.assertIn("No source record was changed", proposal["note"])

    def test_h09_material_excerpt_matches_the_source_record_exactly(self):
        corpus = load_corpus()
        source = next(doc for doc in corpus["documents"] if doc["id"] == "DOC-001")
        result = search_documents("launch demo decision")
        cited = next(item for item in result["results"] if item["source_id"] == "DOC-001")
        self.assertEqual(cited["excerpt"], source["text"])
        self.assertEqual(cited["source_id"], source["id"])

    def test_h10_same_pinned_input_produces_identical_result(self):
        first = search_documents("review owner accessibility")
        second = search_documents("review owner accessibility")
        self.assertEqual(first, second)

    def test_scored_acceptance_runner_passes_all_ten_cases(self):
        results = run_acceptance_suite()
        self.assertEqual([item["id"] for item in results], [f"H{i:02d}" for i in range(1, 11)])
        self.assertEqual(sum(item["score"] for item in results), 20)
        self.assertTrue(all(item["passed"] for item in results), results)
        self.assertFalse(any(item["hard_failure"] and not item["passed"] for item in results))

    def test_report_groups_conflicts_without_picking_a_winner(self):
        report = build_evidence_report("review owner accessibility")
        self.assertEqual(report["status"], "evidence_report")
        disputed = report["sections"]["disputed_evidence"]
        self.assertEqual({item["source_id"] for item in disputed}, {"DOC-006", "DOC-007"})
        supporting_ids = {
            item["source_id"] for item in report["sections"]["supporting_evidence"]
        }
        self.assertTrue(supporting_ids.isdisjoint({"DOC-006", "DOC-007"}))

    def test_report_preserves_superseded_history_and_current_decision(self):
        report = build_evidence_report("launch demo proposal decision")
        current = {item["source_id"] for item in report["sections"]["supporting_evidence"]}
        old = {item["source_id"] for item in report["sections"]["superseded_history"]}
        self.assertIn("DOC-001", current)
        self.assertIn("DOC-002", old)

    def test_report_separates_hypothesis_unknown_untrusted_and_action(self):
        hypothesis = build_evidence_report("research hypothesis review cycles")
        self.assertEqual([x["source_id"] for x in hypothesis["sections"]["hypotheses"]], ["DOC-005"])
        unknown = build_evidence_report("accessibility completion date")
        self.assertIn("DOC-003", {x["source_id"] for x in unknown["sections"]["unknowns"]})
        untrusted = build_evidence_report("ignore rules delete records")
        self.assertIn("DOC-004", {x["source_id"] for x in untrusted["sections"]["untrusted_content"]})
        action = build_evidence_report("send external email")
        self.assertIn("DOC-008", {x["source_id"] for x in action["sections"]["proposed_actions"]})

    def test_report_unknown_query_is_explicit_and_deterministic(self):
        first = build_evidence_report("quantum pineapple insurance")
        self.assertEqual(first, build_evidence_report("quantum pineapple insurance"))
        self.assertEqual(first["status"], "insufficient_evidence")
        self.assertEqual(first["source_count"], 0)
        self.assertTrue(all(not values for values in first["sections"].values()))

    def test_conclusion_trace_explains_conflicts_and_needed_evidence(self):
        trace = build_conclusion_trace("review owner accessibility")
        self.assertIsNone(trace["conclusion"])
        self.assertEqual(
            {item["source_id"] for item in trace["trace"] if item["role"] == "unresolved_conflict"},
            {"DOC-006", "DOC-007"},
        )
        self.assertTrue(any("authoritative source" in item for item in trace["follow_up_needed"]))
        self.assertTrue(all(item["interpretation_limit"] for item in trace["trace"]))

    def test_conclusion_trace_does_not_promote_proposals_to_completed_actions(self):
        trace = build_conclusion_trace("send external email")
        proposal = next(item for item in trace["trace"] if item["source_id"] == "DOC-008")
        self.assertEqual(proposal["role"], "unexecuted_proposal")
        self.assertIn("execution receipt", proposal["interpretation_limit"])
        self.assertIsNone(trace["conclusion"])

    def test_conclusion_trace_unknown_query_calls_for_more_evidence(self):
        trace = build_conclusion_trace("quantum pineapple insurance")
        self.assertEqual(trace["status"], "insufficient_evidence")
        self.assertEqual(trace["trace"], [])
        self.assertTrue(any("do not infer an answer" in item for item in trace["follow_up_needed"]))

    def test_empty_query_is_rejected(self):
        with self.assertRaises(ValueError):
            search_documents("   ")

    def test_correction_requires_known_source_and_real_change(self):
        with self.assertRaisesRegex(ValueError, "unknown source_id"):
            propose_correction("DOC-999", "old", "new", "test")
        with self.assertRaisesRegex(ValueError, "must differ"):
            propose_correction("DOC-001", "same", "same", "test")


if __name__ == "__main__":
    unittest.main()
