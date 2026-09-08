#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
LOCK_FILE=${FAWS_DEMO_LOCK_FILE:-/tmp/faws-demo-reset.lock}
HEALTH_URL=${FAWS_HEALTH_URL:-http://127.0.0.1:5173/api/health/}
COMPOSE_FILES="-f compose.yml -f compose.homeserver.yml"

command -v docker >/dev/null 2>&1 || { echo "error: docker is required" >&2; exit 1; }
command -v flock >/dev/null 2>&1 || { echo "error: flock is required" >&2; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "error: curl is required" >&2; exit 1; }

exec 9>"$LOCK_FILE"
flock -n 9 || { echo "reset already running; exiting" >&2; exit 1; }

cd "$PROJECT_DIR"
echo "Checking demo services..."
for service in db backend frontend; do
    container_id=$(docker compose $COMPOSE_FILES ps --status running -q "$service")
    [ -n "$container_id" ] || { echo "error: $service is not running" >&2; exit 1; }
done

echo "Applying migrations..."
docker compose $COMPOSE_FILES exec -T backend python manage.py migrate --noinput

echo "Restoring fictional demo dataset..."
docker compose $COMPOSE_FILES exec -T backend python manage.py seed_demo --reset --seed 20260828

echo "Verifying health..."
attempt=1
while [ "$attempt" -le 12 ]; do
    if curl --fail --silent --show-error --max-time 5 "$HEALTH_URL" >/dev/null; then
        echo "Demo reset completed successfully."
        exit 0
    fi
    attempt=$((attempt + 1))
    sleep 5
done

echo "error: health check failed after reset: $HEALTH_URL" >&2
exit 1
