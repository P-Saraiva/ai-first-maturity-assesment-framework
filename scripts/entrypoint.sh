#!/usr/bin/env sh
set -e

# Initialize database schema
python scripts/setup_database.py

# Start Gunicorn with JSON-form entrypoint for proper signal handling
exec gunicorn 'app:application' \
  --bind 0.0.0.0:5001 \
  --workers "${WORKERS:-2}" \
  --threads "${THREADS:-2}" \
  --timeout "${TIMEOUT:-120}" \
  --graceful-timeout "${GRACEFUL_TIMEOUT:-30}" \
  --log-level "${LOG_LEVEL:-info}"