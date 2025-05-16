"""
Alembic environment script for database migrations.
"""

import logging
import os
from logging.config import fileConfig

from flask import current_app
from alembic import context

# Alembic Config object
config = context.config

# Setup loggers
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")


def get_engine():
    """Get SQLAlchemy engine from Flask app."""
    try:
        # Flask-SQLAlchemy <3 and Alchemical
        return current_app.extensions["migrate"].db.get_engine()
    except (TypeError, AttributeError):
        # Flask-SQLAlchemy >=3
        return current_app.extensions["migrate"].db.engine


def get_engine_url():
    """Get database URL for migrations."""
    # First check for direct DATABASE_URL from environment (Render)
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        # SQLAlchemy requires postgresql:// instead of postgres://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
            logger.info("Using environment DATABASE_URL (modified for SQLAlchemy)")
        return database_url

    # Otherwise use the URL from the Flask app's engine
    try:
        return get_engine().url.render_as_string(hide_password=False).replace("%", "%%")
    except AttributeError:
        return str(get_engine().url).replace("%", "%%")


# Configure database URL in Alembic config
url = get_engine_url()
logger.info(
    f"Using database URL: {url.split('@')[0].split(':')[0]}://*****@{url.split('@')[1] if '@' in url else 'localhost:5432'}"
)
config.set_main_option("sqlalchemy.url", url)

# Get metadata for autogenerate
target_db = current_app.extensions["migrate"].db


def get_metadata():
    """Get metadata for migrations."""
    if hasattr(target_db, "metadatas"):
        return target_db.metadatas[None]
    return target_db.metadata


def run_migrations_offline():
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=get_metadata(), literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate
    a connection with the context.
    """

    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    # Get the configured engine
    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            process_revision_directives=process_revision_directives,
            **current_app.extensions["migrate"].configure_args,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
