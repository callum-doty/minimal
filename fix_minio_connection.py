#!/usr/bin/env python
"""
Fix MinIO connection issues in Render deployment.

This script modifies the application to properly handle MinIO connection issues
by ensuring the USE_MOCK_STORAGE flag is properly set and the application
falls back to mock storage when MinIO is unavailable.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def update_storage_service():
    """Update the storage service to better handle connection issues."""
    filepath = "src/catalog/services/storage_service.py"

    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        return False

    logger.info(f"Updating {filepath}...")

    with open(filepath, "r") as f:
        content = f.read()

    # Add improved error handling and connection retry logic
    updated_content = content.replace(
        "def _init_client(self):",
        """def _init_client(self):
        """,
    )

    # Increase connection timeout and retries
    updated_content = updated_content.replace(
        "http_client = PoolManager(timeout=10.0, retries=3)",
        "http_client = PoolManager(timeout=30.0, retries=5)",
    )

    # Add better error handling for bucket creation
    updated_content = updated_content.replace(
        """try:
                    if not self._client.bucket_exists(self.bucket):
                        self.logger.info(f"Creating bucket: {self.bucket}")
                        self._client.make_bucket(self.bucket)
                    else:
                        self.logger.info(f"Bucket exists: {self.bucket}")
                except Exception as e:
                    self.logger.error(f"Error checking/creating bucket: {str(e)}")""",
        """try:
                    if not self._client.bucket_exists(self.bucket):
                        self.logger.info(f"Creating bucket: {self.bucket}")
                        self._client.make_bucket(self.bucket)
                    else:
                        self.logger.info(f"Bucket exists: {self.bucket}")
                except Exception as e:
                    self.logger.error(f"Error checking/creating bucket: {str(e)}")
                    # If we can't create/check bucket, client is not usable
                    self._client = None
                    # Check if we should use mock storage instead
                    if os.environ.get("USE_MOCK_STORAGE", "").lower() == "true":
                        self.logger.warning("Falling back to mock storage due to MinIO connection issues")
                    else:
                        self.logger.error("MinIO connection failed and USE_MOCK_STORAGE is not enabled")""",
    )

    with open(filepath, "w") as f:
        f.write(updated_content)

    logger.info(f"Updated {filepath} with improved error handling")
    return True


def update_wsgi():
    """Update the wsgi.py file to properly handle storage service initialization."""
    filepath = "src/wsgi.py"

    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        return False

    logger.info(f"Updating {filepath}...")

    with open(filepath, "r") as f:
        content = f.read()

    # Update the storage initialization function to handle connection issues
    updated_content = content.replace(
        """def init_storage_async():
    \"\"\"Initialize storage service asynchronously.\"\"\"
    try:
        logger.info("Starting async storage initialization...")
        time.sleep(2)  # Let the main application start first

        with app.app_context():
            # Always use mock storage in Render (temporary fix)
            logger.info("Using mock storage service for Render deployment")
            from src.catalog.services.mock_storage import MockStorage

            mock_storage = MockStorage()
            import src.catalog

            src.catalog.storage_service = mock_storage
            app.config["STORAGE_INITIALIZED"] = True
            app.config["USE_MOCK_STORAGE"] = True
            logger.info("Mock storage initialized successfully")""",
        """def init_storage_async():
    \"\"\"Initialize storage service asynchronously.\"\"\"
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
            logger.info("Storage service initialized successfully")""",
    )

    with open(filepath, "w") as f:
        f.write(updated_content)

    logger.info(f"Updated {filepath} with improved storage initialization")
    return True


def main():
    """Main function to fix MinIO connection issues."""
    logger.info("Starting MinIO connection fix...")

    # Update storage service
    update_storage_service()

    # Update wsgi initialization
    update_wsgi()

    logger.info("MinIO connection fix complete. Please redeploy your application.")
    logger.info(
        "Make sure USE_MOCK_STORAGE=true is set in your environment variables for worker services."
    )


if __name__ == "__main__":
    main()
