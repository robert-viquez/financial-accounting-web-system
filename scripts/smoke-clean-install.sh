#!/usr/bin/env bash
set -Eeuo pipefail

readonly IMAGE="${IMAGE:-faws:smoke}"
readonly CONTAINER="${FAWS_TEST_CONTAINER:-faws-test-${GITHUB_RUN_ID:-local}}"
readonly VOLUME="${FAWS_TEST_VOLUME:-faws-test-data-${GITHUB_RUN_ID:-local}}"
readonly PORT="${FAWS_TEST_PORT:-18080}"
readonly BASE_URL="http://127.0.0.1:${PORT}"
readonly ADMIN_USERNAME="ci-first-admin"
readonly ADMIN_EMAIL="ci-admin@example.invalid"
readonly ADMIN_PASSWORD="Faws-${RANDOM}-$(date +%s)-Aa!"

cleanup() {
  docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
  docker volume rm "$VOLUME" >/dev/null 2>&1 || true
}
trap cleanup EXIT
cleanup

docker run -d --name "$CONTAINER" -p "${PORT}:80" -v "${VOLUME}:/data" "$IMAGE" >/dev/null

for attempt in {1..40}; do
  health="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{end}}' "$CONTAINER")"
  if [[ "$health" == "healthy" ]] && curl --fail --silent --max-time 5 "$BASE_URL/api/health/" >/dev/null; then break; fi
  if [[ "$attempt" == 40 ]]; then docker logs "$CONTAINER"; exit 1; fi
  sleep 3
done

curl --fail --silent "$BASE_URL/" | grep -q '<div id="app"></div>'
curl --fail --silent "$BASE_URL/setup" | grep -q '<div id="app"></div>'
curl --fail --silent "$BASE_URL/api/health/" | grep -Eq '"status"[[:space:]]*:[[:space:]]*"ok"'
curl --fail --silent "$BASE_URL/api/setup/status/" | grep -Eq '"setup_required"[[:space:]]*:[[:space:]]*true'
docker exec "$CONTAINER" runuser -u appuser -- python manage.py shell -c \
  'from django.contrib.auth.models import User; from compras.models import Compra; from inventario.models import Producto; from terceros.models import Cliente, Proveedor; from usuarios.models import ConfiguracionEmpresa; from ventas.models import Venta; assert not User.objects.exists(); assert not Producto.objects.exists(); assert not Proveedor.objects.exists(); assert not Venta.objects.exists(); assert not Compra.objects.exists(); assert not ConfiguracionEmpresa.objects.exists(); assert list(Cliente.objects.values_list("nombre", flat=True)) == ["Estimado Cliente"]'

curl --fail --silent --json "{\"username\":\"$ADMIN_USERNAME\",\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\",\"password_confirm\":\"$ADMIN_PASSWORD\"}" "$BASE_URL/api/setup/admin/" >/dev/null
second_status="$(curl --silent --output /dev/null --write-out '%{http_code}' --json "{\"username\":\"other-admin\",\"password\":\"$ADMIN_PASSWORD\",\"password_confirm\":\"$ADMIN_PASSWORD\"}" "$BASE_URL/api/setup/admin/")"
[[ "$second_status" == "403" ]]
curl --fail --silent --json "{\"username\":\"$ADMIN_USERNAME\",\"password\":\"$ADMIN_PASSWORD\"}" "$BASE_URL/api/token/" | grep -q '"access"'

secret_before="$(docker exec "$CONTAINER" sha256sum /data/.django_secret_key | awk '{print $1}')"
docker restart "$CONTAINER" >/dev/null
for attempt in {1..40}; do
  if curl --fail --silent --max-time 5 "$BASE_URL/api/health/" >/dev/null; then break; fi
  if [[ "$attempt" == 40 ]]; then docker logs "$CONTAINER"; exit 1; fi
  sleep 3
done
curl --fail --silent "$BASE_URL/api/setup/status/" | grep -Eq '"setup_required"[[:space:]]*:[[:space:]]*false'
curl --fail --silent --json "{\"username\":\"$ADMIN_USERNAME\",\"password\":\"$ADMIN_PASSWORD\"}" "$BASE_URL/api/token/" | grep -q '"access"'
secret_after="$(docker exec "$CONTAINER" sha256sum /data/.django_secret_key | awk '{print $1}')"
[[ "$secret_before" == "$secret_after" ]]

echo "Standalone image clean-install and restart persistence test passed."
