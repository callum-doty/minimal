#!/bin/bash
# failsafe-start.sh - A wrapper script that ensures port binding happens quickly

set -e  # Exit immediately if a command exits with a non-zero status

# Print environment info for debugging
echo "Starting service with Failsafe Script"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "PORT: ${PORT}"

# Create necessary directories
mkdir -p ./data/documents
mkdir -p ./tmp
export TMPDIR=$(pwd)/tmp

# Set variables
PORT=${PORT:-5000}
FLASK_APP=src/wsgi.py

# Start minimal app to ensure port binding
echo "Starting minimal app to ensure port binding..."
python minimal_app.py &
MINIMAL_PID=$!

# Wait a moment
sleep 2

# Try to start the main app
echo "Attempting to start main application..."
gunicorn --bind "0.0.0.0:${PORT}" --workers=1 --timeout=120 src.wsgi:application

# If gunicorn exits with an error, check if minimal app is still running
if [ $? -ne 0 ]; then
    echo "Main application failed to start, keeping minimal app running"
    wait $MINIMAL_PID
else
    # Kill the minimal app if main app started successfully
    kill $MINIMAL_PID 2>/dev/null || true
fi