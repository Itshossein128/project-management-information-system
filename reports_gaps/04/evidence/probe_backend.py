"""Audit probes: PASS confirms the observed defect, not compliance with SPEC-04.

Run from apps/api/core after copying this file temporarily into field_reports/tests/.
All writes use pytest-django's isolated test database and roll back per test.
"""
import pytest

from field_reports import services
from field_reports.models import DailyReport, DailyReportActivity, ReportStatus

pytestmark = pytest.mark.django_db


def test_batch_bypasses_derived_guard(auth_client, project, user):
    report = DailyReport.objects.create(
        project=project, report_date='2024-10-01', is_auto_summary=True,
        created_by=user, updated_by=user,
    )
    row = DailyReportActivity.objects.create(
        report=report, activity_description='derived source row', is_derived=True,
        quantity_measured=False,
    )
    base = f'/api/v1/projects/{project.id}/daily-reports'
    direct = auth_client.post(f'{base}/{report.id}/activities/', {
        'activity_description': 'manual', 'quantity_measured': False,
    }, format='json')
    batch = auth_client.post(f'{base}/sync-batch/', [{
        'local_id': 'probe-derived', 'report_date': '2024-10-01', 'activities': [],
    }], format='json')
    remaining = DailyReportActivity.objects.filter(pk=row.id).exists()
    print(f'DERIVED_GUARD direct={direct.status_code} batch={batch.status_code} '
          f'result={batch.data["results"][0]["status"]} original_row_exists={remaining}')
    assert direct.status_code == 400
    assert batch.data['results'][0]['status'] == 'merged'
    assert remaining is False


def test_header_validation_error_leaves_new_summary(auth_client, project):
    url = f'/api/v1/projects/{project.id}/daily-reports/sync-batch/'
    response = auth_client.post(url, [{
        'local_id': 'probe-invalid-header', 'report_date': '2024-10-02',
        'temp_min': 40, 'temp_max': 10,
    }], format='json')
    exists = DailyReport.objects.filter(project=project, report_date='2024-10-02').exists()
    print(f'INVALID_HEADER result={response.data["results"][0]["status"]} '
          f'new_summary_exists={exists}')
    assert response.data['results'][0]['status'] == 'error'
    assert exists is True


def test_approval_between_status_check_and_merge_is_overwritten(auth_client, project, user, monkeypatch):
    report = DailyReport.objects.create(
        project=project, report_date='2024-10-03', created_by=user, updated_by=user,
    )
    original = services._apply_header_merge

    def approve_then_merge(instance, payload, actor, local_id):
        # Deterministic interleaving: the persisted approval happens after the
        # earlier draft read. This is not a simultaneous two-connection test.
        DailyReport.objects.filter(pk=instance.pk).update(status=ReportStatus.APPROVED)
        assert DailyReport.objects.get(pk=instance.pk).status == ReportStatus.APPROVED
        return original(instance, payload, actor, local_id)

    monkeypatch.setattr(services, '_apply_header_merge', approve_then_merge)
    response = auth_client.post(
        f'/api/v1/projects/{project.id}/daily-reports/sync-batch/', [{
            'local_id': 'probe-race', 'report_date': '2024-10-03',
            'general_notes': 'offline edit after approval',
        }], format='json',
    )
    report.refresh_from_db()
    print(f'APPROVAL_INTERLEAVING result={response.data["results"][0]["status"]} '
          f'persisted_status={report.status} notes={report.general_notes}')
    assert response.data['results'][0]['status'] == 'merged'
    assert report.status == ReportStatus.DRAFT


def test_approved_report_found_inside_ensure_is_modified(auth_client, project, user, monkeypatch):
    from field_reports.services import daily_report_aggregation as aggregation
    original = aggregation.ensure_daily_report_summary

    def concurrently_created_approved_summary(project_id, report_date, user=None):
        DailyReport.objects.create(
            project_id=project_id, report_date=report_date,
            is_auto_summary=True, status=ReportStatus.APPROVED,
            created_by=user, updated_by=user,
        )
        return original(project_id, report_date, user=user)

    monkeypatch.setattr(aggregation, 'ensure_daily_report_summary', concurrently_created_approved_summary)
    response = auth_client.post(
        f'/api/v1/projects/{project.id}/daily-reports/sync-batch/', [{
            'local_id': 'probe-ensure-race', 'report_date': '2024-10-04',
            'general_notes': 'offline mutated approved summary',
        }], format='json',
    )
    report = DailyReport.objects.get(project=project, report_date='2024-10-04')
    print(f'ENSURE_INTERLEAVING result={response.data["results"][0]["status"]} '
          f'persisted_status={report.status} notes={report.general_notes}')
    assert report.status == ReportStatus.APPROVED
    assert report.general_notes == 'offline mutated approved summary'
    assert response.data['results'][0]['status'] == 'created'
