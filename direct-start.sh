#!/bin/bash
# direct-start.sh - Execute direct.py with proper binding

set -e  # Exit immediately if any command fails

# Print diagnostic information
echo "=== DIRECT BINDING SCRIPT ==="
echo "Current directory: $(pwd)"
echo "Files in directory: $(ls -la)"
echo "PORT: ${PORT:-5000}"

# Ensure the port is correctly exported
export PORT=${PORT:-5000}

# Print binding message for logs
echo "*** BINDING DIRECTLY TO 0.0.0.0:${PORT} ***"

# Execute the direct binding script
exec python direct.py