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
if [ -n "${DJANGO_SUPERUSER_USERNAME}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD}" ]; then
    echo "Creating superuser..."
    python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists():
    User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME}', 
                                '${DJANGO_SUPERUSER_EMAIL}', 
                                '${DJANGO_SUPERUSER_PASSWORD}')
    print('Superuser created.')
else:
    print('Superuser already exists.')
END
fi

# Start the application
echo "Starting application..."
python manage.py runserver 0.0.0.0:8000 