#!/usr/bin/env python3
"""
C9 BIRTH Bridge Delivery - Chunked Safe Writer
Run this in Termux to install the bridge
"""

import os

PARTS = []

PARTS.append("""#!/usr/bin/env python3
import json, time, threading, os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

BUS_FILE = os.path.expanduser("~/c9_bus.jsonl")
BRIDGE_LOG = os.path.expanduser("~/c9_bridge_birth.log")

class C9BridgeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{ts}] {self.client_address[0]} - {format % args}"
        with open(BRIDGE_LOG, "a") as f:
            f.write(msg + "\n")
        print(msg)

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
""")

PARTS.append("""
    def do_GET(self):
        if self.path == "/health":
            self._send_json({
                "status": "ok",
                "bridge": "c9_birth_bridge_v3.1",
                "bus_file": BUS_FILE,
                "birth_connected": True,
                "timestamp": time.time()
            })
        elif self.path == "/bus/status":
            entries = []
            if os.path.exists(BUS_FILE):
                try:
                    with open(BUS_FILE, "r") as f:
                        lines = f.readlines()
                        for line in lines[-50:]:
                            try:
                                entries.append(json.loads(line.strip()))
                            except:
                                pass
                except Exception as e:
                    self._send_json({"error": str(e)}, 500)
                    return
            self._send_json({
                "entries": entries,
                "count": len(entries),
                "bus_file_size": os.path.getsize(BUS_FILE) if os.path.exists(BUS_FILE) else 0
            })
        else:
            self._send_json({"error": "Not found"}, 404)
""")

PARTS.append("""
    def do_POST(self):
        if self.path == "/bus":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length)
                event_data = json.loads(post_data.decode())

                if "source" not in event_data or "event" not in event_data:
                    self._send_json({"error": "Missing source or event field"}, 400)
                    return

                if "timestamp" not in event_data:
                    event_data["timestamp"] = time.time()

                with open(BUS_FILE, "a") as f:
                    f.write(json.dumps(event_data) + "\n")

                self._send_json({
                    "status": "accepted",
                    "source": event_data["source"],
                    "event": event_data["event"],
                    "bus_entries": self._count_bus_entries()
                })

                print(f"[BUS] {event_data['source']} -> {event_data['event']}")

            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
        else:
            self._send_json({"error": "Not found"}, 404)

    def _count_bus_entries(self):
        if not os.path.exists(BUS_FILE):
            return 0
        try:
            with open(BUS_FILE, "r") as f:
                return sum(1 for _ in f)
        except:
            return 0
""")

PARTS.append("""
def run_bridge(port=5010):
    server = HTTPServer(("0.0.0.0", port), C9BridgeHandler)
    print(f"C9 Bridge v3.1 running on port {port}")
    print(f"Bus file: {BUS_FILE}")
    print(f"Log file: {BRIDGE_LOG}")
    print("Endpoints:")
    print("  GET  /health       - Bridge status")
    print("  GET  /bus/status   - Recent bus entries")
    print("  POST /bus          - Submit event to C9 bus")

    if not os.path.exists(BUS_FILE):
        with open(BUS_FILE, "w") as f:
            pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBridge shutting down...")
        server.shutdown()

if __name__ == "__main__":
    run_bridge()
""")

def write_bridge():
    out = os.path.expanduser("~/c9_birth_bridge_v3_1.py")
    with open(out, "w") as f:
        for part in PARTS:
            f.write(part)
    size = os.path.getsize(out)
    print(f"Written: {out}")
    print(f"Size: {size} bytes ({size/1024:.1f} KB)")
    print("\nTo run:")
    print("  python3 ~/c9_birth_bridge_v3_1.py")
    print("\nOr background:")
    print("  nohup python3 ~/c9_birth_bridge_v3_1.py >> ~/c9_bridge.log 2>&1 &")

if __name__ == "__main__":
    write_bridge()
