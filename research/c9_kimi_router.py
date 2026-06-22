#!/usr/bin/env python3
"""
C9 Kimi Router v2.0
Routes hard tasks from AutoBaby/C9 modules to Kimi K2.6 cloud API.
Endpoints: /health, /route, /autobaby_task, /research
"""
import http.server, socketserver, json, urllib.request, os, sys, threading, time

sys.path.insert(0, os.path.expanduser("~"))

# Kimi API config â corrected endpoint
KIMI_BASE_URL = "https://api.moonshot.cn/v1"  # China endpoint (use .ai for global)
KIMI_API_KEY = os.environ.get("MOONSHOT_API_KEY", "")
KIMI_MODEL = "kimi-k2.6"

BUS_FILE = os.path.expanduser("~/c9_bus.jsonl")
ROUTER_LOG = os.path.expanduser("~/kimi_router.log")
PORT = 5011

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(ROUTER_LOG, "a") as f:
        f.write(line + "\n")

def write_bus(event_type, module, data):
    try:
        entry = {"t": time.time(), "event": event_type, "module": module, "data": data}
        with open(BUS_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        log(f"Bus write error: {e}")

def call_kimi(messages, max_tokens=2048, temperature=0.7):
    """Call Kimi K2.6 API."""
    if not KIMI_API_KEY:
        return {"error": "MOONSHOT_API_KEY not set", "content": "[Kimi cloud disabled â no API key]"}
    try:
        req_data = {
            "model": KIMI_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        req = urllib.request.Request(
            f"{KIMI_BASE_URL}/chat/completions",
            data=json.dumps(req_data).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {KIMI_API_KEY}"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage = result.get("usage", {})
        return {"content": content, "usage": usage, "model": result.get("model", KIMI_MODEL)}
    except Exception as e:
        return {"error": str(e), "content": f"[Kimi API error: {e}]"}

class KimiRouterHandler(http.server.BaseHTTPRequestHandler):
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
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            self._send_json({
                "status": "ok",
                "model": KIMI_MODEL,
                "cloud_enabled": bool(KIMI_API_KEY),
                "version": "2.0"
            })
            return
        self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(n).decode() if n > 0 else "{}"
            try:
                data = json.loads(body)
            except:
                data = {}

            if self.path == "/route":
                task = data.get("task", "")
                context = data.get("context", "")
                log(f"Routing task to Kimi: {task[:60]}...")
                messages = [
                    {"role": "system", "content": "You are C9-Kimi, a specialized research assistant for the Cloud-9 Assembly Project. You handle complex cosmology, physics, quantum mechanics, and cross-disciplinary analysis. Be thorough and structured."},
                    {"role": "user", "content": f"Task: {task}\n\nContext: {context}\n\nProvide a detailed, well-reasoned response."}
                ]
                result = call_kimi(messages, max_tokens=data.get("max_tokens", 2048))
                write_bus("kimi_response", "c9_kimi_router", {
                    "task_preview": task[:100],
                    "success": "error" not in result
                })
                self._send_json(result)
                return

            if self.path == "/autobaby_task":
                question = data.get("question", "")
                log(f"AutoBaby task â Kimi: {question[:60]}...")
                messages = [
                    {"role": "system", "content": "You are Kimi K2.6, assisting the Cloud-9 Assembly Project. The user runs an autonomous agent called AutoBaby on a Termux phone. Provide concise but thorough answers."},
                    {"role": "user", "content": question}
                ]
                result = call_kimi(messages, max_tokens=1024)
                write_bus("autobaby_kimi_response", "c9_kimi_router", {
                    "question_preview": question[:80],
                    "success": "error" not in result
                })
                self._send_json(result)
                return

            if self.path == "/research":
                topic = data.get("topic", "")
                depth = data.get("depth", "standard")
                depth_prompt = {
                    "standard": "Provide a comprehensive overview with key findings.",
                    "deep": "Provide an in-depth analysis with multiple perspectives and connections to related fields.",
                    "exhaustive": "Provide an exhaustive treatment covering history, current state, future directions, mathematical foundations, and connections to cosmology/physics/AI."
                }.get(depth, "standard")
                log(f"Research request [{depth}]: {topic[:60]}...")
                messages = [
                    {"role": "system", "content": "You are C9-Kimi Research Mode. You conduct deep interdisciplinary research for the Cloud-9 Assembly Project."},
                    {"role": "user", "content": f"Research Topic: {topic}\n\n{depth_prompt}\n\nFormat with clear sections and actionable insights."}
                ]
                result = call_kimi(messages, max_tokens=4096, temperature=0.8)
                self._send_json(result)
                return

            self._send_json({"error": f"Unknown endpoint: {self.path}"}, 404)
        except Exception as e:
            log(f"Router error: {e}")
            self._send_json({"error": str(e)}, 500)

def bus_watcher():
    """Watch C9 bus for autobaby_task events and auto-route to Kimi."""
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
                                question = data.get("question", "")
                                if question and KIMI_API_KEY:
                                    log(f"Auto-routing bus task: {question[:50]}...")
                                    messages = [
                                        {"role": "system", "content": "You are Kimi K2.6 assisting Cloud-9 Assembly."},
                                        {"role": "user", "content": question}
                                    ]
                                    result = call_kimi(messages, max_tokens=1024)
                                    write_bus("autobaby_kimi_auto", "c9_kimi_router", {
                                        "auto_routed": True,
                                        "question_preview": question[:60],
                                        "success": "error" not in result
                                    })
                        except:
                            pass
                    last_pos = f.tell()
            time.sleep(5)
        except Exception as e:
            log(f"Bus watcher error: {e}")
            time.sleep(10)

class ReusableServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    log(f"C9 Kimi Router v2.0 starting...")
    log(f"Model: {KIMI_MODEL}")
    log(f"Cloud: {'ENABLED' if KIMI_API_KEY else 'DISABLED (set MOONSHOT_API_KEY)'}")
    watcher = threading.Thread(target=bus_watcher, daemon=True)
    watcher.start()
    with ReusableServer(("127.0.0.1", PORT), KimiRouterHandler) as httpd:
        log(f"Kimi Router ready at http://127.0.0.1:{PORT}")
        log("Endpoints: /health, /route, /autobaby_task, /research")
        httpd.serve_forever()
