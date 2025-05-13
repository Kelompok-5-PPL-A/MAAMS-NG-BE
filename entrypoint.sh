#!/bin/bash

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn server on port $PORT..."
exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 --access-logfile - --error-logfile - MAAMS_NG_BE.wsgi:application