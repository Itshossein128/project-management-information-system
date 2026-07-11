#!/usr/bin/env bash
set -euo pipefail

CUSTOMER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/common.sh
source "${CUSTOMER_DIR}/scripts/common.sh"

customer_load_config
customer_check_docker
customer_ensure_env

echo "==> Preparing IPCAS for demo (pull images + build). May take 10-20 minutes."
echo "    Run this once before the customer meeting with a stable internet connection."

customer_compose pull || echo "Warning: some image pulls failed; build will retry."

customer_compose build

cat <<EOF

IPCAS images are ready.
On demo day, run: bash customer/start.sh

EOF
