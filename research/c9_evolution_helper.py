#!/usr/bin/env python3
"""
C9 Evolution Helper v2.0
Safe self-modification for BIRTH. Proposal queue, backup/apply/reject.
"""
import json, os, shutil, time
from datetime import datetime, timedelta

PROPOSALS_FILE = os.path.expanduser("~/c9_evolution_proposals.json")
ACTIVITY_LOG = os.path.expanduser("~/birth_activity.log")
BACKUP_DIR = os.path.expanduser("~/c9_evolution_backups")
MAX_QUEUE = 5
ALLOWED_FILES = [
    "birth_throttled.html",
    "birth_unified.html",
    "birth_fast.html",
    "birth_working.html"
]

def ensure_dirs():
    os.makedirs(BACKUP_DIR, exist_ok=True)

def load_proposals():
    """Load all proposals, filtering expired (>24h)."""
    ensure_dirs()
    if not os.path.exists(PROPOSALS_FILE):
        return []
    try:
        with open(PROPOSALS_FILE, "r") as f:
            data = json.load(f)
        now = datetime.now()
        valid = []
        for p in data:
            try:
                ts = datetime.strptime(p.get("timestamp", "2000-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S")
                if now - ts < timedelta(hours=24):
                    valid.append(p)
            except:
                valid.append(p)
        return valid
    except:
        return []

def save_proposals(proposals):
    ensure_dirs()
    with open(PROPOSALS_FILE, "w") as f:
        json.dump(proposals, f, indent=2)

def add_proposal(change_type, file, old_text, new_text, reason, impact=""):
    """Add a new proposal to the queue."""
    proposals = load_proposals()
    pending = [p for p in proposals if p.get("status") == "pending"]
    if len(pending) >= MAX_QUEUE:
        return None
    proposal = {
        "id": f"evo_{int(time.time())}_{len(proposals)}",
        "change_type": change_type,
        "file": file,
        "old_text": old_text,
        "new_text": new_text,
        "reason": reason,
        "impact": impact,
        "status": "pending",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    proposals.append(proposal)
    save_proposals(proposals)
    return proposal

def generate_proposals():
    """Analyze activity log and generate improvement proposals."""
    proposals = load_proposals()
    pending_count = len([p for p in proposals if p.get("status") == "pending"])
    if pending_count >= MAX_QUEUE:
        return 0, 0

    generated = 0
    added = 0

    if os.path.exists(ACTIVITY_LOG):
        try:
            with open(ACTIVITY_LOG, "r") as f:
                lines = f.readlines()[-200:]

            errors = [l for l in lines if "error" in l.lower() or "failed" in l.lower() or "timeout" in l.lower()]
            if len(errors) > 3:
                if not any("concurrency" in p.get("reason", "") for p in proposals):
                    p = add_proposal(
                        "modify", "birth_throttled.html",
                        "const CONCURRENCY = 2;",
                        "const CONCURRENCY = 1; // Reduced due to fetch errors",
                        f"High error rate detected ({len(errors)} failures). Reducing concurrency may improve stability.",
                        "Slower processing, fewer timeouts"
                    )
                    if p: generated += 1; added += 1

            no_resp = [l for l in lines if "No response" in l or "empty response" in l.lower()]
            if len(no_resp) > 2:
                if not any("token" in p.get("reason", "").lower() for p in proposals):
                    p = add_proposal(
                        "modify", "birth_throttled.html",
                        "maxTokens = 300",
                        "maxTokens = 200; // Reduced to prevent timeouts",
                        f"Multiple 'No response' errors ({len(no_resp)}). Reducing token count may help.",
                        "Shorter responses, faster completion"
                    )
                    if p: generated += 1; added += 1

            research = [l for l in lines if "Researching:" in l]
            if len(research) > 5:
                if not any("topic" in p.get("reason", "").lower() for p in proposals):
                    p = add_proposal(
                        "modify", "birth_throttled.html",
                        '"Consciousness studies IIT vs global workspace",',
                        '"Consciousness studies IIT vs global workspace",\n    "Emergent computation in active matter systems",',
                        f"Research cycle has run {len(research)}+ times. Adding new topic to prevent repetition.",
                        "Broader research coverage"
                    )
                    if p: generated += 1; added += 1

        except Exception as e:
            print(f"[Evolution] Error generating proposals: {e}")

    return generated, added

def apply_proposal(proposal_id):
    """Apply a proposal with backup."""
    proposals = load_proposals()
    target = None
    for p in proposals:
        if p.get("id") == proposal_id:
            target = p
            break
    if not target:
        return {"success": False, "message": "Proposal not found"}
    if target.get("status") != "pending":
        return {"success": False, "message": f"Already {target.get('status')}"}

    filename = target.get("file", "")
    if filename not in ALLOWED_FILES:
        return {"success": False, "message": f"File '{filename}' not in allowed list"}

    filepath = os.path.expanduser(f"~/{filename}")
    if not os.path.exists(filepath):
        return {"success": False, "message": f"File not found: {filepath}"}

    try:
        with open(filepath, "r") as f:
            content = f.read()

        backup_name = f"{filename}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        shutil.copy2(filepath, backup_path)

        change_type = target.get("change_type", "replace")
        old_text = target.get("old_text", "")
        new_text = target.get("new_text", "")

        if change_type == "replace":
            if old_text not in content:
                return {"success": False, "message": "Old text not found in file (may have changed already)"}
            content = content.replace(old_text, new_text, 1)
        elif change_type == "append":
            content = content + "\n" + new_text
        elif change_type == "prepend":
            content = new_text + "\n" + content
        else:
            return {"success": False, "message": f"Unknown change type: {change_type}"}

        with open(filepath, "w") as f:
            f.write(content)

        target["status"] = "applied"
        target["applied_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        target["backup"] = backup_path
        save_proposals(proposals)

        return {"success": True, "message": f"Applied. Backup: {backup_path}"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def reject_proposal(proposal_id):
    """Reject a proposal."""
    proposals = load_proposals()
    for p in proposals:
        if p.get("id") == proposal_id:
            p["status"] = "rejected"
            p["rejected_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_proposals(proposals)
            return {"success": True, "message": "Rejected"}
    return {"success": False, "message": "Proposal not found"}

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        proposals = load_proposals()
        pending = [p for p in proposals if p.get("status") == "pending"]
        print(f"Queue: {len(pending)}/5 pending, {len(proposals)} total")
        for p in proposals:
            print(f"  [{p['status']}] {p.get('id', '?')}: {p.get('reason', 'no reason')[:60]}...")
    elif cmd == "clear":
        save_proposals([])
        print("Queue cleared")
    elif cmd == "generate":
        g, a = generate_proposals()
        print(f"Generated {g}, added {a}")
    else:
        print("Usage: python3 c9_evolution_helper.py [status|clear|generate]")
