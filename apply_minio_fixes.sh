#!/bin/bash
# Script to apply MinIO connection fixes and update the Render deployment

set -e  # Exit on any error

echo "===== Applying MinIO Connection Fixes ====="

# Make the fix script executable
chmod +x fix_minio_connection.py

# Run the fix script
echo "Running fix_minio_connection.py..."
python fix_minio_connection.py

# Check if git is available and if this is a git repository
if command -v git &> /dev/null && git rev-parse --is-inside-work-tree &> /dev/null; then
    echo "Git repository detected, committing changes..."
    git add src/catalog/services/storage_service.py src/wsgi.py render.yaml
    git commit -m "Fix MinIO connection issues by improving error handling and fallback to mock storage"
    
    echo "Changes committed. You can now push these changes to your repository."
    echo "Run: git push origin <your-branch>"
else
    echo "Not a git repository or git not available. Changes have been applied locally."
    echo "Please commit and push these changes to your repository manually."
fi

echo ""
echo "===== Next Steps ====="
echo "1. Push the changes to your repository"
echo "2. Redeploy your application on Render"
echo "3. Verify that the application is using mock storage correctly"
echo ""
echo "Note: The USE_MOCK_STORAGE environment variable has been set to 'true' for all services"
echo "in render.yaml. This will ensure that your application uses mock storage instead of"
echo "trying to connect to MinIO, which was causing the connection timeout errors."
