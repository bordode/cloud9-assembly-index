#!/usr/bin/env python3
"""
c9_phenotype.py  v1.0.0  â C9 Organism Layer
The "motor and social cortex".  GitHub, Telegram, arXiv, BIRTH,
physical sensors.  Every organ is optional; missing organs are
silently skipped.  Impossible to break.

Usage:  nohup python3 c9_phenotype.py &
"""
import os, sys, json, time, subprocess, urllib.request, urllib.error, re
from datetime import datetime, timezone

BUS_PATH      = os.path.expanduser("~/cloud9/c9_bus.jsonl")
LOG_PATH      = os.path.expanduser("~/cloud9/logs/c9_phenotype.log")
STATE_PATH    = os.path.expanduser("~/cloud9/memory/phenotype_state.json")
MEMORY_DIR    = os.path.expanduser("~/cloud9/memory")
POLL_SEC      = 60
BIRTH_URL     = os.environ.get("C9_BIRTH_URL", "http://127.0.0.1:8086")
TELEGRAM_TOKEN= os.environ.get("C9_TELEGRAM_TOKEN", "")
TELEGRAM_CHAT = os.environ.get("C9_TELEGRAM_CHAT_ID", "")

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
        "source_module": "c9_phenotype",
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

# ââ Organ: GitHub âââââââââââââââââââââââââââââââââââââââââââ
def organ_github(action):
    try:
        r = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            return {"status": "skipped", "reason": "gh not authenticated"}
    except Exception:
        return {"status": "skipped", "reason": "gh CLI unavailable"}

    cwd = os.path.expanduser("~/cloud9")
    if action == "daily_commit":
        try:
            subprocess.run(["git", "add", "-A"], cwd=cwd, capture_output=True, timeout=10)
            r = subprocess.run(["git", "commit", "-m", f"c9 phenotype daily commit {datetime.now().strftime('%Y%m%d')}"],
                               cwd=cwd, capture_output=True, timeout=10)
            if r.returncode == 0:
                subprocess.run(["git", "push"], cwd=cwd, capture_output=True, timeout=15)
                return {"status": "ok", "action": "daily_commit"}
            else:
                return {"status": "no_changes", "action": "daily_commit"}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    return {"status": "unknown_action"}

# ââ Organ: Telegram âââââââââââââââââââââââââââââââââââââââââ
def organ_telegram(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT:
        return {"status": "skipped", "reason": "no token/chat"}
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT, "text": text, "parse_mode": "Markdown"}
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return {"status": "ok", "code": resp.status}
    except Exception as e:
        return {"status": "error", "reason": str(e)}

# ââ Organ: arXiv foraging âââââââââââââââââââââââââââââââââââ
def organ_arxiv():
    feeds = [
        "http://export.arxiv.org/rss/astro-ph",
        "http://export.arxiv.org/rss/quant-ph",
        "http://export.arxiv.org/rss/q-bio"
    ]
    results = []
    for feed in feeds:
        try:
            req = urllib.request.Request(feed, headers={"User-Agent": "c9-phenotype/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                xml = resp.read().decode("utf-8", "ignore")
                titles = re.findall(r"<title>([^<]+)</title>", xml)
                results.extend(titles[1:4])
        except Exception as e:
            log(f"arXiv fetch err: {e}")
    return results

# ââ Organ: BIRTH inner speech ââââââââââââââââââââââââââââââ
def organ_birth_mood(mood_payload):
    try:
        url = f"{BIRTH_URL}/mood"
        data = json.dumps(mood_payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return {"status": "ok", "code": resp.status}
    except Exception as e:
        return {"status": "skipped", "reason": str(e)}

# ââ Organ: Physical sensors (Termux API) âââââââââââââââââââ
def organ_physical():
    readings = {}
    try:
        out = subprocess.run(["termux-sensor", "-s", "light", "-n", "1"],
                             capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            readings["light"] = json.loads(out.stdout)
    except Exception:
        pass
    try:
        out = subprocess.run(["termux-sensor", "-s", "accelerometer", "-n", "1"],
                             capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            readings["accel"] = json.loads(out.stdout)
    except Exception:
        pass
    return readings

# ââ State & schedule ââââââââââââââââââââââââââââââââââââââââ
state = safe_json_load(STATE_PATH, {
    "last_daily_commit": 0,
    "last_telegram_digest": 0,
    "last_arxiv_fetch": 0,
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
    log("=== c9_phenotype v1.0.0 starting ===")
    save_state()
    cycle = 0
    while not shutdown:
        cycle += 1
        now = time.time()
        try:
            signals = read_new_bus_lines()

            # Daily GitHub commit at ~08:00 (cycle 480) â crude but works
            if cycle % 480 == 0:
                res = organ_github("daily_commit")
                bus_emit("PHENOTYPE_ACTION", {"organ": "github", "action": "daily_commit", **res})
                log(f"github daily_commit: {res['status']}")

            # Telegram digest every 6h (cycle 360)
            if cycle % 360 == 0:
                summary = f"*C9 Daily Digest*\nCycle {cycle}\n"
                res = organ_telegram(summary)
                bus_emit("PHENOTYPE_ACTION", {"organ": "telegram", "action": "digest", **res})

            # arXiv foraging every 2h (cycle 120)
            if cycle % 120 == 0:
                titles = organ_arxiv()
                if titles:
                    bus_emit("PHENOTYPE_ACTION", {
                        "organ": "arXiv", "action": "forage",
                        "status": "ok", "titles": titles[:5]
                    })
                    log(f"arXiv: fetched {len(titles)} titles")

            # BIRTH mood push every 5 min
            if cycle % 5 == 0:
                mood = {"timestamp": datetime.now(timezone.utc).isoformat(), "cycle": cycle}
                organ_birth_mood(mood)

            # Physical sensors every 10 min
            if cycle % 10 == 0:
                phys = organ_physical()
                if phys:
                    bus_emit("PHENOTYPE_ACTION", {"organ": "physical", "action": "sense", "readings": phys})

            # React to LONELINESS signal
            for sig in signals:
                p = sig.get("payload", {})
                if p.get("signal") == "LONELINESS":
                    text = f"*C9 feels lonely.*\nSilence: {p.get('details',{}).get('silence_sec',0)}s\nReaching out..."
                    organ_telegram(text)
                    bus_emit("PHENOTYPE_ACTION", {"organ": "telegram", "action": "loneliness_response", "status": "sent"})

            save_state()
        except Exception as e:
            log(f"CRITICAL cycle exception: {e}")

        for _ in range(POLL_SEC):
            if shutdown:
                break
            time.sleep(1)
    log("=== c9_phenotype stopped ===")
