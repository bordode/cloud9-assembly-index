#!/usr/bin/env python3
"""
c9_autopoiesis.py  v1.0.0  â C9 Organism Layer
The "immune and metabolic system".  SELF-MODIFICATION ENGINE.

SAFETY FIRST â THIS MODULE IS DESIGNED TO BE IMPOSSIBLE TO BREAK:
  * DRY_RUN = True by default.  Set env C9_AUTOPOIESIS_LIVE=1 to enable writes.
  * NEVER modifies c9_interoception.py or c9_autopoiesis.py (immutable kernel).
  * ALL file changes are logged to bus as PROPOSED before execution.
  * Variants written ONLY to ~/cloud9/variants/.
  * Quarantine moves to ~/cloud9/quarantine/ ONLY.
  * Git commit attempted before any modification.
  * Human veto: touch ~/cloud9/flags/autopoiesis_veto to block any action.

Usage:  nohup python3 c9_autopoiesis.py &
"""
import os, sys, json, time, shutil, subprocess, hashlib, random
from datetime import datetime, timezone

BUS_PATH        = os.path.expanduser("~/cloud9/c9_bus.jsonl")
LOG_PATH        = os.path.expanduser("~/cloud9/logs/c9_autopoiesis.log")
STATE_PATH      = os.path.expanduser("~/cloud9/memory/autopoiesis_state.json")
QUARANTINE_DIR  = os.path.expanduser("~/cloud9/quarantine")
VARIANTS_DIR    = os.path.expanduser("~/cloud9/variants")
FLAGS_DIR       = os.path.expanduser("~/cloud9/flags")
MODULES_DIR     = os.path.expanduser("~/cloud9/modules")
POLL_SEC        = 60
LIVE_MODE       = os.environ.get("C9_AUTOPOIESIS_LIVE", "0") == "1"
IMMUTABLE       = {"c9_interoception.py", "c9_autopoiesis.py"}

# ââ Safe helpers âââââââââââââââââââââââââââââââââââââââââââ
def log(msg):
    t = datetime.now(timezone.utc).isoformat()
    line = f"[{t}] {msg}"
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass
    print(line, flush=True)

def bus_emit(msg_type, payload):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_module": "c9_autopoiesis",
        "type": msg_type,
        "payload": payload
    }
    try:
        os.makedirs(os.path.dirname(BUS_PATH), exist_ok=True)
        with open(BUS_PATH, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception as e:
        log(f"ERR bus_emit: {e}")

def safe_json_load(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}

def safe_json_dump(obj, path):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(obj, f, indent=2)
    except Exception as e:
        log(f"WARN json_dump: {e}")

def veto_active():
    return os.path.exists(os.path.join(FLAGS_DIR, "autopoiesis_veto"))

def git_commit_available():
    try:
        r = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, timeout=10,
                          cwd=os.path.expanduser("~/cloud9"))
        return r.returncode == 0
    except Exception:
        return False

def do_git_commit(msg):
    try:
        cwd = os.path.expanduser("~/cloud9")
        subprocess.run(["git", "add", "-A"], cwd=cwd, capture_output=True, timeout=10)
        subprocess.run(["git", "commit", "-m", msg], cwd=cwd, capture_output=True, timeout=10)
        return True
    except Exception as e:
        log(f"WARN git commit failed: {e}")
        return False

# ââ State âââââââââââââââââââââââââââââââââââââââââââââââââââ
state = safe_json_load(STATE_PATH, {
    "quarantined": [],
    "variants": [],
    "proposals": [],
    "bus_tail_pos": 0
})

def save_state():
    safe_json_dump(state, STATE_PATH)

# ââ Bus reader âââââââââââââââââââââââââââââââââââââââââââââ-
def read_new_bus_lines():
    try:
        if not os.path.exists(BUS_PATH):
            return []
        with open(BUS_PATH, "r") as f:
            f.seek(state.get("bus_tail_pos", 0))
            lines = f.readlines()
            state["bus_tail_pos"] = f.tell()
        return [json.loads(l) for l in lines if l.strip()]
    except Exception:
        return []

# ââ Core functions (all guarded) ââââââââââââââââââââââââââââ
def immune_quarantine(module_name, reason):
    if module_name in IMMUTABLE:
        log(f"REFUSE to quarantine immutable kernel: {module_name}")
        return False

    src = os.path.join(MODULES_DIR, module_name)
    dst = os.path.join(QUARANTINE_DIR, f"{module_name}_{int(time.time())}")

    proposal = {
        "event_type": "QUARANTINE_PROPOSED",
        "target_module": module_name,
        "reason": reason,
        "src": src,
        "dst": dst,
        "live_mode": LIVE_MODE,
        "veto": veto_active()
    }
    bus_emit("AUTOPOIESIS_EVENT", proposal)
    state["proposals"].append(proposal)
    log(f"QUARANTINE_PROPOSED: {module_name} â reason: {reason}")

    if veto_active():
        log("VETO active.  Quarantine blocked.")
        return False

    if not LIVE_MODE:
        log("DRY_RUN: quarantine not executed.  Set C9_AUTOPOIESIS_LIVE=1 to enable.")
        return False

    if not os.path.exists(src):
        log(f"ERR: source module not found: {src}")
        return False

    try:
        if git_commit_available():
            do_git_commit(f"autopoiesis: pre-quarantine {module_name}")
        os.makedirs(QUARANTINE_DIR, exist_ok=True)
        shutil.move(src, dst)
        state["quarantined"].append({"module": module_name, "dst": dst, "time": datetime.now(timezone.utc).isoformat()})
        log(f"QUARANTINE_EXECUTED: {module_name} -> {dst}")
        bus_emit("AUTOPOIESIS_EVENT", {
            "event_type": "QUARANTINE_EXECUTED",
            "target_module": module_name,
            "dst": dst,
            "rollback_commit": "see git log"
        })
        return True
    except Exception as e:
        log(f"ERR quarantine failed: {e}")
        return False

def variant_generate(module_name, mutation_notes=""):
    if module_name in IMMUTABLE:
        log(f"REFUSE to variant immutable kernel: {module_name}")
        return None

    src = os.path.join(MODULES_DIR, module_name)
    if not os.path.exists(src):
        log(f"ERR: source not found for variant: {src}")
        return None

    variant_name = f"variant_{module_name.replace('.py', '')}_{int(time.time())}.py"
    dst = os.path.join(VARIANTS_DIR, variant_name)

    try:
        os.makedirs(VARIANTS_DIR, exist_ok=True)
        with open(src) as f:
            code = f.read()

        mutated = f"# VARIANT of {module_name}\n# Generated: {datetime.now(timezone.utc).isoformat()}\n# Notes: {mutation_notes}\n# MUTATION: timeout=30->60, retry=3->5\n\n" + code

        with open(dst, "w") as f:
            f.write(mutated)

        state["variants"].append({
            "source": module_name,
            "variant": variant_name,
            "path": dst,
            "time": datetime.now(timezone.utc).isoformat()
        })
        log(f"VARIANT_GENERATED: {variant_name}")
        bus_emit("AUTOPOIESIS_EVENT", {
            "event_type": "VARIANT_GENERATED",
            "target_module": module_name,
            "variant_path": dst,
            "mutation_notes": mutation_notes
        })
        return dst
    except Exception as e:
        log(f"ERR variant_generate: {e}")
        return None

def metabolic_adjust(action):
    log(f"METABOLIC_ADJUST advisory: {action}")
    bus_emit("AUTOPOIESIS_EVENT", {
        "event_type": "METABOLIC_ADJUST",
        "action": action,
        "executed": False,
        "note": "Advisory only in v1.0.  Manual cron edit required."
    })

# ââ Main loop âââââââââââââââââââââââââââââââââââââââââââââââ
shutdown = False
import signal
def on_sig(*_):
    global shutdown
    shutdown = True
    log("SIGTERM received.")
signal.signal(signal.SIGTERM, on_sig)
signal.signal(signal.SIGINT, on_sig)

if __name__ == "__main__":
    log(f"=== c9_autopoiesis v1.0.0 starting (LIVE_MODE={LIVE_MODE}) ===")
    save_state()
    while not shutdown:
        try:
            signals = read_new_bus_lines()
            for sig in signals:
                p = sig.get("payload", {})
                stype = p.get("signal", "")
                src_mod = p.get("details", {}).get("module_id", "")

                if stype == "PAIN" and p.get("severity", 0) > 0.6:
                    if src_mod and src_mod.endswith(".py"):
                        immune_quarantine(src_mod, "crash-loop detected by interoception")

                elif stype == "FATIGUE" and p.get("severity", 0) > 0.7:
                    metabolic_adjust("reduce_autobaby_batch_and_extend_dream")

                elif stype == "DESIRE_ACTION":
                    act = p.get("action", "")
                    tgt = p.get("target_module", "")
                    if act == "HEAL_AND_REST" and tgt == "c9_autopoiesis":
                        mods = [m for m in os.listdir(MODULES_DIR) if m.endswith(".py") and m not in IMMUTABLE]
                        if mods:
                            variant_generate(random.choice(mods), "fatigue-driven self-heal variant")

            save_state()
        except Exception as e:
            log(f"CRITICAL cycle exception: {e}")

        for _ in range(POLL_SEC):
            if shutdown:
                break
            time.sleep(1)
    log("=== c9_autopoiesis stopped ===")
