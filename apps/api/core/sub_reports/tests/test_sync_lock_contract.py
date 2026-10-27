"""Stable lock outcomes for versioned sync (feature 037, T051)."""
from uuid import uuid4

import pytest
from rest_framework.test import APIClient

from sub_reports.models import DisciplineSubReport, DisciplineSubReportActivity, SubReportStatus

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def enable_v2_sync(settings):
    settings.V2_OFFLINE_SYNC_ENABLED = True


def send(client, project, operation):
    return client.post(
        f'/api/v1/projects/{project.id}/daily-reports/sync-operations/v2/',
        {'contract_version': 2, 'operations': [operation]},
        format='json',
    )


def update_op(report, description='changed'):
    return {
        'operation_id': str(uuid4()), 'local_report_id': str(uuid4()),
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': str(report.report_date), 'report_id': str(report.id)},
        'action': 'update', 'target': {'kind': 'header'}, 'base_revision': None, 'depends_on': [],
        'payload': {'form_code': description},
    }


def test_approved_and_non_current_targets_conflict_without_changes(project, user):
    client = APIClient()
    client.force_authenticate(user)
    approved = DisciplineSubReport.objects.create(
        project=project, unit='buildings', discipline='civil', report_date='2026-10-22',
        status=SubReportStatus.APPROVED, is_current=True, created_by=user, form_code='KEEP',
        lineage_id=uuid4(), version_number=1,
    )
    response = send(client, project, update_op(approved, 'INJECTED'))
    assert response.status_code == 200, response.content
    result = response.data['results'][0]
    assert result['outcome'] == 'conflict'
    assert result['status'] == 'sync_conflict'
    assert result['error']['code'] == 'conflict_report_approved'
    approved.refresh_from_db()
    assert approved.form_code == 'KEEP'
    assert approved.status == SubReportStatus.APPROVED

    stale = DisciplineSubReport.objects.create(
        project=project, unit='buildings', discipline='civil', report_date='2026-10-23',
        status=SubReportStatus.DRAFT, is_current=False, created_by=user, form_code='OLD',
        lineage_id=uuid4(), version_number=1,
    )
    stale_response = send(client, project, update_op(stale, 'NEWER'))
    assert stale_response.data['results'][0]['error']['code'] == 'non_current_report'
    stale.refresh_from_db()
    assert stale.form_code == 'OLD'


def test_sync_does_not_approve_and_denied_user_cannot_write(project, user, other_user):
    client = APIClient()
    client.force_authenticate(user)
    report = DisciplineSubReport.objects.create(
        project=project, unit='buildings', discipline='civil', report_date='2026-10-24',
        status=SubReportStatus.DRAFT, is_current=True, created_by=user, form_code='DRAFT',
        lineage_id=uuid4(), version_number=1,
    )
    operation = update_op(report)
    operation['action'] = 'approve'
    operation['target'] = {'kind': 'workflow'}
    response = send(client, project, operation)
    assert response.data['results'][0]['error']['code'] == 'unsupported_target'
    report.refresh_from_db()
    assert report.status == SubReportStatus.DRAFT

    other = APIClient()
    other.force_authenticate(other_user)
    denied = send(other, project, update_op(report, 'NOPE'))
    assert denied.status_code == 403
    report.refresh_from_db()
    assert report.form_code == 'DRAFT'
    assert not DisciplineSubReportActivity.objects.filter(sub_report=report).exists()
