#!/bin/sh
set -e

ROLE="${ROLE:-web}"
PORT="${PORT:-8010}"
WORKERS="${WORKERS:-4}"
THREADS="${THREADS:-2}"
TIMEOUT="${TIMEOUT:-120}"

echo "▶️  Running as ROLE=$ROLE"

if [ "$ROLE" = "web" ]; then
  echo "▶️  Applying migrations..."
  python manage.py migrate --noinput

  if [ "${CREATE_SUPERUSER:-0}" = "1" ]; then
    echo "👤 Ensuring superuser..."
    python manage.py shell <<'PY'
from django.contrib.auth import get_user_model
from decouple import config
User = get_user_model()
email = config('DJANGO_SUPERUSER_EMAIL', default=None)
password = config('DJANGO_SUPERUSER_PASSWORD', default=None)
first_name = config('DJANGO_SUPERUSER_FIRST_NAME', default='Admin')
if email and password:
    if not User.objects.filter(email=email).exists():
        print(f"Creating superuser {email}...")
        u = User.objects.create_superuser(email=email, password=password, first_name=first_name)
        print("Superuser created.")
    else:
        print("Superuser exists; skipping.")
else:
    print("No superuser env provided; skipping.")
PY
  fi

  echo "📦 Collecting static files..."
  python manage.py collectstatic --noinput

  echo "🚀 Starting Gunicorn on :$PORT..."
  exec gunicorn core.wsgi:application \
      --bind 0.0.0.0:$PORT \
      --workers $WORKERS \
      --threads $THREADS \
      --timeout $TIMEOUT

elif [ "$ROLE" = "worker" ]; then
  echo "🚚 Starting Celery worker..."
  exec celery -A core worker -l info
else
  echo "❌ Unknown ROLE=$ROLE"; exit 1
fi
