#!/usr/bin/env bash
set -e

# run DB migrations
# Assuming flask-migrate is set up, otherwise adjust this command
# Make sure FLASK_APP is set correctly (e.g., in Dockerfile or Render env)
if [ -d "migrations" ]; then
    echo "Running database migrations..."
    flask db upgrade
else
    echo "Migrations directory not found, skipping migrations."
fi

# seed/refresh admin (uses ADMIN_EMAIL & ADMIN_PASSWORD env vars)
# Check if the command exists before running
if flask create-admin --help > /dev/null 2>&1; then
    echo "Creating/updating admin user..."
    flask create-admin --email "${ADMIN_EMAIL:-admin@example.com}" --password "${ADMIN_PASSWORD:-password}"
else
    echo "flask create-admin command not found, skipping admin creation."
    echo "Ensure the Flask CLI is correctly set up in src/cli.py and registered in src/__init__.py"
fi

# launch
echo "Starting Gunicorn..."
gunicorn "src:create_app()" \
  --bind 0.0.0.0:${PORT:-10000} \
  --workers ${WEB_CONCURRENCY:-4} \
  --timeout 120

