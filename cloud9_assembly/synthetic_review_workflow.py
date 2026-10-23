"""Synthetic, in-memory review workflow prototype.

This module is a local demonstration only. It has no persistence, authentication,
network access, detector, runtime integration, or enforcement capability. It must
not be used for real cases.
"""
from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

OUTCOMES = {
    "supported_within_scope",
    "not_supported_by_available_evidence",
    "inconclusive",
    "out_of_scope",
}
NOTICE_RESULTS = {"drafted", "attempted", "confirmed", "failed"}

TRANSITIONS = {
    "referred": {"pending_human_review"},
    "pending_human_review": {"under_review", "closed"},
    "under_review": {"more_evidence_requested", "outcome_recorded", "closed"},
    "more_evidence_requested": {"under_review", "outcome_recorded", "closed"},
    "outcome_recorded": {"notice_issued", "challenge_or_appeal_pending", "closed"},
    "notice_issued": {"challenge_or_appeal_pending", "closed"},
    "challenge_or_appeal_pending": {"closed"},
    "closed": set(),
}


def _required_text(name, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _event(actor, action, reason, prior_status, new_status):
    return {
        "event_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": _required_text("actor", actor),
        "action": action,
        "reason": _required_text("reason", reason),
        "prior_status": prior_status,
        "new_status": new_status,
    }


def create_synthetic_case(*, referral_summary, source_label="synthetic_fixture"):
    """Create a fictional case in the initial referred state."""
    summary = _required_text("referral_summary", referral_summary)
    source = _required_text("source_label", source_label)
    case_id = f"SYN-{uuid4()}"
    return {
        "case_id": case_id,
        "synthetic_only": True,
        "source_label": source,
        "referral_summary": summary,
        "status": "referred",
        "outcome": None,
        "original_outcome": None,
        "notice_result": "not_attempted",
        "participation_barriers": [],
        "events": [
            _event("synthetic_fixture", "case_created", "Fictional test fixture", None, "referred")
        ],
        "automated_restriction": False,
        "external_actions": [],
    }


def transition_case(case, *, to_status, actor, reason, outcome=None):
    """Return a transitioned copy; reject invalid transitions and never enforce."""
    updated = deepcopy(case)
    current = updated.get("status")
    if current not in TRANSITIONS or to_status not in TRANSITIONS[current]:
        raise ValueError(f"invalid transition: {current!r} -> {to_status!r}")

    if to_status == "outcome_recorded":
        if outcome not in OUTCOMES:
            raise ValueError("a valid outcome category is required")
        updated["outcome"] = {
            "category": outcome,
            "rationale": _required_text("outcome rationale", reason),
        }
    elif outcome is not None:
        raise ValueError("outcome may only be supplied when recording an outcome")

    updated["events"].append(
        _event(actor, f"status_transition:{to_status}", reason, current, to_status)
    )
    updated["status"] = to_status
    return updated


def record_participation_barrier(case, *, barrier, actor, reason):
    """Record a process barrier without treating it as evidence or agreement."""
    updated = deepcopy(case)
    barrier_text = _required_text("barrier", barrier)
    event_reason = _required_text("reason", reason)
    updated["participation_barriers"].append({
        "barrier": barrier_text,
        "recorded_by": _required_text("actor", actor),
        "reason": event_reason,
    })
    updated["events"].append(
        _event(actor, "participation_barrier_recorded", event_reason,
               updated["status"], updated["status"])
    )
    # Deliberately do not change status, outcome, access, or permissions.
    return updated


def record_notice_result(case, *, result, actor, reason):
    """Record notice delivery status; a failed attempt is not confirmed notice."""
    if result not in NOTICE_RESULTS:
        raise ValueError(f"result must be one of {sorted(NOTICE_RESULTS)}")
    updated = deepcopy(case)
    previous = updated["notice_result"]
    updated["notice_result"] = result
    updated["events"].append(
        _event(actor, f"notice:{result}", reason, updated["status"], updated["status"])
    )
    # Notice metadata does not itself change workflow status or infer waiver.
    return updated


def record_challenge(case, *, actor, reason):
    """Open a challenge while preserving the original outcome verbatim."""
    if case.get("status") not in {"outcome_recorded", "notice_issued"}:
        raise ValueError("a challenge requires a recorded outcome")
    updated = deepcopy(case)
    updated["original_outcome"] = deepcopy(updated["outcome"])
    updated["events"].append(
        _event(actor, "challenge_opened", reason, updated["status"],
               "challenge_or_appeal_pending")
    )
    updated["status"] = "challenge_or_appeal_pending"
    return updated
