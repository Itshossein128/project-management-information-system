#!/usr/bin/env bash
# Run against an already migrated/seeded isolated environment. No deploy occurs.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${R0_PYTHON:-${ROOT_DIR}/apps/api/.venv/bin/python}"
echo '==> Phase A: intentional failures must block the gate'
for scenario in workflow-failure api-failure web-failure missing-api cancelled; do
  "${PYTHON}" "${ROOT_DIR}/scripts/drill_gate_failure.py" --scenario "$scenario"
done
echo '==> Phase B: healthy checks must pass the gate'
"${PYTHON}" "${ROOT_DIR}/scripts/drill_gate_failure.py" --scenario success
echo '==> Phase C: live integration smoke (all checks required)'
"${PYTHON}" "${ROOT_DIR}/scripts/run_smoke_test.py" "$@"
echo 'PASS R.0 gate and integration smoke rehearsal'
