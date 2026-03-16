import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def health_check():
    token = os.getenv('TG_TOKEN')
    return f"OK | TOKEN set: {bool(token)}", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
