#!/usr/bin/env python3
import json, os
from http.server import BaseHTTPRequestHandler

C9_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLL = os.path.join(C9_DIR, "collections", "2026-08-11", "c9_collection_2026_0811_weeklyscience.json")

class handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass

    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def do_GET(self):
        if self.path in ["/", "/api"]:
            self._json({"name": "Cloud-9 Assembly API", "version": "2026.08.11", "endpoints": ["/api/health", "/api/collection", "/api/stats"]})
        elif self.path == "/api/health":
            self._json({"status": "healthy", "services": {"dummy_api": "127.0.0.1:9876", "birth": "127.0.0.1:8082"}})
        elif self.path == "/api/collection":
            if os.path.exists(COLL):
                with open(COLL) as f: self._json(json.load(f))
            else: self._json({"error": "Collection not found"}, 404)
        elif self.path == "/api/stats":
            if os.path.exists(COLL):
                with open(COLL) as f:
                    d = json.load(f)
                self._json({"entries": d["entry_count"], "avg_ac": d["average_ac_score"], "patterns": len(d["meta_patterns"])})
            else: self._json({"error": "Not found"}, 404)
        else: self._json({"error": "Not found"}, 404)

    def do_POST(self):
        self._json({"status": "DUMMY_MODE", "message": "Read-only API"})
