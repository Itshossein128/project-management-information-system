"""Existing online writers must advance the same revisions used by offline sync."""
from datetime import date

import pytest

from sub_reports.models import DisciplineSubReport, DisciplineSubReportActivity, SubReportStatus

pytestmark = pytest.mark.django_db


@pytest.fixture
def report(project, user):
    return DisciplineSubReport.objects.create(project=project, unit='buildings', discipline='civil',
        report_date=date(2026, 10, 20), status=SubReportStatus.DRAFT, created_by=user)


def base(project, report):
    return f'/api/v1/projects/{project.id}/units/buildings/daily-reports/{report.id}/'


def test_header_patch_changes_revision(auth_client, project, report):
    previous = report.sync_revision
    response = auth_client.patch(base(project, report), {'form_code': 'updated'}, format='json')
    assert response.status_code == 200, response.data
    report.refresh_from_db()
    assert report.form_code == 'updated'
    assert report.sync_revision != previous


def test_activity_patch_changes_only_target_revision(auth_client, project, report):
    target = DisciplineSubReportActivity.objects.create(sub_report=report, row_number=1,
        shift='shift_1', activity_description='first')
    other = DisciplineSubReportActivity.objects.create(sub_report=report, row_number=2,
        shift='shift_1', activity_description='other')
    before, other_before = target.sync_revision, other.sync_revision
    response = auth_client.patch(base(project, report) + f'activities/{target.id}/', {'notes': 'edited'}, format='json')
    assert response.status_code == 200, response.data
    target.refresh_from_db(); other.refresh_from_db()
    assert target.notes == 'edited'
    assert target.sync_revision != before
    assert other.sync_revision == other_before


def test_activity_delete_leaves_changed_tombstone_revision(auth_client, project, report):
    target = DisciplineSubReportActivity.objects.create(sub_report=report, row_number=1,
        shift='shift_1', activity_description='first')
    before = target.sync_revision
    response = auth_client.delete(base(project, report) + f'activities/{target.id}/')
    assert response.status_code == 204, response.data
    target.refresh_from_db()
    assert target.is_deleted is True
    assert target.sync_revision != before


def test_submit_changes_header_revision(auth_client, project, report):
    before = report.sync_revision
    response = auth_client.post(base(project, report) + 'submit/')
    assert response.status_code == 200, response.data
    report.refresh_from_db()
    assert report.status == SubReportStatus.SUBMITTED
    assert report.sync_revision != before
