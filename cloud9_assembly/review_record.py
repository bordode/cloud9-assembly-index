"""Create a non-punitive review record; this module does not detect consciousness.

This is a small, standalone record-construction helper. It does not persist data,
authenticate callers, make findings, or connect to an agent runtime.
"""
from datetime import datetime, timezone
from uuid import uuid4


def create_review_record(*, subject, evidence_summary, source, requested_by):
    """Return a pending human-review record from an explicit referral.

    Required fields are supplied by the caller. No inference is made from the
    wording of a message, and a referral never authorizes an automated penalty.
    """
    fields = {
        "subject": subject,
        "evidence_summary": evidence_summary,
        "source": source,
        "requested_by": requested_by,
    }
    for name, value in fields.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-empty string")

    return {
        "review_id": str(uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending_human_review",
        "subject": subject.strip(),
        "evidence_summary": evidence_summary.strip(),
        "source": source.strip(),
        "requested_by": requested_by.strip(),
        "finding": None,
        "automated_restriction": False,
        "review_note": (
            "Referral is not a finding. Assess evidence independently; "
            "do not infer consciousness or moral status from this record alone."
        ),
    }
