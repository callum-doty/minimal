#!/usr/bin/env python
"""
Direct database migration script for Render deployment.

This script runs database migrations directly using Alembic,
without going through Flask-Migrate, which can help bypass
initialization issues with the Flask application.
"""

import os
import sys
import logging
import argparse
from alembic import command
from alembic.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_migrations(directory="migrations", revision="head", sql=False, tag=None):
    """Run database migrations directly with Alembic."""
    try:
        # Create Alembic config
        config = Config(os.path.join(directory, "alembic.ini"))
        config.set_main_option("script_location", directory)

        # Get database URL from environment
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL environment variable not set")
            return False

        # Convert postgres:// to postgresql:// for SQLAlchemy
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
            logger.info(
                "Converted postgres:// to postgresql:// for SQLAlchemy compatibility"
            )

        # Set database URL in config
        config.set_main_option("sqlalchemy.url", database_url)

        # Log the database we're connecting to (hiding credentials)
        if "@" in database_url:
            visible_url = f"{database_url.split('@')[0].split(':')[0]}://*****@{database_url.split('@')[1]}"
        else:
            visible_url = database_url
        logger.info(f"Running migrations with database URL: {visible_url}")

        # Run the migration
        logger.info(f"Running migration to revision: {revision}")
        command.upgrade(config, revision, sql=sql, tag=tag)

        logger.info("Migration completed successfully")
        return True
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run database migrations directly with Alembic"
    )
    parser.add_argument(
        "--directory", default="migrations", help="Migration script directory"
    )
    parser.add_argument("--revision", default="head", help="Revision to upgrade to")
    parser.add_argument(
        "--sql",
        action="store_true",
        help="Don't emit SQL to database - dump to standard output instead",
    )
    parser.add_argument("--tag", help="Arbitrary 'tag' name")

    args = parser.parse_args()

    success = run_migrations(
        directory=args.directory, revision=args.revision, sql=args.sql, tag=args.tag
    )

    sys.exit(0 if success else 1)
