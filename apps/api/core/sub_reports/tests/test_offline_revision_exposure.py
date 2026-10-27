"""Clients need server-issued per-target revisions to detect stale edits."""
from datetime import date
from uuid import uuid4

import pytest

from sub_reports.models import DisciplineSubReport, DisciplineSubReportActivity, SubReportStatus

pytestmark = pytest.mark.django_db


def test_current_report_and_activity_expose_server_revision(auth_client, project, user):
    report = DisciplineSubReport.objects.create(project=project, unit='buildings', discipline='civil',
        report_date=date(2026, 10, 20), status=SubReportStatus.DRAFT, created_by=user)
    row = DisciplineSubReportActivity.objects.create(sub_report=report, row_number=1,
        shift='shift_1', activity_description='work')
    base = f'/api/v1/projects/{project.id}/units/buildings/daily-reports/'
    response = auth_client.get(base + 'current/', {'date': '2026-10-20'})
    assert response.status_code == 200
    assert response.data.get('sync_revision') == str(report.sync_revision)
    rows = auth_client.get(base + f'{report.id}/activities/')
    assert rows.status_code == 200
    assert rows.data[0].get('sync_revision') == str(row.sync_revision)


def test_client_cannot_override_server_activity_revision(auth_client, project, user):
    report = DisciplineSubReport.objects.create(project=project, unit='buildings', discipline='civil',
        report_date=date(2026, 10, 21), status=SubReportStatus.DRAFT, created_by=user)
    row = DisciplineSubReportActivity.objects.create(sub_report=report, row_number=1,
        shift='shift_1', activity_description='work')
    forged = str(uuid4())
    response = auth_client.patch(
        f'/api/v1/projects/{project.id}/units/buildings/daily-reports/{report.id}/activities/{row.id}/',
        {'notes': 'new', 'sync_revision': forged}, format='json',
    )
    assert response.status_code == 200
    row.refresh_from_db()
    assert str(row.sync_revision) != forged
    assert response.data.get('sync_revision') == str(row.sync_revision)
