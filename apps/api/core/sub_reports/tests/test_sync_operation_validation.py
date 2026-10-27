"""Nine valid operations stay committed when one row fails (feature 037, T046)."""
from uuid import uuid4

import pytest
from rest_framework.test import APIClient

from projects.models import Activity, Stakeholder, WBS
from sub_reports.models import DisciplineSubReportActivity, DisciplineSubReportLabor

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def enable_v2_sync(settings):
    settings.V2_OFFLINE_SYNC_ENABLED = True


def test_nine_successes_one_invalid_and_blocked_dependent(project, user):
    node = WBS.add_root(project=project, wbs_code='1', wbs_name='Root')
    activity = Activity.objects.create(
        project=project, wbs=node, activity_code='R1', activity_name='Retry', status='in_progress', created_by=user,
    )
    contractor = Stakeholder.objects.create(project=project, name='Retry Co', role='contractor', created_by=user)
    client = APIClient()
    client.force_authenticate(user)
    local_report_id = str(uuid4())
    header = {
        'operation_id': str(uuid4()), 'local_report_id': local_report_id,
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-27', 'report_id': None},
        'action': 'create_report', 'target': {'kind': 'header'}, 'base_revision': None, 'depends_on': [],
        'payload': {'form_code': 'RETRY'},
    }
    labors = []
    for index in range(8):
        labors.append({
            'operation_id': str(uuid4()), 'local_report_id': local_report_id,
            'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-27', 'report_id': None},
            'action': 'create', 'target': {'kind': 'labor', 'client_id': str(uuid4()), 'server_id': None},
            'base_revision': None, 'depends_on': [header['operation_id']],
            'payload': {'labor_category': 'direct', 'job_title': 'Mason', 'present_count': index + 1},
        })
    invalid = {
        'operation_id': str(uuid4()), 'local_report_id': local_report_id,
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-27', 'report_id': None},
        'action': 'create',
        'target': {'kind': 'activity', 'client_id': str(uuid4()), 'server_id': None},
        'base_revision': None, 'depends_on': [header['operation_id']],
        'payload': {
            'row_number': 1, 'shift': 'shift_1', 'activity_ref': str(activity.id),
            'activity_description': 'bad quantity', 'contractor_ref': str(contractor.id),
            'crew_name': 'Crew A', 'quantity': -1,
        },
    }
    blocked = {
        'operation_id': str(uuid4()), 'local_report_id': local_report_id,
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-27', 'report_id': None},
        'action': 'create', 'target': {'kind': 'labor', 'client_id': str(uuid4()), 'server_id': None},
        'base_revision': None, 'depends_on': [invalid['operation_id']],
        'payload': {'labor_category': 'direct', 'job_title': 'Mason', 'present_count': 9},
    }
    response = client.post(
        f'/api/v1/projects/{project.id}/daily-reports/sync-operations/v2/',
        {'contract_version': 2, 'operations': [header, *labors, invalid, blocked]},
        format='json',
    )
    assert response.status_code == 200, response.content
    by_id = {item['operation_id']: item for item in response.data['results']}
    assert len(response.data['synced_ids']) == 9
    invalid_result = by_id[invalid['operation_id']]
    assert invalid_result['outcome'] == 'validation_error'
    assert invalid_result['error']['code'] == 'quantity_must_be_positive'
    assert invalid_result['error']['field'] == 'quantity'
    assert invalid_result['error']['message']
    assert invalid_result['error']['message'] != invalid_result['error']['code']
    assert invalid_result['target']['client_id'] == invalid['target']['client_id']
    assert by_id[blocked['operation_id']]['error']['code'] == 'blocked_dependency'
    report_id = by_id[header['operation_id']]['target']['report_id']
    assert DisciplineSubReportLabor.objects.filter(sub_report_id=report_id, is_deleted=False).count() == 8
    assert not DisciplineSubReportActivity.objects.filter(sub_report_id=report_id).exists()

    corrected = {
        'operation_id': str(uuid4()), 'local_report_id': local_report_id,
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-27', 'report_id': report_id},
        'action': 'create',
        'target': {'kind': 'activity', 'client_id': invalid['target']['client_id'], 'server_id': None},
        'base_revision': None, 'depends_on': [invalid['operation_id']],
        'supersedes_operation_id': invalid['operation_id'],
        'payload': {**invalid['payload'], 'quantity': 2},
    }
    retried = client.post(
        f'/api/v1/projects/{project.id}/daily-reports/sync-operations/v2/',
        {'contract_version': 2, 'operations': [corrected]},
        format='json',
    )
    assert retried.data['results'][0]['outcome'] == 'success', retried.content
    assert DisciplineSubReportActivity.objects.filter(sub_report_id=report_id, is_deleted=False).count() == 1
    assert DisciplineSubReportLabor.objects.filter(sub_report_id=report_id, is_deleted=False).count() == 8
