#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Load monorepo root .env
ROOT_ENV="$(cd ../.. && pwd)/.env"
if [[ -f "$ROOT_ENV" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ROOT_ENV"
  set +a
fi

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is not set. Copy .env.example to .env in the monorepo root." >&2
  exit 1
fi

if [[ ! -x ./.venv/bin/python ]]; then
  echo "Create venv first: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi

exec ./.venv/bin/python core/manage.py "$@"
