#!/usr/bin/env bash
# Host regression evidence; separate DB, inline test preparation/cache overrides.
set -euo pipefail
cd "$(dirname "$0")/../.."
set -a
source .env
set +a
export TEST_DATABASE_NAME="test_a7p5_regression_$(date +%s)_$$"
export AUDIT_LOG_ASYNC=false CELERY_TASK_ALWAYS_EAGER=true
export IMPORT_CGROUP_ROOT=/sys/fs/cgroup/system.slice/a7p5-containment.service
export A7P5_CGROUP_HOST_ROOT="$IMPORT_CGROUP_ROOT"
export IMPORT_SCRATCH_ROOT=/run/a7p5-host-regression
mkdir -p specs/055-a7-p5-import-operations/evidence/runtime
sudo --preserve-env=DATABASE_URL,TEST_DATABASE_NAME,AUDIT_LOG_ASYNC,CELERY_TASK_ALWAYS_EAGER,IMPORT_CGROUP_ROOT,A7P5_CGROUP_HOST_ROOT,IMPORT_SCRATCH_ROOT env PYTHONDONTWRITEBYTECODE=1 \
  apps/api/.venv/bin/python -m pytest -c apps/api/core/pytest.ini \
  apps/api/core/schedule/tests/test_a7_p5_*.py \
  apps/api/core/schedule/tests/test_a7_p2_import_safety.py \
  apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py \
  apps/api/core/schedule/tests/test_a7_p4_import_experience.py \
  apps/api/core/schedule/tests/test_msp_import.py \
  apps/api/core/schedule/tests/test_p6_import.py \
  apps/api/core/schedule/tests/test_mpp_import.py \
  apps/api/core/schedule/tests/test_mpp_equivalence.py \
  -q --tb=short -p no:cacheprovider \
  --junitxml=specs/055-a7-p5-import-operations/evidence/runtime/host-pytest.xml
