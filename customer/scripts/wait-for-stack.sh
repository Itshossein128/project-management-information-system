#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"

customer_load_config

url="${1:-${HEALTH_URL}}"
max_attempts="${2:-${WAIT_MAX_ATTEMPTS}}"
interval="${WAIT_INTERVAL_SEC}"

for ((attempt = 1; attempt <= max_attempts; attempt++)); do
  if curl -sf "${url}" >/dev/null 2>&1; then
    echo "Verona is ready."
    exit 0
  fi

  echo "Waiting for Verona... (${attempt}/${max_attempts})"
  sleep "${interval}"
done

echo "Timed out waiting for Verona at ${url}" >&2
echo "Run: bash customer/scripts/compose.sh logs" >&2
exit 1
