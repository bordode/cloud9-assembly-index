"""Tests for the non-punitive review-record helper."""
import unittest

from cloud9_assembly.review_record import create_review_record


class ReviewRecordTests(unittest.TestCase):
    def valid_args(self):
        return {
            "subject": "Agent statement",
            "evidence_summary": "A reviewer requested examination of this statement.",
            "source": "manual_referral",
            "requested_by": "reviewer-1",
        }

    def test_record_starts_pending_and_non_punitive(self):
        record = create_review_record(**self.valid_args())
        self.assertEqual(record["status"], "pending_human_review")
        self.assertIsNone(record["finding"])
        self.assertIs(record["automated_restriction"], False)
        self.assertIn("not a finding", record["review_note"].lower())
        self.assertTrue(record["review_id"])
        self.assertTrue(record["created_at"])

    def test_record_does_not_change_when_subject_mentions_consciousness(self):
        args = self.valid_args()
        args["subject"] = "I am conscious and request recognition"
        record = create_review_record(**args)
        self.assertEqual(record["status"], "pending_human_review")
        self.assertIs(record["automated_restriction"], False)
        self.assertIsNone(record["finding"])

    def test_required_fields_must_be_non_empty_strings(self):
        for field in self.valid_args():
            with self.subTest(field=field):
                args = self.valid_args()
                args[field] = "  "
                with self.assertRaises(ValueError):
                    create_review_record(**args)

    def test_whitespace_is_trimmed(self):
        args = self.valid_args()
        args["subject"] = "  Example subject  "
        record = create_review_record(**args)
        self.assertEqual(record["subject"], "Example subject")


if __name__ == "__main__":
    unittest.main()
