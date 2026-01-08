#!/usr/bin/env bash
set -e

cd /app

echo "Running migrations..."
alembic upgrade head

echo "Starting app..."
exec python -m app.main
