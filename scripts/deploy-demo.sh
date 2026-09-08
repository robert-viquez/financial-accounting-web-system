#!/usr/bin/env bash

set -Eeuo pipefail

readonly DEPLOY_DIR="/docker/faws-demo/financial-accounting-web-system"
readonly HEALTH_URL="http://127.0.0.1:5173/api/health/"
readonly HEALTH_ATTEMPTS=20
readonly HEALTH_DELAY_SECONDS=5

cd "$DEPLOY_DIR"

echo "Fetching origin/main..."
git fetch --prune origin main

remote_commit="$(git rev-parse origin/main)"
expected_commit="${EXPECTED_COMMIT:-$remote_commit}"

if [[ "$remote_commit" != "$expected_commit" ]]; then
  echo "Skipping superseded deployment: validated commit $expected_commit is no longer origin/main ($remote_commit)."
  exit 0
fi

echo "Updating deployment checkout to $expected_commit..."
git reset --hard "$expected_commit"

echo "Validating Docker Compose configuration..."
docker compose config --quiet

echo "Building and updating services..."
docker compose up --detach --build

echo "Applying database migrations..."
docker compose exec --no-TTY backend python manage.py migrate --noinput

echo "Waiting for $HEALTH_URL..."
for ((attempt = 1; attempt <= HEALTH_ATTEMPTS; attempt++)); do
  if curl --fail --silent --show-error --max-time 5 "$HEALTH_URL" >/dev/null; then
    echo "Health check passed on attempt $attempt."
    echo "Deployed commit: $(git rev-parse HEAD)"
    exit 0
  fi

  echo "Health check attempt $attempt/$HEALTH_ATTEMPTS failed."
  if (( attempt < HEALTH_ATTEMPTS )); then
    sleep "$HEALTH_DELAY_SECONDS"
  fi
done

echo "Deployment failed: health did not recover." >&2
docker compose ps || true
docker compose logs --tail 100 backend frontend || true
exit 1
