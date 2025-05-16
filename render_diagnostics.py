#!/usr/bin/env python
"""
Remote debugging script for Render deployment.

This script dumps diagnostic information about the environment,
database connections, and service availability.
"""

import os
import sys
import logging
import socket
import json
import traceback
import time
import subprocess
import psycopg2
import importlib.util
import urllib.request

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_system_info():
    """Gather system information."""
    logger.info("=== System Information ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Hostname: {socket.gethostname()}")

    # Check working directory and files
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Directory contents: {os.listdir('.')}")

    # Check available memory
    try:
        memory_info = subprocess.check_output(["free", "-m"]).decode("utf-8")
        logger.info(f"Memory Info:\n{memory_info}")
    except Exception as e:
        logger.warning(f"Couldn't get memory info: {e}")

    # Check disk space
    try:
        disk_info = subprocess.check_output(["df", "-h"]).decode("utf-8")
        logger.info(f"Disk Info:\n{disk_info}")
    except Exception as e:
        logger.warning(f"Couldn't get disk info: {e}")


def check_environment_variables():
    """Log non-sensitive environment variables."""
    logger.info("=== Environment Variables ===")

    # Track presence of key variables
    required_vars = [
        "DATABASE_URL",
        "PORT",
        "REDIS_URL",
        "MINIO_ENDPOINT",
        "PYTHONPATH",
    ]
    found_vars = {}

    for var in required_vars:
        if var in os.environ:
            # Hide credentials but confirm presence
            value = os.environ[var]
            if "URL" in var and "@" in value:
                # Show server part of URL without credentials
                parts = value.split("@")
                prefix = parts[0].split(":")[0]
                suffix = parts[1]
                masked_value = f"{prefix}://*****@{suffix}"
            else:
                # For other variables show normal value
                masked_value = value

            logger.info(f"{var}: {masked_value}")
            found_vars[var] = True
        else:
            logger.warning(f"{var}: NOT SET")
            found_vars[var] = False

    # Return status of required variables
    return found_vars


def check_network_connectivity():
    """Check network connectivity to key services."""
    logger.info("=== Network Connectivity ===")

    # Define external services to check
    services = {
        "Google DNS": "8.8.8.8:53",
        "PostgreSQL": (
            os.environ.get("DATABASE_URL", "").split("@")[-1].split("/")[0]
            if "@" in os.environ.get("DATABASE_URL", "")
            else None
        ),
        "MinIO": os.environ.get("MINIO_ENDPOINT", ""),
        "Redis": (
            os.environ.get("REDIS_URL", "").split("@")[-1].split("/")[0]
            if "@" in os.environ.get("REDIS_URL", "")
            else None
        ),
    }

    # Try to connect to each service
    results = {}
    for service_name, address in services.items():
        if not address:
            logger.warning(f"{service_name}: No address available")
            results[service_name] = False
            continue

        # Split host and port
        if ":" in address:
            host, port = address.split(":")
            port = int(port)
        else:
            host = address
            port = 80  # Default port

        logger.info(f"Checking {service_name} at {host}:{port}...")

        # Try to connect
        try:
            start_time = time.time()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((host, port))
            s.close()
            duration = time.time() - start_time
            logger.info(f"{service_name}: Connected in {duration:.2f}s")
            results[service_name] = True
        except Exception as e:
            logger.warning(f"{service_name}: Failed to connect - {str(e)}")
            results[service_name] = False

    return results


def check_database_connection():
    """Test database connection."""
    logger.info("=== Database Connection ===")

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set")
        return False

    # Convert postgres:// to postgresql:// for SQLAlchemy
    if database_url.startswith("postgres://"):
        pg_url = database_url.replace("postgres://", "postgresql://", 1)
        logger.info("Converted postgres:// to postgresql:// for compatibility")
    else:
        pg_url = database_url

    # Log connection info (hiding credentials)
    visible_url = f"{pg_url.split('@')[0].split(':')[0]}://*****@{pg_url.split('@')[1]}"
    logger.info(f"Connecting to: {visible_url}")

    try:
        # Connect to database
        conn = psycopg2.connect(pg_url)
        cursor = conn.cursor()

        # Check if we can query
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        logger.info(f"Connected successfully: {version}")

        # Check for required extensions
        cursor.execute("SELECT extname FROM pg_extension")
        extensions = [row[0] for row in cursor.fetchall()]
        logger.info(f"Installed extensions: {extensions}")

        # Check if important tables exist
        cursor.execute(
            """
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """
        )
        tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"Found tables: {tables}")

        # Close connection
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False


def check_application_imports():
    """Check if we can import application modules."""
    logger.info("=== Application Imports ===")

    modules = [
        "src.catalog",
        "src.catalog.config",
        "src.catalog.services.storage_service",
        "src.catalog.services.mock_storage",
    ]

    for module_name in modules:
        try:
            module = importlib.import_module(module_name)
            logger.info(f"Successfully imported: {module_name}")
        except Exception as e:
            logger.error(f"Failed to import {module_name}: {str(e)}")
            logger.error(traceback.format_exc())


def run_http_server_check():
    """Check if HTTP server is running on expected port."""
    logger.info("=== HTTP Server Check ===")

    port = os.environ.get("PORT", "5000")
    logger.info(f"Checking for HTTP server on port {port}")

    try:
        # Try to connect to localhost on expected port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex(("127.0.0.1", int(port)))
        if result == 0:
            logger.info(f"Port {port} is open - server appears to be running")

            # Try to get a response
            try:
                response = urllib.request.urlopen(f"http://127.0.0.1:{port}/health")
                logger.info(f"HTTP GET /health - Status: {response.status}")
                logger.info(f"Response: {response.read().decode('utf-8')}")
            except Exception as e:
                logger.warning(f"HTTP GET failed: {str(e)}")
        else:
            logger.warning(f"Port {port} is not open - server may not be running")
    except Exception as e:
        logger.error(f"Error checking for HTTP server: {str(e)}")
    finally:
        s.close()


if __name__ == "__main__":
    logger.info("=== Render Deployment Diagnostics ===")

    # Run all checks
    check_system_info()
    env_vars = check_environment_variables()
    network = check_network_connectivity()
    db_ok = check_database_connection()
    check_application_imports()
    run_http_server_check()

    # Print summary
    logger.info("\n=== Diagnostic Summary ===")
    logger.info(
        f"Environment Variables: {'ALL PRESENT' if all(env_vars.values()) else 'MISSING SOME'}"
    )
    logger.info(f"Database Connection: {'SUCCESS' if db_ok else 'FAILED'}")
    logger.info(
        f"Network Connectivity: {', '.join([s for s, v in network.items() if v])}"
    )
    logger.info(
        f"Network Issues: {', '.join([s for s, v in network.items() if not v]) or 'None'}"
    )

    # Save results to file for future reference
    with open("render_diagnostics.json", "w") as f:
        json.dump(
            {
                "timestamp": time.time(),
                "environment_variables": env_vars,
                "network_connectivity": network,
                "database_connection": db_ok,
            },
            f,
            indent=2,
        )

    logger.info("Diagnostics complete. Results saved to render_diagnostics.json")
