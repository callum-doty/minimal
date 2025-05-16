"""
Simple Express-like fallback app for Render deployment.
This bare-bones app ensures port binding works even if the main app fails.
"""

from flask import Flask
import os
import sys

# Create simple app
app = Flask(__name__)


@app.route("/")
def home():
    """Simple home page that confirms the app is running."""
    return """
    <html>
        <head>
            <title>Render App - Fallback Mode</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .container { max-width: 800px; margin: 0 auto; background: #f5f5f5; padding: 20px; border-radius: 5px; }
                h1 { color: #333; }
                .info { margin: 10px 0; padding: 10px; background: #fff; border-radius: 3px; }
                .success { color: green; }
                .warning { color: orange; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Fallback App - Running Successfully</h1>
                <div class="info success">
                    <p>✅ The fallback app is running on port {0}.</p>
                    <p>This confirms that your Flask app is binding to the correct port as required by Render.</p>
                </div>
                <div class="info warning">
                    <p>⚠️ Note: This is a fallback application. Your main application may still have initialization issues.</p>
                    <p>Check Render logs for more details on why your main application is not starting properly.</p>
                </div>
                <div class="info">
                    <h3>Environment Information:</h3>
                    <p>PORT: {0}</p>
                    <p>Python Version: {1}</p>
                    <p>Working Directory: {2}</p>
                </div>
            </div>
        </body>
    </html>
    """.format(
        os.environ.get("PORT", 5000), sys.version, os.getcwd()
    )


@app.route("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy", "mode": "fallback"}, 200


if __name__ == "__main__":
    # Get port from environment
    port = int(os.environ.get("PORT", 5000))

    # Print port binding information
    print(f"*** FALLBACK APP: Starting on port {port} ***")

    # Run the app
    app.run(host="0.0.0.0", port=port)
