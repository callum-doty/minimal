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
    db_user = os.environ.get("DB_USER", "custom_user")
    db_password = os.environ.get("DB_PASSWORD", "strong_password")
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = os.environ.get("DB_PORT", "5432")
    db_name = os.environ.get("DB_NAME", "catalog_db")

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
        "endpoint": os.environ.get("MINIO_ENDPOINT", "localhost:9000"),
        "access_key": os.environ.get("MINIO_ACCESS_KEY", "minioaccess"),
        "secret_key": os.environ.get("MINIO_SECRET_KEY", "miniosecret"),
        "secure": os.environ.get("MINIO_SECURE", "false").lower() == "true",
        "bucket": os.environ.get("MINIO_BUCKET", "documents"),
    }


def configure_app(app):
    """Configure Flask app based on environment."""
    # Set basic security settings
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-please-change")

    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Redis and Celery configuration
    redis_uri = get_redis_uri()
    app.config["REDIS_URL"] = redis_uri
    app.config["CELERY_BROKER_URL"] = redis_uri
    app.config["CELERY_RESULT_BACKEND"] = redis_uri

    # Configure Flask-Caching
    app.config["CACHE_TYPE"] = "redis"
    app.config["CACHE_REDIS_URL"] = redis_uri
    app.config["CACHE_DEFAULT_TIMEOUT"] = 300

    # Configure CSRF protection
    app.config["WTF_CSRF_CHECK_DEFAULT"] = False
    app.config["WTF_CSRF_TIME_LIMIT"] = None
    app.config["WTF_CSRF_SSL_STRICT"] = False

    # Configure session cookies
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Check if running in secure environment
    render_service = os.environ.get("RENDER_SERVICE_NAME")
    if render_service or os.environ.get("BEHIND_PROXY", "false").lower() == "true":
        app.config["SESSION_COOKIE_SECURE"] = True
        app.config["PREFERRED_URL_SCHEME"] = "https"

    # MinIO configuration
    minio_config = get_minio_config()
    app.config["MINIO_ENDPOINT"] = minio_config["endpoint"]
    app.config["MINIO_ACCESS_KEY"] = minio_config["access_key"]
    app.config["MINIO_SECRET_KEY"] = minio_config["secret_key"]
    app.config["MINIO_SECURE"] = minio_config["secure"]
    app.config["MINIO_BUCKET"] = minio_config["bucket"]

    # File upload configurations
    app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_FOLDER", "./uploads")
    app.config["MAX_CONTENT_LENGTH"] = int(
        os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024)
    )

    # Log configuration information (safely omitting secrets)
    db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    masked_db_uri = (
        f"{db_uri.split('@')[0].split(':')[0]}://*****@{db_uri.split('@')[1]}"
        if "@" in db_uri
        else db_uri
    )
    logger.info(f"Database URI: {masked_db_uri}")

    masked_redis = (
        f"{redis_uri.split('@')[0]}@{redis_uri.split('@')[1]}"
        if "@" in redis_uri
        else redis_uri
    )
    logger.info(f"Redis URI: {masked_redis}")

    logger.info(
        f"MinIO Endpoint: {minio_config['endpoint']}, Secure: {minio_config['secure']}"
    )
    logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'not set')}")

    return app
