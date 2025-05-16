"""
Mock storage service for environments without MinIO.
"""

import os
import logging
import io
from PIL import Image, ImageDraw
from flask import current_app

logger = logging.getLogger(__name__)


class MockStorage:
    """Mock storage implementation that doesn't require MinIO."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing mock storage service")
        self._storage = {}  # In-memory storage
        self.bucket = "documents"

    @property
    def client(self):
        """Return self as mock client."""
        return self

    def upload_file(self, file_path, object_name=None):
        """Mock upload a file."""
        if object_name is None:
            object_name = os.path.basename(file_path)

        self.logger.info(f"Mock upload: {file_path} -> {object_name}")

        try:
            # Read the file content
            with open(file_path, "rb") as f:
                content = f.read()

            # Store in memory
            self._storage[object_name] = content
            return f"{self.bucket}/{object_name}"
        except Exception as e:
            self.logger.error(f"Mock upload failed: {str(e)}")
            raise

    def get_file(self, object_name):
        """Get mock file data."""
        self.logger.info(f"Mock get file: {object_name}")

        # Return file if exists
        if object_name in self._storage:
            return self._storage[object_name]

        # Return placeholder image
        return self._get_placeholder_image()

    def download_file(self, object_name, file_path):
        """Mock download file."""
        self.logger.info(f"Mock download: {object_name} -> {file_path}")

        if object_name in self._storage:
            try:
                # Write to file
                with open(file_path, "wb") as f:
                    f.write(self._storage[object_name])
                return file_path
            except Exception as e:
                self.logger.error(f"Mock download failed: {str(e)}")
                raise
        else:
            self.logger.error(f"File not found: {object_name}")
            raise FileNotFoundError(f"File not found: {object_name}")

    def list_files(self):
        """List mock files."""
        return list(self._storage.keys())

    def get_file_url(self, object_name, expires=3600):
        """Get a mock URL for an object."""
        return f"/api/documents/{object_name}"

    def delete_file(self, object_name):
        """Delete mock file."""
        if object_name in self._storage:
            del self._storage[object_name]
            return True
        return False

    def _get_placeholder_image(self):
        """Return a placeholder image."""
        try:
            img = Image.new("RGB", (300, 300), color=(240, 240, 240))
            d = ImageDraw.Draw(img)
            d.text((100, 140), "Mock Storage", fill=(120, 120, 120))

            img_io = io.BytesIO()
            img.save(img_io, "PNG")
            img_io.seek(0)
            return img_io.getvalue()
        except Exception:
            return b""
