#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

ROOT_ENV="$(cd ../.. && pwd)/.env"
if [[ -f "$ROOT_ENV" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ROOT_ENV"
  set +a
fi

DATABASE_URL="${DATABASE_URL:-postgres://ipcas:ipcas@localhost:5433/ipcas}"

if [[ ! -x ./.venv/bin/python ]]; then
  exit 0
fi

./.venv/bin/python - "$DATABASE_URL" <<'PY'
import sys
import time

import dj_database_url
import psycopg

url = sys.argv[1]
cfg = dj_database_url.parse(url)
host = cfg.get("HOST") or "localhost"
port = int(cfg.get("PORT") or 5432)
user = cfg.get("USER") or "ipcas"
password = cfg.get("PASSWORD") or ""
dbname = cfg.get("NAME") or "ipcas"

deadline = time.monotonic() + 30
last_err = None
while time.monotonic() < deadline:
    try:
        with psycopg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname,
            connect_timeout=2,
        ):
            sys.exit(0)
    except psycopg.OperationalError as exc:
        last_err = exc
        time.sleep(1)

print(
    f"PostgreSQL is not reachable at {host}:{port} ({dbname}).\n"
    "Start it with: pnpm db:up\n"
    f"Last error: {last_err}",
    file=sys.stderr,
)
sys.exit(1)
PY
