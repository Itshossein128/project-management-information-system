#!/usr/bin/env bash
set -euo pipefail

CUSTOMER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/common.sh
source "${CUSTOMER_DIR}/scripts/common.sh"

customer_load_config
customer_check_docker
customer_ensure_env

config_example="${CUSTOMER_DIR}/ipcas.config.example"
config_file="${CUSTOMER_DIR}/ipcas.config"
if [[ ! -f "${config_file}" && -f "${config_example}" ]]; then
  cp "${config_example}" "${config_file}"
  echo "Created customer/ipcas.config from example."
fi

echo "==> Building and starting IPCAS (first run may take several minutes)..."
customer_compose up -d --build

"${CUSTOMER_DIR}/scripts/wait-for-stack.sh" "${HEALTH_URL}" "${WAIT_MAX_ATTEMPTS}"

customer_open_browser "${APP_URL}"

cat <<EOF

IPCAS is installed and running.

Open in browser: ${APP_URL}
Demo login: +10000000001 / devpass123

To stop:   ${CUSTOMER_DIR}/stop.sh  (or stop.bat on Windows)
To update: ${CUSTOMER_DIR}/update.sh (or update.bat on Windows)

EOF
