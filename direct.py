# direct.py - Direct binding to 0.0.0.0
import os
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify(
        {
            "status": "online",
            "message": "Direct binding app running on 0.0.0.0",
            "port": os.environ.get("PORT", "5000"),
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Explicitly print binding information
    print(f"=== BINDING DIRECTLY TO 0.0.0.0:{port} ===")
    # The critical part - binding to 0.0.0.0 not 127.0.0.1
    app.run(host="0.0.0.0", port=port)
