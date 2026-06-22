#!/usr/bin/env python3
"""
C9 AutoBaby Watcher v2.0
Monitors the C9 bus and local task queue for "hard" tasks.
Routes complex research/cosmology/physics tasks to Kimi router.
Simple tasks stay local (Ollama/Phi-3).
"""
import os, sys, json, time, threading, urllib.request

sys.path.insert(0, os.path.expanduser("~"))

BUS_FILE = os.path.expanduser("~/c9_bus.jsonl")
TASK_QUEUE = os.path.expanduser("~/c9_autobaby_queue.jsonl")
WATCHER_LOG = os.path.expanduser("~/autobaby_watcher.log")
KIMI_ROUTER_URL = "http://127.0.0.1:5011"
LOCAL_PROXY_URL = "http://127.0.0.1:8083/v1/chat/completions"

# Keywords that indicate a "hard" task (needs Kimi)
HARD_KEYWORDS = [
    "quantum", "cosmology", "cosmological", "assembly index", "dark matter",
    "black hole", "entropy", "thermodynamics", "holography", "complexity",
    "neuromorphic", "consciousness", "IIT", "global workspace", "QBism",
    "causal set", "spin glass", "topological", "anyons", "TDA",
    "research", "analyze", "compare", "synthesize", "evaluate",
    "arxiv", "paper", "publication", "theorem", "proof"
]

# Keywords that are "simple" (stay local)
SIMPLE_KEYWORDS = [
    "hello", "hi", "what is 2+2", "time", "date", "weather",
    "simple", "basic", "quick", "short"
]

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(WATCHER_LOG, "a") as f:
        f.write(line + "\n")

def write_bus(event_type, data):
    try:
        entry = {"t": time.time(), "event": event_type, "module": "autobaby_watcher", "data": data}
        with open(BUS_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        log(f"Bus write error: {e}")

def classify_task(text):
    """Classify task as 'hard' (Kimi) or 'simple' (local)."""
    text_lower = text.lower()

    # Check simple first (overrides)
    if any(kw in text_lower for kw in SIMPLE_KEYWORDS):
        return "simple"

    # Check hard
    if any(kw in text_lower for kw in HARD_KEYWORDS):
        return "hard"

    # Default: if text is long or has complex structure, treat as hard
    if len(text) > 200:
        return "hard"

    return "simple"

def route_to_kimi(question):
    """Send task to Kimi router."""
    try:
        req = urllib.request.Request(
            f"{KIMI_ROUTER_URL}/autobaby_task",
            data=json.dumps({"question": question, "source": "autobaby_watcher", "priority": "high"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
        return result
    except Exception as e:
        return {"error": str(e), "content": f"[Kimi routing failed: {e}]"}

def route_to_local(question):
    """Send task to local Ollama/Phi-3."""
    try:
        req = urllib.request.Request(
            LOCAL_PROXY_URL,
            data=json.dumps({
                "model": "phi3",
                "messages": [{"role": "user", "content": question}],
                "max_tokens": 512,
                "temperature": 0.7
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {"content": content, "source": "local"}
    except Exception as e:
        return {"error": str(e), "content": f"[Local routing failed: {e}]"}

def process_task(task):
    """Process a single task."""
    question = task.get("question", "")
    task_id = task.get("id", f"task_{int(time.time())}")

    classification = classify_task(question)
    log(f"Task {task_id}: '{question[:60]}...' â {classification.upper()}")

    if classification == "hard":
        log(f"  â Routing to Kimi K2.6...")
        result = route_to_kimi(question)
        source = "kimi"
    else:
        log(f"  â Routing to local Phi-3...")
        result = route_to_local(question)
        source = result.get("source", "local")

    # Log result
    write_bus("autobaby_task_complete", {
        "task_id": task_id,
        "classification": classification,
        "source": source,
        "success": "error" not in result,
        "answer_preview": result.get("content", "")[:100]
    })

    # Save to task queue for reference
    try:
        with open(TASK_QUEUE, "a") as f:
            f.write(json.dumps({
                "t": time.time(),
                "task_id": task_id,
                "question": question,
                "classification": classification,
                "source": source,
                "result": result
            }) + "\n")
    except Exception as e:
        log(f"Queue write error: {e}")

    return result

def bus_watcher():
    """Watch C9 bus for autobaby_task events."""
    log("Bus watcher started")
    last_pos = 0
    while True:
        try:
            if os.path.exists(BUS_FILE):
                with open(BUS_FILE, "r") as f:
                    f.seek(last_pos)
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            event = json.loads(line)
                            if event.get("event") == "autobaby_task":
                                data = event.get("data", {})
                                process_task(data)
                        except:
                            pass
                    last_pos = f.tell()
            time.sleep(3)
        except Exception as e:
            log(f"Bus watcher error: {e}")
            time.sleep(10)

def queue_watcher():
    """Watch local task queue file for new tasks."""
    log("Queue watcher started")
    last_pos = 0
    while True:
        try:
            if os.path.exists(TASK_QUEUE):
                with open(TASK_QUEUE, "r") as f:
                    f.seek(last_pos)
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            task = json.loads(line)
                            # Only process tasks without a result yet
                            if "result" not in task and "question" in task:
                                process_task(task)
                        except:
                            pass
                    last_pos = f.tell()
            time.sleep(5)
        except Exception as e:
            log(f"Queue watcher error: {e}")
            time.sleep(10)

def health_beacon():
    """Send periodic heartbeat to bus."""
    while True:
        write_bus("module_heartbeat", {"module": "autobaby_watcher", "status": "alive"})
        time.sleep(60)

if __name__ == "__main__":
    log("C9 AutoBaby Watcher v2.0 starting...")
    log(f"Hard keywords: {len(HARD_KEYWORDS)}")
    log(f"Kimi router: {KIMI_ROUTER_URL}")
    log(f"Local proxy: {LOCAL_PROXY_URL}")

    # Start watchers
    t1 = threading.Thread(target=bus_watcher, daemon=True)
    t2 = threading.Thread(target=queue_watcher, daemon=True)
    t3 = threading.Thread(target=health_beacon, daemon=True)

    t1.start()
    t2.start()
    t3.start()

    log("All watchers running. Waiting for tasks...")

    # Keep main thread alive
    while True:
        time.sleep(3600)
