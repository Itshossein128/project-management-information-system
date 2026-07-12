#!/usr/bin/env bash
set -euo pipefail

CUSTOMER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/common.sh
source "${CUSTOMER_DIR}/scripts/common.sh"

customer_load_config
customer_check_docker
customer_ensure_env

if customer_is_stack_up; then
  echo "IPCAS is already running."
  customer_open_browser "${APP_URL}"
  exit 0
fi

echo "==> Starting IPCAS..."
customer_compose up -d --build

"${CUSTOMER_DIR}/scripts/wait-for-stack.sh" "${HEALTH_URL}" "${WAIT_MAX_ATTEMPTS}"

customer_open_browser "${APP_URL}"

echo "IPCAS is running at ${APP_URL}"
