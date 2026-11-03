#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is required" >&2
  exit 1
fi

echo "Waiting for PostgreSQL..."
until python - <<'PY'
import os
import dj_database_url
import psycopg

cfg = dj_database_url.parse(os.environ["DATABASE_URL"])
conn = psycopg.connect(
    dbname=cfg["NAME"],
    user=cfg["USER"],
    password=cfg["PASSWORD"],
    host=cfg["HOST"],
    port=cfg["PORT"],
)
conn.close()
PY
do
  echo "Postgres is unavailable - sleeping"
  sleep 2
done

if [[ -n "${RABBITMQ_URL:-}" ]]; then
  echo "Waiting for RabbitMQ..."
  until python - <<'PY'
import os
import pika

pika.BlockingConnection(pika.URLParameters(os.environ["RABBITMQ_URL"])).close()
PY
  do
    echo "RabbitMQ is unavailable - sleeping"
    sleep 2
  done
fi

if [[ "${SKIP_MIGRATIONS:-}" != "true" ]]; then
  echo "Running migrations..."
  python manage.py migrate --noinput --fake-initial

  if [[ -n "${RABBITMQ_URL:-}" ]]; then
    python manage.py setup_event_topology || echo "Warning: RabbitMQ topology setup failed"
  fi

  if [[ "${SEED_DEMO_DATA:-}" == "true" ]]; then
    echo "Seeding demo data..."
    python manage.py seed_rbac_dev || echo "Warning: demo seed failed"
  fi

  if [[ "${SEED_TEST_ROLES:-}" == "true" ]]; then
    echo "Seeding test role accounts (R.0.03)..."
    # When demo was already seeded above, skip re-running full demo inside seed_test_roles.
    if [[ "${SEED_DEMO_DATA:-}" == "true" ]]; then
      python manage.py seed_test_roles --skip-demo || echo "Warning: test role seed failed"
    else
      python manage.py seed_test_roles || echo "Warning: test role seed failed"
    fi
  fi
fi

exec "$@"
