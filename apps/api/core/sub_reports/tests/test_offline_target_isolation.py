"""Targeted offline edits must not replace unrelated rows (feature 037, T039)."""
from uuid import uuid4

import pytest
from rest_framework.test import APIClient

from projects.models import Activity, Stakeholder, WBS
from sub_reports.models import DisciplineSubReport, DisciplineSubReportActivity

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def enable_v2_sync(settings):
    settings.V2_OFFLINE_SYNC_ENABLED = True


def endpoint(project):
    return f'/api/v1/projects/{project.id}/daily-reports/sync-operations/v2/'


def post(client, project, operations):
    return client.post(endpoint(project), {'contract_version': 2, 'operations': operations}, format='json')


def header(local_report_id, day='2026-10-27'):
    return {
        'operation_id': str(uuid4()), 'local_report_id': local_report_id,
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': day, 'report_id': None},
        'action': 'create_report', 'target': {'kind': 'header'}, 'base_revision': None, 'depends_on': [],
        'payload': {'form_code': 'ISO'},
    }


def activity_op(local_report_id, activity, contractor, description, depends_on, report_id=None):
    return {
        'operation_id': str(uuid4()), 'local_report_id': local_report_id,
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-27', 'report_id': report_id},
        'action': 'create',
        'target': {'kind': 'activity', 'client_id': str(uuid4()), 'server_id': None},
        'base_revision': None, 'depends_on': depends_on,
        'payload': {
            'row_number': 1, 'shift': 'shift_1', 'activity_ref': str(activity.id),
            'activity_description': description, 'contractor_ref': str(contractor.id), 'crew_name': 'Crew A',
        },
    }


@pytest.fixture
def activity_refs(project, user):
    node = WBS.add_root(project=project, wbs_code='1', wbs_name='Root')
    activity = Activity.objects.create(
        project=project, wbs=node, activity_code='ISO', activity_name='Isolation', status='in_progress', created_by=user,
    )
    contractor = Stakeholder.objects.create(project=project, name='Iso Co', role='contractor', created_by=user)
    return activity, contractor


def test_explicit_update_keeps_other_rows_and_ids(project, user, other_user, activity_refs):
    activity, contractor = activity_refs
    client = APIClient()
    client.force_authenticate(user)
    local_report_id = str(uuid4())
    created_header = header(local_report_id)
    first = activity_op(local_report_id, activity, contractor, 'mine', [created_header['operation_id']])
    second = activity_op(local_report_id, activity, contractor, 'theirs', [created_header['operation_id']])
    second['payload']['row_number'] = 2
    response = post(client, project, [created_header, first, second])
    assert response.status_code == 200, response.content
    by_id = {item['operation_id']: item for item in response.data['results']}
    report_id = by_id[created_header['operation_id']]['target']['report_id']
    mine = by_id[first['operation_id']]['target']
    theirs_id = by_id[second['operation_id']]['target']['server_id']

    DisciplineSubReportActivity.objects.create(
        sub_report_id=report_id, row_number=3, shift='shift_1', crew_name='Other',
        activity_description='added by someone else', activity_ref=activity, contractor_ref=contractor,
    )
    update = {
        'operation_id': str(uuid4()), 'local_report_id': local_report_id,
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-27', 'report_id': report_id},
        'action': 'update',
        'target': {'kind': 'activity', 'client_id': mine['client_id'], 'server_id': mine['server_id']},
        'base_revision': mine['revision'], 'depends_on': [],
        'payload': {'activity_description': 'mine revised'},
    }
    updated = post(client, project, [update])
    assert updated.data['results'][0]['outcome'] == 'success'
    assert updated.data['results'][0]['target']['server_id'] == mine['server_id']
    rows = DisciplineSubReportActivity.objects.filter(sub_report_id=report_id, is_deleted=False)
    assert rows.count() == 3
    assert rows.get(pk=mine['server_id']).activity_description == 'mine revised'
    assert rows.get(pk=theirs_id).activity_description == 'theirs'
    assert rows.get(activity_description='added by someone else').crew_name == 'Other'


def test_stale_revision_does_not_change_the_row(project, user, activity_refs):
    activity, contractor = activity_refs
    client = APIClient()
    client.force_authenticate(user)
    local_report_id = str(uuid4())
    created_header = header(local_report_id)
    created = activity_op(local_report_id, activity, contractor, 'stable', [created_header['operation_id']])
    response = post(client, project, [created_header, created])
    by_id = {item['operation_id']: item for item in response.data['results']}
    target = by_id[created['operation_id']]['target']
    stale = {
        'operation_id': str(uuid4()), 'local_report_id': local_report_id,
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-27', 'report_id': target['report_id']},
        'action': 'update',
        'target': {'kind': 'activity', 'client_id': target['client_id'], 'server_id': target['server_id']},
        'base_revision': str(uuid4()), 'depends_on': [],
        'payload': {'activity_description': 'should not land'},
    }
    rejected = post(client, project, [stale])
    assert rejected.data['results'][0]['outcome'] == 'conflict'
    assert rejected.data['results'][0]['error']['code'] == 'stale_target_revision'
    assert stale['operation_id'] not in rejected.data['synced_ids']
    row = DisciplineSubReportActivity.objects.get(pk=target['server_id'])
    assert row.activity_description == 'stable'


def test_empty_snapshot_and_foreign_project_do_not_mutate(project, user, activity_refs):
    activity, contractor = activity_refs
    client = APIClient()
    client.force_authenticate(user)
    local_report_id = str(uuid4())
    created_header = header(local_report_id)
    created = activity_op(local_report_id, activity, contractor, 'kept', [created_header['operation_id']])
    response = post(client, project, [created_header, created])
    report_id = next(item['target']['report_id'] for item in response.data['results'] if item['operation_id'] == created_header['operation_id'])
    empty = {
        'operation_id': str(uuid4()), 'local_report_id': local_report_id,
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-27', 'report_id': report_id},
        'action': 'create', 'target': {'kind': 'activity', 'client_id': str(uuid4()), 'server_id': None},
        'base_revision': None, 'depends_on': [], 'payload': [],
    }
    rejected = post(client, project, [empty])
    assert rejected.data['results'][0]['error']['code'] == 'snapshot_replacement_forbidden'
    assert DisciplineSubReportActivity.objects.filter(sub_report_id=report_id, is_deleted=False).count() == 1

    from projects.models import Project
    other = Project.objects.create(project_code='ISO-OTHER', project_name='Other', employer='Other', status='active')
    foreign = DisciplineSubReport.objects.create(
        project=other, unit='buildings', discipline='civil', report_date='2026-10-27', created_by=user, form_code='FOREIGN',
    )
    foreign_update = {
        'operation_id': str(uuid4()), 'local_report_id': str(uuid4()),
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-27', 'report_id': str(foreign.id)},
        'action': 'update', 'target': {'kind': 'header'}, 'base_revision': None, 'depends_on': [],
        'payload': {'form_code': 'INJECTED'},
    }
    isolated = post(client, project, [foreign_update])
    assert isolated.data['results'][0]['outcome'] != 'success'
    foreign.refresh_from_db()
    assert foreign.form_code == 'FOREIGN'
