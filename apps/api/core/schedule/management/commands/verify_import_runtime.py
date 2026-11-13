"""Preflight and acceptance matrix for the isolated import runtime.

Refuses shared databases. Eager or mocked execution is reported as not-run,
never as a passing worker result.
"""

from __future__ import annotations

import json
import time
import os
import hashlib
import importlib.metadata
import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.utils import timezone
from rest_framework.test import APIClient

from projects.models import ProjectStatus
from projects.services import create_project_with_creator
from schedule.models import MspImportJob
from schedule.services.import_process import cgroup_ready, scratch_root

_SAMPLE_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<Project xmlns="http://schemas.microsoft.com/project">
  <Tasks>
    <Task>
      <UID>1</UID><Name>Phase</Name><OutlineLevel>1</OutlineLevel>
      <OutlineNumber>1</OutlineNumber><WBS>1</WBS><Summary>1</Summary>
    </Task>
    <Task>
      <UID>2</UID><Name>Work</Name><OutlineLevel>2</OutlineLevel>
      <OutlineNumber>1.1</OutlineNumber><WBS>1.1</WBS><Summary>0</Summary>
      <Duration>PT8H0M0S</Duration>
    </Task>
  </Tasks>
</Project>
"""

_MATRIX_GROUPS = (
    'valid_native',
    'unreadable',
    'admitted_failure',
    'timeout',
    'resource_limit',
    'duplicate_delivery',
    'worker_loss',
    'cleanup',
    'expiry',
    'request_intent',
    'maintenance_budget',
    'scratch_quarantine',
    'healthy_follow_up',
)


def claims_real_worker_success(report: dict) -> bool:
    matrix = report.get('matrix') or {}
    return report.get('eager') is True and any(value == 'pass' for value in matrix.values())


class Command(BaseCommand):
    help = 'Check or record the isolated A.7-P5 import runtime. This does not target shared services.'

    def add_arguments(self, parser):
        parser.add_argument('--preflight', action='store_true')
        parser.add_argument('--run-matrix', action='store_true')
        parser.add_argument('--project-prefix', default='A7P5-')
        parser.add_argument('--reference', default='')
        parser.add_argument('--output', default='')

    def handle(self, *args, **options):
        report = self._preflight(options['project_prefix'])
        if options['run_matrix']:
            report['matrix'] = self._matrix(report, options['project_prefix'], options['reference'])
            report['scenario_evidence'] = getattr(self, '_scenario_evidence', {})
            if any(report['matrix'].get(group) != 'pass' or report['scenario_evidence'].get(group, {}).get('status') != 'pass' for group in _MATRIX_GROUPS):
                report['status'] = 'incomplete'
            if claims_real_worker_success(report):
                report['status'] = 'invalid_evidence'
        report['versions'] = {name: importlib.metadata.version(name) for name in ['Django', 'celery', 'mpxj', 'JPype1', 'redis']}
        report['python'] = sys.version.split()[0]
        report['java'] = subprocess.run(['java', '-version'], capture_output=True, text=True).stderr.splitlines()[0]
        report['source_tree_sha256'] = hashlib.sha256(b''.join(p.read_bytes() for p in sorted((Path(settings.BASE_DIR)/'schedule').rglob('*.py')))).hexdigest()
        if options['output']:
            target = Path(options['output'])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(report, indent=2), encoding='utf-8')
        self.stdout.write(json.dumps({'status': report['status'], 'not_run': report['not_run']}))
        if report['status'] != 'ready':
            raise CommandError('import runtime preflight blocked')

    def _preflight(self, prefix: str) -> dict:
        database = str(connection.settings_dict.get('NAME', ''))
        broker = str(settings.CELERY_BROKER_URL)
        problems = []
        not_run = []
        if 'a7p5' not in database:
            problems.append('database name must contain a7p5')
        if not prefix.startswith('A7P5'):
            problems.append('project prefix must stay in the A7P5 namespace')
        if settings.CELERY_TASK_ALWAYS_EAGER:
            problems.append('eager mode cannot prove a worker')
            not_run.append('real_worker')
        from urllib.parse import urlparse
        target = urlparse(broker)
        phase_broker = (target.hostname == 'redis' and target.port == 6379 and os.environ.get('A7_P5_ISOLATED') == '1') or (target.hostname in {'127.0.0.1', 'localhost'} and target.port == 56379)
        if not phase_broker:
            problems.append('broker must be the explicitly isolated Redis endpoint')
        if settings.IMPORT_PREPARE_INLINE:
            problems.append('inline preparation cannot prove containment')
        if not cgroup_ready():
            not_run.append('cgroup_containment')
            if settings.IMPORT_CONTAINMENT_REQUIRED:
                problems.append('delegated cgroup is required and unavailable')
        try:
            root = scratch_root()
        except OSError:
            problems.append('scratch root is unavailable')
            root = None
        else:
            if root.is_symlink():
                problems.append('scratch root must not be a symlink')
        if settings.IMPORT_EXECUTION_QUEUE == settings.IMPORT_MAINTENANCE_QUEUE:
            not_run.append('separate_maintenance_queue')
        if not problems:
            from config.celery import app
            inspector = app.control.inspect(timeout=3)
            pong = inspector.ping() or {}
            if len(pong) < 2:
                problems.append('independent import and maintenance workers must answer')
            queues = inspector.active_queues() or {}
            consumers = {name: {queue['name'] for queue in values} for name, values in queues.items()}
            if not any(settings.IMPORT_EXECUTION_QUEUE in values for values in consumers.values()) or not any(settings.IMPORT_MAINTENANCE_QUEUE in values for values in consumers.values()):
                problems.append('both dedicated queues must have actual consumers')
            if cgroup_ready():
                from schedule.services.import_process import _arm_cgroup, _finish_cgroup
                import uuid
                probe = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(10)'], start_new_session=True)
                group = None
                try:
                    group = _arm_cgroup(uuid.uuid4(), probe.pid)
                    _finish_cgroup(group, probe)
                except Exception as exc:
                    problems.append('actual helper delegation probe failed: '+type(exc).__name__)
                finally:
                    if probe.poll() is None:
                        probe.kill(); probe.wait()
            if root and os.statvfs(root).f_blocks * os.statvfs(root).f_frsize > int(settings.IMPORT_SCRATCH_QUOTA_BYTES):
                problems.append('scratch filesystem exceeds configured bound')
        report = {
            'status': 'ready' if not problems else 'blocked',
            'database': database,
            'eager': bool(settings.CELERY_TASK_ALWAYS_EAGER),
            'containment': 'cgroup' if cgroup_ready() else 'unavailable',
            'problems': problems,
            'not_run': not_run,
            'profile': settings.IMPORT_PROFILE_ID,
            'effective_limits': {
                name: getattr(settings, name) for name in dir(settings)
                if name.startswith('IMPORT_') and isinstance(getattr(settings, name), (int, float, bool))
            },
            'conversion_timeout_seconds': settings.MPP_CONVERT_TIMEOUT_SECONDS,
            'conversion_routes': ['JPype', 'configured MPXJ Java CLI'],
            'queues': [settings.IMPORT_EXECUTION_QUEUE, settings.IMPORT_MAINTENANCE_QUEUE],
        }
        if problems and not settings.IMPORT_CONTAINMENT_REQUIRED and 'a7p5' not in database:
            raise CommandError('refusing to inspect a shared database')
        return report

    def _matrix(self, preflight: dict, prefix: str, reference: str) -> dict:
        matrix = {group: 'not-run' for group in _MATRIX_GROUPS}
        database = str(preflight.get('database', ''))
        if preflight.get('status') != 'ready' or 'a7p5' not in database or preflight.get('eager'):
            matrix['reason'] = 'phase database and a non-eager worker are required'
            return matrix
        return self._attempt_isolated_matrix(matrix, prefix, reference)

    def _attempt_isolated_matrix(self, matrix: dict, prefix: str, reference: str) -> dict:
        from schedule.tests.a7_p5_runtime_matrix import RuntimeMatrix
        if not cgroup_ready():
            return matrix
        from schedule.services.import_operations import run_maintenance
        recovery = run_maintenance('recovery')
        if recovery['status'] != 'ok':
            return matrix
        self._scenario_evidence = RuntimeMatrix(prefix, reference).run()
        for group, result in self._scenario_evidence.items():
            matrix[group] = result['status']
        return matrix
