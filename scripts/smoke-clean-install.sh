#!/usr/bin/env bash

set -Eeuo pipefail

readonly PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
readonly COMPOSE=(docker compose -f compose.yml)
readonly BASE_URL="http://127.0.0.1:${FRONTEND_PORT:-5173}"
readonly ADMIN_USERNAME="ci-first-admin"
readonly ADMIN_EMAIL="ci-admin@example.invalid"
readonly ADMIN_PASSWORD="Faws-${RANDOM}-$(date +%s)-Aa!"

export COMPOSE_PROJECT_NAME="faws-clean-install-${GITHUB_RUN_ID:-local}"
export DJANGO_DEBUG=false
export DJANGO_SECRET_KEY="ci-only-not-for-production-${RANDOM}-${RANDOM}-${RANDOM}"
export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1,backend"
export DJANGO_SECURE_SSL_REDIRECT=false
export DJANGO_SECURE_HSTS_SECONDS=0
export DJANGO_TRUST_X_FORWARDED_PROTO=true
export CORS_ALLOWED_ORIGINS="http://localhost:${FRONTEND_PORT:-5173}"
export CSRF_TRUSTED_ORIGINS=""
export MYSQL_DATABASE=faws_smoke
export MYSQL_USER=faws_smoke
export MYSQL_PASSWORD="ci-db-${RANDOM}-${RANDOM}"
export MYSQL_ROOT_PASSWORD="ci-root-${RANDOM}-${RANDOM}"
export VITE_API_URL=/api/
export VITE_DEMO_MODE=false
export VITE_DEMO_USERNAME=""
export VITE_DEMO_PASSWORD=""
export ALLOW_DEMO_SEED=false
export DEMO_USERNAME=""
export DEMO_PASSWORD=""

cd "$PROJECT_DIR"

cleanup() {
  "${COMPOSE[@]}" down -v --remove-orphans
}
trap cleanup EXIT

"${COMPOSE[@]}" config --quiet
"${COMPOSE[@]}" down -v --remove-orphans
"${COMPOSE[@]}" up -d --build

for attempt in {1..40}; do
  if curl --fail --silent --max-time 5 "$BASE_URL/api/health/" >/dev/null; then
    break
  fi
  if [[ "$attempt" == 40 ]]; then
    "${COMPOSE[@]}" ps
    "${COMPOSE[@]}" logs --tail 150 db backend frontend
    exit 1
  fi
  sleep 3
done

curl --fail --silent --max-time 5 "$BASE_URL/" >/dev/null
curl --fail --silent "$BASE_URL/api/health/" | grep -Eq '"status"[[:space:]]*:[[:space:]]*"ok"'
curl --fail --silent "$BASE_URL/api/setup/status/" | grep -Eq '"setup_required"[[:space:]]*:[[:space:]]*true'

"${COMPOSE[@]}" exec -T backend python manage.py shell -c \
  'from django.contrib.auth.models import User; from inventario.models import Producto; from terceros.models import Cliente, Proveedor; assert not User.objects.exists(); assert not Producto.objects.exists(); assert not Cliente.objects.exists(); assert not Proveedor.objects.exists()'

curl --fail --silent --json "{\"username\":\"$ADMIN_USERNAME\",\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\",\"password_confirm\":\"$ADMIN_PASSWORD\"}" \
  "$BASE_URL/api/setup/admin/" >/dev/null
curl --fail --silent "$BASE_URL/api/setup/status/" | grep -Eq '"setup_required"[[:space:]]*:[[:space:]]*false'
curl --fail --silent --json "{\"username\":\"$ADMIN_USERNAME\",\"password\":\"$ADMIN_PASSWORD\"}" \
  "$BASE_URL/api/token/" | grep -q '"access"'

echo "Clean-install smoke test passed."
