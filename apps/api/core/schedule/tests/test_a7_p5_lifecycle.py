"""Claim, atomic completion, and sanitized failure recording."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from projects.models import Activity, ProjectStatus, WBS
from projects.services import create_project_with_creator
from schedule.models import ImportProcessingSlot, MspImportJob, MspImportStatus
from schedule.services.import_operations import claim_for_execution
from schedule.tasks import run_msp_import_task
from schedule.tests.test_msp_import import SAMPLE_MSP_XML


def _project(user):
    # Transactional pytest flush removes migration-seeded rows under --reuse-db.
    ImportProcessingSlot.objects.get_or_create(slot_number=1)
    from master_data.models import Permission, Role, RolePermission
    from permissions.constants import DEFAULT_ROLE_PERMISSIONS, PERMISSIONS
    role, _ = Role.objects.get_or_create(role_name='project_manager')
    for code in DEFAULT_ROLE_PERMISSIONS['project_manager']:
        Permission.objects.get_or_create(codename=code, defaults={'label': PERMISSIONS[code]})
        RolePermission.objects.get_or_create(role=role, permission_codename=code)
    project = create_project_with_creator(
        creator=user,
        project_code='A7P5-LIFE',
        project_name='P5 lifecycle',
        employer='P5',
        start_date='2026-01-01',
    )
    project.status = ProjectStatus.ACTIVE
    project.save(update_fields=['status', 'updated_at'])
    return project


@pytest.mark.django_db
def test_claim_stays_below_complete_and_success_is_terminal(user):
    project = _project(user)
    job = MspImportJob.objects.create(
        project=project,
        filename='plan.xml',
        file_data=SAMPLE_MSP_XML,
        created_by=user,
        status=MspImportStatus.PENDING,
        dispatch_deadline_at=timezone.now() + timedelta(minutes=5),
    )
    claimed = claim_for_execution(MspImportJob, job.id)
    assert claimed['outcome'] == 'claimed'
    assert claimed['job'].progress_pct < 100
    assert claimed['job'].execution_token
    duplicate = claim_for_execution(MspImportJob, job.id)
    assert duplicate['outcome'] == 'duplicate'
    job.refresh_from_db()
    job.status = MspImportStatus.PENDING
    job.execution_token = None
    job.save(update_fields=['status', 'execution_token', 'updated_at'])
    run_msp_import_task.apply(args=[str(job.id)])
    job.refresh_from_db()
    assert job.status == MspImportStatus.DONE
    assert job.progress_pct == 100
    assert job.completed_at == job.retention_anchor_at
    assert job.retention_anchor_source == 'terminal'
    assert job.result['activities_created'] >= 1
    assert Activity.objects.filter(project=project, is_deleted=False).exists()


@pytest.mark.django_db
def test_apply_failure_rolls_back_and_hides_the_exception_text(user):
    project = _project(user)
    job = MspImportJob.objects.create(
        project=project,
        filename='plan.xml',
        file_data=SAMPLE_MSP_XML,
        created_by=user,
        status=MspImportStatus.PENDING,
        dispatch_deadline_at=timezone.now() + timedelta(minutes=5),
    )
    with patch(
        'schedule.services.shared_import.Activity.objects.bulk_create',
        side_effect=RuntimeError('SUPER-SECRET-BYTES'),
    ):
        run_msp_import_task.apply(args=[str(job.id)])
    job.refresh_from_db()
    assert job.status == MspImportStatus.FAILED
    assert job.error_code == 'import_failed'
    assert 'SUPER-SECRET-BYTES' not in job.error_message
    assert not Activity.objects.filter(project=project, is_deleted=False).exists()
    assert not WBS.objects.filter(project=project, is_deleted=False).exists()


@pytest.mark.django_db(transaction=True)
def test_project_claim_lock_obeys_its_budget_before_acquisition(user, settings):
    import threading
    import time
    from django.db import OperationalError, connections, transaction
    from projects.models import Project
    settings.IMPORT_LOCK_WAIT_SECONDS = 0.15
    project = _project(user)
    job = MspImportJob.objects.create(project=project,created_by=user,
        status='pending',dispatch_deadline_at=timezone.now()+timedelta(minutes=5))
    held=threading.Event();release=threading.Event()
    def hold():
        try:
            with transaction.atomic():
                Project.objects.select_for_update().get(pk=project.pk)
                held.set();release.wait(3)
        finally:connections.close_all()
    thread=threading.Thread(target=hold);thread.start();assert held.wait(5)
    timer=threading.Timer(.8,release.set);timer.start()
    started=time.monotonic()
    try:
        with pytest.raises(OperationalError):
            claim_for_execution(MspImportJob,job.pk)
        assert time.monotonic()-started<.6
        job.refresh_from_db();assert job.status=='pending' and job.execution_token is None
    finally:
        release.set();timer.cancel();thread.join(5)


@pytest.mark.django_db
@pytest.mark.parametrize('gate',['final','sql'])
def test_cumulative_apply_budget_rolls_back_before_done(user, settings, gate):
    import time
    from schedule.services.import_operations import apply_prepared, record_failure
    from schedule.services.mpp_errors import MppImportError
    settings.IMPORT_APPLY_STATEMENT_SECONDS = .05
    project=_project(user)
    job=MspImportJob.objects.create(project=project,created_by=user,status='pending',
        dispatch_deadline_at=timezone.now()+timedelta(minutes=5))
    claimed=claim_for_execution(MspImportJob,job.pk)
    original_name=project.project_name
    def slow_apply(*args, **kwargs):
        type(project).objects.filter(pk=project.pk).update(project_name='must roll back')
        if gate=='sql':
            from django.db import connection, transaction
            with transaction.atomic():
                time.sleep(.02)
                with connection.cursor() as cursor:cursor.execute('SELECT pg_sleep(0.2)')
        else:time.sleep(.1)
        return {'uncommitted':True}
    with pytest.raises(MppImportError) as error:
        apply_prepared(MspImportJob,job.pk,claimed['token'],None,slow_apply)
    assert error.value.code=='processing_timeout'
    if gate=='sql':
        cause=error.value.__cause__.__cause__
        assert (getattr(cause,'sqlstate',None) or getattr(cause,'pgcode',None))=='57014'
    record_failure(MspImportJob,job.pk,claimed['token'],error.value.code,'Processing timed out.')
    job.refresh_from_db()
    assert job.status=='failed' and job.progress_pct<100 and not job.result
    project.refresh_from_db();assert project.project_name==original_name
