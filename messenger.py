import os
from flask import Flask
import c9_bus_client  # C9 bus injection
app = Flask(__name__)
@app.route("/")
def home():
    return "<h1>Sentinel Node Active</h1><p>Resonance: 2.25 Δ</p>"
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)