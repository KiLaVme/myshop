#!/bin/sh
# entrypoint.sh - виконується при старті контейнера web/app
# 1) чекає доступності PostgreSQL
# 2) генерує та застосовує міграції
# 3) збирає статичні файли
# 4) створює суперкористувача, якщо задані змінні оточення (опційно)
# 5) запускає команду, передану в CMD (gunicorn / runserver / pytest тощо)

set -e

echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
while ! python -c "
import socket, os, sys
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((os.environ.get('DB_HOST', 'db'), int(os.environ.get('DB_PORT', 5432))))
except OSError:
    sys.exit(1)
"; do
  sleep 1
done
echo "PostgreSQL is up."

echo "Generating missing migrations (if any)..."
# У навчальному проєкті міграції генеруються автоматично при старті,
# щоб не тримати в репозиторії десятки згенерованих файлів.
python manage.py makemigrations --noinput

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ] && [ "$DJANGO_SUPERUSER_EMAIL" ]; then
  echo "Ensuring superuser exists..."
  python manage.py createsuperuser --noinput || true
fi

exec "$@"
