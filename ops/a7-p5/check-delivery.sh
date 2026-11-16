#!/usr/bin/env bash
# Full A.7 regression on freshly migrated disposable test databases.
set -euo pipefail
cd "$(dirname "$0")/../.."
evidence="$PWD/specs/056-a7-p6-delivery-acceptance/evidence"
if [[ ${A7_DELIVERY_PART:-all} == all ]]; then
  A7_DELIVERY_PART=core "$0" > /tmp/a7-delivery-core.log 2>&1 & core_pid=$!
  A7_DELIVERY_PART=migrations "$0" > /tmp/a7-delivery-migrations.log 2>&1 & migrations_pid=$!
  core_status=0; migration_status=0
  wait "$core_pid" || core_status=$?
  wait "$migrations_pid" || migration_status=$?
  cat /tmp/a7-delivery-core.log /tmp/a7-delivery-migrations.log
  [[ $core_status == 0 && $migration_status == 0 ]] || exit 1
  python3 - "$evidence" <<'PY'
from pathlib import Path
import sys, xml.etree.ElementTree as ET
root=ET.Element('testsuites',name='A7 final regression')
for name in ['core','migrations']:
    report=ET.parse(Path(sys.argv[1])/f'final-{name}-part-junit.xml').getroot()
    root.extend(list(report))
ET.ElementTree(root).write(Path(sys.argv[1])/'final-core-junit.xml',encoding='utf-8',xml_declaration=True)
PY
  exit 0
fi
set -a
source .env
set +a
export TEST_DATABASE_NAME="test_a7_delivery_${A7_DELIVERY_PART}_$(date +%s)_$$"
export AUDIT_LOG_ASYNC=false CELERY_TASK_ALWAYS_EAGER=true
# Bound optional event publication when host RabbitMQ is absent.
export RABBITMQ_URL='amqp://127.0.0.1:1/?connection_attempts=1&socket_timeout=1'
export IMPORT_CGROUP_ROOT=/sys/fs/cgroup/system.slice/a7p5-containment.service
export A7P5_CGROUP_HOST_ROOT="$IMPORT_CGROUP_ROOT"
export IMPORT_SCRATCH_ROOT=/run/a7p5-delivery-regression
args=()
if [[ $A7_DELIVERY_PART == migrations ]]; then
  args=(apps/api/core/projects/tests/test_project_archive_restore_migrations.py apps/api/core/projects/tests/test_project_status_undo_migrations.py)
else
  args=(apps/api/core/projects/tests/test_a7_p1_reference_project.py
    apps/api/core/projects/tests/test_project_registration*.py
    apps/api/core/projects/tests/test_project_archive_restore*.py
    apps/api/core/projects/tests/test_project_status_undo*.py
    apps/api/core/projects/tests/test_project_activation_feedback.py
    apps/api/core/projects/tests/test_projects.py
    apps/api/core/projects/tests/test_central_data_owning_unit.py
    apps/api/core/projects/tests/test_core_principles_wbs*.py
    apps/api/core/wbs/tests apps/api/core/project_templates/tests
    apps/api/core/schedule/tests apps/api/core/common/tests/test_validators.py
    --ignore-glob='*/schedule/tests/test_a7_p5*'
    --ignore-glob='*/projects/tests/*_migrations.py')
fi
sudo --preserve-env=DATABASE_URL,TEST_DATABASE_NAME,AUDIT_LOG_ASYNC,CELERY_TASK_ALWAYS_EAGER,RABBITMQ_URL,IMPORT_CGROUP_ROOT,A7P5_CGROUP_HOST_ROOT,IMPORT_SCRATCH_ROOT env PYTHONDONTWRITEBYTECODE=1 \
  apps/api/.venv/bin/python -m pytest -c apps/api/core/pytest.ini "${args[@]}" \
  -q --tb=short -p no:cacheprovider \
  --junitxml="$evidence/final-${A7_DELIVERY_PART}-part-junit.xml"
