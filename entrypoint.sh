#!/bin/bash

# Wait for MySQL to be ready
echo "Waiting for MySQL at ${DB_HOST}:${DB_PORT}..."
while ! nc -z ${DB_HOST} ${DB_PORT}; do
    sleep 1
done
echo "MySQL is ready!"

# Apply migrations
echo "Applying migrations..."
python manage.py migrate

# Create superuser if DJANGO_SUPERUSER_USERNAME is set
if [ -n "${DJANGO_SUPERUSER_USERNAME}" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
fi

# Start the application
echo "Starting application..."
python manage.py runserver 0.0.0.0:8000 