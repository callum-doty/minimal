"""
Create Flask application with specific configuration for Render deployment.
"""

import os
import sys
import logging
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the src directory to the path if needed
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Create and configure the Flask application
from src.catalog import create_app

app = create_app()


# Function to initialize storage in background
def init_storage_async():
    """Initialize storage service asynchronously."""
    from src.catalog.services.storage_service import StorageService
    from src.catalog.services.mock_storage import MockStorage
    from src.catalog import storage_service

    try:
        logger.info("Starting async storage initialization...")
        time.sleep(2)  # Let the main application start first

        with app.app_context():
            # Check if mock storage is enabled
            if app.config.get("USE_MOCK_STORAGE"):
                logger.info("Using mock storage service (async)")
                app.config["STORAGE_INITIALIZED"] = True
                return

            # Try to initialize MinIO
            logger.info("Initializing MinIO storage service (async)")
            try:
                if (
                    storage_service is None
                    or not hasattr(storage_service, "client")
                    or storage_service.client is None
                ):
                    storage_svc = StorageService()
                    storage_svc.init_app(app)
                    logger.info("MinIO storage initialized successfully (async)")
                    app.config["STORAGE_INITIALIZED"] = True
                else:
                    logger.info("Storage service already initialized")
                    app.config["STORAGE_INITIALIZED"] = True
            except Exception as e:
                logger.warning(f"Error initializing storage service (async): {str(e)}")
                logger.info("Falling back to mock storage service (async)")
                mock_storage = MockStorage()
                app.config["STORAGE_INITIALIZED"] = True
    except Exception as e:
        logger.error(f"Error in async storage initialization: {str(e)}")


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
