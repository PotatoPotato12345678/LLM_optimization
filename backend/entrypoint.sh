#!/usr/bin/env bash
set -e

# Wait for the database to be ready
python wait_for_db.py

# Run migrations (safe to run every start)
python manage.py migrate --noinput || true

# Start the Django development server
exec python manage.py runserver 0.0.0.0:8000
