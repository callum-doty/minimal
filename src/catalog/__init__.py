# src/catalog/__init__.py
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create extension instances
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
csrf = CSRFProtect()

# Import services
from src.catalog.services.storage_service import StorageService

storage_service = StorageService()


def create_app(test_config=None):
    """Application factory pattern for Flask app"""

    # Create and configure the app
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    # Load configuration
    if os.path.exists("src/catalog/config.py"):
        # Use the new flexible configuration if available
        from src.catalog.config import configure_app

        app = configure_app(app)
    else:
        # Fall back to the original configuration
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY", "dev-key-please-change"),
            SQLALCHEMY_DATABASE_URI=os.environ.get(
                "DATABASE_URL",
                "postgresql://custom_user:strong_password@db:5432/catalog_db",
            ),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            CACHE_TYPE="redis",
            CACHE_REDIS_URL=os.environ.get("REDIS_URL", "redis://redis:6379/0"),
            CACHE_DEFAULT_TIMEOUT=300,
            WTF_CSRF_CHECK_DEFAULT=False,
            WTF_CSRF_TIME_LIMIT=None,
            WTF_CSRF_SSL_STRICT=False,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE="Lax",
        )

    # Override with test config if provided
    if test_config:
        app.config.update(test_config)

    # Detect Render deployment
    render_service = os.environ.get("RENDER_SERVICE_NAME")
    if render_service:
        app.config["SESSION_COOKIE_SECURE"] = True
        app.config["PREFERRED_URL_SCHEME"] = "https"
        logger.info(f"Detected Render deployment: {render_service}")

    # Also keep Railway detection for backward compatibility
    elif "RAILWAY_ENVIRONMENT" in os.environ:
        app.config["SESSION_COOKIE_SECURE"] = True
        app.config["PREFERRED_URL_SCHEME"] = "https"
        logger.info("Detected Railway deployment")

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    csrf.init_app(app)

    # Initialize storage service
    storage_service.init_app(app)

    # Register health check endpoint for Render
    @app.route("/health")
    def health_check():
        """Health check endpoint for Render."""
        try:
            # Check database connection
            db.session.execute("SELECT 1")

            # Try MinIO connection (simplified check)
            minio_status = "connected" if storage_service.client else "disconnected"

            return {
                "status": "healthy",
                "database": "connected",
                "storage": minio_status,
                "environment": os.environ.get("FLASK_ENV", "unknown"),
            }, 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}, 500

    # Register blueprints
    with app.app_context():
        try:
            # Import blueprints here to avoid circular imports
            from src.catalog.web.main_routes import main_routes
            from src.catalog.web.search_routes import search_routes

            app.register_blueprint(main_routes)
            app.register_blueprint(search_routes, url_prefix="/search")

            # Register admin blueprint
            try:
                from src.catalog.web.admin_routes import admin_bp

                app.register_blueprint(admin_bp)
                logger.info("Registered admin blueprint")
            except Exception as e:
                logger.warning(f"Could not register admin blueprint: {str(e)}")

        except Exception as e:
            logger.error(f"Error registering blueprints: {str(e)}")
            raise

    # Add middleware for security headers
    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"

        # Apply HSTS header if behind proxy or in secure environment
        if (
            render_service
            or "RAILWAY_ENVIRONMENT" in os.environ
            or os.environ.get("BEHIND_PROXY", "false").lower() == "true"
        ):
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response

    # Add middleware for handling proxies
    @app.before_request
    def handle_proxy():
        if (
            render_service
            or "RAILWAY_ENVIRONMENT" in os.environ
            or os.environ.get("BEHIND_PROXY", "false").lower() == "true"
        ):
            if "X-Forwarded-Proto" in request.headers:
                if request.headers["X-Forwarded-Proto"] == "https":
                    request.environ["wsgi.url_scheme"] = "https"

    return app
