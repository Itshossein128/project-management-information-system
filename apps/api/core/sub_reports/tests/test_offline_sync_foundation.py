"""Canonical v2 authorization and receipt contract (feature 037, T006).

The v2 route is intentionally exercised over HTTP, including before it exists;
404 for an authorized request is a behavioral RED, not an import failure.
"""
from copy import deepcopy
from datetime import date
from uuid import uuid4

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from master_data.models import MemberStatus, ProjectMember, ProjectMemberPermissionOverride
from projects.models import Activity, Project, Stakeholder, WBS
from sub_reports.models import DisciplineSubReport, DisciplineSubReportActivity, SubReportStatus

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def enable_v2_sync(settings):
    """T035 keeps v2 off except in this isolated contract module."""
    settings.V2_OFFLINE_SYNC_ENABLED = True


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def endpoint(project):
    return f'/api/v1/projects/{project.id}/daily-reports/sync-operations/v2/'


def create_operation(day='2026-10-27'):
    return {
        'operation_id': str(uuid4()), 'local_report_id': str(uuid4()),
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': day, 'report_id': None},
        'action': 'create_report', 'target': {'kind': 'header'},
        'base_revision': None, 'depends_on': [], 'payload': {'form_code': 'T006'},
    }


def send(client, project, operation):
    return client.post(endpoint(project), {'contract_version': 2, 'operations': [operation]}, format='json')


def result(response, operation):
    assert response.status_code == 200, response.content
    assert response.data['contract_version'] == 2
    matches = [r for r in response.data['results'] if r['operation_id'] == operation['operation_id']]
    assert len(matches) == 1
    return matches[0]


def member(project, user, status=MemberStatus.ACTIVE, edit=False):
    membership = ProjectMember.objects.create(project=project, user=user, status=status)
    for permission in (['view_reports', 'edit_reports'] if edit else ['view_reports']):
        ProjectMemberPermissionOverride.objects.create(member=membership, permission_codename=permission, is_granted=True)
    return membership


def test_identical_replay_returns_same_receipt_and_changed_payload_is_rejected(project, user):
    client = client_for(user)
    operation = create_operation()
    first = send(client, project, operation)
    original = result(first, operation)
    assert original['outcome'] == 'success'
    assert first.data['synced_ids'] == [operation['operation_id']]
    replay = send(client, project, deepcopy(operation))
    assert result(replay, operation) == original
    assert replay.data['synced_ids'] == [operation['operation_id']]
    changed = deepcopy(operation)
    changed['payload']['form_code'] = 'ALTERED'
    rejected = send(client, project, changed)
    outcome = result(rejected, changed)
    assert outcome['outcome'] != 'success'
    assert outcome['error']['code'] == 'operation_id_reused'
    assert operation['operation_id'] not in rejected.data['synced_ids']
    reports = DisciplineSubReport.objects.filter(project=project, unit='buildings', report_date=date(2026, 10, 27))
    assert reports.count() == 1
    assert reports.get().form_code == 'T006'


def test_receipt_is_not_disclosed_after_membership_revoked(project, user):
    client = client_for(user)
    operation = create_operation()
    assert result(send(client, project, operation), operation)['outcome'] == 'success'
    ProjectMember.objects.filter(project=project, user=user).update(status=MemberStatus.INACTIVE)
    denied = send(client, project, operation)
    assert denied.status_code in (403, 404)
    assert operation['operation_id'] not in str(denied.data)


@pytest.mark.parametrize('state,edit', [(MemberStatus.ACTIVE, False), (MemberStatus.INACTIVE, True), (MemberStatus.SUSPENDED, True)])
def test_membership_and_edit_permission_checked_at_mutation(project, user, other_user, state, edit):
    allowed = create_operation('2026-10-26')
    assert result(send(client_for(user), project, allowed), allowed)['outcome'] == 'success'
    member(project, other_user, state, edit)
    operation = create_operation()
    response = send(client_for(other_user), project, operation)
    assert response.status_code in (403, 404)
    assert not DisciplineSubReport.objects.filter(project=project, report_date=date(2026, 10, 27)).exists()


def test_nonmember_denied_and_global_admin_policy_preserved(project, other_user):
    operation = create_operation()
    denied = send(client_for(other_user), project, operation)
    assert denied.status_code in (403, 404)
    admin = get_user_model().objects.create_user(username='sync-admin', mobile='+989120006001', full_name='Admin', is_staff=True, is_superuser=True)
    response = send(client_for(admin), project, operation)
    assert result(response, operation)['outcome'] == 'success'
    assert response.data['synced_ids'] == [operation['operation_id']]


def test_same_operation_id_is_scoped_by_actor_and_project(project, user, other_user):
    member(project, other_user, edit=True)
    other = Project.objects.create(project_code='T006-OTHER', project_name='Other', employer='Other', status='active')
    member(other, user, edit=True)
    operation = create_operation()
    first = result(send(client_for(user), project, operation), operation)
    assert first['outcome'] == 'success'
    # Different payload in a different scope must not be mistaken for the first receipt.
    another_actor = deepcopy(operation)
    another_actor['scope']['report_date'] = '2026-10-28'
    actor_result = result(send(client_for(other_user), project, another_actor), another_actor)
    assert actor_result['outcome'] == 'success'
    another_project = deepcopy(operation)
    another_project['scope']['report_date'] = '2026-10-29'
    project_result = result(send(client_for(user), other, another_project), another_project)
    assert project_result['outcome'] == 'success'
    assert DisciplineSubReport.objects.filter(project=project, report_date=date(2026, 10, 28)).exists()
    assert DisciplineSubReport.objects.filter(project=other, report_date=date(2026, 10, 29)).exists()


def test_cross_project_target_and_reference_are_refused(project, user):
    other = Project.objects.create(project_code='T006-FOREIGN', project_name='Foreign', employer='Other', status='active')
    foreign_report = DisciplineSubReport.objects.create(project=other, unit='buildings', discipline='civil', report_date=date(2026, 10, 27), status=SubReportStatus.DRAFT, created_by=user, form_code='UNCHANGED')
    node = WBS.add_root(project=other, wbs_code='1', wbs_name='Foreign root')
    foreign_activity = Activity.objects.create(project=other, wbs=node, activity_code='F1', activity_name='Foreign', status='in_progress', created_by=user)
    contractor = Stakeholder.objects.create(project=project, name='Local contractor', role='contractor', created_by=user)
    local_report = DisciplineSubReport.objects.create(project=project, unit='buildings', discipline='civil', report_date=date(2026, 10, 27), status=SubReportStatus.DRAFT, created_by=user)
    target = create_operation()
    target['scope']['report_id'] = str(foreign_report.id)
    target['action'] = 'update'
    target['payload'] = {'form_code': 'INJECTED'}
    target_response = send(client_for(user), project, target)
    target_result = result(target_response, target)
    assert target_result['outcome'] != 'success'
    assert target['operation_id'] not in target_response.data['synced_ids']
    foreign_report.refresh_from_db()
    assert foreign_report.form_code == 'UNCHANGED'
    ref = create_operation()
    ref['scope']['report_id'] = str(local_report.id)
    ref['action'] = 'create'
    ref['target'] = {'kind': 'activity', 'client_id': str(uuid4()), 'server_id': None}
    ref['payload'] = {'row_number': 1, 'shift': 'shift_1', 'activity_ref': str(foreign_activity.id), 'activity_description': 'Invalid reference', 'contractor_ref': str(contractor.id), 'crew_name': 'Crew A'}
    ref_response = send(client_for(user), project, ref)
    ref_result = result(ref_response, ref)
    assert ref_result['outcome'] == 'validation_error'
    assert ref_result['error']['code'] == 'activity_not_in_project_scope'
    assert ref['operation_id'] not in ref_response.data['synced_ids']
    assert not DisciplineSubReportActivity.objects.filter(sub_report=local_report).exists()
