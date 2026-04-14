import os
import io
import requests
import pandas as pd
from flask import Flask, jsonify

# Configuration
FILE_ID   = os.getenv('GDRIVE_FILE_ID')
THRESHOLD = float(os.getenv('THRESHOLD', '85.0'))

app = Flask(__name__)

def fetch_data():
    """Fetch CSV from Google Drive."""
    if not FILE_ID:
        raise ValueError("GDRIVE_FILE_ID environment variable not set")
    url = f'https://drive.google.com/uc?export=download&id={FILE_ID}'
    try:
        r = requests.Session().get(url, timeout=15, allow_redirects=True)
        r.raise_for_status()
        return pd.read_csv(io.StringIO(r.text))
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to fetch data: {e}")

@app.route("/")
def health_check():
    return jsonify({
        "status": "ok",
        "file_id_set": bool(FILE_ID),
        "threshold": THRESHOLD
    }), 200

@app.route("/analyze")
def analyze():
    try:
        df = fetch_data()
        if "BT" not in df.columns:
            return jsonify({"error": "'BT' column not found in data"}), 400
        peak_val = float(df["BT"].max())
        mean_val = float(df["BT"].mean())
        status   = "DANGER" if peak_val > THRESHOLD else "STABLE"
        return jsonify({
            "peak_uT":   round(peak_val, 4),
            "mean_uT":   round(mean_val, 4),
            "threshold": THRESHOLD,
            "status":    status
        }), 200
    except Exception as e:
        return jsonify({"error": f"{type(e).__name__}: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8080))
    app.run(host="0.0.0.0", port=port)
