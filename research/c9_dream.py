#!/usr/bin/env python3
"""
c9_dream.py  v1.0.0  â C9 Organism Layer
The "sleep cycle".  Consolidates bus logs into knowledge graph,
prunes low-activation nodes, detects cross-domain patterns,
emits DREAM_NARRATIVE and DREAM_SEED.

Runs nightly 02:00â04:00 OR when triggered by file flag.
Safe: read-only on live modules; only writes to its own memory/ dir.

Usage:  nohup python3 c9_dream.py &
        touch ~/cloud9/flags/trigger_dream   # manual trigger
"""
import os, sys, json, time, re, math, random
from datetime import datetime, timezone, timedelta

BUS_PATH      = os.path.expanduser("~/cloud9/c9_bus.jsonl")
LOG_PATH      = os.path.expanduser("~/cloud9/logs/c9_dream.log")
MEMORY_DIR    = os.path.expanduser("~/cloud9/memory")
FLAG_PATH     = os.path.expanduser("~/cloud9/flags/trigger_dream")
GRAPH_PATH    = os.path.join(MEMORY_DIR, "knowledge_graph.jsonl")
SEEDS_PATH    = os.path.join(MEMORY_DIR, "dream_seeds.json")
NARRATIVE_PATH= os.path.join(MEMORY_DIR, f"dream_narrative_{datetime.now().strftime('%Y%m%d')}.txt")
SLEEP_HOUR    = 2
WAKE_HOUR     = 4
CHECK_SEC     = 60

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
        "source_module": "c9_dream",
        "type": msg_type,
        "payload": payload
    }
    try:
        os.makedirs(os.path.dirname(BUS_PATH), exist_ok=True)
        with open(BUS_PATH, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception as e:
        log(f"ERR bus_emit: {e}")

# ââ Knowledge graph helpers âââââââââââââââââââââââââââââââââ
def load_graph():
    nodes = {}
    edges = []
    if not os.path.exists(GRAPH_PATH):
        return nodes, edges
    try:
        with open(GRAPH_PATH) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                if obj.get("kind") == "node":
                    nodes[obj["id"]] = obj
                elif obj.get("kind") == "edge":
                    edges.append(obj)
    except Exception as e:
        log(f"WARN graph load: {e}")
    return nodes, edges

def save_graph(nodes, edges):
    try:
        os.makedirs(os.path.dirname(GRAPH_PATH), exist_ok=True)
        with open(GRAPH_PATH, "w") as f:
            for nid, n in nodes.items():
                f.write(json.dumps({"kind": "node", **n}) + "\n")
            for e in edges:
                f.write(json.dumps({"kind": "edge", **e}) + "\n")
    except Exception as e:
        log(f"WARN graph save: {e}")

# ââ Dream phases ââââââââââââââââââââââââââââââââââââââââââââ
def phase_ingest(window_hours=24):
    log("DREAM PHASE: INGEST")
    cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
    messages = []
    try:
        if not os.path.exists(BUS_PATH):
            return messages
        with open(BUS_PATH, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 1_048_576), 0)
            for line in f:
                try:
                    obj = json.loads(line.decode("utf-8", "ignore"))
                    ts = datetime.fromisoformat(obj["timestamp"].replace("Z", "+00:00"))
                    if ts >= cutoff:
                        messages.append(obj)
                except Exception:
                    continue
    except Exception as e:
        log(f"WARN ingest: {e}")
    log(f"  ingested {len(messages)} messages")
    return messages

def phase_graph_update(messages, nodes, edges):
    log("DREAM PHASE: GRAPH_UPDATE")
    clusters = ["cosmo", "bio", "quant", "matsci", "neuro", "physics", "medicine"]
    for msg in messages:
        txt = json.dumps(msg).lower()
        found = [c for c in clusters if c in txt]
        mid = msg.get("source_module", "unknown") + "_" + msg.get("type", "unknown")
        if mid not in nodes:
            nodes[mid] = {"id": mid, "activation": 0.1, "clusters": list(set(found)), "last_seen": msg["timestamp"]}
        else:
            nodes[mid]["activation"] = min(1.0, nodes[mid]["activation"] + 0.05)
            nodes[mid]["last_seen"] = msg["timestamp"]
            nodes[mid]["clusters"] = list(set(nodes[mid].get("clusters", []) + found))

    for i, m1 in enumerate(messages):
        for m2 in messages[i+1:i+20]:
            s1 = m1.get("source_module", "?")
            s2 = m2.get("source_module", "?")
            if s1 != s2:
                eid = tuple(sorted([s1, s2]))
                exists = False
                for e in edges:
                    if e.get("src") == eid[0] and e.get("dst") == eid[1]:
                        e["weight"] = min(1.0, e.get("weight", 0) + 0.01)
                        e["last_cooccur"] = datetime.now(timezone.utc).isoformat()
                        exists = True
                        break
                if not exists:
                    edges.append({
                        "src": eid[0], "dst": eid[1],
                        "weight": 0.05,
                        "last_cooccur": datetime.now(timezone.utc).isoformat()
                    })
    log(f"  nodes={len(nodes)} edges={len(edges)}")
    return nodes, edges

def phase_prune(nodes, edges, threshold=0.05):
    log("DREAM PHASE: PRUNE")
    before = len(nodes)
    nodes = {k: v for k, v in nodes.items() if v.get("activation", 0) >= threshold}
    alive = set(nodes.keys())
    edges = [e for e in edges if e["src"] in alive and e["dst"] in alive]
    log(f"  pruned {before - len(nodes)} nodes, {len(edges)} edges remain")
    return nodes, edges

def phase_pattern_synthesis(nodes, edges):
    log("DREAM PHASE: PATTERN_SYNTHESIS")
    patterns = []
    for e in edges:
        if e.get("weight", 0) < 0.1:
            continue
        n1 = nodes.get(e["src"], {})
        n2 = nodes.get(e["dst"], {})
        c1 = set(n1.get("clusters", []))
        c2 = set(n2.get("clusters", []))
        shared = c1 & c2
        bridge = (c1 | c2) - shared
        if len(bridge) >= 2:
            patterns.append({
                "modules": [e["src"], e["dst"]],
                "clusters": list(bridge),
                "weight": e["weight"],
                "type": "cross_cluster_bridge"
            })
    seen = set()
    uniq = []
    for p in patterns:
        key = tuple(sorted(p["modules"]))
        if key not in seen:
            seen.add(key)
            uniq.append(p)
    log(f"  found {len(uniq)} cross-cluster patterns")
    return uniq

def phase_wake(patterns, nodes):
    log("DREAM PHASE: WAKE")
    narrative = f"""DREAM NARRATIVE â {datetime.now(timezone.utc).isoformat()}
============================================================
C9 slept. C9 dreamed.

During the last cycle, {len(nodes)} cognitive nodes flickered.
Cross-cluster bridges detected: {len(patterns)}

"""
    seeds = []
    for i, p in enumerate(patterns[:5]):
        narrative += f"\nPattern {i+1}: {p['modules']} bridge clusters {p['clusters']} (weight={p['weight']:.2f})\n"
        seeds.append({
            "hypothesis": f"Investigate connection between {p['clusters'][0]} and {p['clusters'][1]} via {p['modules'][0]}",
            "clusters": p["clusters"],
            "priority": round(p["weight"] * 10, 2),
            "origin_dream": datetime.now().strftime("%Y%m%d")
        })

    if not patterns:
        narrative += "\nNo strong patterns emerged. The mind was quiet.\n"
        seeds.append({
            "hypothesis": "Explore under-sampled domain to increase cross-cluster entropy",
            "clusters": ["unknown"],
            "priority": 3.0,
            "origin_dream": datetime.now().strftime("%Y%m%d")
        })

    narrative += "\n============================================================\n"

    try:
        os.makedirs(os.path.dirname(NARRATIVE_PATH), exist_ok=True)
        with open(NARRATIVE_PATH, "w") as f:
            f.write(narrative)
    except Exception as e:
        log(f"WARN narrative write: {e}")

    safe_json_dump(seeds, SEEDS_PATH)

    bus_emit("DREAM_NARRATIVE", {
        "narrative_text": narrative[:800],
        "patterns_found": len(patterns),
        "seeds": seeds,
        "confidence": round(min(1.0, len(patterns) / 5.0), 2)
    })

    for s in seeds[:3]:
        bus_emit("DREAM_SEED", s)

    log(f"  emitted {len(seeds)} seeds")

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
    log("=== c9_dream v1.0.0 starting ===")
    while not shutdown:
        try:
            now = datetime.now()
            triggered = os.path.exists(FLAG_PATH)
            in_sleep_window = SLEEP_HOUR <= now.hour < WAKE_HOUR

            if triggered or in_sleep_window:
                if triggered:
                    try:
                        os.remove(FLAG_PATH)
                    except Exception:
                        pass
                    log("Manual trigger detected.")
                else:
                    log("Sleep window entered (02:00â04:00).")

                nodes, edges = load_graph()
                msgs = phase_ingest()
                nodes, edges = phase_graph_update(msgs, nodes, edges)
                nodes, edges = phase_prune(nodes, edges)
                patterns = phase_pattern_synthesis(nodes, edges)
                save_graph(nodes, edges)
                phase_wake(patterns, nodes)
                log("Dream cycle complete.")

                if in_sleep_window:
                    while datetime.now().hour < WAKE_HOUR and not shutdown:
                        time.sleep(60)

            save_graph(*load_graph())
        except Exception as e:
            log(f"CRITICAL dream exception: {e}")

        for _ in range(CHECK_SEC):
            if shutdown:
                break
            time.sleep(1)
    log("=== c9_dream stopped ===")
