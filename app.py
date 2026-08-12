from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

C9_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLL = os.path.join(C9_DIR, "collections", "2026-08-11", "c9_collection_2026_0811_weeklyscience.json")

@app.route("/")
@app.route("/api")
def home():
    return jsonify({
        "name": "Cloud-9 Assembly API",
        "version": "2026.08.11",
        "status": "alive",
        "endpoints": ["/api/health", "/api/collection", "/api/stats"]
    })

@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": "2026-08-11T00:00:00Z",
        "services": {
            "dummy_api": "127.0.0.1:9876",
            "birth_proxy": "127.0.0.1:8082",
            "ai_router": "127.0.0.1:8790"
        }
    })

@app.route("/api/collection")
def collection():
    if os.path.exists(COLL):
        with open(COLL) as f:
            return jsonify(json.load(f))
    return jsonify({"error": "Collection not found"}), 404

@app.route("/api/stats")
def stats():
    if os.path.exists(COLL):
        with open(COLL) as f:
            d = json.load(f)
        return jsonify({
            "entry_count": d.get("entry_count", 0),
            "average_ac_score": d.get("average_ac_score", 0),
            "meta_patterns": len(d.get("meta_patterns", [])),
            "layer_distribution": d.get("layer_distribution", {}),
            "date": d.get("date")
        })
    return jsonify({"error": "Collection not found"}), 404

# Local testing
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
