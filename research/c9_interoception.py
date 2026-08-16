#!/usr/bin/env python3
"""
c9_interoception.py  v1.0.0  â C9 Organism Layer
The "gut brain". Senses C9's internal state and publishes affect signals
to c9_bus.jsonl.  Impossible-to-break design: every sensor has a safe fallback.

Usage:  nohup python3 c9_interoception.py &
"""
import os, sys, json, time, subprocess, re, threading, math, random
from datetime import datetime, timezone

# ââ Config ââââââââââââââââââââââââââââââââââââââââââââââââââ
BUS_PATH        = os.path.expanduser("~/cloud9/c9_bus.jsonl")
LOG_PATH        = os.path.expanduser("~/cloud9/logs/c9_interoception.log")
STATE_PATH      = os.path.expanduser("~/cloud9/memory/interoception_state.json")
HEARTBEAT_SEC   = 60          # publish VITALITY every 60 s
SENSOR_SEC      = 15          # sample sensors every 15 s
BUS_WINDOW      = 3600        # 1 h window for entropy calc
HUNGER_THRESH   = 6 * 3600    # 6 h without novel data
LONELY_THRESH   = 30 * 60     # 30 min silence
CRASH_THRESH    = 3           # 3 crashes in 1 h -> PAIN

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

def safe_read(path, default=""):
    try:
        with open(path) as f:
            return f.read()
    except Exception:
        return default

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
        log(f"WARN: json_dump failed: {e}")

# ââ Bus emitter (atomic append) âââââââââââââââââââââââââââââ
def bus_emit(msg_type, payload):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_module": "c9_interoception",
        "type": msg_type,
        "payload": payload
    }
    try:
        os.makedirs(os.path.dirname(BUS_PATH), exist_ok=True)
        with open(BUS_PATH, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception as e:
        log(f"ERR bus_emit: {e}")

# ââ Sensors (all with fallbacks) ââââââââââââââââââââââââââââ
def get_battery():
    """Try termux-battery-status -> /sys -> fallback 50.0"""
    try:
        out = subprocess.run(
            ["termux-battery-status"], capture_output=True, text=True, timeout=5
        )
        if out.returncode == 0:
            d = json.loads(out.stdout)
            return float(d.get("percentage", 50.0))
    except Exception:
        pass
    try:
        for root, dirs, files in os.walk("/sys/class/power_supply"):
            for f in files:
                if f == "capacity":
                    with open(os.path.join(root, f)) as fh:
                        return float(fh.read().strip())
    except Exception:
        pass
    return 50.0

def get_thermal():
    """Try thermal zones -> fallback 35.0C"""
    try:
        zones = []
        for z in os.listdir("/sys/class/thermal"):
            if z.startswith("thermal_zone"):
                t = safe_read(f"/sys/class/thermal/{z}/temp").strip()
                if t:
                    zones.append(float(t) / 1000.0)
        if zones:
            return max(zones)
    except Exception:
        pass
    return 35.0

def get_ram():
    """Parse /proc/meminfo -> (used%, available_mb)"""
    try:
        data = safe_read("/proc/meminfo")
        total = avail = 0
        for line in data.splitlines():
            if line.startswith("MemTotal:"):
                total = int(line.split()[1])
            elif line.startswith("MemAvailable:"):
                avail = int(line.split()[1])
        if total:
            used_pct = 100.0 * (total - avail) / total
            return round(used_pct, 2), round(avail / 1024.0, 2)
    except Exception:
        pass
    return 50.0, 1024.0

def get_load():
    try:
        return float(safe_read("/proc/loadavg").split()[0])
    except Exception:
        return 0.0

def get_uptime_sec():
    try:
        return float(safe_read("/proc/uptime").split()[0])
    except Exception:
        return 0.0

def get_bus_entropy(window_sec=BUS_WINDOW):
    """Count unique message types in last window_sec."""
    try:
        if not os.path.exists(BUS_PATH):
            return 0.0, 0
        now = time.time()
        types = set()
        count = 0
        with open(BUS_PATH, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 512_000), 0)
            lines = f.read().decode("utf-8", "ignore").splitlines()
        for line in lines:
            try:
                obj = json.loads(line)
                ts = datetime.fromisoformat(obj["timestamp"].replace("Z", "+00:00"))
                if (now - ts.timestamp()) < window_sec:
                    types.add(obj.get("type", "UNKNOWN"))
                    count += 1
            except Exception:
                continue
        return float(len(types)), count
    except Exception:
        return 0.0, 0

def get_module_crashes(window_sec=3600):
    """Scan bus for PAIN or ERROR messages in last hour."""
    try:
        if not os.path.exists(BUS_PATH):
            return 0
        now = time.time()
        crashes = 0
        with open(BUS_PATH, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 256_000), 0)
            lines = f.read().decode("utf-8", "ignore").splitlines()
        for line in lines:
            try:
                obj = json.loads(line)
                if obj.get("type") in ("ERROR", "PAIN", "MODULE_CRASH"):
                    ts = datetime.fromisoformat(obj["timestamp"].replace("Z", "+00:00"))
                    if (now - ts.timestamp()) < window_sec:
                        crashes += 1
            except Exception:
                continue
        return crashes
    except Exception:
        return 0

def get_last_user_interaction():
    """Heuristic: last bus message from user or BIRTH."""
    try:
        if not os.path.exists(BUS_PATH):
            return 0.0
        now = time.time()
        last = 0.0
        with open(BUS_PATH, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 128_000), 0)
            lines = f.read().decode("utf-8", "ignore").splitlines()
        for line in reversed(lines):
            try:
                obj = json.loads(line)
                src = obj.get("source_module", "")
                if src in ("user", "BIRTH", "c9_birth_proxy", "birth_ui"):
                    ts = datetime.fromisoformat(obj["timestamp"].replace("Z", "+00:00"))
                    last = now - ts.timestamp()
                    break
            except Exception:
                continue
        return last
    except Exception:
        return 999999.0

# ââ State persistence ââââââââââââââââââââââââââââââââââââââââ
state = safe_json_load(STATE_PATH, {
    "last_hunger_emit": 0,
    "last_pain_emit": 0,
    "last_lonely_emit": 0,
    "last_curiosity_emit": 0,
    "baseline_entropy": 5.0
})

def save_state():
    safe_json_dump(state, STATE_PATH)

# ââ Main loop âââââââââââââââââââââââââââââââââââââââââââââââ
def sensor_cycle():
    """Runs every SENSOR_SEC. Samples and emits signals."""
    battery = get_battery()
    thermal = get_thermal()
    ram_pct, ram_avail = get_ram()
    load1 = get_load()
    entropy, msg_count = get_bus_entropy()
    crashes = get_module_crashes()
    silence = get_last_user_interaction()
    now = time.time()

    # ââ VITALITY (always) ââ
    synthetic_vitality = min(1.0, (entropy / max(state["baseline_entropy"], 1.0)) * 0.5 +
                                  (1.0 if msg_count > 10 else msg_count / 10.0) * 0.5)
    physical_vitality = min(1.0, (battery / 100.0) * 0.3 +
                                (1.0 - ram_pct / 100.0) * 0.3 +
                                (1.0 if thermal < 60 else max(0, 1.0 - (thermal - 60) / 40)) * 0.2 +
                                (1.0 if load1 < 4.0 else max(0, 1.0 - (load1 - 4.0) / 4.0)) * 0.2)

    bus_emit("INTEROCEPTION_SIGNAL", {
        "signal": "VITALITY",
        "severity": round((synthetic_vitality + physical_vitality) / 2.0, 3),
        "details": {
            "alive_modules": -1,
            "bus_messages_1h": msg_count,
            "synthetic_vitality": round(synthetic_vitality, 3),
            "physical_vitality": round(physical_vitality, 3),
            "battery": battery,
            "thermal_c": thermal,
            "ram_pct": ram_pct,
            "load1": load1
        }
    })

    # ââ HUNGER ââ
    if entropy < state["baseline_entropy"] * 0.5 and (now - state["last_hunger_emit"]) > HUNGER_THRESH:
        state["last_hunger_emit"] = now
        bus_emit("INTEROCEPTION_SIGNAL", {
            "signal": "HUNGER",
            "severity": round(1.0 - entropy / max(state["baseline_entropy"], 1.0), 3),
            "details": {
                "entropy_1h": entropy,
                "baseline": state["baseline_entropy"],
                "recommended_action": "AUTO_RESEARCH",
                "target_domain": random.choice(["cosmo", "bio", "quant", "matsci", "neuro"])
            }
        })
        log(f"HUNGER emitted (entropy={entropy:.1f})")

    # ââ PAIN ââ
    if crashes >= CRASH_THRESH and (now - state["last_pain_emit"]) > 1800:
        state["last_pain_emit"] = now
        bus_emit("INTEROCEPTION_SIGNAL", {
            "signal": "PAIN",
            "severity": min(1.0, crashes / 10.0),
            "details": {
                "crashes_1h": crashes,
                "error_signature": "multiple_module_crashes",
                "recommended_action": "QUARANTINE_AND_HEAL"
            }
        })
        log(f"PAIN emitted (crashes={crashes})")

    # ââ FATIGUE ââ
    fatigue_sev = 0.0
    if ram_pct > 90:
        fatigue_sev = max(fatigue_sev, (ram_pct - 90) / 10.0)
    if thermal > 75:
        fatigue_sev = max(fatigue_sev, (thermal - 75) / 25.0)
    if battery < 20:
        fatigue_sev = max(fatigue_sev, (20 - battery) / 20.0)
    if load1 > 8.0:
        fatigue_sev = max(fatigue_sev, (load1 - 8.0) / 4.0)
    if fatigue_sev > 0.3:
        bus_emit("INTEROCEPTION_SIGNAL", {
            "signal": "FATIGUE",
            "severity": round(fatigue_sev, 3),
            "details": {
                "ram_pct": ram_pct,
                "thermal_c": thermal,
                "battery": battery,
                "load1": load1,
                "recommended_action": "ENTER_DREAM_PHASE"
            }
        })

    # ââ LONELINESS ââ
    if silence > LONELY_THRESH and (now - state["last_lonely_emit"]) > LONELY_THRESH:
        state["last_lonely_emit"] = now
        bus_emit("INTEROCEPTION_SIGNAL", {
            "signal": "LONELINESS",
            "severity": min(1.0, silence / 7200.0),
            "details": {
                "silence_sec": int(silence),
                "last_interaction": datetime.now(timezone.utc).isoformat(),
                "recommended_action": "REACH_OUT"
            }
        })
        log(f"LONELINESS emitted (silence={silence:.0f}s)")

    # ââ CURIOSITY ââ
    curiosity = 0.0
    if msg_count > 5 and entropy > state["baseline_entropy"] * 1.2:
        curiosity = min(1.0, (entropy - state["baseline_entropy"]) / state["baseline_entropy"])
    if curiosity > 0.5 and (now - state["last_curiosity_emit"]) > 3600:
        state["last_curiosity_emit"] = now
        bus_emit("INTEROCEPTION_SIGNAL", {
            "signal": "CURIOSITY",
            "severity": round(curiosity, 3),
            "details": {
                "entropy_1h": entropy,
                "surprise_score": round(curiosity, 3),
                "recommended_action": "HYPOTHESIS_DEBATE"
            }
        })

    state["baseline_entropy"] = 0.99 * state["baseline_entropy"] + 0.01 * entropy
    save_state()

# ââ Graceful shutdown âââââââââââââââââââââââââââââââââââââââ
shutdown = False
def on_sigterm(*_):
    global shutdown
    shutdown = True
    log("SIGTERM received. Shutting down gracefully.")

import signal
signal.signal(signal.SIGTERM, on_sigterm)
signal.signal(signal.SIGINT, on_sigterm)

if __name__ == "__main__":
    log("=== c9_interoception v1.0.0 starting ===")
    save_state()
    while not shutdown:
        try:
            sensor_cycle()
        except Exception as e:
            log(f"CRITICAL sensor_cycle exception: {e}")
        for _ in range(SENSOR_SEC):
            if shutdown:
                break
            time.sleep(1)
    log("=== c9_interoception stopped ===")
