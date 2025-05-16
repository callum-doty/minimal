# minimal_app.py
from flask import Flask, jsonify
import os

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify(
        {
            "status": "online",
            "message": "Minimal Document Catalog API is running",
            "version": "1.0.0-minimal",
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "mode": "minimal"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
