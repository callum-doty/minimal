"""
Minimal fallback application for when there are import errors in the main app.
This is a super simple Flask app that just binds to the port and serves basic endpoints.
"""

from flask import Flask, jsonify
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create minimal app
app = Flask(__name__)


@app.route("/")
def index():
    """Root endpoint for the minimal app."""
    return jsonify(
        {
            "status": "online",
            "mode": "minimal",
            "message": "Minimal Document Catalog API is running",
            "version": "1.0.0-minimal",
        }
    )


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "mode": "minimal",
            "python_version": sys.version,
            "port": os.environ.get("PORT", "5000"),
        }
    )


@app.route("/debug/environment")
def debug_env():
    """Show non-sensitive environment variables."""
    safe_env = {}
    for key, value in os.environ.items():
        if not any(
            secret in key.lower() for secret in ["key", "token", "secret", "password"]
        ):
            safe_env[key] = value
        else:
            safe_env[key] = "[REDACTED]"

    return jsonify(
        {
            "environment": safe_env,
            "working_directory": os.getcwd(),
            "files": os.listdir("."),
        }
    )


@app.route("/debug/import-check")
def debug_imports():
    """Check if core modules can be imported."""
    results = {}

    # Try to import core modules
    modules_to_check = ["flask", "sqlalchemy", "src", "src.catalog.config"]

    for module in modules_to_check:
        try:
            __import__(module)
            results[module] = "SUCCESS"
        except ImportError as e:
            results[module] = f"FAILED: {str(e)}"

    return jsonify({"import_checks": results, "python_path": sys.path})


@app.route("/api/upload", methods=["POST"])
def upload_placeholder():
    """Placeholder for upload endpoint."""
    return (
        jsonify(
            {
                "status": "not_implemented",
                "message": "This is a minimal app. Upload functionality is not available.",
            }
        ),
        503,
    )  # Service Unavailable


@app.route("/api/documents", methods=["GET"])
def documents_placeholder():
    """Placeholder for documents endpoint."""
    return (
        jsonify(
            {
                "status": "not_implemented",
                "message": "This is a minimal app. Document listing is not available.",
            }
        ),
        503,
    )  # Service Unavailable


if __name__ == "__main__":
    # Get port from environment
    port = int(os.environ.get("PORT", 5000))

    # Log startup information
    logger.info(f"Starting minimal app on port {port}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")

    # Run the app
    app.run(host="0.0.0.0", port=port)
