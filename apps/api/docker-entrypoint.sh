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

echo "Running migrations..."
python manage.py migrate --noinput

if [[ -n "${RABBITMQ_URL:-}" ]]; then
  python manage.py setup_event_topology || echo "Warning: RabbitMQ topology setup failed"
fi

exec "$@"
