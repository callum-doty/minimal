#!/bin/bash
# render-init-db.sh - Initialize database for Render deployment

set -e  # Exit immediately if a command exits with a non-zero status

echo "Starting database initialization for Render deployment..."

# Run migrations
echo "Running database migrations..."
FLASK_APP=src/wsgi.py python -m flask db upgrade

# Initialize taxonomy if needed
echo "Initializing keyword taxonomy..."
python -c "
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.catalog import create_app, db
from src.catalog.models import KeywordTaxonomy

app = create_app()
with app.app_context():
    # Check if we already have taxonomy terms
    existing_count = KeywordTaxonomy.query.count()
    if existing_count > 0:
        print(f'Found {existing_count} existing taxonomy terms. Skipping initialization.')
    else:
        print('No taxonomy terms found. Run scripts/initialize_taxonomy.py to set up the taxonomy.')
"

echo "Database initialization complete!"