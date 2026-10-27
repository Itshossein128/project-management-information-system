"""Dependency order and replay for v2 operations (feature 037, T033)."""
from uuid import uuid4

import pytest
from rest_framework.test import APIClient

from projects.models import Activity, Stakeholder, WBS
from sub_reports.models import DisciplineSubReportActivity

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def enable_v2_sync(settings):
    settings.V2_OFFLINE_SYNC_ENABLED = True


def endpoint(project):
    return f'/api/v1/projects/{project.id}/daily-reports/sync-operations/v2/'


def post(client, project, operations):
    return client.post(endpoint(project), {'contract_version': 2, 'operations': operations}, format='json')


def test_create_edit_delete_chain_replays_without_duplicate_rows(project, user):
    node = WBS.add_root(project=project, wbs_code='1', wbs_name='Root')
    activity = Activity.objects.create(project=project, wbs=node, activity_code='A1', activity_name='Pour', status='in_progress', created_by=user)
    contractor = Stakeholder.objects.create(project=project, name='Crew Co', role='contractor', created_by=user)
    client = APIClient()
    client.force_authenticate(user)
    local_report_id = str(uuid4())
    client_row = str(uuid4())
    create_report = {
        'operation_id': str(uuid4()), 'local_report_id': local_report_id,
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-27', 'report_id': None},
        'action': 'create_report', 'target': {'kind': 'header'}, 'base_revision': None, 'depends_on': [],
        'payload': {'form_code': 'CHAIN'},
    }
    create_row = {
        'operation_id': str(uuid4()), 'local_report_id': local_report_id,
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-27', 'report_id': None},
        'action': 'create', 'target': {'kind': 'activity', 'client_id': client_row, 'server_id': None},
        'base_revision': None, 'depends_on': [create_report['operation_id']],
        'payload': {
            'row_number': 1, 'shift': 'shift_1', 'activity_ref': str(activity.id),
            'activity_description': 'first pour', 'contractor_ref': str(contractor.id), 'crew_name': 'Crew A',
        },
    }
    created = post(client, project, [create_row, create_report])
    assert created.status_code == 200, created.content
    by_id = {item['operation_id']: item for item in created.data['results']}
    assert by_id[create_report['operation_id']]['outcome'] == 'success'
    assert by_id[create_row['operation_id']]['outcome'] == 'success'
    assert by_id[create_row['operation_id']]['target']['client_id'] == client_row
    server_id = by_id[create_row['operation_id']]['target']['server_id']
    revision = by_id[create_row['operation_id']]['target']['revision']
    report_id = by_id[create_report['operation_id']]['target']['report_id']

    update = {
        'operation_id': str(uuid4()), 'local_report_id': local_report_id,
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-27', 'report_id': report_id},
        'action': 'update', 'target': {'kind': 'activity', 'client_id': client_row, 'server_id': server_id},
        'base_revision': revision, 'depends_on': [],
        'payload': {'activity_description': 'revised pour'},
    }
    updated = post(client, project, [update])
    assert updated.data['results'][0]['outcome'] == 'success'
    next_revision = updated.data['results'][0]['target']['revision']

    delete = {
        'operation_id': str(uuid4()), 'local_report_id': local_report_id,
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-27', 'report_id': report_id},
        'action': 'delete', 'target': {'kind': 'activity', 'client_id': client_row, 'server_id': server_id},
        'base_revision': next_revision, 'depends_on': [], 'payload': {},
    }
    deleted = post(client, project, [delete])
    assert deleted.data['results'][0]['outcome'] == 'success'
    row = DisciplineSubReportActivity.objects.get(pk=server_id)
    assert row.is_deleted is True
    assert DisciplineSubReportActivity.objects.filter(sub_report_id=report_id).count() == 1

    replay = post(client, project, [create_row])
    assert replay.data['results'][0] == by_id[create_row['operation_id']]
    assert DisciplineSubReportActivity.objects.filter(sub_report_id=report_id).count() == 1

    altered = dict(create_row)
    altered['payload'] = {**create_row['payload'], 'activity_description': 'changed identity'}
    rejected = post(client, project, [altered])
    assert rejected.data['results'][0]['error']['code'] == 'operation_id_reused'


def test_missing_and_cyclic_dependencies_do_not_mutate(project, user):
    client = APIClient()
    client.force_authenticate(user)
    missing = {
        'operation_id': str(uuid4()), 'local_report_id': str(uuid4()),
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-28', 'report_id': None},
        'action': 'create_report', 'target': {'kind': 'header'}, 'base_revision': None,
        'depends_on': [str(uuid4())], 'payload': {'form_code': 'BLOCKED'},
    }
    left = {
        'operation_id': str(uuid4()), 'local_report_id': str(uuid4()),
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-29', 'report_id': None},
        'action': 'create_report', 'target': {'kind': 'header'}, 'base_revision': None,
        'depends_on': [], 'payload': {'form_code': 'LEFT'},
    }
    right = {
        'operation_id': str(uuid4()), 'local_report_id': str(uuid4()),
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-30', 'report_id': None},
        'action': 'create_report', 'target': {'kind': 'header'}, 'base_revision': None,
        'depends_on': [], 'payload': {'form_code': 'RIGHT'},
    }
    left['depends_on'] = [right['operation_id']]
    right['depends_on'] = [left['operation_id']]
    response = post(client, project, [missing, left, right])
    assert response.status_code == 200
    assert response.data['synced_ids'] == []
    assert {item['error']['code'] for item in response.data['results']} == {'blocked_dependency'}
    from sub_reports.models import DisciplineSubReport
    assert not DisciplineSubReport.objects.filter(project=project, form_code__in=['BLOCKED', 'LEFT', 'RIGHT']).exists()


def test_offline_create_then_edit_in_one_batch_resolves_client_row(project, user):
    client = APIClient()
    client.force_authenticate(user)
    local_id, row_id = str(uuid4()), str(uuid4())
    scope = {'kind': 'unit', 'unit': 'electrical', 'report_date': '2026-10-27', 'report_id': None}
    header = {'operation_id': str(uuid4()), 'local_report_id': local_id, 'scope': scope,
              'action': 'create_report', 'target': {'kind': 'header'}, 'base_revision': None,
              'depends_on': [], 'payload': {'form_code': 'CHAIN'}}
    create = {'operation_id': str(uuid4()), 'local_report_id': local_id, 'scope': scope,
              'action': 'create', 'target': {'kind': 'general_activity', 'client_id': row_id, 'server_id': None},
              'base_revision': None, 'depends_on': [header['operation_id']],
              'payload': {'row_number': 1, 'activity_description': 'first'}}
    update = {'operation_id': str(uuid4()), 'local_report_id': local_id, 'scope': scope,
              'action': 'update', 'target': {'kind': 'general_activity', 'client_id': row_id, 'server_id': None},
              'base_revision': None, 'depends_on': [header['operation_id'], create['operation_id']],
              'payload': {'activity_description': 'edited offline'}}
    response = post(client, project, [header, create, update])
    assert response.status_code == 200
    outcomes = {item['operation_id']: item for item in response.data['results']}
    assert outcomes[header['operation_id']]['outcome'] == 'success'
    assert outcomes[create['operation_id']]['outcome'] == 'success'
    assert outcomes[update['operation_id']]['outcome'] == 'success', outcomes[update['operation_id']]
    assert outcomes[update['operation_id']]['target']['server_id'] == outcomes[create['operation_id']]['target']['server_id']
    from sub_reports.models import DisciplineSubReportGeneralActivity
    row = DisciplineSubReportGeneralActivity.objects.get(pk=outcomes[create['operation_id']]['target']['server_id'])
    assert row.activity_description == 'edited offline'
    replay = post(client, project, [header, create, update])
    assert replay.status_code == 200
    assert replay.data['results'] == response.data['results']
    assert DisciplineSubReportGeneralActivity.objects.filter(sub_report=row.sub_report).count() == 1
