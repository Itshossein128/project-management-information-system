"""Seven-day original-byte retention."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.core.cache import cache
from django.utils import timezone

from projects.models import ProjectStatus
from projects.services import create_project_with_creator
from schedule.models import MspImportJob, MspImportStatus, P6ImportJob
from schedule.services.import_operations import run_maintenance


@pytest.fixture(autouse=True)
def _clear_maintenance_cache():
    yield
    for key in ('a7p5-catchup-complete', 'a7p5-cohort-recovery', 'a7p5-cohort-purge', 'a7p5-leader-purge'):
        cache.delete(key)


def _project(user):
    project = create_project_with_creator(
        creator=user,
        project_code='A7P5-RETAIN',
        project_name='P5 retention',
        employer='P5',
        start_date='2026-01-01',
    )
    project.status = ProjectStatus.ACTIVE
    project.save(update_fields=['status', 'updated_at'])
    return project


@pytest.mark.django_db
def test_purge_follows_the_168_hour_boundary_and_keeps_history(user, settings):
    settings.IMPORT_MAINTENANCE_GAP_SECONDS = 0
    project = _project(user)
    digest = 'ab' * 32
    due = MspImportJob.objects.create(
        project=project, filename='due.xml', status=MspImportStatus.DONE, file_data=b'abc',
        created_by=user, source_sha256=digest, source_size=3, result={'kept': 1},
        completed_at=timezone.now() - timedelta(hours=168),
        retention_anchor_at=timezone.now() - timedelta(hours=168),
        retention_anchor_source='terminal',
    )
    early = MspImportJob.objects.create(
        project=project, filename='early.xml', status=MspImportStatus.DONE, file_data=b'early',
        created_by=user, source_sha256=digest, source_size=5,
        retention_anchor_at=timezone.now() - timedelta(hours=168) + timedelta(seconds=30),
        retention_anchor_source='terminal', completed_at=timezone.now(),
    )
    active = MspImportJob.objects.create(
        project=project, filename='active.xml', status=MspImportStatus.PENDING, file_data=b'active',
        created_by=user, retention_anchor_at=timezone.now() - timedelta(days=30),
    )
    now = timezone.now()
    due.refresh_from_db()
    due.retention_anchor_at = now - timedelta(hours=168)
    due.completed_at = due.retention_anchor_at
    due.save(update_fields=['retention_anchor_at', 'completed_at', 'updated_at'])
    early.retention_anchor_at = now - timedelta(hours=168) + timedelta(seconds=30)
    early.save(update_fields=['retention_anchor_at', 'updated_at'])
    run_maintenance('purge', now=now)
    due.refresh_from_db()
    early.refresh_from_db()
    active.refresh_from_db()
    assert due.file_data is None
    assert due.file_purged_at is not None
    assert due.source_sha256 == digest
    assert due.result == {'kept': 1}
    assert due.completed_at is not None
    stamped = due.file_purged_at
    run_maintenance('purge', now=now)
    due.refresh_from_db()
    assert due.file_purged_at == stamped
    assert bytes(early.file_data) == b'early'
    assert bytes(active.file_data) == b'active'


@pytest.mark.django_db
def test_purge_drains_a_201_row_cohort(user, settings):
    settings.IMPORT_MAINTENANCE_GAP_SECONDS = 0
    project = _project(user)
    anchor = timezone.now() - timedelta(hours=169)
    for index in range(201):
        model = MspImportJob if index % 2 == 0 else P6ImportJob
        model.objects.create(
            project=project,
            filename=f'{index}.bin',
            status=MspImportStatus.FAILED,
            file_data=b'x',
            created_by=user,
            source_sha256='cd' * 32,
            source_size=1,
            retention_anchor_at=anchor,
            retention_anchor_source='legacy_backfill',
            error_code='import_failed',
        )
    result = run_maintenance('purge', now=timezone.now())
    assert result['status'] == 'ok'
    assert result['n'] == 201
    assert result['elapsed_seconds'] < result['bound_seconds']
    assert MspImportJob.objects.filter(project=project, file_purged_at__isnull=False).count() == 101
    assert P6ImportJob.objects.filter(project=project, file_purged_at__isnull=False).count() == 100


@pytest.mark.django_db
@pytest.mark.parametrize('model', [MspImportJob, P6ImportJob])
@pytest.mark.parametrize('outcome', [MspImportStatus.DONE, MspImportStatus.FAILED])
def test_exact_boundary_in_both_families_and_outcomes(user, settings, model, outcome):
    settings.IMPORT_MAINTENANCE_GAP_SECONDS = 0
    now = timezone.now()
    project = _project(user)
    anchor = now - timedelta(hours=168)
    job = model.objects.create(project=project, created_by=user, status=outcome,
        file_data=b'private', source_sha256='ab'*32, source_size=7,
        completed_at=anchor, retention_anchor_at=anchor,
        retention_anchor_source='terminal', result={'kept': True})
    # The aged fixture must also predate the maintenance cohort cutoff.
    model.objects.filter(pk=job.pk).update(created_at=anchor)
    run_maintenance('purge', now=now-timedelta(microseconds=1))
    job.refresh_from_db(); assert bytes(job.file_data) == b'private'
    run_maintenance('purge', now=now)
    job.refresh_from_db(); assert job.file_data is None
    first = job.file_purged_at
    run_maintenance('purge', now=now+timedelta(microseconds=1))
    job.refresh_from_db()
    assert job.file_purged_at == first
    assert job.completed_at == anchor and job.result == {'kept': True}
