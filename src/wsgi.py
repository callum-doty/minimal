"""
Create Flask application with specific configuration for Render deployment.
"""

import os
import sys

# Add the src directory to the path if needed
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.catalog import create_app

app = create_app()

if __name__ == "__main__":
    # Print environment variables for debugging (excluding secrets)
    print("Environment:")
    for key in sorted(os.environ.keys()):
        if key in [
            "DATABASE_URL",
            "SQLALCHEMY_DATABASE_URI",
            "REDIS_URL",
            "MINIO_ENDPOINT",
        ]:
            # Show partial values for connection strings (hiding credentials)
            value = os.environ[key]
            if "@" in value:
                parts = value.split("@")
                prefix = parts[0].split(":")[0]
                suffix = parts[1]
                print(f"  {key}: {prefix}://*****@{suffix}")
            else:
                print(f"  {key}: [Set]")
        elif not any(
            secret in key.lower() for secret in ["key", "token", "secret", "password"]
        ):
            # Show non-sensitive environment variables
            print(f"  {key}: {os.environ[key]}")

    # Run the application
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
