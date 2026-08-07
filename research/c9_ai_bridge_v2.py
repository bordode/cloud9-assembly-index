#!/usr/bin/env python3
"""
C9 AI Bridge v2.0
Reads actual bus data, module states, and feeds context to local phi3:mini.
Does NOT disrupt running modules.
"""

import json, os, sys, urllib.request, socket, subprocess
from datetime import datetime, timezone

BUS = os.path.expanduser("~/c9_bus.jsonl")
API = "http://localhost:8080/v1/chat/completions"
MODEL = "phi3:mini"

def check_port(port, timeout=1):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        r = s.connect_ex(("localhost", port))
        s.close()
        return r == 0
    except:
        return False

def get_module_census():
    """Get real running module info from ps"""
    try:
        ps = subprocess.check_output(["ps", "aux"], text=True)
        modules = []
        keywords = ["sovereign", "physical", "mimic", "sentry", "agape", 
                    "jarvis", "continuous", "oracle", "librarian", 
                    "autobaby", "quantum", "birth", "bridge", "launcher"]
        for line in ps.split("\n"):
            if "python3" in line:
                for kw in keywords:
                    if kw in line.lower():
                        parts = line.split()
                        if len(parts) >= 11:
                            pid = parts[1]
                            cmd = parts[-1].split("/")[-1][:40]
                            cpu = parts[2]
                            mem = parts[3]
                            modules.append({"pid": pid, "name": cmd, "cpu": cpu, "mem": mem})
                        break
        return modules
    except Exception as e:
        return [{"error": str(e)}]

def get_bus_summary():
    """Read last N events from bus"""
    if not os.path.exists(BUS):
        return {"error": "No bus file"}
    try:
        with open(BUS, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 100000), 0)
            tail = f.read().decode("utf-8", errors="ignore").strip()

        lines = [l for l in tail.split("\n") if l.strip()]
        events = []
        for line in lines[-50:]:
            try:
                evt = json.loads(line)
                events.append({
                    "module": evt.get("module", evt.get("source", "?")),
                    "event": evt.get("event_type", evt.get("type", "?")),
                    "time": evt.get("timestamp", evt.get("t", 0))
                })
            except:
                pass

        # Count by module
        counts = {}
        for e in events:
            m = e["module"]
            counts[m] = counts.get(m, 0) + 1

        return {
            "total_events_scanned": len(lines),
            "parsed_events": len(events),
            "module_activity": counts,
            "latest_modules": list(set(e["module"] for e in events[-10:]))
        }
    except Exception as e:
        return {"error": str(e)}

def ask_phi3(prompt, system="You are C9's onboard AI. Analyze the data concisely."):
    req = urllib.request.Request(
        API,
        data=json.dumps({
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 300,
            "temperature": 0.7
        }).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return resp["choices"][0]["message"]["content"]

def main():
    if not check_port(8080):
        print("ERROR: llama-server not on port 8080")
        sys.exit(1)

    # Gather real data
    modules = get_module_census()
    bus = get_bus_summary()

    # Build context-rich prompt
    mod_lines = "\n".join([f"- {m['name']} (PID {m['pid']}, CPU {m['cpu']}%, MEM {m['mem']}%)" 
                             for m in modules[:15]])

    bus_lines = "\n".join([f"- {k}: {v} events" for k, v in bus.get("module_activity", {}).items()])

    prompt = f"""C9 ECOSYSTEM STATUS REPORT

RUNNING MODULES ({len(modules)}):
{mod_lines}

BUS ACTIVITY (last 50 events):
{bus_lines}

Provide a brief status assessment. Is the system healthy? Any concerns?"""

    print("=" * 50)
    print("Querying phi3:mini with real C9 context...")
    print("=" * 50)

    response = ask_phi3(prompt)
    print(response)

    # Log to bus
    evt = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "ai_status_report",
        "module": "c9_ai_bridge",
        "data": {
            "query": "C9 status",
            "response": response[:300],
            "modules_count": len(modules),
            "model": MODEL
        }
    }
    with open(BUS, "a") as f:
        f.write(json.dumps(evt) + "\n")

    print("\n[Logged to bus]")

if __name__ == "__main__":
    main()
