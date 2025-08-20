#!/bin/sh

echo "=== Starting Django Application ==="

# Créer le dossier cache s'il n'existe pas
mkdir -p /app/cache
chmod 777 /app/cache

echo "Checking for missing migrations..."
python manage.py makemigrations --check --dry-run

if [ $? -ne 0 ]; then
    echo "Generating new migrations..."
    python manage.py makemigrations --noinput
fi

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000