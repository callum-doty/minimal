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

# Define function to start minimal app
start_minimal_app() {
    echo "Starting minimal fallback application..."
    gunicorn --bind "0.0.0.0:${PORT:-5000}" --workers=1 minimal_app:app
}

# Function to start main app
start_main_app() {
    echo "Attempting to start main application..."
    if [ -f "./start.sh" ]; then
        # Try to start the main application with our standard script
        ./start.sh || start_minimal_app
    else
        # Directly try gunicorn if start.sh is missing
        gunicorn --bind "0.0.0.0:${PORT:-5000}" --workers=1 --timeout=300 src.wsgi:application || start_minimal_app
    fi
}

# Main execution logic
if [ "$SERVICE_TYPE" = "web" ]; then
    # Start a background timer to ensure something binds to the port
    {
        sleep 15  # Give the main app 15 seconds to bind to a port
        
        # Check if anything is listening on the expected port
        if ! nc -z localhost ${PORT:-5000} 2>/dev/null; then
            echo "*** WARNING: No application bound to port within 15 seconds ***"
            echo "*** Starting minimal fallback application to maintain port binding ***"
            
            # Kill any existing gunicorn processes that might be stuck
            pkill -f gunicorn 2>/dev/null || true
            
            # Start the minimal app
            start_minimal_app
        else
            echo "Application successfully bound to port within timeout period"
        fi
    } &
    TIMER_PID=$!
    
    # Start the main application
    start_main_app
    
    # If we get here, the main application exited
    echo "Main application exited."
    
    # Kill the timer if it's still running
    kill $TIMER_PID 2>/dev/null || true
    
    # Check if anything is still listening on the port
    if ! nc -z localhost ${PORT:-5000} 2>/dev/null; then
        echo "No application is binding to port. Starting minimal app..."
        start_minimal_app
    else
        echo "Port is still bound. No action needed."
    fi
else
    # For non-web services, just run the normal start script
    if [ -f "./start.sh" ]; then
        exec ./start.sh
    else
        echo "Error: start.sh not found"
        exit 1
    fi
fi