#!/bin/sh
# Startup for the web service in docker-compose.yaml: migrate, collect static, serve.
set -e

python manage.py migrate

python manage.py collectstatic --noinput
exec gunicorn website.wsgi:application --bind 0.0.0.0:8000 --workers 3
