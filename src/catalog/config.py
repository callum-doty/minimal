"""
Configuration loader for different environments.
This allows the application to run locally with docker-compose or in Render.
"""

import os
import logging

logger = logging.getLogger(__name__)


def get_database_uri():
    """Get the database URI based on the environment."""
    # First priority: Check for Render's DATABASE_URL
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        # Render provides PostgreSQL connection strings that begin with postgres://
        # but SQLAlchemy requires postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
            logger.info("Using Render DATABASE_URL (modified for SQLAlchemy)")
        return database_url

    # Second priority: Check for explicit configuration
    db_user = os.environ.get("DB_USER") or os.environ.get(
        "POSTGRES_USER", "custom_user"
    )
    db_password = os.environ.get("DB_PASSWORD") or os.environ.get(
        "POSTGRES_PASSWORD", "strong_password"
    )
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = os.environ.get("DB_PORT", "5432")
    db_name = os.environ.get("DB_NAME") or os.environ.get("POSTGRES_DB", "catalog_db")

    # Build the connection string
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def get_redis_uri():
    """Get Redis URI based on environment."""
    # First priority: Check for Render's REDIS_URL
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        logger.info("Using Render REDIS_URL")
        return redis_url

    # Second priority: Check for explicit configuration
    redis_host = os.environ.get("REDIS_HOST", "localhost")
    redis_port = os.environ.get("REDIS_PORT", "6379")
    redis_db = os.environ.get("REDIS_DB", "0")

    # Build the connection string
    return f"redis://{redis_host}:{redis_port}/{redis_db}"


def get_minio_config():
    """Get MinIO configuration based on environment."""
    return {
        "endpoint": os.environ.get("MINIO_ENDPOINT")
        or os.environ.get("MINIO_URL", "localhost:9000"),
        "access_key": os.environ.get("MINIO_ACCESS_KEY", "minioaccess"),
        "secret_key": os.environ.get("MINIO_SECRET_KEY", "miniosecret"),
        "secure": os.environ.get("MINIO_SECURE", "false").lower() == "true",
        "bucket": os.environ.get("MINIO_BUCKET")
        or os.environ.get("STORAGE_BUCKET", "documents"),
    }


def configure_app(app):
    """Configure Flask app based on environment."""
    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Redis and Celery configuration
    redis_uri = get_redis_uri()
    app.config["REDIS_URL"] = redis_uri
    app.config["CELERY_BROKER_URL"] = redis_uri
    app.config["CELERY_RESULT_BACKEND"] = redis_uri

    # MinIO configuration
    minio_config = get_minio_config()
    app.config["MINIO_ENDPOINT"] = minio_config["endpoint"]
    app.config["MINIO_ACCESS_KEY"] = minio_config["access_key"]
    app.config["MINIO_SECRET_KEY"] = minio_config["secret_key"]
    app.config["MINIO_SECURE"] = minio_config["secure"]
    app.config["MINIO_BUCKET"] = minio_config["bucket"]

    # Add flag for using mock storage if MinIO is not available
    app.config["USE_MOCK_STORAGE"] = (
        os.environ.get("USE_MOCK_STORAGE", "false").lower() == "true"
    )

    # Handle other Flask configurations
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "your_secure_random_key_here"
    )
    app.config["SITE_PASSWORD"] = os.environ.get("SITE_PASSWORD", None)

    # Security settings
    app.config["SECURE_COOKIES"] = (
        os.environ.get("SECURE_COOKIES", "false").lower() == "true"
    )
    app.config["BEHIND_PROXY"] = (
        os.environ.get("BEHIND_PROXY", "false").lower() == "true"
    )

    # File upload settings
    app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_FOLDER", "./uploads")
    app.config["MAX_CONTENT_LENGTH"] = int(
        os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024)
    )
    app.config["ALLOWED_EXTENSIONS"] = {
        "pdf",
        "png",
        "jpg",
        "jpeg",
        "tiff",
        "tif",
        "gif",
        "bmp",
    }

    # Storage directories
    app.config["STORAGE_DIR"] = os.environ.get("STORAGE_DIR", "./data")
    app.config["TMPDIR"] = os.environ.get("TMPDIR", "./tmp")

    # Ensure directories exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["STORAGE_DIR"], exist_ok=True)
    os.makedirs(app.config["TMPDIR"], exist_ok=True)

    # Log configurations
    logger.info(
        f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[0].split(':')[0]}://*****@{app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1]}"
    )
    logger.info(
        f"Redis URI: {redis_uri.split('@')[0]}@{redis_uri.split('@')[1] if '@' in redis_uri else redis_uri.split('//')[1]}"
    )
    logger.info(
        f"MinIO Endpoint: {minio_config['endpoint']}, Secure: {minio_config['secure']}, Use Mock: {app.config['USE_MOCK_STORAGE']}"
    )

    return app
