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
# "confirmation_reported" records only that a caller supplied a claim/reference.
# It deliberately does not assert that notice was delivered or received.
NOTICE_RESULTS = {"drafted", "attempted", "confirmation_reported", "failed"}
CLOSURE_DISPOSITIONS = {
    "withdrawn",
    "out_of_scope",
    "administrative_duplicate",
    "resolved_after_review",
    "other_documented_reason",
}

TRANSITIONS = {
    "referred": {"pending_human_review"},
    "pending_human_review": {"under_review", "closed"},
    "under_review": {"more_evidence_requested", "outcome_recorded", "closed"},
    "more_evidence_requested": {"under_review", "outcome_recorded", "closed"},
    "outcome_recorded": {"notice_issued", "challenge_or_appeal_pending", "closed"},
    "notice_issued": {"challenge_or_appeal_pending", "closed"},
    # A challenge cannot be closed through the generic transition helper.
    # A separately specified challenge-resolution process is required first.
    "challenge_or_appeal_pending": set(),
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
        "notice_confirmation_reference": None,
        "notice_delivery_status": "not_verified",
        "notice_result_history": [],
        "participation_barriers": [],
        "closure_record": None,
        "events": [
            _event("synthetic_fixture", "case_created", "Fictional test fixture", None, "referred")
        ],
        "automated_restriction": False,
        "external_actions": [],
    }


def transition_case(
    case, *, to_status, actor, reason, outcome=None, closure_disposition=None
):
    """Return a transitioned copy; require an explicit record for generic closure."""
    updated = deepcopy(case)
    current = updated.get("status")
    if current not in TRANSITIONS or to_status not in TRANSITIONS[current]:
        raise ValueError(f"invalid transition: {current!r} -> {to_status!r}")

    if to_status == "closed":
        if updated.get("participation_barriers"):
            raise ValueError(
                "cannot close while participation barriers are recorded; "
                "this prototype has no barrier-resolution process"
            )
        if closure_disposition not in CLOSURE_DISPOSITIONS:
            raise ValueError(
                f"closure_disposition must be one of {sorted(CLOSURE_DISPOSITIONS)}"
            )
    elif closure_disposition is not None:
        raise ValueError("closure_disposition may only be supplied when closing a case")

    if to_status == "notice_issued" and updated.get("notice_result") != "drafted":
        raise ValueError("a notice must be drafted before it can be marked notice_issued")

    if to_status == "outcome_recorded":
        if updated.get("outcome") is not None:
            raise ValueError("an existing outcome cannot be overwritten; use a separately reviewed correction process")
        if outcome not in OUTCOMES:
            raise ValueError("a valid outcome category is required")
        updated["outcome"] = {
            "category": outcome,
            "rationale": _required_text("outcome rationale", reason),
        }
    elif outcome is not None:
        raise ValueError("outcome may only be supplied when recording an outcome")

    if to_status == "closed":
        updated["closure_record"] = {
            "disposition": closure_disposition,
            "reason": _required_text("closure reason", reason),
            "participation_barrier_count_at_closure": 0,
            "participation_barrier_resolution_status": "no_barrier_recorded",
            "notice_delivery_status_at_closure": updated.get("notice_delivery_status", "not_verified"),
            "does_not_establish_response_or_waiver": True,
            # Explicit gaps against the fuller design specification. These are
            # limitation labels, not claims that the missing processes exist.
            "outstanding_uncertainty_status": "not_captured_by_prototype",
            "retention_deletion_schedule_status": "not_implemented",
            "post_closure_review_route_status": (
                "separate_request_supported_authorized_reopening_not_implemented"
            ),
        }

    updated["events"].append(
        _event(actor, f"status_transition:{to_status}", reason, current, to_status)
    )
    updated["status"] = to_status
    return updated


def record_participation_barrier(case, *, barrier, actor, reason):
    """Record a process barrier without treating it as evidence or agreement."""
    if case.get("status") == "closed":
        raise ValueError(
            "cannot add a participation barrier to a closed case; "
            "this prototype has no reopening or post-closure review process"
        )
    updated = deepcopy(case)
    barrier_text = _required_text("barrier", barrier)
    event_reason = _required_text("reason", reason)
    actor_text = _required_text("actor", actor)
    updated["participation_barriers"].append({
        "barrier": barrier_text,
        "recorded_by": actor_text,
        "reason": event_reason,
    })
    updated["events"].append(
        _event(actor_text, "participation_barrier_recorded", event_reason,
               updated["status"], updated["status"])
    )
    # Deliberately do not change status, outcome, access, or permissions.
    return updated



POST_CLOSURE_REVIEW_DECISIONS = {
    "accepted_for_reopening_review",
    "reopening_not_warranted",
    "more_information_requested",
    "inconclusive",
}


def create_post_closure_review_request(
    closed_case, *, barrier_or_information, discovered_when,
    requested_review_reason, source_label="synthetic_fixture",
):
    """Create a separate synthetic request linked to a closed case.

    This records a request only. It does not reopen or mutate the original case.
    """
    if not isinstance(closed_case, dict) or not closed_case.get("synthetic_only"):
        raise ValueError("post-closure review request requires a synthetic case record")
    if closed_case.get("status") != "closed" or not isinstance(
        closed_case.get("closure_record"), dict
    ):
        raise ValueError("post-closure review request requires a closed case with a closure record")
    request = {
        "request_id": f"SYN-REVIEW-{uuid4()}",
        "synthetic_only": True,
        "original_case_id": _required_text("case_id", closed_case.get("case_id")),
        "source_label": _required_text("source_label", source_label),
        "barrier_or_new_information": _required_text(
            "barrier_or_information", barrier_or_information
        ),
        "discovered_when": _required_text("discovered_when", discovered_when),
        "requested_review_reason": _required_text(
            "requested_review_reason", requested_review_reason
        ),
        "status": "request_recorded",
        "decision": None,
        "decision_record": None,
        "original_closure_snapshot": deepcopy(closed_case["closure_record"]),
        "original_outcome_snapshot": deepcopy(closed_case.get("outcome")),
        "events": [
            _event(
                "synthetic_fixture", "post_closure_review_request_recorded",
                "Separate request recorded; original case remains closed.",
                "closed", "request_recorded",
            )
        ],
        "automated_restriction": False,
        "external_actions": [],
    }
    return request


def record_post_closure_review_decision(
    request, *, decision, actor, reason, evidence_limitations, next_steps,
    reviewer_conflict_check,
):
    """Record a procedural request decision without reopening the original case."""
    if not isinstance(request, dict) or not request.get("synthetic_only"):
        raise ValueError("a synthetic post-closure review request is required")
    if request.get("status") != "request_recorded":
        raise ValueError("a decision can only be recorded once for a request in request_recorded state")
    if decision not in POST_CLOSURE_REVIEW_DECISIONS:
        raise ValueError(f"decision must be one of {sorted(POST_CLOSURE_REVIEW_DECISIONS)}")
    reason_text = _required_text("reason", reason)
    limitations_text = _required_text("evidence_limitations", evidence_limitations)
    next_steps_text = _required_text("next_steps", next_steps)
    actor_text = _required_text("actor", actor)
    conflict_check_text = _required_text("reviewer_conflict_check", reviewer_conflict_check)
    updated = deepcopy(request)
    updated["decision"] = decision
    updated["status"] = "decision_recorded"
    updated["decision_record"] = {
        "decision": decision,
        "actor_label": actor_text,
        "reason": reason_text,
        "evidence_limitations": limitations_text,
        "next_steps": next_steps_text,
        "reviewer_conflict_check": conflict_check_text,
        "reviewer_conflict_check_status": "reported_not_verified",
        "authority_verified": False,
        "reviewer_independence_verified": False,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "does_not_reopen_original_case": True,
    }
    updated["events"].append(
        _event(
            actor_text, f"post_closure_review_decision:{decision}", reason_text,
            "request_recorded", "decision_recorded",
        )
    )
    # This prototype cannot authenticate authority or alter the linked case.
    return updated



REOPENING_DECISIONS = {"reopening_authorized", "reopening_not_authorized"}


def create_reopening_decision_record(
    request, *, decision, actor, reason, scope,
    evidence_limitations, next_steps, authority_basis, reviewer_conflict_check,
):
    """Record a separate synthetic reopening decision without mutating the case.

    This is a decision-record schema demonstration, not an authorization service.
    Actor identity and authority cannot be verified in this prototype.
    """
    if not isinstance(request, dict) or not request.get("synthetic_only"):
        raise ValueError("a synthetic post-closure review request is required")
    if request.get("status") != "decision_recorded":
        raise ValueError("a post-closure request decision must be recorded first")
    if request.get("decision") != "accepted_for_reopening_review":
        raise ValueError("reopening decision requires acceptance for reopening review")
    if decision not in REOPENING_DECISIONS:
        raise ValueError(f"decision must be one of {sorted(REOPENING_DECISIONS)}")
    return {
        "decision_record_id": f"SYN-REOPEN-{uuid4()}",
        "synthetic_only": True,
        "original_case_id": _required_text("original_case_id", request.get("original_case_id")),
        "request_id": _required_text("request_id", request.get("request_id")),
        "decision": decision,
        "actor_label": _required_text("actor", actor),
        "reason": _required_text("reason", reason),
        "scope": _required_text("scope", scope),
        "evidence_limitations": _required_text("evidence_limitations", evidence_limitations),
        "next_steps": _required_text("next_steps", next_steps),
        "authority_basis": _required_text("authority_basis", authority_basis),
        "reviewer_conflict_check": _required_text("reviewer_conflict_check", reviewer_conflict_check),
        "reviewer_conflict_check_status": "reported_not_verified",
        "authority_verified": False,
        "reviewer_independence_verified": False,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "original_closure_snapshot": deepcopy(request["original_closure_snapshot"]),
        "original_outcome_snapshot": deepcopy(request["original_outcome_snapshot"]),
        "changes_case_status": False,
        "overwrites_original_closure": False,
        "automated_restriction": False,
        "external_actions": [],
        "event": _event(
            actor, f"separate_reopening_decision:{decision}", reason,
            "closed", "closed",
        ),
    }


def record_notice_result(case, *, result, actor, reason, confirmation_reference=None):
    """Record notice metadata; caller-reported confirmation remains unverified."""
    if result not in NOTICE_RESULTS:
        raise ValueError(f"result must be one of {sorted(NOTICE_RESULTS)}")

    status = case.get("status")
    if result == "drafted":
        if status != "outcome_recorded":
            raise ValueError("a notice can only be drafted after an outcome and before issuance")
    elif status != "notice_issued":
        raise ValueError("attempted, confirmation_reported, or failed notice requires notice_issued status")

    if result == "confirmation_reported":
        reference = _required_text("confirmation_reference", confirmation_reference)
    elif confirmation_reference is not None:
        raise ValueError("confirmation_reference may only be supplied for confirmation_reported")
    else:
        reference = None

    actor_text = _required_text("actor", actor)
    reason_text = _required_text("reason", reason)
    updated = deepcopy(case)
    prior_result = updated["notice_result"]
    entry = {
        "result": result,
        "prior_result": prior_result,
        "confirmation_reference": reference,
        "actor": actor_text,
        "reason": reason_text,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "verification_status": "unverified_metadata",
    }
    updated.setdefault("notice_result_history", []).append(entry)
    updated["notice_result"] = result
    updated["notice_confirmation_reference"] = reference
    # Never infer delivery or receipt from caller-supplied metadata.
    updated["notice_delivery_status"] = "not_verified"
    updated["events"].append(
        _event(actor_text, f"notice:{result}", reason_text, updated["status"], updated["status"])
    )
    # The history is ordinary mutable in-memory data, not immutable audit evidence.
    return updated


def record_challenge(case, *, actor, reason):
    """Open a challenge while preserving the original outcome verbatim."""
    if not isinstance(case, dict) or not case.get("synthetic_only"):
        raise ValueError("a synthetic case record is required")
    if case.get("status") not in {"outcome_recorded", "notice_issued"}:
        raise ValueError("a challenge requires a recorded outcome")
    if not isinstance(case.get("outcome"), dict):
        raise ValueError("a challenge requires an existing outcome record")
    updated = deepcopy(case)
    updated["original_outcome"] = deepcopy(updated["outcome"])
    updated["events"].append(
        _event(actor, "challenge_opened", reason, updated["status"],
               "challenge_or_appeal_pending")
    )
    updated["status"] = "challenge_or_appeal_pending"
    return updated
