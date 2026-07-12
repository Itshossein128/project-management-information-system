#!/usr/bin/env bash
set -euo pipefail

CUSTOMER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/common.sh
source "${CUSTOMER_DIR}/scripts/common.sh"

customer_load_config
customer_check_docker

echo "==> Stopping IPCAS..."
customer_compose down

echo "IPCAS stopped. Your data is kept in Docker volumes."
echo "Run start.sh (or start.bat) to start again."
