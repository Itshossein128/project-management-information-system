"""Dispatch recovery, cohort bounds, and maintenance exclusion."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.core.cache import cache
from django.utils import timezone

from projects.models import ProjectStatus
from projects.services import create_project_with_creator
from schedule.models import MspImportJob, MspImportStatus, P6ImportJob
from schedule.services.import_operations import purge_bound, recovery_bound, run_maintenance


@pytest.fixture(autouse=True)
def _clear_maintenance_cache():
    yield
    for key in (
        'a7p5-catchup-complete', 'a7p5-cohort-recovery', 'a7p5-cohort-purge',
        'a7p5-leader-recovery', 'a7p5-leader-purge',
    ):
        cache.delete(key)


def _project(user, suffix):
    project = create_project_with_creator(
        creator=user,
        project_code=f'A7P5-RECOVERY-{suffix}',
        project_name=f'P5 recovery {suffix}',
        employer='P5',
        start_date='2026-01-01',
    )
    project.status = ProjectStatus.ACTIVE
    project.save(update_fields=['status', 'updated_at'])
    return project


def test_recovery_bound_matches_the_documented_formula():
    assert recovery_bound(201) == 60 + 480 + 10 * 201 + 3
    assert purge_bound(201) == 3600 + 480 + 10 * 201 + 3


def test_slow_broker_does_not_extend_the_request_publish_budget(settings):
    import threading
    import time
    from types import SimpleNamespace
    from schedule.services.import_operations import _publish

    settings.CELERY_TASK_ALWAYS_EAGER = False
    settings.IMPORT_PUBLISH_BUDGET_SECONDS = 0.05
    release = threading.Event()
    task = SimpleNamespace(apply_async=lambda **kwargs: release.wait(1))
    job = SimpleNamespace(id='isolated-budget-probe', task_id='fixed')
    started = time.monotonic()
    try:
        _publish(task, job)
        assert time.monotonic() - started < 0.3
    finally:
        release.set()


@pytest.mark.django_db
def test_expired_pending_is_terminal_and_a_large_cohort_finishes(user, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = False
    settings.IMPORT_MAINTENANCE_GAP_SECONDS = 0
    project = _project(user, 'COHORT')
    past = timezone.now() - timedelta(minutes=1)
    for index in range(201):
        model = MspImportJob if index % 2 == 0 else P6ImportJob
        model.objects.create(
            project=project,
            filename=f'{index}.xml',
            status=MspImportStatus.PENDING,
            created_by=user,
            dispatch_deadline_at=past,
            task_id=f'task-{index}',
        )
    later = []
    nested = {}

    def hook(kind, processed, cutoff):
        if processed == 0 and not later:
            arrived = MspImportJob.objects.create(
                project=project,
                filename='later.xml',
                status=MspImportStatus.PENDING,
                created_by=user,
                dispatch_deadline_at=past,
                task_id='later',
            )
            later.append(arrived.id)
            nested['result'] = run_maintenance('recovery', now=timezone.now())

    result = run_maintenance('recovery', now=timezone.now(), hook=hook)
    assert result['status'] == 'ok'
    assert result['n'] == 201
    assert result['elapsed_seconds'] < result['bound_seconds']
    assert MspImportJob.objects.filter(project=project, status=MspImportStatus.FAILED).count() == 101
    assert P6ImportJob.objects.filter(project=project, status=MspImportStatus.FAILED).count() == 100
    assert MspImportJob.objects.get(pk=later[0]).status == MspImportStatus.PENDING
    assert nested['result']['status'] == 'blocked'


@pytest.mark.django_db
def test_republish_does_not_extend_the_deadline(user, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = False
    settings.IMPORT_EXECUTION_QUEUE = 'a7p5-unit-nobody'
    project = _project(user, 'DEADLINE')
    deadline = timezone.now() + timedelta(minutes=4)
    job = MspImportJob.objects.create(
        project=project,
        filename='plan.xml',
        status=MspImportStatus.PENDING,
        created_by=user,
        dispatch_deadline_at=deadline,
        dispatch_count=0,
        task_id='fixed-task',
    )
    result = run_maintenance('recovery', now=timezone.now())
    job.refresh_from_db()
    assert result['status'] == 'ok'
    assert job.dispatch_deadline_at == deadline
    assert job.status == MspImportStatus.PENDING


@pytest.mark.django_db
def test_budget_exhaustion_blocks_admission(user, settings):
    settings.IMPORT_MAINTENANCE_GAP_SECONDS = 0
    project = _project(user, 'BUDGET')
    past = timezone.now() - timedelta(minutes=1)
    MspImportJob.objects.create(
        project=project, filename='a.xml', status=MspImportStatus.PENDING,
        created_by=user, dispatch_deadline_at=past, task_id='a',
    )
    seen = {'count': 0}

    def clock():
        seen['count'] += 1
        return 0 if seen['count'] < 3 else 100

    result = run_maintenance('recovery', now=timezone.now(), monotonic=clock, sleeper=lambda _seconds: None)
    assert result['status'] == 'failed'
    from schedule.services.import_operations import admission_closed
    settings.IMPORT_ADMISSION_REQUIRES_CATCHUP = True
    assert admission_closed()


@pytest.mark.django_db
def test_maintenance_republish_uses_the_same_finite_budget(user, settings, monkeypatch):
    import threading
    import time
    from schedule.services.import_operations import _republish
    from schedule.tasks import run_msp_import_task
    settings.CELERY_TASK_ALWAYS_EAGER = False
    settings.IMPORT_PUBLISH_BUDGET_SECONDS = 0.05
    project = _project(user, 'REPUBLISH-BUDGET')
    deadline = timezone.now() + timedelta(minutes=4)
    job = MspImportJob.objects.create(project=project, created_by=user,
        status='pending', task_id='fixed', dispatch_deadline_at=deadline)
    release = threading.Event()
    monkeypatch.setattr(run_msp_import_task, 'apply_async', lambda **kwargs: release.wait(1))
    started = time.monotonic()
    try:
        _republish('msp', str(job.pk), job.task_id, timezone.now())
        assert time.monotonic() - started < 0.3
        job.refresh_from_db()
        assert job.dispatch_deadline_at == deadline and job.status == 'pending'
    finally:
        release.set()


def test_mandatory_command_cannot_report_blocked_as_success(monkeypatch):
    from django.core.management import call_command
    from django.core.management.base import CommandError
    monkeypatch.setattr('schedule.management.commands.maintain_import_jobs.run_maintenance',
        lambda *a, **kw: {'status': 'blocked'})
    with pytest.raises(CommandError):
        call_command('maintain_import_jobs', operation='recovery')


def test_invalid_batch_is_a_command_error():
    from django.core.management import call_command
    from django.core.management.base import CommandError
    with pytest.raises(CommandError):
        call_command('maintain_import_jobs', batch_size=101)
