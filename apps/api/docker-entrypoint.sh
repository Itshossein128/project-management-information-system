#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is required" >&2
  exit 1
fi

echo "Waiting for PostgreSQL..."
until python - <<'PY'
import os
import sys
import dj_database_url
import psycopg

url = os.environ["DATABASE_URL"]
cfg = dj_database_url.parse(url)
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

echo "Running migrations..."
python manage.py migrate --noinput

exec "$@"
