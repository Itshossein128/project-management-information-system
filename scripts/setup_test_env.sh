#!/usr/bin/env bash
# Bring up the isolated R.0.03 test stack, migrate/seed, and verify health.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.test-env.yml}"
ENV_FILE="${ENV_FILE:-.env.test-env}"

if [[ ! -f "${ENV_FILE}" ]]; then
  if [[ -f .env.test-env.example ]]; then
    echo "==> Creating ${ENV_FILE} from .env.test-env.example"
    cp .env.test-env.example "${ENV_FILE}"
  else
    echo "Missing ${ENV_FILE} and .env.test-env.example" >&2
    exit 1
  fi
fi

echo "==> Starting isolated test services (${COMPOSE_FILE})"
docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" up -d \
  postgres-test redis-test rabbitmq-test

SKIP_MINIO=false
if docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" up -d minio-test minio-test-init; then
  echo "==> Waiting for MinIO bucket init"
  docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" up --wait minio-test-init 2>/dev/null \
    || docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" run --rm minio-test-init \
    || echo "Warning: MinIO init did not complete"
else
  echo "Warning: MinIO image unavailable — continuing without object storage."
  echo "         Try: docker pull quay.io/minio/minio:latest && retag as minio/minio:latest"
  SKIP_MINIO=true
fi

# Load host-oriented env for local manage.py / verify against published ports.
set -a
# shellcheck disable=SC1090
source "${ENV_FILE}"
set +a

API_VENV="${ROOT_DIR}/apps/api/.venv/bin/python"
if [[ ! -x "${API_VENV}" ]]; then
  echo "Missing apps/api/.venv — create the API venv first." >&2
  exit 1
fi

echo "==> Waiting for Postgres on ${DATABASE_URL}"
for _ in $(seq 1 60); do
  if "${API_VENV}" - <<'PY'
import os, sys
import dj_database_url
import psycopg
cfg = dj_database_url.parse(os.environ["DATABASE_URL"])
# Ensure target DB exists (POSTGRES_DB should create it; recreate if volume reused).
admin = dict(cfg)
admin["NAME"] = "postgres"
try:
    conn = psycopg.connect(
        dbname=admin["NAME"], user=admin["USER"], password=admin["PASSWORD"],
        host=admin["HOST"], port=admin["PORT"], connect_timeout=2,
        autocommit=True,
    )
except Exception:
    sys.exit(1)
with conn.cursor() as cur:
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (cfg["NAME"],))
    if cur.fetchone() is None:
        cur.execute(f'CREATE DATABASE "{cfg["NAME"]}" OWNER "{cfg["USER"]}"')
conn.close()
conn = psycopg.connect(
    dbname=cfg["NAME"], user=cfg["USER"], password=cfg["PASSWORD"],
    host=cfg["HOST"], port=cfg["PORT"], connect_timeout=2,
)
conn.close()
PY
  then
    break
  fi
  sleep 1
done

echo "==> Migrating test database"
(
  cd "${ROOT_DIR}/apps/api/core"
  set -a
  # shellcheck disable=SC1090
  source "${ROOT_DIR}/${ENV_FILE}"
  set +a
  ../.venv/bin/python manage.py migrate --noinput
  ../.venv/bin/python manage.py verify_blueprint_schema
  ../.venv/bin/python manage.py seed_test_roles
)

echo "==> Optionally starting api-test container"
if [[ "${START_API_CONTAINER:-false}" == "true" ]]; then
  docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" up -d api-test
fi

echo "==> Running verify_test_env.py"
VERIFY_ARGS=(--env-file "${ENV_FILE}")
if [[ "${SKIP_MINIO}" == "true" ]]; then
  VERIFY_ARGS+=(--skip-minio)
fi
"${API_VENV}" "${ROOT_DIR}/scripts/verify_test_env.py" "${VERIFY_ARGS[@]}"

echo "Test environment ready."
echo "  Postgres : localhost:5434 / ipcas_test_env"
echo "  Redis    : localhost:6380"
echo "  RabbitMQ : amqp://localhost:5673/  (mgmt :15673)"
if [[ "${SKIP_MINIO}" == "true" ]]; then
  echo "  MinIO    : SKIPPED (image pull denied)"
else
  echo "  MinIO    : http://localhost:9001  (console :9002, bucket ipcas-test-files)"
fi
echo "  Accounts : password devpass123 — see permissions.test_accounts.TEST_ROLE_ACCOUNTS"
