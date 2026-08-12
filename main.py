import os
import json
from flask import Flask, jsonify
import c9_bus_client  # C9 bus injection

app = Flask(__name__)

# ─── Embedded Cloud-9 Assembly Index Data ───────────────────
# Self-contained: no Google Drive or external dependency needed.
# Update these values directly in this file as new results come in.
CLOUD9_DATA = {
    "version": "1.5.0",
    "last_updated": "2026-05-17",
    "status": "operational",
    "empirical_results": {
        "sdss_shell": {
            "shell_kpc": "14-18",
            "redshift": "0.16-0.19",
            "z_score": 2.462,
            "p_value": 0.007,
            "n_galaxies": 23,
            "bootstrap_iterations": 10000,
            "status": "sub-threshold but real"
        },
        "ibm_quantum": {
            "hardware": "IBM Kingston",
            "date": "2026-04-12",
            "status": "confirmed operational"
        }
    },
    "assembly_index_results": [
        {"system": "Exciton-Polariton (U. Penn)",  "A_c": 8.97,   "energy_orders": 2.3},
        {"system": "Alfven Wave Plasma (UCLA)",     "A_c": 30.92,  "energy_orders": 10},
        {"system": "Perseus Cluster (U. Tokyo)",    "A_c": 64.89,  "energy_orders": 10},
        {"system": "GW190728 Dark Matter (MIT)",    "A_c": 210.36, "energy_orders": 79}
    ],
    "scaling_law": "A_c = 2.5 * log10(E_max/E_min) + 16.1",
    "threshold_5_41_sigma": {
        "description": "Validated metric for uninterrupted causal history",
        "status": "active"
    },
    "neuromorphic": {
        "hardware": "Intel Loihi 2",
        "snn_A_c": 5.1,
        "transformer_A_c": 4.6
    },
    "github": "https://github.com/bordode/cloud9-assembly-index"
}

THRESHOLD = float(os.getenv("THRESHOLD", "5.41"))

@app.route("/")
def health_check():
    return jsonify({
        "status": "ok",
        "service": "Cloud-9 Assembly Index API",
        "version": CLOUD9_DATA["version"],
        "last_updated": CLOUD9_DATA["last_updated"],
        "threshold_sigma": THRESHOLD
    }), 200

@app.route("/data")
def get_data():
    """Return all embedded Cloud-9 results."""
    return jsonify(CLOUD9_DATA), 200

@app.route("/analyze")
def analyze():
    """Analyze current A_c values against threshold."""
    results = CLOUD9_DATA["assembly_index_results"]
    above = [r for r in results if r["A_c"] >= THRESHOLD]
    below = [r for r in results if r["A_c"] < THRESHOLD]
    peak = max(results, key=lambda x: x["A_c"])
    return jsonify({
        "status": "ok",
        "threshold_sigma": THRESHOLD,
        "total_systems": len(results),
        "above_threshold": len(above),
        "below_threshold": len(below),
        "peak_system": peak["system"],
        "peak_A_c": peak["A_c"],
        "scaling_law": CLOUD9_DATA["scaling_law"],
        "systems": results
    }), 200

@app.route("/empirical")
def empirical():
    """Return current empirical SDSS + IBM results."""
    return jsonify(CLOUD9_DATA["empirical_results"]), 200

@app.route("/status")
def full_status():
    """Full system status — used by monitoring servers."""
    return jsonify({
        "cloud9_version": CLOUD9_DATA["version"],
        "sdss_z_score": CLOUD9_DATA["empirical_results"]["sdss_shell"]["z_score"],
        "sdss_status": CLOUD9_DATA["empirical_results"]["sdss_shell"]["status"],
        "ibm_status": CLOUD9_DATA["empirical_results"]["ibm_quantum"]["status"],
        "peak_A_c": 210.36,
        "peak_system": "GW190728 Dark Matter",
        "scaling_law": CLOUD9_DATA["scaling_law"],
        "threshold_5_41_sigma": "active",
        "server_status": "operational"
    }), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
