#!/bin/bash
# start.sh - Script to start the application on Render

set -e  # Exit immediately if a command exits with a non-zero status

# Print environment info for debugging
echo "Starting service with environment: SERVICE_TYPE=${SERVICE_TYPE}"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"

# Create necessary directories
mkdir -p ./data/documents
mkdir -p ./tmp
export TMPDIR=$(pwd)/tmp

# Set the default service type if not specified
SERVICE_TYPE=${SERVICE_TYPE:-"web"}

# Handle service based on type
case $SERVICE_TYPE in
  "web")
    echo "Starting web service..."
    
    # Try to run database migrations
    FLASK_APP=src/wsgi.py python -m flask db upgrade
    
    # Start the Flask application with proper settings for proxies
    echo "Starting with proxy settings..."
    gunicorn --bind "0.0.0.0:${PORT:-5000}" --workers=1 --timeout=120 --forwarded-allow-ips='*' src.wsgi:application
    ;;
    
  "worker")
    echo "Starting Celery worker..."
    
    # List available tasks (for debugging)
    echo "Listing available tasks..."
    python -c "import sys; print('Python path:', sys.path); from src.catalog.tasks.celery_app import celery_app; print('Available tasks:', list(celery_app.tasks.keys()))"
    
    # Start with very limited concurrency to prevent memory issues
    celery -A src.catalog.tasks.celery_app worker -Q document_processing,analysis,celery --loglevel=info --concurrency=2
    ;;
    
  "beat")
    echo "Starting Celery beat..."
    
    # Start the beat scheduler with a smaller interval
    celery -A src.catalog.tasks.celery_app beat --loglevel=info --max-interval=60
    ;;
    
  *)
    echo "ERROR: Unknown service type '${SERVICE_TYPE}'"
    echo "Valid values are: web, worker, beat"
    exit 1
    ;;
esac