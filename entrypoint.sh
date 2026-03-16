#!/bin/sh
set -e
cd /app/backend
python manage.py migrate --noinput
python manage.py seed_data 2>/dev/null || true
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 2
