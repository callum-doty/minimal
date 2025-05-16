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

storage_service = None  # Will be initialized in create_app or wsgi.py


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
                "version": "1.0.0",
            }, 200
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}, 500

    # Register blueprints - MODIFIED FOR YOUR PROJECT STRUCTURE
    with app.app_context():
        try:
            # Modified: Use src.catalog.web instead of src.catalog.routes
            logger.info("Registering blueprints from src.catalog.web...")

            # Check if admin_routes.py exists and contains a blueprint
            try:
                from src.catalog.web.admin_routes import admin_bp

                app.register_blueprint(admin_bp, url_prefix="/api/admin")
                logger.info("Registered admin_bp blueprint")
            except (ImportError, AttributeError) as e:
                logger.warning(f"Could not import admin_bp blueprint: {str(e)}")

            # Check if main_routes.py exists and contains a blueprint
            try:
                from src.catalog.web.main_routes import main_bp

                app.register_blueprint(main_bp, url_prefix="/api")
                logger.info("Registered main_bp blueprint")
            except (ImportError, AttributeError) as e:
                logger.warning(f"Could not import main_bp blueprint: {str(e)}")

            # Check if search_routes.py exists and contains a blueprint
            try:
                from src.catalog.web.search_routes import search_bp

                app.register_blueprint(search_bp, url_prefix="/api/search")
                logger.info("Registered search_bp blueprint")
            except (ImportError, AttributeError) as e:
                logger.warning(f"Could not import search_bp blueprint: {str(e)}")

            # Add a fallback route for root path
            @app.route("/")
            def index():
                return {
                    "status": "online",
                    "message": "Document Catalog API is running",
                    "version": "1.0.0",
                }

        except Exception as e:
            logger.error(f"Error registering blueprints: {str(e)}")

    logger.info("Flask application initialized successfully")
    return app
