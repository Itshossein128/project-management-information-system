"""Exercise project/report lock order with two real PostgreSQL connections."""
import threading
from datetime import date

import pytest
from django.db import DatabaseError, connection, transaction

from projects.models import Project
from sub_reports.models import DisciplineSubReport, DisciplineSubReportActivity, SubReportStatus
from sub_reports import unit_report_services as svc


@pytest.mark.django_db(transaction=True)
def test_submit_waits_for_project_lock_before_taking_report_lock(project, user, monkeypatch):
    if connection.vendor != 'postgresql':
        pytest.fail('This concurrency test requires PostgreSQL')
    report = DisciplineSubReport.objects.create(project=project, unit='buildings', discipline='civil',
        report_date=date(2026, 10, 20), status=SubReportStatus.DRAFT, created_by=user)
    DisciplineSubReportActivity.objects.create(
        sub_report=report, row_number=1, shift='shift_1', crew_name='Crew',
        activity_description='Lock ordering activity', quantity=1, unit='m2', worker_count=1,
    )
    report_locked = threading.Event()
    worker_started = threading.Event()
    errors = []
    original_lock = svc.lock_current_version
    def observed_lock(*args, **kwargs):
        result = original_lock(*args, **kwargs)
        report_locked.set()
        return result
    monkeypatch.setattr(svc, 'lock_current_version', observed_lock)
    def submit():
        connection.close()
        try:
            worker_started.set()
            svc.submit_unit_report(report, user=user, unit='buildings')
        except Exception as exc:
            errors.append(exc)
        finally:
            connection.close()
    with transaction.atomic():
        Project.objects.select_for_update().get(pk=project.pk)
        worker = threading.Thread(target=submit)
        worker.start()
        assert worker_started.wait(5)
        report_locked.wait(2)
        blocked = False
        try:
            with transaction.atomic():
                DisciplineSubReport.objects.select_for_update(nowait=True).get(pk=report.pk)
        except DatabaseError:
            blocked = True
    worker.join(timeout=20)
    assert not worker.is_alive(), 'submission did not finish after project lock released'
    assert not errors, errors
    assert not blocked, 'submit locked report while waiting for project; aggregation can deadlock'
    report.refresh_from_db()
    assert report.status == SubReportStatus.SUBMITTED
