#!/bin/sh
set -eu

DATA_DIR="${FAWS_DATA_DIR:-/data}"
SECRET_FILE="${DJANGO_SECRET_KEY_FILE:-$DATA_DIR/.django_secret_key}"

mkdir -p "$DATA_DIR/media"
chown -R appuser:appuser "$DATA_DIR"

if [ -z "${DJANGO_SECRET_KEY:-}" ]; then
    if [ ! -s "$SECRET_FILE" ]; then
        umask 077
        python -c 'import secrets,sys; open(sys.argv[1], "w").write(secrets.token_urlsafe(64))' "$SECRET_FILE"
        chown appuser:appuser "$SECRET_FILE"
    fi
    DJANGO_SECRET_KEY="$(cat "$SECRET_FILE")"
    export DJANGO_SECRET_KEY
fi

if [ "${DATABASE_ENGINE:-sqlite}" = "sqlite" ]; then
    export SQLITE_PATH="${SQLITE_PATH:-$DATA_DIR/faws.sqlite3}"
fi

runuser -u appuser -- python manage.py migrate --noinput

nginx

workers="${WEB_CONCURRENCY:-1}"
threads="${GUNICORN_THREADS:-4}"
exec gunicorn config.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers "$workers" \
    --threads "$threads" \
    --timeout "${GUNICORN_TIMEOUT:-60}" \
    --access-logfile - \
    --error-logfile - \
    --user appuser \
    --group appuser
