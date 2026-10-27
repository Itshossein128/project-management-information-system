"""Official correction transfer stays idempotent (feature 037, T056)."""
from uuid import uuid4

import pytest
from rest_framework.test import APIClient

from sub_reports.models import DisciplineSubReport, SubReportStatus

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def enable_v2_sync(settings):
    settings.V2_OFFLINE_SYNC_ENABLED = True


def transfer(report, reason='fix the approved day'):
    return {
        'operation_id': str(uuid4()), 'local_report_id': str(uuid4()),
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': str(report.report_date), 'report_id': str(report.id)},
        'action': 'correct_transfer', 'target': {'kind': 'header'}, 'base_revision': None, 'depends_on': [],
        'payload': {'reason': reason},
    }


def test_correction_transfer_replays_without_a_second_version(project, user, other_user):
    client = APIClient()
    client.force_authenticate(user)
    approved = DisciplineSubReport.objects.create(
        project=project, unit='buildings', discipline='civil', report_date='2026-10-25',
        status=SubReportStatus.APPROVED, is_current=True, created_by=user, form_code='APPROVED',
        lineage_id=uuid4(), version_number=1,
    )
    direct = transfer(approved)
    direct['action'] = 'update'
    direct['payload'] = {'form_code': 'PATCHED'}
    blocked = client.post(
        f'/api/v1/projects/{project.id}/daily-reports/sync-operations/v2/',
        {'contract_version': 2, 'operations': [direct]}, format='json',
    )
    assert blocked.data['results'][0]['error']['code'] == 'conflict_report_approved'
    approved.refresh_from_db()
    assert approved.form_code == 'APPROVED'
    assert approved.is_current is True

    operation = transfer(approved)
    first = client.post(
        f'/api/v1/projects/{project.id}/daily-reports/sync-operations/v2/',
        {'contract_version': 2, 'operations': [operation]}, format='json',
    )
    assert first.status_code == 200, first.content
    assert first.data['results'][0]['outcome'] == 'success', first.content
    destination = first.data['results'][0]['target']['report_id']
    assert destination != str(approved.id)
    assert first.data['results'][0]['target']['supersedes'] == str(approved.id)
    replay = client.post(
        f'/api/v1/projects/{project.id}/daily-reports/sync-operations/v2/',
        {'contract_version': 2, 'operations': [operation]}, format='json',
    )
    assert replay.data['results'][0]['target']['report_id'] == destination
    assert DisciplineSubReport.objects.filter(lineage_id=approved.lineage_id).count() == 2

    other = APIClient()
    other.force_authenticate(other_user)
    denied = other.post(
        f'/api/v1/projects/{project.id}/daily-reports/sync-operations/v2/',
        {'contract_version': 2, 'operations': [transfer(approved, 'denied')]}, format='json',
    )
    assert denied.status_code == 403
    assert DisciplineSubReport.objects.filter(lineage_id=approved.lineage_id).count() == 2
