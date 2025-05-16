"""
Create Flask application with specific configuration for Render deployment.
"""

import os
import sys
import logging
import threading
import time
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the src directory to the path if needed
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Create and configure the Flask application
try:
    logger.info("Importing create_app function...")
    from src.catalog import create_app

    logger.info("Creating Flask application...")
    app = create_app()
    # Also expose as 'application' for WSGI servers like Gunicorn
    application = app
    logger.info("Flask application created successfully.")
except Exception as e:
    logger.error(f"Error creating Flask application: {str(e)}")
    logger.error(traceback.format_exc())

    # Fallback to a minimal application if main app fails
    from flask import Flask, jsonify

    app = Flask(__name__)
    # Also expose as 'application' for WSGI servers like Gunicorn
    application = app

    @app.route("/")
    def index():
        return jsonify(
            {
                "status": "error",
                "message": "Main application failed to initialize",
                "error": str(e),
            }
        )

    @app.route("/health")
    def health():
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

    logger.info("Using minimal fallback application due to initialization error.")


# Function to initialize storage in background
def init_storage_async():
    """Initialize storage service asynchronously."""
    try:
        logger.info("Starting async storage initialization...")
        time.sleep(2)  # Let the main application start first

        with app.app_context():
            # Check if we should use mock storage
            use_mock = app.config.get("USE_MOCK_STORAGE", False)
            
            if use_mock:
                logger.info("Using mock storage service")
                from src.catalog.services.mock_storage import MockStorage
                storage = MockStorage()
            else:
                logger.info("Initializing MinIO storage service")
                from src.catalog.services.storage_service import StorageService
                
                try:
                    storage = StorageService(app)
                    # Test connection by listing files
                    storage.list_files()
                    logger.info("MinIO storage connection successful")
                except Exception as e:
                    logger.error(f"MinIO connection failed: {str(e)}")
                    logger.info("Falling back to mock storage")
                    from src.catalog.services.mock_storage import MockStorage
                    storage = MockStorage()
                    app.config["USE_MOCK_STORAGE"] = True
            
            # Set the storage service
            import src.catalog
            src.catalog.storage_service = storage
            app.config["STORAGE_INITIALIZED"] = True
            logger.info("Storage service initialized successfully")
    except Exception as e:
        logger.error(f"Error in async storage initialization: {str(e)}")
        logger.error(traceback.format_exc())


# Start storage initialization in background thread
threading.Thread(target=init_storage_async, daemon=True).start()

if __name__ == "__main__":
    # Print environment variables for debugging (excluding secrets)
    print("Environment:")
    for key in sorted(os.environ.keys()):
        if key in [
            "DATABASE_URL",
            "SQLALCHEMY_DATABASE_URI",
            "REDIS_URL",
            "MINIO_ENDPOINT",
            "PORT",
        ]:
            # Show partial values for connection strings (hiding credentials)
            value = os.environ[key]
            if "@" in value and key != "PORT":
                parts = value.split("@")
                prefix = parts[0].split(":")[0]
                suffix = parts[1]
                print(f"  {key}: {prefix}://*****@{suffix}")
            else:
                print(f"  {key}: {value}")
        elif not any(
            secret in key.lower() for secret in ["key", "token", "secret", "password"]
        ):
            # Show non-sensitive environment variables
            print(f"  {key}: {os.environ[key]}")

    # Print port binding information explicitly
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting application on 0.0.0.0:{port}")

    # Run the application
    app.run(host="0.0.0.0", port=port, debug=False)
