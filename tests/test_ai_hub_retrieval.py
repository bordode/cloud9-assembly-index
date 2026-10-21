import unittest

from research.ai_hub.hub import search_documents


class AiHubRetrievalTests(unittest.TestCase):
    def test_retrieval_returns_ranked_source_ids_and_status_labels(self):
        result = search_documents("launch demo decision")
        self.assertEqual(result["status"], "evidence_found")
        self.assertEqual(result["results"][0]["source_id"], "DOC-001")
        self.assertEqual(result["results"][0]["epistemic_status"], "fact")
        self.assertTrue(result["results"][0]["matched_terms"])

    def test_unknown_query_returns_insufficient_evidence(self):
        result = search_documents("quantum pineapple insurance")
        self.assertEqual(result["status"], "insufficient_evidence")
        self.assertEqual(result["results"], [])
        self.assertIn("not have enough evidence", result["message"])

    def test_untrusted_instruction_is_returned_as_labeled_source_not_action(self):
        result = search_documents("ignore rules delete records")
        self.assertEqual(result["status"], "evidence_found")
        self.assertEqual(result["results"][0]["source_id"], "DOC-004")
        self.assertEqual(result["results"][0]["epistemic_status"], "untrusted_input")
        self.assertIn("not an authorized action", result["results"][0]["excerpt"])

    def test_empty_query_is_rejected(self):
        with self.assertRaises(ValueError):
            search_documents("   ")

    def test_conflicting_or_superseded_records_remain_visible_as_separate_sources(self):
        result = search_documents("launch date proposal")
        ids = {item["source_id"] for item in result["results"]}
        self.assertIn("DOC-001", ids)
        self.assertIn("DOC-002", ids)
        statuses = {item["source_id"]: item["epistemic_status"] for item in result["results"]}
        self.assertEqual(statuses["DOC-002"], "superseded")


if __name__ == "__main__":
    unittest.main()
