#!/usr/bin/env python3
"""
C9 Orchestrator v2.0
Health monitoring, bus logging, module heartbeat tracking.
Runs on port 5012.
"""
import http.server, socketserver, json, os, sys, time, threading, subprocess

sys.path.insert(0, os.path.expanduser("~"))

BUS_FILE = os.path.expanduser("~/c9_bus.jsonl")
STATE_FILE = os.path.expanduser("~/c9_state.json")
ORCH_LOG = os.path.expanduser("~/c9_orchestrator.log")
PORT = 5012

# Expected modules and their check methods
MODULES = {
    "llama-server": {"port": 8080, "type": "service"},
    "birth_proxy": {"port": 8082, "type": "service"},
    "openai_proxy": {"port": 8083, "type": "service"},
    "c9_bridge": {"port": 5010, "type": "service"},
    "c9_oracle": {"port": 5009, "type": "service"},
    "c9_kimi_router": {"port": 5011, "type": "service"},
    "sovereign_living_manifold": {"pattern": "sovereign_living_manifold.py", "type": "process"},
    "c9_physical_manifold": {"pattern": "c9_physical_manifold_v2.py", "type": "process"},
    "cloud9_mimic_node": {"pattern": "cloud9_mimic_node.py", "type": "process"},
    "c9_sentry": {"pattern": "c9_sentry_minimal.py", "type": "process"},
    "agape_phone": {"pattern": "agape_phone.py", "type": "process"},
    "jarvis_interface": {"pattern": "jarvis_interface.py", "type": "process"},
    "run_continuous": {"pattern": "run_continuous.py", "type": "process"},
    "c9_quantum_bridge": {"pattern": "c9_quantum_bridge_v2.py", "type": "process"},
    "c9_librarian": {"pattern": "c9_librarian.py", "type": "process"},
}

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(ORCH_LOG, "a") as f:
        f.write(line + "\n")

def write_bus(event_type, module, data):
    try:
        entry = {"t": time.time(), "event": event_type, "module": module, "data": data}
        with open(BUS_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        log(f"Bus write error: {e}")

def check_port(port):
    try:
        import urllib.request
        req = urllib.request.Request(f"http://127.0.0.1:{port}/health", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except:
        return False

def check_process(pattern):
    try:
        result = subprocess.run(['pgrep', '-f', pattern], capture_output=True, text=True)
        return result.returncode == 0 and result.stdout.strip() != ""
    except:
        return False

def check_module(name, config):
    if config["type"] == "service":
        return check_port(config["port"])
    else:
        return check_process(config["pattern"])

def health_check():
    """Periodic health check of all modules."""
    while True:
        try:
            status = {}
            for name, config in MODULES.items():
                healthy = check_module(name, config)
                status[name] = {
                    "healthy": healthy,
                    "last_check": time.time()
                }
                if not healthy:
                    log(f"â ï¸ {name} is DOWN")
                    write_bus("module_down", "c9_orchestrator", {"module": name})

            # Save state
            try:
                with open(STATE_FILE, "w") as f:
                    json.dump({
                        "timestamp": time.time(),
                        "modules": status,
                        "healthy_count": sum(1 for s in status.values() if s["healthy"]),
                        "total_count": len(status)
                    }, f, indent=2)
            except Exception as e:
                log(f"State save error: {e}")

            write_bus("orchestrator_health", "c9_orchestrator", {
                "healthy": sum(1 for s in status.values() if s["healthy"]),
                "total": len(status)
            })

        except Exception as e:
            log(f"Health check error: {e}")

        time.sleep(30)

class OrchestratorHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            try:
                if os.path.exists(STATE_FILE):
                    with open(STATE_FILE, "r") as f:
                        state = json.load(f)
                else:
                    state = {"modules": {}, "healthy_count": 0, "total_count": len(MODULES)}
                self._send_json({
                    "status": "ok",
                    "healthy": state.get("healthy_count", 0),
                    "total": state.get("total_count", len(MODULES)),
                    "modules": state.get("modules", {}),
                    "timestamp": time.time()
                })
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)
            return

        if self.path == "/status":
            # Quick status without file read
            status = {}
            for name, config in MODULES.items():
                status[name] = {"healthy": check_module(name, config)}
            self._send_json({
                "status": "ok",
                "modules": status,
                "healthy": sum(1 for s in status.values() if s["healthy"]),
                "total": len(status)
            })
            return

        self._send_json({"error": "Not found"}, 404)

class ReusableServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    log("C9 Orchestrator v2.0 starting...")

    # Start health checker
    hc = threading.Thread(target=health_check, daemon=True)
    hc.start()

    with ReusableServer(("127.0.0.1", PORT), OrchestratorHandler) as httpd:
        log(f"Orchestrator ready at http://127.0.0.1:{PORT}")
        log("Endpoints: /health, /status")
        httpd.serve_forever()
