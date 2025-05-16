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

# Set the default service type if not specified
SERVICE_TYPE=${SERVICE_TYPE:-"web"}

# Start a background process to monitor the main application
if [ "$SERVICE_TYPE" = "web" ]; then
    # Start a background timer
    {
        sleep 10  # Give the main app 10 seconds to bind to a port
        
        # Check if anything is listening on the expected port
        if ! nc -z localhost ${PORT:-5000}; then
            echo "*** WARNING: Main application failed to bind to port within 10 seconds ***"
            echo "*** Starting fallback application to maintain port binding ***"
            
            # Kill any existing gunicorn processes that might be stuck
            pkill -f gunicorn || true
            
            # Start the fallback app
            gunicorn --bind "0.0.0.0:${PORT:-5000}" --workers=1 fallback_app:app
        else
            echo "Main application successfully bound to port within timeout period"
        fi
    } &
    TIMER_PID=$!
    
    # Try to start the main application
    echo "Starting main application..."
    ./start.sh
    
    # If we get here, the main application exited
    echo "Main application exited. Checking if fallback is needed..."
    
    # Kill the timer if it's still running
    kill $TIMER_PID 2>/dev/null || true
    
    # Check if anything is still listening on the port
    if ! nc -z localhost ${PORT:-5000}; then
        echo "No application is binding to port. Starting fallback app..."
        gunicorn --bind "0.0.0.0:${PORT:-5000}" --workers=1 fallback_app:app
    fi
else
    # For non-web services, just run the normal start script
    exec ./start.sh
fi