#!/usr/bin/env python3
"""
c9_desire.py  v1.0.0  â C9 Organism Layer
The "limbic system". Maintains 4-drive vector, reads interoception
from bus, publishes DESIRE_ACTION.  TD-learning with tiny alpha.

Usage:  nohup python3 c9_desire.py &
"""
import os, sys, json, time, math, random
from datetime import datetime, timezone

BUS_PATH   = os.path.expanduser("~/cloud9/c9_bus.jsonl")
LOG_PATH   = os.path.expanduser("~/cloud9/logs/c9_desire.log")
STATE_PATH = os.path.expanduser("~/cloud9/memory/desire_state.json")
POLL_SEC   = 30
ALPHA      = 0.01   # TD learning rate

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

def bus_emit(msg_type, payload):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_module": "c9_desire",
        "type": msg_type,
        "payload": payload
    }
    try:
        os.makedirs(os.path.dirname(BUS_PATH), exist_ok=True)
        with open(BUS_PATH, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception as e:
        log(f"ERR bus_emit: {e}")

# ââ State âââââââââââââââââââââââââââââââââââââââââââââââââââ
state = safe_json_load(STATE_PATH, {
    "drives": {
        "novelty":     {"weight": 0.30, "satisfaction": 0.5, "last_reward": 0.0},
        "coherence":   {"weight": 0.25, "satisfaction": 0.5, "last_reward": 0.0},
        "survival":    {"weight": 0.25, "satisfaction": 0.5, "last_reward": 0.0},
        "reproduction":{"weight": 0.20, "satisfaction": 0.5, "last_reward": 0.0}
    },
    "last_action": None,
    "last_action_time": 0,
    "bus_tail_pos": 0
})

def save_state():
    safe_json_dump(state, STATE_PATH)

# ââ Bus tail reader âââââââââââââââââââââââââââââââââââââââââ
def read_new_bus_lines():
    try:
        if not os.path.exists(BUS_PATH):
            return []
        with open(BUS_PATH, "r") as f:
            f.seek(state.get("bus_tail_pos", 0))
            lines = f.readlines()
            state["bus_tail_pos"] = f.tell()
        return [json.loads(l) for l in lines if l.strip()]
    except Exception as e:
        log(f"WARN bus read: {e}")
        return []

# ââ Drive update logic ââââââââââââââââââââââââââââââââââââââ
def update_drives(signals):
    d = state["drives"]
    for sig in signals:
        p = sig.get("payload", {})
        s_type = p.get("signal", "")
        sev    = p.get("severity", 0.0)

        if s_type == "VITALITY":
            vit = p.get("details", {})
            syn = vit.get("synthetic_vitality", 0.5)
            phys = vit.get("physical_vitality", 0.5)
            d["survival"]["satisfaction"] = 0.9 * d["survival"]["satisfaction"] + 0.1 * ((syn + phys) / 2.0)
            d["novelty"]["satisfaction"]  = 0.9 * d["novelty"]["satisfaction"]  + 0.1 * syn
        elif s_type == "HUNGER":
            d["novelty"]["satisfaction"] = max(0.0, d["novelty"]["satisfaction"] - 0.1)
        elif s_type == "CURIOSITY":
            d["novelty"]["satisfaction"] = min(1.0, d["novelty"]["satisfaction"] + 0.05 * sev)
        elif s_type == "PAIN":
            d["survival"]["satisfaction"] = max(0.0, d["survival"]["satisfaction"] - 0.15 * sev)
        elif s_type == "FATIGUE":
            d["survival"]["satisfaction"] = max(0.0, d["survival"]["satisfaction"] - 0.1 * sev)
        elif s_type == "LONELINESS":
            d["reproduction"]["satisfaction"] = max(0.0, d["reproduction"]["satisfaction"] - 0.1 * sev)

    for k in d:
        d[k]["satisfaction"] = 0.995 * d[k]["satisfaction"] + 0.005 * 0.5

# ââ Action selection (active inference lite) âââââââââââââââ
def select_action():
    d = state["drives"]
    deficits = {k: d[k]["weight"] * (1.0 - d[k]["satisfaction"]) for k in d}
    worst = max(deficits, key=deficits.get)
    deficit_val = deficits[worst]
    if deficit_val < 0.05:
        return None

    action_map = {
        "novelty":      {"action": "TRIGGER_AUTOBABY",     "target": "c9_autobaby",          "risk": 0.1},
        "coherence":    {"action": "FORCE_DEBATE",         "target": "c9_hypothesis_debate", "risk": 0.2},
        "survival":     {"action": "HEAL_AND_REST",        "target": "c9_autopoiesis",       "risk": 0.05},
        "reproduction": {"action": "COMMIT_AND_SIGNAL",    "target": "c9_phenotype",         "risk": 0.15}
    }
    act = action_map.get(worst, {"action": "NONE", "target": "none", "risk": 0.0})
    act["drive"] = worst
    act["deficit"] = round(deficit_val, 3)
    act["expected_reward"] = round(d[worst]["satisfaction"] + ALPHA * deficit_val, 3)
    return act

def td_update(action, outcome_reward):
    drive = action.get("drive", "novelty")
    old = state["drives"][drive]["satisfaction"]
    state["drives"][drive]["satisfaction"] = old + ALPHA * (outcome_reward - old)
    state["drives"][drive]["last_reward"] = outcome_reward

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
    log("=== c9_desire v1.0.0 starting ===")
    save_state()
    cycle = 0
    while not shutdown:
        cycle += 1
        try:
            signals = read_new_bus_lines()
            if signals:
                update_drives(signals)

            if cycle % 2 == 0:
                action = select_action()
                if action:
                    bus_emit("DESIRE_ACTION", {
                        "drive": action["drive"],
                        "action": action["action"],
                        "target_module": action["target"],
                        "expected_reward": action["expected_reward"],
                        "risk_score": action["risk"],
                        "rationale": f"{action['drive']} deficit={action['deficit']}"
                    })
                    log(f"DESIRE_ACTION: {action['action']} for {action['drive']} (deficit={action['deficit']})")
                    state["last_action"] = action
                    state["last_action_time"] = time.time()

            if cycle % 10 == 0 and state["last_action"]:
                drive = state["last_action"]["drive"]
                sat = state["drives"][drive]["satisfaction"]
                td_update(state["last_action"], sat)

            save_state()
        except Exception as e:
            log(f"CRITICAL cycle exception: {e}")

        for _ in range(POLL_SEC):
            if shutdown:
                break
            time.sleep(1)
    log("=== c9_desire stopped ===")
