"""
Initialize the Flask application and its extensions.
"""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# Create logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

# Import services
from src.catalog.services.storage_service import StorageService
from src.catalog.services.mock_storage import MockStorage

storage_service = None  # Will be initialized in create_app


def create_app(test_config=None):
    """Create and configure the Flask application."""
    # Create the Flask app
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    from src.catalog.config import configure_app

    app = configure_app(app)

    # Override with test config if provided
    if test_config:
        app.config.update(test_config)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Initialize storage service placeholder
    global storage_service
    storage_service = None  # Will be initialized asynchronously in wsgi.py

    # Register health check endpoint
    @app.route("/health")
    def health_check():
        """Health check endpoint for Render."""
        try:
            # Check database connection
            db.session.execute("SELECT 1")

            # Check storage initialization status
            storage_status = "initializing"
            if app.config.get("STORAGE_INITIALIZED"):
                storage_status = "initialized"
            elif app.config.get("USE_MOCK_STORAGE"):
                storage_status = "mock_storage"

            return {
                "status": "healthy",
                "database": "connected",
                "storage": storage_status,
            }, 200
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}, 500

    # Register blueprints
    with app.app_context():
        # Import and register blueprints
        from src.catalog.routes.upload import upload_bp

        app.register_blueprint(upload_bp, url_prefix="/api/upload")

        from src.catalog.routes.documents import documents_bp

        app.register_blueprint(documents_bp, url_prefix="/api/documents")

        from src.catalog.routes.admin import admin_bp

        app.register_blueprint(admin_bp, url_prefix="/api/admin")

        logger.info("Registered admin blueprint")

    return app
