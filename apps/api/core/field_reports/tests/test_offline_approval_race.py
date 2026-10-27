"""Real two-connection race between a legacy batch and report approval."""
import threading
from datetime import date

import pytest
from django.db import connection, transaction
from rest_framework.test import APIClient

from field_reports import services
from field_reports.models import DailyReport, DailyReportActivity, ReportStatus


@pytest.mark.django_db(transaction=True)
def test_approved_report_wins_over_stale_batch_read(project, user, monkeypatch):
    if connection.vendor != 'postgresql':
        pytest.fail('This test requires PostgreSQL independent connections')
    report = DailyReport.objects.create(project=project, report_date=date(2026, 10, 20),
        status=ReportStatus.DRAFT, is_auto_summary=True, created_by=user, updated_by=user,
        general_notes='original')
    entered_merge = threading.Event()
    worker_started = threading.Event()
    errors, replies = [], []
    original_merge = services._apply_header_merge
    def observed_merge(*args, **kwargs):
        entered_merge.set()
        return original_merge(*args, **kwargs)
    monkeypatch.setattr(services, '_apply_header_merge', observed_merge)
    def batch():
        connection.close()
        try:
            client = APIClient()
            client.force_authenticate(user=user)
            worker_started.set()
            replies.append(client.post(f'/api/v1/projects/{project.id}/daily-reports/sync-batch/',
                [{'local_id': 'race', 'report_date': '2026-10-20', 'general_notes': 'stale'}], format='json'))
        except Exception as exc:
            errors.append(exc)
        finally:
            connection.close()
    with transaction.atomic():
        locked = DailyReport.objects.select_for_update().get(pk=report.pk)
        locked.status = ReportStatus.APPROVED
        locked.save(update_fields=['status'])
        worker = threading.Thread(target=batch)
        worker.start()
        assert worker_started.wait(5)
        entered_merge.wait(3)
    worker.join(timeout=20)
    assert not worker.is_alive(), 'batch failed to finish after approval committed'
    assert not errors, errors
    report.refresh_from_db()
    assert report.status == ReportStatus.APPROVED
    assert report.general_notes == 'original'
    assert replies[0].data['results'][0]['status'] == 'conflict'


def test_approved_report_discovered_in_ensure_is_not_edited(auth_client, project, user, monkeypatch):
    from field_reports.services import daily_report_aggregation as aggregation
    original_ensure = aggregation.ensure_daily_report_summary
    def concurrently_approved(project_id, report_date, user=None):
        report = DailyReport.objects.create(project_id=project_id, report_date=report_date,
            is_auto_summary=True, status=ReportStatus.APPROVED,
            created_by=user, updated_by=user, general_notes='original')
        DailyReportActivity.objects.create(report=report, is_derived=True,
            activity_description='protected derived row', shift='shift_1')
        return original_ensure(project_id, report_date, user=user)
    monkeypatch.setattr(aggregation, 'ensure_daily_report_summary', concurrently_approved)
    response = auth_client.post(f'/api/v1/projects/{project.id}/daily-reports/sync-batch/',
        [{'local_id': 'ensure-race', 'report_date': '2026-10-21', 'general_notes': 'stale'}], format='json')
    report = DailyReport.objects.get(project=project, report_date='2026-10-21')
    assert report.status == ReportStatus.APPROVED
    assert report.general_notes == 'original'
    assert report.activities.filter(activity_description='protected derived row').exists()
    assert response.data['results'][0]['status'] == 'conflict'


@pytest.mark.django_db(transaction=True)
def test_approved_report_wins_over_stale_direct_patch(project, user, monkeypatch):
    from field_reports.daily_report_views import DailyReportViewSet
    report = DailyReport.objects.create(project=project, report_date=date(2026, 10, 22),
        status=ReportStatus.DRAFT, is_auto_summary=True, created_by=user, updated_by=user,
        general_notes='original')
    read_stale = threading.Event()
    original_get = DailyReportViewSet.get_object
    def observed_get(view):
        instance = original_get(view)
        read_stale.set()
        return instance
    monkeypatch.setattr(DailyReportViewSet, 'get_object', observed_get)
    errors, replies = [], []
    def patch_report():
        connection.close()
        try:
            client = APIClient()
            client.force_authenticate(user=user)
            replies.append(client.patch(f'/api/v1/projects/{project.id}/daily-reports/{report.id}/',
                {'general_notes': 'stale'}, format='json'))
        except Exception as exc:
            errors.append(exc)
        finally:
            connection.close()
    with transaction.atomic():
        locked = DailyReport.objects.select_for_update().get(pk=report.pk)
        locked.status = ReportStatus.APPROVED
        locked.save(update_fields=['status'])
        worker = threading.Thread(target=patch_report)
        worker.start()
        read_stale.wait(3)
    worker.join(timeout=20)
    assert not worker.is_alive(), 'patch did not finish after approval committed'
    assert not errors, errors
    report.refresh_from_db()
    assert report.status == ReportStatus.APPROVED
    assert report.general_notes == 'original'
    assert replies[0].status_code in (400, 409)
