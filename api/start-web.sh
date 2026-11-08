#!/bin/sh
# Startup for the web service in docker-compose.yaml: migrate, reindex, collect static, serve.
set -e

python manage.py migrate

# algolia_reindex ignores AUTO_INDEXING, so skip it here when indexing is off
# (ALGOLIA_AUTO_INDEXING=false, parsed the same way as in website/settings.py).
if [ "$(printf %s "${ALGOLIA_AUTO_INDEXING:-true}" | tr '[:upper:]' '[:lower:]')" = "false" ]; then
	echo "Skipping algolia_reindex: ALGOLIA_AUTO_INDEXING=false"
else
	python manage.py algolia_reindex
fi

python manage.py collectstatic --noinput
exec gunicorn website.wsgi:application --bind 0.0.0.0:8000 --workers 3
