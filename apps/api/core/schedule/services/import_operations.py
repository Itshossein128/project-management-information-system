"""Lifecycle, dispatch, recovery, and retention for schedule import jobs."""

from __future__ import annotations

import logging
import math
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout
from dataclasses import dataclass
from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from django.db import connection, models, transaction
from django.db.models import Q
from django.utils import timezone

from projects.models import Project
from schedule.models import MspImportJob, MspImportStatus, P6ImportJob
from schedule.services.import_fidelity import ImportFidelityError
from schedule.services.import_process import ProcessingBusy, prepare_bytes
from schedule.services.import_safety import (
    ImportSafetyError,
    assert_can_import,
    file_sha256,
    find_inflight_job,
    message_for,
    replacement_block_code,
)
from schedule.services.mpp_errors import (
    IMPORT_FAILED,
    INPUT_EXPIRED,
    PROCESSING_INTERRUPTED,
    PROCESSING_TIMEOUT,
    PUBLIC_MESSAGES,
    MppImportError,
)
from schedule.tests.a7_p5_runtime_support import FaultRefused, IsolatedFault, barrier

logger = logging.getLogger(__name__)

CATCHUP_CACHE_KEY = 'a7p5-catchup-complete'
TERMINAL = 'terminal'
LEGACY = 'legacy_backfill'


class RetryRejected(Exception):
    """Retry linkage is missing or not visible. The response must not identify the target."""


@dataclass
class StartOutcome:
    kind: str
    job: object | None = None
    code: str = ''
    message: str = ''


def recovery_bound(count: int) -> int:
    return 60 + 480 + 10 * count + math.ceil(count / 100)


def purge_bound(count: int) -> int:
    return 3600 + 480 + 10 * count + math.ceil(count / 100)


def admission_closed() -> bool:
    if not settings.IMPORT_ADMISSION_REQUIRES_CATCHUP:
        return False
    return cache.get(CATCHUP_CACHE_KEY) != 'open'


def mark_catchup_complete() -> None:
    cache.set(CATCHUP_CACHE_KEY, 'open', timeout=None)


def close_admission() -> None:
    cache.set(CATCHUP_CACHE_KEY, 'blocked', timeout=None)


def _family_models():
    return (('msp', MspImportJob), ('p6', P6ImportJob))


def resolve_retry(job_model, project, intent: str, retry_of: str | None):
    chosen = intent or 'new'
    if chosen not in {'new', 'retry'}:
        raise RetryRejected()
    if chosen == 'new':
        if retry_of:
            raise RetryRejected()
        return None
    if not retry_of:
        raise RetryRejected()
    try:
        identifier = uuid.UUID(str(retry_of))
    except (TypeError, ValueError) as exc:
        raise RetryRejected() from exc
    predecessor = job_model.objects.filter(
        pk=identifier,
        project=project,
        status=MspImportStatus.FAILED,
    ).first()
    if predecessor is None:
        raise RetryRejected()
    return predecessor


def _refusal(project, user, replace: bool) -> str | None:
    try:
        assert_can_import(project, user)
    except ImportSafetyError as exc:
        return exc.code
    if replace:
        return replacement_block_code(project)
    return None


def _stamp_terminal(job, now, code: str, message: str, result=None) -> None:
    job.status = MspImportStatus.FAILED
    job.error_code = code
    job.error_message = message
    if result is not None:
        job.result = result
    job.completed_at = now
    job.retention_anchor_at = now
    job.retention_anchor_source = TERMINAL
    job.save()


def _safe_message(code: str) -> str:
    safety = message_for(code)
    if safety != code:
        return safety
    return PUBLIC_MESSAGES.get(code, PUBLIC_MESSAGES[IMPORT_FAILED])


def begin_import(*, job_model, task, project, user, file_bytes: bytes, filename: str, replace: bool, intent: str, retry_of: str, family: str) -> StartOutcome:
    barrier('before_intake')
    predecessor = resolve_retry(job_model, project, intent, retry_of or None)
    digest = file_sha256(file_bytes)
    size = len(file_bytes)
    if size > int(settings.IMPORT_UPLOAD_LIMIT_BYTES):
        raise MppImportError('file_too_large', 'File size must not exceed 50 MB.')
    with transaction.atomic():
        locked = Project.objects.select_for_update().get(pk=project.pk)
        refusal = _refusal(locked, user, replace)
        if refusal is None:
            inflight = find_inflight_job(job_model, locked, user, replace, file_bytes)
            if inflight is not None:
                return StartOutcome(kind='queued', job=inflight)
    if admission_closed():
        raise ProcessingBusy()
    prepare_bytes(file_bytes, filename, family)
    now = timezone.now()
    with transaction.atomic():
        locked = Project.objects.select_for_update().get(pk=project.pk)
        refusal = _refusal(locked, user, replace)
        if refusal:
            job = job_model.objects.create(
                project=locked,
                filename=filename,
                replace_existing=replace,
                file_data=file_bytes,
                created_by=user,
                status=MspImportStatus.FAILED,
                error_code=refusal,
                error_message=_safe_message(refusal),
                source_sha256=digest,
                source_size=size,
                completed_at=now,
                retention_anchor_at=now,
                retention_anchor_source=TERMINAL,
                retry_of=predecessor,
            )
            return StartOutcome(kind='refused', job=job, code=refusal, message=_safe_message(refusal))
        inflight = find_inflight_job(job_model, locked, user, replace, file_bytes)
        if inflight is not None:
            return StartOutcome(kind='queued', job=inflight)
        delivery = uuid.uuid4()
        job = job_model.objects.create(
            project=locked,
            filename=filename,
            replace_existing=replace,
            file_data=file_bytes,
            created_by=user,
            status=MspImportStatus.PENDING,
            source_sha256=digest,
            source_size=size,
            queued_at=now,
            dispatch_deadline_at=now + timedelta(seconds=int(settings.IMPORT_DISPATCH_DEADLINE_SECONDS)),
            task_id=str(delivery),
            retry_of=predecessor,
        )
    _publish(task, job)
    barrier('after_intake')
    return StartOutcome(kind='queued', job=job)


def _publish(task, job) -> None:
    barrier('before_publish')
    try:
        if settings.CELERY_TASK_ALWAYS_EAGER:
            task.apply_async(
                args=[str(job.id)], task_id=job.task_id, queue=settings.IMPORT_EXECUTION_QUEUE,
            )
        else:
            pool = ThreadPoolExecutor(max_workers=1)
            try:
                future = pool.submit(
                    task.apply_async,
                    args=[str(job.id)],
                    task_id=job.task_id,
                    queue=settings.IMPORT_EXECUTION_QUEUE,
                    retry=False,
                )
                future.result(timeout=float(settings.IMPORT_PUBLISH_BUDGET_SECONDS))
            finally:
                # Context-manager shutdown waits for a blocked transport and
                # silently defeats the request's publication deadline.
                pool.shutdown(wait=False, cancel_futures=True)
    except FuturesTimeout:
        logger.warning('import publish exceeded budget job=%s', job.id)
        return
    except Exception as exc:
        logger.warning('import publish failed job=%s exc_type=%s', job.id, type(exc).__name__)
        return
    type(job).objects.filter(pk=job.pk, status=MspImportStatus.PENDING).update(
        last_dispatched_at=timezone.now(),
        dispatch_count=models.F('dispatch_count') + 1,
    )


def _lock_pair(job_model, job_id):
    with connection.cursor() as cursor:
        cursor.execute('SET LOCAL lock_timeout = %s', [max(1, int(float(settings.IMPORT_LOCK_WAIT_SECONDS) * 1000))])
    preview = job_model.objects.get(pk=job_id)
    Project.objects.select_for_update().get(pk=preview.project_id)
    return job_model.objects.select_for_update().get(pk=job_id)


def claim_for_execution(job_model, job_id, now=None):
    moment = now or timezone.now()
    with transaction.atomic():
        job = _lock_pair(job_model, job_id)
        if job.status in {MspImportStatus.DONE, MspImportStatus.FAILED}:
            return {'outcome': 'terminal', 'job': job}
        if job.status == MspImportStatus.RUNNING:
            if job.execution_deadline_at and job.execution_deadline_at > moment and job.execution_token:
                return {'outcome': 'duplicate', 'job': job}
            _stamp_terminal(job, moment, PROCESSING_INTERRUPTED, PUBLIC_MESSAGES[PROCESSING_INTERRUPTED])
            return {'outcome': 'terminal', 'job': job}
        if job.dispatch_deadline_at and job.dispatch_deadline_at <= moment:
            _stamp_terminal(job, moment, IMPORT_FAILED, PUBLIC_MESSAGES[IMPORT_FAILED])
            return {'outcome': 'terminal', 'job': job}
        job.status = MspImportStatus.RUNNING
        job.execution_token = uuid.uuid4()
        job.started_at = moment
        job.execution_deadline_at = moment + timedelta(seconds=int(settings.IMPORT_EXECUTION_HARD_SECONDS))
        job.progress_pct = 10
        job.save()
        return {'outcome': 'claimed', 'job': job, 'token': job.execution_token}


def note_progress(job_model, job_id, token, pct: int) -> None:
    job_model.objects.filter(
        pk=job_id,
        execution_token=token,
        status=MspImportStatus.RUNNING,
    ).update(progress_pct=min(int(pct), 99))


def _budgets(deadline) -> None:
    remaining = (deadline - timezone.now()).total_seconds()
    if remaining <= 0:
        raise MppImportError(PROCESSING_TIMEOUT, PUBLIC_MESSAGES[PROCESSING_TIMEOUT])
    statement_ms = max(1, int(min(settings.IMPORT_APPLY_STATEMENT_SECONDS, remaining) * 1000))
    lock_ms = max(1, int(min(settings.IMPORT_LOCK_WAIT_SECONDS, remaining) * 1000))
    with connection.cursor() as cursor:
        cursor.execute('SET LOCAL statement_timeout = %s', [statement_ms])
        cursor.execute('SET LOCAL lock_timeout = %s', [lock_ms])


def apply_prepared(job_model, job_id, token, prepared, execute) -> dict:
    barrier('before_apply')
    with transaction.atomic():
        job = _lock_pair(job_model, job_id)
        if job.status != MspImportStatus.RUNNING or job.execution_token != token:
            return {'outcome': 'fenced', 'job': job}
        if job.execution_deadline_at and job.execution_deadline_at <= timezone.now():
            raise MppImportError(PROCESSING_TIMEOUT, PUBLIC_MESSAGES[PROCESSING_TIMEOUT])
        apply_deadline = min(job.execution_deadline_at, timezone.now()+timedelta(seconds=float(settings.IMPORT_APPLY_STATEMENT_SECONDS)))
        _budgets(apply_deadline)
        barrier('during_apply')

        def on_progress(pct: int) -> None:
            _budgets(apply_deadline)
            note_progress(job_model, job_id, token, pct)

        def bounded_query(execute_query, sql, params, many, context):
            # Transaction cleanup must remain possible after budget exhaustion.
            if sql.lstrip().upper().startswith(('ROLLBACK', 'RELEASE SAVEPOINT')):
                return execute_query(sql, params, many, context)
            remaining=(apply_deadline-timezone.now()).total_seconds()
            if remaining <= 0:
                raise MppImportError(PROCESSING_TIMEOUT, PUBLIC_MESSAGES[PROCESSING_TIMEOUT])
            if not sql.lstrip().upper().startswith('SET LOCAL'):
                execute_query('SET LOCAL statement_timeout = %s', [max(1,int(remaining*1000))], False, context)
            try:
                return execute_query(sql, params, many, context)
            except Exception as exc:
                cause = getattr(exc, '__cause__', None)
                sqlstate = getattr(cause, 'sqlstate', None) or getattr(cause, 'pgcode', None)
                if sqlstate in {'57014','55P03'}:
                    raise MppImportError(PROCESSING_TIMEOUT, PUBLIC_MESSAGES[PROCESSING_TIMEOUT]) from exc
                raise

        with connection.execute_wrapper(bounded_query):
            result = execute(
                job.project,
                bytes(job.file_data or b''),
                filename=job.filename,
                replace=job.replace_existing,
                progress_callback=on_progress,
                user=job.created_by,
                prepared=prepared,
            )
            _budgets(apply_deadline)
            moment = timezone.now()
            job.status = MspImportStatus.DONE
            job.progress_pct = 100
            job.result = result
            job.error_code = ''
            job.error_message = ''
            barrier('after_domain_write')
            job.completed_at = moment
            job.retention_anchor_at = moment
            job.retention_anchor_source = TERMINAL
            job.save()
            return {'outcome': 'done', 'result': result}



def record_failure(job_model, job_id, token, code: str, message: str, result=None) -> None:
    barrier('during_failure_recording')
    _record_failure(job_model, job_id, token, code, message, result)


def _record_failure(job_model, job_id, token, code: str, message: str, result=None) -> None:
    moment = timezone.now()
    with transaction.atomic():
        job = _lock_pair(job_model, job_id)
        if job.execution_token != token or job.status != MspImportStatus.RUNNING:
            return
        _stamp_terminal(job, moment, code, message, result=result)


def _failure_parts(exc: BaseException) -> tuple[str, str, dict | None]:
    if isinstance(exc, ImportFidelityError):
        return exc.code, exc.message, {'blocking': exc.as_dicts()}
    if isinstance(exc, (ImportSafetyError, MppImportError)):
        return exc.code, exc.message or PUBLIC_MESSAGES.get(exc.code, PUBLIC_MESSAGES[IMPORT_FAILED]), None
    if isinstance(exc, IsolatedFault):
        return PROCESSING_INTERRUPTED, PUBLIC_MESSAGES[PROCESSING_INTERRUPTED], None
    return IMPORT_FAILED, PUBLIC_MESSAGES[IMPORT_FAILED], None


def run_claimed_import(job_model, job_id, execute, family: str) -> dict:
    claimed = claim_for_execution(job_model, job_id)
    job = claimed['job']
    if claimed['outcome'] == 'terminal':
        return job.result or {'error_code': job.error_code}
    if claimed['outcome'] == 'duplicate':
        return {'duplicate': True}
    token = claimed['token']
    try:
        payload = bytes(job.file_data or b'')
        if not payload:
            raise MppImportError(INPUT_EXPIRED, PUBLIC_MESSAGES[INPUT_EXPIRED])
        barrier('before_prepare')
        prepared = prepare_bytes(payload, job.filename, family)
        note_progress(job_model, job_id, token, 40)
        outcome = apply_prepared(job_model, job_id, token, prepared, execute)
        barrier('after_commit')
        return outcome.get('result') or outcome
    except FaultRefused:
        raise
    except Exception as exc:
        code, message, result = _failure_parts(exc)
        logger.warning('import attempt failed job=%s code=%s exc_type=%s', job_id, code, type(exc).__name__)
        try:
            record_failure(job_model, job_id, token, code, message, result=result)
        except FaultRefused:
            raise
        except IsolatedFault:
            _record_failure(
                job_model, job_id, token, PROCESSING_INTERRUPTED, PUBLIC_MESSAGES[PROCESSING_INTERRUPTED],
            )
        return {'error_code': code}


def _leader(scope: str):
    token = str(uuid.uuid4())
    key = f'a7p5-leader-{scope}'
    if not cache.add(key, token, timeout=max(int(settings.IMPORT_RECONCILE_INTERVAL_SECONDS), 30)):
        return None
    with connection.cursor() as cursor:
        cursor.execute('SELECT pg_try_advisory_lock(hashtext(%s))', [f'a7p5-{scope}'])
        locked = cursor.fetchone()[0]
    if not locked:
        cache.delete(key)
        return None
    return key, token


def _unlock(scope: str, leader) -> None:
    if leader is None:
        return
    key, token = leader
    with connection.cursor() as cursor:
        cursor.execute('SELECT pg_advisory_unlock(hashtext(%s))', [f'a7p5-{scope}'])
    if cache.get(key) == token:
        cache.delete(key)


def _cohort_ids(kind: str, now, cutoff):
    rows = []
    if kind == 'recovery':
        for family, model in _family_models():
            queryset = model.objects.filter(created_at__lte=cutoff).filter(
                Q(status=MspImportStatus.PENDING, dispatch_deadline_at__lte=now)
                | Q(status=MspImportStatus.RUNNING, execution_deadline_at__lte=now)
                | Q(status=MspImportStatus.PENDING, dispatch_deadline_at__gt=now, dispatch_count=0)
            )
            for identifier, created in queryset.order_by('created_at', 'id').values_list('id', 'created_at'):
                rows.append((created, family, identifier))
    else:
        horizon = now - timedelta(hours=int(settings.IMPORT_RETENTION_HOURS))
        for family, model in _family_models():
            queryset = model.objects.filter(
                created_at__lte=cutoff,
                status__in=(MspImportStatus.DONE, MspImportStatus.FAILED),
                retention_anchor_at__isnull=False,
                retention_anchor_at__lte=horizon,
                file_purged_at__isnull=True,
            ).exclude(file_data__isnull=True)
            for identifier, created in queryset.order_by('created_at', 'id').values_list('id', 'created_at'):
                rows.append((created, family, identifier))
    rows.sort()
    return rows


def _recover_one(job, now) -> None:
    if job.status == MspImportStatus.PENDING and job.dispatch_deadline_at and job.dispatch_deadline_at <= now:
        _stamp_terminal(job, now, IMPORT_FAILED, PUBLIC_MESSAGES[IMPORT_FAILED])
        return
    if job.status == MspImportStatus.RUNNING and job.execution_deadline_at and job.execution_deadline_at <= now:
        _stamp_terminal(job, now, PROCESSING_INTERRUPTED, PUBLIC_MESSAGES[PROCESSING_INTERRUPTED])
        return
    if job.status == MspImportStatus.PENDING and job.task_id:
        job._republish = True


def _republish(family: str, job_id: str, task_id: str, now) -> None:
    from schedule.tasks import run_msp_import_task, run_p6_import_task

    task = run_msp_import_task if family == 'msp' else run_p6_import_task
    model = MspImportJob if family == 'msp' else P6ImportJob
    job = model.objects.filter(pk=job_id, status=MspImportStatus.PENDING).first()
    if job is not None:
        _publish(task, job)



def _purge_one(job, now) -> None:
    anchor = job.retention_anchor_at
    if anchor is None or job.status not in {MspImportStatus.DONE, MspImportStatus.FAILED}:
        return
    if anchor + timedelta(hours=int(settings.IMPORT_RETENTION_HOURS)) > now:
        return
    if job.file_data is None or job.file_purged_at is not None:
        return
    digest = job.source_sha256
    size = job.source_size
    completed = job.completed_at
    result = job.result
    job.file_data = None
    job.file_purged_at = now
    job.save(update_fields=['file_data', 'file_purged_at', 'updated_at'])
    job.refresh_from_db()
    if job.source_sha256 != digest or job.source_size != size or job.completed_at != completed or job.result != result:
        raise RuntimeError('purge changed retained history')


def run_maintenance(kind: str, *, now=None, dry_run: bool = False, monotonic=None, sleeper=None, hook=None) -> dict:
    moment = now or timezone.now()
    clock = monotonic or time.monotonic
    pause = sleeper or time.sleep
    leader = _leader(kind)
    if leader is None:
        return {'operation': kind, 'status': 'blocked', 'reason': 'leader'}
    started = clock()
    try:
        state_key = f'a7p5-cohort-{kind}'
        state = cache.get(state_key) or {}
        if not state or state.get('complete'):
            cutoff = moment
            state = {'cutoff': cutoff.isoformat(), 'complete': False}
            cache.set(state_key, state, timeout=None)
        else:
            cutoff = datetime_from_iso(state['cutoff'])
        rows = _cohort_ids(kind, moment, cutoff)
        count = len(rows)
        batch_size = int(settings.IMPORT_MAINTENANCE_BATCH_SIZE)
        item_budget = float(settings.IMPORT_MAINTENANCE_ITEM_SECONDS)
        gap = float(settings.IMPORT_MAINTENANCE_GAP_SECONDS)
        pending = list(rows)
        barrier('maintenance-' + kind)
        processed = []
        deferred = []
        unfinished = []
        waited = False
        while pending:
            if hook is not None:
                hook(kind, len(processed), cutoff)
            batch = pending[:batch_size]
            rest = pending[batch_size:]
            next_deferred = []
            progressed = False
            for _created, family, identifier in batch:
                item_started = clock()
                model = MspImportJob if family == 'msp' else P6ImportJob
                republish = False
                family_name = family
                job_pk = str(identifier)
                task_id = ''
                if dry_run:
                    processed.append(str(identifier))
                    progressed = True
                else:
                    with transaction.atomic():
                        project_id = model.objects.filter(pk=identifier).values_list('project_id', flat=True).first()
                        project = Project.objects.select_for_update(skip_locked=True).filter(pk=project_id).first()
                        job = model.objects.select_for_update(skip_locked=True).filter(pk=identifier).first() if project is not None else None
                        if job is None:
                            next_deferred.append((_created, family, identifier))
                        elif kind == 'recovery':
                            _recover_one(job, moment)
                            republish = bool(getattr(job, '_republish', False))
                            task_id = job.task_id
                            job_pk = str(job.pk)
                            processed.append(str(identifier))
                            progressed = True
                        else:
                            _purge_one(job, moment)
                            processed.append(str(identifier))
                            progressed = True
                if republish:
                    _republish(family_name, job_pk, task_id, moment)
                if clock() - item_started > item_budget:
                    unfinished = [str(item[2]) for item in next_deferred + rest]
                    close_admission()
                    return _maintenance_result(kind, cutoff, count, started, clock, processed, next_deferred, unfinished, 'failed')
            pending = next_deferred + rest
            deferred = next_deferred
            if not progressed:
                if waited:
                    unfinished = [str(item[2]) for item in pending]
                    close_admission()
                    return _maintenance_result(kind, cutoff, count, started, clock, processed, deferred, unfinished, 'failed')
                waited = True
            if pending:
                pause(gap)
        cache.set(state_key, {'cutoff': state['cutoff'], 'complete': True}, timeout=None)
        if kind == 'recovery' and not dry_run:
            from schedule.services.import_process import reconcile_abandoned_scratch
            scratch = reconcile_abandoned_scratch(now=moment, monotonic=clock)
            if scratch['status'] != 'ok':
                close_admission()
                result = _maintenance_result(kind, cutoff, count, started, clock, processed, [], [], 'failed')
                result['reason'] = 'scratch_not_verified'
                result['scratch'] = scratch
                return result
            mark_catchup_complete()
        return _maintenance_result(kind, cutoff, count, started, clock, processed, [], [], 'ok')
    finally:
        _unlock(kind, leader)


def datetime_from_iso(value: str):
    parsed = datetime.fromisoformat(value)
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def _maintenance_result(kind, cutoff, count, started, clock, processed, deferred, unfinished, status) -> dict:
    bound = recovery_bound(count) if kind == 'recovery' else purge_bound(count)
    return {
        'operation': kind,
        'status': status,
        'cutoff': cutoff.isoformat(),
        'n': count,
        'processed_ids': processed,
        'deferred': [str(item[2]) for item in deferred],
        'unfinished': unfinished,
        'elapsed_seconds': clock() - started,
        'bound_seconds': bound,
    }
