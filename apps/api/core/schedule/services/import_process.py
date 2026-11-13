"""Contained preparation of untrusted schedule uploads.

The helper process is the only place that starts a JVM. Callers pass bytes and
receive a validated prepared plan. Filenames from the upload are metadata and
are never used as path components.
"""

from __future__ import annotations

import json
import logging
import selectors
import time
import os
import signal
import socket
import subprocess
import sys
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.db import transaction, connection
from django.utils import timezone
from django.utils.dateparse import parse_date

from schedule.models import ImportProcessingSlot
from schedule.services.mpp_errors import (
    CONVERSION_FAILED,
    MPP_CORRUPT,
    PROCESSING_RESOURCE_LIMIT,
    PROCESSING_TIMEOUT,
    PUBLIC_MESSAGES,
    MppImportError,
)

logger = logging.getLogger(__name__)
SCRATCH_UNFINISHED_KEY = 'a7p5-scratch-unfinished'

PROTOCOL_VERSION = 1
ALLOWED_NAMES = frozenset({
    'manifest.json', 'input.bin', 'prepared.json', 'output.xml', 'diagnostics.txt', 'release',
})
_RELATION_TYPES = frozenset({'FS', 'SS', 'FF', 'SF'})
_TASK_STRINGS = {
    'uid': 128,
    'outline_number': 128,
    'wbs_code': 128,
    'name': 4000,
    'node_key': 256,
}
_OPTIONAL_STRINGS = {'parent_key': 256}


class ProcessingBusy(Exception):
    """Preparation capacity is held by other work. No business job should be created."""


def reboot_id() -> str:
    path = Path('/proc/sys/kernel/random/boot_id')
    try:
        return path.read_text(encoding='utf-8').strip() or 'unknown'
    except OSError:
        return 'unknown'


def hostname() -> str:
    return os.environ.get('IMPORT_RUNTIME_HOST_ID', socket.gethostname())[:255]


def scratch_root() -> Path:
    root = Path(settings.IMPORT_SCRATCH_ROOT)
    root.mkdir(parents=True, mode=0o700, exist_ok=True)
    if root.is_symlink():
        raise MppImportError(CONVERSION_FAILED, PUBLIC_MESSAGES[CONVERSION_FAILED])
    os.chmod(root, 0o700)
    return root


def cgroup_ready() -> bool:
    root = Path(settings.IMPORT_CGROUP_ROOT) if settings.IMPORT_CGROUP_ROOT else None
    if root is None or not root.is_dir() or root.is_symlink():
        return False
    controllers = root / 'cgroup.controllers'
    if not controllers.is_file():
        return False
    try:
        have = set(controllers.read_text(encoding='utf-8').split())
    except OSError:
        return False
    if not {'memory', 'pids', 'cpu'} <= have:
        return False
    return os.access(root, os.W_OK)


def _public(code: str) -> MppImportError:
    return MppImportError(code, PUBLIC_MESSAGES.get(code, PUBLIC_MESSAGES[CONVERSION_FAILED]))


def _containment_clear(slot: ImportProcessingSlot) -> bool:
    identity = slot.containment_id or ''
    if not identity:
        return True
    if identity.startswith('pgroup:'):
        parts = identity.split(':')
        if len(parts) != 3:
            return False
        _, boot, pid_text = parts
        if boot != reboot_id():
            return True
        return not Path(f'/proc/{pid_text}').exists()
    if identity.startswith('cgroup:'):
        path = Path(identity.split(':', 1)[1])
        if path.is_symlink():
            return False
        procs = path / 'cgroup.procs'
        root = Path(settings.IMPORT_CGROUP_ROOT)
        if path.parent != root or not path.name.startswith('import-'):
            return False
        if not path.exists():
            return True
        if not procs.is_file() or procs.is_symlink():
            return False
        try:
            return procs.read_text(encoding='utf-8').strip() == ''
        except OSError:
            return False
    return False


def acquire_slot(*, family: str, subject_id: uuid.UUID, deadline):
    now = timezone.now()
    with transaction.atomic():
        slot = (
            ImportProcessingSlot.objects.select_for_update()
            .order_by('slot_number')
            .first()
        )
        if slot is None or slot.quarantined:
            raise _public(CONVERSION_FAILED)
        if slot.execution_token:
            if slot.deadline and slot.deadline > now:
                raise ProcessingBusy()
            if not _containment_clear(slot):
                slot.quarantined = True
                slot.save(update_fields=['quarantined'])
                raise _public(CONVERSION_FAILED)
        token = uuid.uuid4()
        slot.execution_token = token
        slot.family = family[:16]
        slot.subject_id = subject_id
        slot.owner_host = hostname()
        slot.reboot_id = reboot_id()[:64]
        slot.deadline = deadline
        slot.containment_id = ''
        slot.quarantined = False
        slot.save()
        return token


def release_slot(token: uuid.UUID) -> None:
    ImportProcessingSlot.objects.filter(execution_token=token, quarantined=False).update(
        execution_token=None,
        family='',
        subject_id=None,
        owner_host='',
        reboot_id='',
        deadline=None,
        containment_id='',
    )


def quarantine_slot(token: uuid.UUID) -> None:
    ImportProcessingSlot.objects.filter(execution_token=token).update(quarantined=True)


def _check_string(value, limit: int, field: str) -> str:
    if not isinstance(value, str) or len(value) > limit:
        raise _public(CONVERSION_FAILED)
    if '\x00' in value:
        raise _public(CONVERSION_FAILED)
    return value


def _optional_date(value):
    if value is None:
        return None
    if not isinstance(value, str):
        raise _public(CONVERSION_FAILED)
    parsed = parse_date(value[:10])
    if parsed is None:
        raise _public(CONVERSION_FAILED)
    return parsed


def _optional_decimal(value):
    if value is None:
        return None
    if not isinstance(value, str) or len(value) > 40:
        raise _public(CONVERSION_FAILED)
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise _public(CONVERSION_FAILED) from exc


def _optional_int(value):
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or abs(value) > 1_000_000:
        raise _public(CONVERSION_FAILED)
    return value


def _predecessor(raw) -> dict:
    if not isinstance(raw, dict) or set(raw) - {'uid', 'type', 'relation_type', 'lag_days', 'lag_exact'}:
        raise _public(CONVERSION_FAILED)
    relation = raw.get('relation_type')
    if relation is not None and relation not in _RELATION_TYPES:
        raise _public(CONVERSION_FAILED)
    return {
        'uid': _check_string(raw.get('uid', ''), 128, 'predecessor'),
        'type': _check_string(raw.get('type', ''), 32, 'type'),
        'relation_type': relation,
        'lag_days': _optional_int(raw.get('lag_days')),
        'lag_exact': bool(raw.get('lag_exact', True)),
    }


def encode_prepared(parsed) -> bytes:
    from schedule.services.msp_import import ParsedTask

    tasks = []
    for task in parsed.tasks:
        if not isinstance(task, ParsedTask):
            raise _public(CONVERSION_FAILED)
        item = {
            'uid': task.uid,
            'outline_level': task.outline_level,
            'outline_number': task.outline_number,
            'wbs_code': task.wbs_code,
            'name': task.name,
            'is_summary': task.is_summary,
            'start': task.start.isoformat() if task.start else None,
            'finish': task.finish.isoformat() if task.finish else None,
            'duration_days': task.duration_days,
            'percent_complete': str(task.percent_complete) if task.percent_complete is not None else None,
            'total_slack': task.total_slack,
            'free_slack': task.free_slack,
            'is_critical': task.is_critical,
            'predecessors': task.predecessors,
            'node_key': task.node_key,
            'parent_key': task.parent_key,
            'is_milestone': task.is_milestone,
            'milestone_flag': task.milestone_flag,
            'duration_inexact': task.duration_inexact,
            'actual_start': task.actual_start.isoformat() if task.actual_start else None,
            'actual_finish': task.actual_finish.isoformat() if task.actual_finish else None,
            'percent_invalid': task.percent_invalid,
            'critical_known': task.critical_known,
            'total_slack_days': task.total_slack_days,
            'free_slack_days': task.free_slack_days,
            'slack_inexact': task.slack_inexact,
            'free_slack_inexact': task.free_slack_inexact,
            'weight_invalid': task.weight_invalid,
        }
        tasks.append(item)
    payload = {
        'version': PROTOCOL_VERSION,
        'recognized_kind': parsed.recognized_kind,
        'warnings': list(parsed.warnings),
        'has_calendar': bool(parsed.has_calendar),
        'tasks': tasks,
    }
    encoded = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    if len(encoded) > int(settings.IMPORT_OUTPUT_LIMIT_BYTES):
        raise _public(PROCESSING_RESOURCE_LIMIT)
    return encoded


def decode_prepared(raw: bytes):
    from schedule.services.msp_import import ParseResult, ParsedTask

    if len(raw) > int(settings.IMPORT_OUTPUT_LIMIT_BYTES):
        raise _public(PROCESSING_RESOURCE_LIMIT)
    try:
        payload = json.loads(raw.decode('utf-8'))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise _public(CONVERSION_FAILED) from exc
    if not isinstance(payload, dict) or payload.get('version') != PROTOCOL_VERSION:
        raise _public(CONVERSION_FAILED)
    if set(payload) - {'version', 'recognized_kind', 'warnings', 'has_calendar', 'tasks'}:
        raise _public(CONVERSION_FAILED)
    kind = payload.get('recognized_kind')
    if kind not in {'msp', 'mpp', 'xml', 'xer', ''}:
        raise _public(CONVERSION_FAILED)
    warnings = payload.get('warnings')
    if not isinstance(warnings, list) or len(warnings) > 5000:
        raise _public(CONVERSION_FAILED)
    clean_warnings = [_check_string(item, 500, 'warning') for item in warnings]
    tasks_raw = payload.get('tasks')
    if not isinstance(tasks_raw, list):
        raise _public(CONVERSION_FAILED)
    if len(tasks_raw) > 20000:
        raise _public(PROCESSING_RESOURCE_LIMIT)
    tasks = []
    allowed = set(_TASK_STRINGS) | set(_OPTIONAL_STRINGS) | {
        'outline_level', 'is_summary', 'start', 'finish', 'duration_days', 'percent_complete',
        'total_slack', 'free_slack', 'is_critical', 'predecessors', 'is_milestone', 'milestone_flag',
        'duration_inexact', 'actual_start', 'actual_finish', 'percent_invalid', 'critical_known',
        'total_slack_days', 'free_slack_days', 'slack_inexact', 'free_slack_inexact', 'weight_invalid',
    }
    for raw_task in tasks_raw:
        if not isinstance(raw_task, dict) or set(raw_task) - allowed:
            raise _public(CONVERSION_FAILED)
        predecessors = raw_task.get('predecessors') or []
        if not isinstance(predecessors, list) or len(predecessors) > 500:
            raise _public(CONVERSION_FAILED)
        level = raw_task.get('outline_level')
        if isinstance(level, bool) or not isinstance(level, int) or not 0 <= level <= 100:
            raise _public(CONVERSION_FAILED)
        parent = raw_task.get('parent_key')
        tasks.append(ParsedTask(
            uid=_check_string(raw_task.get('uid', ''), _TASK_STRINGS['uid'], 'uid'),
            outline_level=level,
            outline_number=_check_string(raw_task.get('outline_number', ''), _TASK_STRINGS['outline_number'], 'outline'),
            wbs_code=_check_string(raw_task.get('wbs_code', ''), _TASK_STRINGS['wbs_code'], 'wbs'),
            name=_check_string(raw_task.get('name', ''), _TASK_STRINGS['name'], 'name'),
            is_summary=bool(raw_task.get('is_summary')),
            start=_optional_date(raw_task.get('start')),
            finish=_optional_date(raw_task.get('finish')),
            duration_days=_optional_int(raw_task.get('duration_days')),
            percent_complete=_optional_decimal(raw_task.get('percent_complete')),
            total_slack=_optional_int(raw_task.get('total_slack')),
            free_slack=_optional_int(raw_task.get('free_slack')),
            is_critical=raw_task.get('is_critical') if raw_task.get('is_critical') is None else bool(raw_task.get('is_critical')),
            predecessors=[_predecessor(item) for item in predecessors],
            node_key=_check_string(raw_task.get('node_key', ''), _TASK_STRINGS['node_key'], 'node'),
            parent_key=None if parent is None else _check_string(parent, _OPTIONAL_STRINGS['parent_key'], 'parent'),
            is_milestone=bool(raw_task.get('is_milestone')),
            milestone_flag=bool(raw_task.get('milestone_flag')),
            duration_inexact=bool(raw_task.get('duration_inexact')),
            actual_start=_optional_date(raw_task.get('actual_start')),
            actual_finish=_optional_date(raw_task.get('actual_finish')),
            percent_invalid=bool(raw_task.get('percent_invalid')),
            critical_known=bool(raw_task.get('critical_known')),
            total_slack_days=_optional_int(raw_task.get('total_slack_days')),
            free_slack_days=_optional_int(raw_task.get('free_slack_days')),
            slack_inexact=bool(raw_task.get('slack_inexact')),
            free_slack_inexact=bool(raw_task.get('free_slack_inexact')),
            weight_invalid=bool(raw_task.get('weight_invalid')),
        ))
    parsed = ParseResult(tasks=tasks, warnings=clean_warnings, has_calendar=bool(payload.get('has_calendar')))
    parsed.recognized_kind = kind
    return parsed


def _parse_inline(file_bytes: bytes, filename: str, family: str):
    if family == 'p6':
        from schedule.services.p6_import import parse_p6_xer
        return parse_p6_xer(file_bytes)
    from schedule.services.msp_import import parse_msp_family
    return parse_msp_family(file_bytes, filename=filename)


def _directory_size(root: Path) -> int:
    total = 0
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        dirnames[:] = [name for name in dirnames if not (current / name).is_symlink()]
        for name in filenames:
            path = current / name
            if path.is_symlink():
                continue
            try:
                total += path.stat().st_size
            except OSError:
                continue
    return total


def kill_process_group(proc: subprocess.Popen, grace: float) -> None:
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=max(grace, 0.1))
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    proc.wait(timeout=max(grace, 0.1))


def spawn_session(argv: list[str], *, cwd: Path, env: dict, deadline_seconds: float) -> subprocess.CompletedProcess:
    """Run argv in a new session and always reap the group."""
    proc = subprocess.Popen(
        argv,
        cwd=str(cwd),
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = proc.communicate(timeout=deadline_seconds)
    except subprocess.TimeoutExpired as exc:
        kill_process_group(proc, float(settings.IMPORT_PREPARE_GRACE_SECONDS))
        raise MppImportError(PROCESSING_TIMEOUT, PUBLIC_MESSAGES[PROCESSING_TIMEOUT]) from exc
    finally:
        if proc.poll() is None:
            kill_process_group(proc, float(settings.IMPORT_PREPARE_GRACE_SECONDS))
    limit = int(settings.IMPORT_DIAGNOSTIC_LIMIT_BYTES)
    if len(stdout or b'') > limit or len(stderr or b'') > limit:
        raise _public(PROCESSING_RESOURCE_LIMIT)
    return subprocess.CompletedProcess(argv, proc.returncode, stdout, stderr)


def _helper_env() -> dict:
    allowed = {}
    for key in ('PATH', 'LANG', 'LC_ALL', 'HOME', 'JAVA_HOME', 'MPP_MPXJ_CLASSPATH', 'MPP_MPXJ_JAR_DIR'):
        value = os.environ.get(key)
        if value:
            allowed[key] = value
    allowed['PATH'] = allowed.get('PATH', '/usr/bin:/bin')
    allowed['PYTHONPATH'] = str(settings.BASE_DIR)
    allowed['IMPORT_HELPER'] = '1'
    allowed['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    allowed['PYTHONDONTWRITEBYTECODE'] = '1'
    allowed['MPP_CONVERT_TIMEOUT_SECONDS'] = str(settings.MPP_CONVERT_TIMEOUT_SECONDS)
    return allowed


def _assert_containment_policy() -> str:
    if cgroup_ready():
        return 'cgroup'
    if settings.IMPORT_CONTAINMENT_REQUIRED:
        raise _public(CONVERSION_FAILED)
    return 'process'


def _write_manifest(workspace: Path, payload: dict) -> None:
    path = workspace / 'manifest.json'
    path.write_text(json.dumps(payload), encoding='utf-8')
    os.chmod(path, 0o600)


def _resource_exhausted(group: Path) -> bool:
    for filename, keys in [('memory.events', {'oom', 'oom_kill'}), ('pids.events', {'max'})]:
        try:
            values = dict(line.split() for line in (group / filename).read_text().splitlines())
            if any(int(values.get(key, '0')) for key in keys):
                return True
        except (OSError, ValueError):
            continue
    return False


def _finish_cgroup(group: Path, proc=None) -> None:
    """Stop every descendant, reap the direct child and remove only this group."""
    if group.parent != Path(settings.IMPORT_CGROUP_ROOT) or not group.name.startswith('import-'):
        raise _public(CONVERSION_FAILED)
    if group.exists():
        if (group / 'cgroup.procs').read_text().strip():
            (group / 'cgroup.kill').write_text('1')
        limit = time.monotonic() + float(settings.IMPORT_PREPARE_GRACE_SECONDS)
        while (group / 'cgroup.procs').read_text().strip():
            if time.monotonic() >= limit:
                raise _public(CONVERSION_FAILED)
            time.sleep(0.02)
    if proc is not None:
        proc.wait(timeout=max(float(settings.IMPORT_PREPARE_GRACE_SECONDS), 0.1))
    if group.exists():
        group.rmdir()


def _run_helper(workspace: Path, manifest: dict, token: uuid.UUID) -> subprocess.CompletedProcess:
    mode = _assert_containment_policy()
    started = time.monotonic()
    deadline = started + float(settings.IMPORT_PREPARE_TIMEOUT_SECONDS)
    env = _helper_env()
    for key in ('IMPORT_OUTPUT_LIMIT_BYTES', 'IMPORT_HELPER_HEAP_BYTES'):
        env[key] = str(getattr(settings, key))
    env['TMPDIR'] = str(workspace)
    env['IMPORT_HELPER_DEADLINE'] = str(deadline)
    env['IMPORT_HELPER_CONVERT_DEADLINE'] = str(started + float(settings.MPP_CONVERT_TIMEOUT_SECONDS))
    if os.environ.get('A7_P5_ISOLATED') == '1' and 'a7p5' in str(settings.DATABASES['default']['NAME']):
        env['A7_P5_ISOLATED'] = '1'
        if os.environ.get('A7_P5_FAULT_DIR'):
            env['A7_P5_FAULT_DIR'] = os.environ['A7_P5_FAULT_DIR']
    argv = [sys.executable, '-m', 'schedule.services.import_helper', str(workspace / 'manifest.json')]
    if mode == 'process':
        (workspace / 'input.bin').write_bytes(manifest.pop('_input'))
        (workspace / 'release').write_text('ready', encoding='utf-8')
        _write_manifest(workspace, manifest)
        return spawn_session(argv, cwd=workspace, env=env, deadline_seconds=max(0.01, deadline-time.monotonic()))
    _write_manifest(workspace, {key: value for key, value in manifest.items() if key != '_input'})
    proc = subprocess.Popen(argv, cwd=str(workspace), env=env, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    group = None
    selector = selectors.DefaultSelector()
    streams = {'stdout': bytearray(), 'stderr': bytearray()}
    try:
        group = _arm_cgroup(token, proc.pid)
        ImportProcessingSlot.objects.filter(execution_token=token).update(containment_id=f'cgroup:{group}')
        if not _pid_in_cgroup(group, proc.pid):
            raise _public(CONVERSION_FAILED)
        (workspace / 'input.bin').write_bytes(manifest['_input'])
        (workspace / 'release').write_text('ready', encoding='utf-8')
        selector.register(proc.stdout, selectors.EVENT_READ, 'stdout')
        selector.register(proc.stderr, selectors.EVENT_READ, 'stderr')
        while selector.get_map():
            # Descendants can inherit pipes after the helper exits. Inspect
            # kernel events while draining, before a deadline masks pids/OOM.
            if _resource_exhausted(group):
                raise _public(PROCESSING_RESOURCE_LIMIT)
            if time.monotonic() >= deadline:
                raise _public(PROCESSING_TIMEOUT)
            for key, _ in selector.select(timeout=min(0.1, max(0, deadline-time.monotonic()))):
                chunk = os.read(key.fileobj.fileno(), 8192)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                streams[key.data].extend(chunk)
                if len(streams[key.data]) > int(settings.IMPORT_DIAGNOSTIC_LIMIT_BYTES):
                    raise _public(PROCESSING_RESOURCE_LIMIT)
            for filename in ('prepared.json', 'output.xml'):
                output = workspace / filename
                if output.exists() and output.stat().st_size > int(settings.IMPORT_OUTPUT_LIMIT_BYTES):
                    raise _public(PROCESSING_RESOURCE_LIMIT)
            if proc.poll() is not None:
                break
        proc.wait(timeout=max(0.01, deadline-time.monotonic()))
        if proc.returncode == 124:
            raise _public(PROCESSING_TIMEOUT)
        if os.statvfs(workspace).f_bavail == 0:
            raise _public(PROCESSING_RESOURCE_LIMIT)
        if _resource_exhausted(group):
            raise _public(PROCESSING_RESOURCE_LIMIT)
        return subprocess.CompletedProcess(argv, proc.returncode, bytes(streams['stdout']), bytes(streams['stderr']))
    except subprocess.TimeoutExpired as exc:
        raise _public(PROCESSING_TIMEOUT) from exc
    finally:
        selector.close()
        if group is not None:
            try:
                peak = int((group / 'memory.peak').read_text())
                logger.warning('A7P5_RESOURCE token=%s peak_memory_bytes=%s elapsed_seconds=%.3f', token, peak, time.monotonic()-started)
            except OSError:
                pass
            _finish_cgroup(group, proc)
        else:
            kill_process_group(proc, float(settings.IMPORT_PREPARE_GRACE_SECONDS))
            abandoned = Path(settings.IMPORT_CGROUP_ROOT) / f'import-{token}'
            if abandoned.is_dir():
                _finish_cgroup(abandoned, proc)
        proc.stdout.close()
        proc.stderr.close()


def _arm_cgroup(token: uuid.UUID, pid: int) -> Path:
    root = Path(settings.IMPORT_CGROUP_ROOT)
    path = root / f'import-{token}'
    if path.exists() or root.is_symlink():
        raise _public(CONVERSION_FAILED)
    path.mkdir(mode=0o700)
    (path / 'memory.max').write_text(str(settings.IMPORT_HELPER_MEMORY_BYTES), encoding='utf-8')
    (path / 'memory.swap.max').write_text(str(settings.IMPORT_HELPER_SWAP_BYTES), encoding='utf-8')
    (path / 'memory.oom.group').write_text('1', encoding='utf-8')
    (path / 'pids.max').write_text(str(settings.IMPORT_HELPER_PIDS), encoding='utf-8')
    (path / 'cpu.max').write_text('100000 100000', encoding='utf-8')
    (path / 'cgroup.procs').write_text(str(pid), encoding='utf-8')
    return path


def _pid_in_cgroup(path: Path, pid: int) -> bool:
    try:
        procs = (path / 'cgroup.procs').read_text(encoding='utf-8').split()
    except OSError:
        return False
    return str(pid) in procs


def _workspace(token: uuid.UUID) -> Path:
    root = scratch_root()
    if _directory_size(root) > int(settings.IMPORT_SCRATCH_QUOTA_BYTES):
        raise _public(PROCESSING_RESOURCE_LIMIT)
    workspace = root / str(token)
    if workspace.exists() or workspace.is_symlink():
        raise _public(CONVERSION_FAILED)
    workspace.mkdir(mode=0o700)
    return workspace


def cleanup_execution_dir(path: Path) -> str:
    """Remove one finished workspace. Returns removed, preserved, or rejected."""
    root = scratch_root().resolve()
    if path.is_symlink():
        return 'rejected'
    try:
        resolved = path.resolve()
    except OSError:
        return 'rejected'
    if resolved != path or root not in resolved.parents:
        return 'rejected'
    if not path.is_dir():
        return 'preserved'
    children = list(path.iterdir())
    if any(child.is_symlink() for child in children):
        return 'rejected'
    names = {child.name for child in children}
    if not names <= ALLOWED_NAMES:
        return 'preserved'
    for child in children:
        child.unlink()
    path.rmdir()
    return 'removed'


def cleanup_finished_workspace(token: uuid.UUID) -> str:
    path = scratch_root() / str(token)
    if not path.exists():
        return 'removed'
    slot = ImportProcessingSlot.objects.filter(execution_token=token).first()
    if slot is not None and not _containment_clear(slot):
        quarantine_slot(token)
        return 'preserved'
    result = cleanup_execution_dir(path)
    if result != 'removed':
        quarantine_slot(token)
    return result


def _prepare_with_slot(file_bytes: bytes, filename: str, family: str, mode: str):
    if settings.IMPORT_CONTAINMENT_REQUIRED and not cgroup_ready():
        raise _public(CONVERSION_FAILED)
    subject = uuid.uuid4()
    deadline = timezone.now() + timedelta(seconds=int(settings.IMPORT_PREPARE_TIMEOUT_SECONDS))
    token = None
    workspace = None
    try:
        token = acquire_slot(family=family, subject_id=subject, deadline=deadline)
        if settings.IMPORT_PREPARE_INLINE and mode == 'parse':
            parsed = _parse_inline(file_bytes, filename, family)
            return decode_prepared(encode_prepared(parsed))
        if settings.IMPORT_PREPARE_INLINE and mode == 'convert':
            from schedule.services.mpp_convert import _convert_in_process
            return _convert_in_process(file_bytes)
        if len(file_bytes) > int(settings.IMPORT_SCRATCH_QUOTA_BYTES):
            raise _public(PROCESSING_RESOURCE_LIMIT)
        workspace = _workspace(token)
        manifest = {
            'version': PROTOCOL_VERSION,
            'mode': mode,
            'family': family,
            'filename': Path(filename).name[:255],
            'token': str(token),
            'host': hostname(),
            'reboot_id': reboot_id(),
            'deadline': deadline.isoformat(),
            'profile': settings.IMPORT_PROFILE_ID,
            '_input': file_bytes,
        }
        ImportProcessingSlot.objects.filter(execution_token=token).update(
            containment_id=f'pgroup:{reboot_id()}:pending',
        )
        completed = _run_helper(workspace, manifest, token)
        if completed.returncode != 0:
            error_path = workspace / 'diagnostics.txt'
            code = CONVERSION_FAILED
            if error_path.is_file() and not error_path.is_symlink():
                try:
                    recorded = json.loads(error_path.read_text(encoding='utf-8')[:1024])
                    if recorded.get('code') in PUBLIC_MESSAGES:
                        code = recorded['code']
                except (OSError, json.JSONDecodeError):
                    code = CONVERSION_FAILED
            raise _public(code)
        if mode == 'convert':
            output = workspace / 'output.xml'
            if not output.is_file() or output.is_symlink():
                raise _public(MPP_CORRUPT)
            if output.stat().st_size > int(settings.IMPORT_OUTPUT_LIMIT_BYTES):
                raise _public(PROCESSING_RESOURCE_LIMIT)
            return output.read_bytes()
        prepared_path = workspace / 'prepared.json'
        if not prepared_path.is_file() or prepared_path.is_symlink():
            raise _public(CONVERSION_FAILED)
        if prepared_path.stat().st_size > int(settings.IMPORT_OUTPUT_LIMIT_BYTES):
            raise _public(PROCESSING_RESOURCE_LIMIT)
        return decode_prepared(prepared_path.read_bytes())
    finally:
        if token is not None and workspace is not None:
            outcome = cleanup_finished_workspace(token)
            if outcome == 'removed':
                release_slot(token)
        elif token is not None:
            release_slot(token)


def prepare_bytes(file_bytes: bytes, filename: str, family: str):
    """Validate and parse an upload without exposing a caller-controlled path."""
    return _prepare_with_slot(file_bytes, filename, family, 'parse')


def convert_contained(mpp_bytes: bytes) -> bytes:
    return _prepare_with_slot(mpp_bytes, 'input.mpp', 'msp', 'convert')


def _reconcile_scratch_candidate(child: Path, moment, dry_run: bool):
    if child.is_symlink() or not child.is_dir():
        return 'preserved', False
    manifest_path = child / 'manifest.json'
    if not manifest_path.is_file() or manifest_path.is_symlink():
        return 'preserved', False
    try:
        if manifest_path.stat().st_size > 64 * 1024:
            return 'preserved', False
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        deadline = datetime.fromisoformat(manifest['deadline'])
        if timezone.is_naive(deadline):
            deadline = timezone.make_aware(deadline, timezone.get_current_timezone())
        token = uuid.UUID(str(manifest['token']))
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return 'preserved', False
    if child.name != str(token) or deadline > moment:
        return 'preserved', False
    slot = ImportProcessingSlot.objects.filter(execution_token=token).first()
    if dry_run:
        return ('preserved' if slot is not None and not _containment_clear(slot) else 'removed'), False
    if slot is not None and not _containment_clear(slot):
        if slot.owner_host != hostname() or slot.reboot_id != reboot_id():
            quarantine_slot(token)
            return 'preserved', True
        try:
            if not slot.containment_id.startswith('cgroup:'):
                raise _public(CONVERSION_FAILED)
            _finish_cgroup(Path(slot.containment_id.split(':', 1)[1]))
            ImportProcessingSlot.objects.filter(execution_token=token).update(quarantined=False)
        except (OSError, MppImportError):
            quarantine_slot(token)
            return 'preserved', True
    if slot is not None and slot.containment_id.startswith('cgroup:'):
        try:
            _finish_cgroup(Path(slot.containment_id.split(':', 1)[1]))
            ImportProcessingSlot.objects.filter(execution_token=token).update(quarantined=False)
        except (OSError, MppImportError):
            quarantine_slot(token)
            return 'preserved', True
    if cleanup_execution_dir(child) == 'removed':
        release_slot(token)
        return 'removed', False
    quarantine_slot(token)
    return 'preserved', True


def _ordered_scratch_children() -> list[Path]:
    """Unfinished identities stay ahead of directories that appeared later."""
    listed = list(scratch_root().iterdir())
    remembered = [name for name in (cache.get(SCRATCH_UNFINISHED_KEY) or []) if isinstance(name, str)]
    rank = {name: index for index, name in enumerate(remembered)}
    return sorted(listed, key=lambda path: (path.name not in rank, rank.get(path.name, 0), path.name))


def _remember_unfinished(result: dict, names: list[str], *, dry_run: bool) -> dict:
    result['unfinished'] = names
    for name in names:
        if name not in result['removed'] and name not in result['preserved']:
            result['preserved'].append(name)
    if not dry_run:
        if names:
            cache.set(SCRATCH_UNFINISHED_KEY, names, timeout=None)
        else:
            cache.delete(SCRATCH_UNFINISHED_KEY)
    return result


def reconcile_abandoned_scratch(now=None, *, dry_run: bool = False, monotonic=None) -> dict:
    """Drain one finite owned-resource cohort; fail closed on unverifiable work.

    Leader acquisition stays local because import_operations imports this module.
    """
    from schedule.services.import_operations import _leader, _unlock, close_admission, recovery_bound
    moment = now or timezone.now()
    clock = monotonic or time.monotonic
    started = clock()
    result = {
        'status': 'ok', 'removed': [], 'preserved': [], 'unfinished': [], 'deferred': [],
        'cutoff': moment.isoformat(), 'n': 0,
    }
    leader = _leader('scratch')
    if leader is None:
        result.update(status='blocked', reason='leader', elapsed_seconds=clock()-started)
        if not dry_run:
            close_admission()
        return result

    def fail(reason: str, names: list[str]) -> dict:
        result['status'] = 'failed'
        result['reason'] = reason
        return _remember_unfinished(result, names, dry_run=dry_run)

    try:
        children = _ordered_scratch_children()
        result['n'] = len(children)
        result['bound_seconds'] = recovery_bound(len(children))
        batch_size = max(1, int(settings.IMPORT_MAINTENANCE_BATCH_SIZE))
        item_budget = float(settings.IMPORT_MAINTENANCE_ITEM_SECONDS)
        gap = float(settings.IMPORT_MAINTENANCE_GAP_SECONDS)
        pending = children
        waited = False
        while pending:
            batch = pending[:batch_size]
            rest = pending[batch_size:]
            next_deferred: list[Path] = []
            progressed = False
            for index, child in enumerate(batch):
                item_started = clock()
                if clock() - item_started > item_budget:
                    pending_names = [item.name for item in next_deferred + batch[index:] + rest]
                    return fail('item_budget', pending_names)
                try:
                    with transaction.atomic():
                        with connection.cursor() as cursor:
                            cursor.execute("SET LOCAL lock_timeout = '3000ms'")
                            cursor.execute("SET LOCAL statement_timeout = '10000ms'")
                        action, unverified = _reconcile_scratch_candidate(child, moment, dry_run)
                except Exception as exc:
                    # No raw exception, path, or source content reaches public diagnostics.
                    logger.warning('scratch reconciliation failed exc_type=%s', type(exc).__name__)
                    action, unverified = 'preserved', True
                over_budget = clock() - item_started > item_budget
                if unverified:
                    next_deferred.append(child)
                else:
                    result[action].append(child.name)
                    progressed = True
                if over_budget:
                    pending_names = [item.name for item in next_deferred + batch[index + 1:] + rest]
                    return fail('item_budget', pending_names)
            pending = next_deferred + rest
            result['deferred'] = [item.name for item in next_deferred]
            if not progressed:
                if waited:
                    return fail('unverified', [item.name for item in pending])
                waited = True
            if pending and gap:
                time.sleep(gap)
        if not dry_run:
            cache.delete(SCRATCH_UNFINISHED_KEY)
        return result
    finally:
        try:
            result['elapsed_seconds'] = clock() - started
            if result['status'] != 'ok' and not dry_run:
                close_admission()
        finally:
            _unlock('scratch', leader)


# Imported for encode date typing; kept referenced for static readers.
_ = (date, datetime)
