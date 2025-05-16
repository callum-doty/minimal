"""
Storage service for handling file operations with MinIO.
"""

import os
import logging
from minio import Minio
from urllib3 import PoolManager
import io
from flask import current_app

logger = logging.getLogger(__name__)


class MinIOStorage:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MinIOStorage, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        """Initialize the MinIO client."""
        if self._client is None:
            self.logger = logging.getLogger(__name__)
            http_client = PoolManager(timeout=30.0, retries=5)

            # Check for environment variables - first check the new Render-specific ones
            endpoint = os.getenv("MINIO_ENDPOINT") or os.getenv(
                "MINIO_URL", "minio:9000"
            )
            access_key = os.getenv("MINIO_ACCESS_KEY", "minioaccess")
            secret_key = os.getenv("MINIO_SECRET_KEY", "miniosecret")
            secure = os.getenv("MINIO_SECURE", "").lower() == "true"

            self.logger.info(
                f"Initializing Minio client with endpoint: {endpoint}, secure: {secure}"
            )

            try:
                self._client = Minio(
                    endpoint=endpoint,
                    access_key=access_key,
                    secret_key=secret_key,
                    secure=secure,
                    http_client=http_client,
                )
                self.bucket = os.getenv("MINIO_BUCKET", "documents")

                # Make sure the bucket exists
                try:
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
                        self.logger.warning(
                            "Falling back to mock storage due to MinIO connection issues"
                        )
                    else:
                        self.logger.error(
                            "MinIO connection failed and USE_MOCK_STORAGE is not enabled"
                        )
            except Exception as e:
                self.logger.error(f"Error initializing MinIO client: {str(e)}")
                self._client = None

    @property
    def client(self):
        """Get the MinIO client instance."""
        if self._client is None:
            self._init_client()
        return self._client

    def upload_file(self, filepath, filename):
        """Upload file to MinIO"""
        if self.client is None:
            self.logger.error("MinIO client is not initialized")
            raise Exception("MinIO client is not initialized")

        try:
            self.logger.info(f"Uploading file to MinIO: {filename}")

            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")

            self.client.fput_object(
                bucket_name=self.bucket, object_name=filename, file_path=filepath
            )

            # Verify the file was uploaded
            try:
                self.client.stat_object(self.bucket, filename)
                self.logger.info(f"Successfully uploaded file: {filename}")
            except Exception as e:
                self.logger.error(f"File upload verification failed: {str(e)}")
                raise

            return f"{self.bucket}/{filename}"
        except Exception as e:
            self.logger.error(f"MinIO upload failed: {str(e)}")
            raise Exception(f"MinIO upload failed: {str(e)}")

    def get_file(self, filename):
        """Get file data from MinIO"""
        if self.client is None:
            self.logger.error("MinIO client is not initialized")
            return self._get_placeholder_image()

        try:
            self.logger.info(f"Getting file from MinIO: {filename}")

            # Check if file exists first
            try:
                self.client.stat_object(self.bucket, filename)
            except Exception as e:
                self.logger.error(f"File does not exist in MinIO: {filename}")
                # Return a default placeholder image if file doesn't exist
                return self._get_placeholder_image()

            data = io.BytesIO()
            response = self.client.get_object(self.bucket, filename)

            for d in response.stream(32 * 1024):
                data.write(d)
            data.seek(0)

            self.logger.info(f"Successfully retrieved file: {filename}")
            return data.getvalue()
        except Exception as e:
            self.logger.error(f"MinIO download failed: {str(e)}")
            # Return a default placeholder image for errors
            return self._get_placeholder_image()

    def _get_placeholder_image(self):
        """Return a placeholder image for missing files"""
        # Path to a default placeholder image in your static directory
        placeholder_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "static",
            "img",
            "placeholder.png",
        )

        # If the placeholder exists, return it
        if os.path.exists(placeholder_path):
            with open(placeholder_path, "rb") as f:
                return f.read()

        # Otherwise generate a simple blank image using PIL
        try:
            from PIL import Image, ImageDraw

            img = Image.new("RGB", (300, 300), color=(240, 240, 240))
            d = ImageDraw.Draw(img)
            d.text((100, 140), "No Image", fill=(120, 120, 120))

            img_io = io.BytesIO()
            img.save(img_io, "PNG")
            img_io.seek(0)
            return img_io.getvalue()
        except Exception:
            # If all else fails, return empty bytes
            return b""

    def download_file(self, filename, download_path):
        """Download file from MinIO to a local path"""
        if self.client is None:
            self.logger.error("MinIO client is not initialized")
            raise Exception("MinIO client is not initialized")

        try:
            self.logger.info(f"Downloading file from MinIO: {filename}")
            self.client.fget_object(
                bucket_name=self.bucket, object_name=filename, file_path=download_path
            )

            if os.path.exists(download_path):
                self.logger.info(f"Successfully downloaded file: {filename}")
                return download_path
            else:
                raise FileNotFoundError(
                    f"Download failed - file not created: {download_path}"
                )
        except Exception as e:
            self.logger.error(f"MinIO download failed: {str(e)}")
            raise Exception(f"MinIO download failed: {str(e)}")

    def list_files(self):
        """List all files in the bucket"""
        if self.client is None:
            self.logger.error("MinIO client is not initialized")
            return []

        files = []
        try:
            objects = self.client.list_objects(self.bucket, recursive=True)
            for obj in objects:
                files.append(obj.object_name)
            return files
        except Exception as e:
            self.logger.error(f"Error listing MinIO files: {str(e)}")
            return []

    def get_file_url(self, object_name, expires=3600):
        """Get a presigned URL for an object."""
        if self.client is None:
            self.logger.error("MinIO client is not initialized")
            return None

        try:
            url = self.client.presigned_get_object(
                self.bucket, object_name, expires=expires
            )
            return url
        except Exception as e:
            self.logger.error(f"Error getting presigned URL: {str(e)}")
            return None

    def delete_file(self, object_name):
        """Delete a file from MinIO."""
        if self.client is None:
            self.logger.error("MinIO client is not initialized")
            return False

        try:
            self.logger.info(f"Deleting file {self.bucket}/{object_name}")
            self.client.remove_object(self.bucket, object_name)
            self.logger.info(f"File deleted successfully: {object_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting file: {str(e)}")
            return False


# For backward compatibility with the StorageService class pattern
class StorageService:
    def __init__(self, app=None):
        # Check if we should use mock storage before initializing MinIO
        self.use_mock_storage = False
        self.mock_storage = None
        self.minio_storage = None

        if app is not None:
            self.init_app(app)
        else:
            # Check environment variable directly if no app is provided
            self.use_mock_storage = (
                os.environ.get("USE_MOCK_STORAGE", "").lower() == "true"
            )
            if not self.use_mock_storage:
                self.minio_storage = MinIOStorage()

    def init_app(self, app):
        """Initialize the storage service with the app."""
        # Check if we should use mock storage
        self.use_mock_storage = app.config.get("USE_MOCK_STORAGE", False)

        if self.use_mock_storage:
            # Use mock storage instead of MinIO
            logger.info("Using mock storage instead of MinIO (USE_MOCK_STORAGE=True)")
            from src.catalog.services.mock_storage import MockStorage

            self.mock_storage = MockStorage()
            return

        # Only initialize MinIO if not using mock storage
        logger.info("Initializing MinIO storage")
        self.minio_storage = MinIOStorage()

        # Update MinIO configuration from app config
        endpoint = app.config.get("MINIO_ENDPOINT")
        access_key = app.config.get("MINIO_ACCESS_KEY")
        secret_key = app.config.get("MINIO_SECRET_KEY")
        secure = app.config.get("MINIO_SECURE", False)
        bucket = app.config.get("MINIO_BUCKET", "documents")

        if endpoint and access_key and secret_key:
            # Set environment variables for MinIOStorage
            os.environ["MINIO_ENDPOINT"] = endpoint
            os.environ["MINIO_ACCESS_KEY"] = access_key
            os.environ["MINIO_SECRET_KEY"] = secret_key
            os.environ["MINIO_SECURE"] = "true" if secure else "false"
            os.environ["MINIO_BUCKET"] = bucket

            # Reinitialize the client with the new settings
            self.minio_storage._client = None
            self.minio_storage._init_client()

    @property
    def client(self):
        """Get the storage client."""
        if self.use_mock_storage:
            return self.mock_storage.client if self.mock_storage else None
        return self.minio_storage.client if self.minio_storage else None

    def upload_file(self, file_path, object_name=None):
        """Upload a file to storage."""
        if object_name is None:
            object_name = os.path.basename(file_path)

        if self.use_mock_storage:
            return self.mock_storage.upload_file(file_path, object_name)
        return self.minio_storage.upload_file(file_path, object_name)

    def download_file(self, object_name, file_path):
        """Download a file from storage."""
        if self.use_mock_storage:
            return self.mock_storage.download_file(object_name, file_path)
        return self.minio_storage.download_file(object_name, file_path)

    def get_file(self, object_name):
        """Get file data from storage."""
        if self.use_mock_storage:
            return self.mock_storage.get_file(object_name)
        return self.minio_storage.get_file(object_name)

    def get_file_url(self, object_name, expires=3600):
        """Get a presigned URL for an object."""
        if self.use_mock_storage:
            return self.mock_storage.get_file_url(object_name, expires)
        return self.minio_storage.get_file_url(object_name, expires)

    def list_files(self):
        """List all files in storage."""
        if self.use_mock_storage:
            return self.mock_storage.list_files()
        return self.minio_storage.list_files()

    def delete_file(self, object_name):
        """Delete a file from storage."""
        if self.use_mock_storage:
            return self.mock_storage.delete_file(object_name)
        return self.minio_storage.delete_file(object_name)
