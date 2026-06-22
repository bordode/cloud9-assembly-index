#!/usr/bin/env python3
"""C9 Diagnostic Tool v2.0 â Quick health check of all services."""
import urllib.request, json, os, subprocess, time

SERVICES = {
    "llama-server": 8080,
    "BIRTH proxy": 8082,
    "OpenAI proxy": 8083,
    "C9 bridge": 5010,
    "C9 oracle": 5009,
    "C9 orchestrator": 5012,
    "Kimi router": 5011,
}

PROCESSES = [
    "birth_proxy_fixed.py", "c9_birth_bridge.py", "c9_orchestrator.py",
    "c9_kimi_router.py", "sovereign_living_manifold.py",
    "c9_physical_manifold_v2.py", "cloud9_mimic_node.py",
    "c9_sentry_minimal.py", "agape_phone.py", "jarvis_interface.py",
    "run_continuous.py", "c9_quantum_bridge_v2.py", "c9_oracle.py",
    "c9_librarian.py", "autobaby_watcher.py",
]

def check_port(port, path="/health"):
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200, json.loads(resp.read())
    except Exception as e:
        return False, str(e)

def check_process(pattern):
    try:
        result = subprocess.run(['pgrep', '-f', pattern], capture_output=True, text=True)
        return result.returncode == 0 and result.stdout.strip() != ""
    except:
        return False

print("âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ")
print("â     C9 ECOSYSTEM DIAGNOSTIC v2.0                              â")
print(f"â     {time.strftime('%Y-%m-%d %H:%M:%S')}                                    â")
print("âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ")
print()

print("ð¡ SERVICES:")
for name, port in SERVICES.items():
    ok, data = check_port(port)
    status = "ð¢" if ok else "ð´"
    extra = ""
    if ok and isinstance(data, dict):
        if "evolution" in data:
            extra = f" (evo:{data['evolution']})"
        elif "cloud_enabled" in data:
            extra = f" (cloud:{data['cloud_enabled']})"
        elif "healthy" in data:
            extra = f" ({data['healthy']}/{data.get('total','?')} up)"
    print(f"   {status} {name:20s} port {port:5d} {'OK' if ok else 'DOWN'}{extra}")

print()
print("ð§  PROCESSES:")
for proc in PROCESSES:
    ok = check_process(proc)
    status = "ð¢" if ok else "ð´"
    print(f"   {status} {proc}")

print()
print("ð FILES:")
for f in ["c9_bus.jsonl", "c9_state.json", "birth_evolution.html", "c9_evolution_proposals.json"]:
    path = os.path.expanduser(f"~/{f}")
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    status = "ð¢" if exists else "ð´"
    print(f"   {status} {f:30s} {size:>10,} bytes")

print()
print("âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ")
