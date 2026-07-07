#!/usr/bin/env bash
set -euo pipefail

CUSTOMER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/common.sh
source "${CUSTOMER_DIR}/scripts/common.sh"

customer_load_config
customer_check_docker
customer_check_git
customer_ensure_env

echo "==> Pulling latest code (${GIT_REMOTE}/${GIT_BRANCH})..."
(
  cd "$(customer_root_dir)"
  git fetch "${GIT_REMOTE}"
  git pull "${GIT_REMOTE}" "${GIT_BRANCH}"
)

echo "==> Rebuilding and restarting IPCAS..."
customer_compose up -d --build --remove-orphans

"${CUSTOMER_DIR}/scripts/wait-for-stack.sh" "${HEALTH_URL}" "${WAIT_MAX_ATTEMPTS}"

customer_open_browser "${APP_URL}"

echo "IPCAS updated and running at ${APP_URL}"
