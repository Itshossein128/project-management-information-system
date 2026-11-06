"""Access-history reconstruction, scope, redaction, and durability."""

import pytest
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIClient

from authentication.services import LoginService, PasswordResetService
from master_data.models import ProjectMemberPermissionOverride, RoleAccessChange
from permissions.role_services import REDACTED, AuditUnavailable, record_access_change
from permissions.services import set_permission_override


def _client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.mark.django_db
def test_person_trail_distinguishes_role_and_exception_and_hides_it_from_viewer(
    auth_client, project, member, other_user, site_supervisor_role, user,
):
    assigned = auth_client.patch(
        f'/api/v1/projects/{project.id}/members/{member.user_id}/',
        {'role_ids': [str(site_supervisor_role.id)]},
        format='json',
    )
    assert assigned.status_code == status.HTTP_200_OK
    set_permission_override(member, 'edit_costs', False, actor=user)
    set_permission_override(member, 'edit_costs', None, actor=user)

    history = auth_client.get(f'/api/v1/projects/{project.id}/access-changes/')
    assert history.status_code == status.HTTP_200_OK
    origins = {row['action']: row['origin'] for row in history.data['results']}
    assert origins['roles_replaced'] == 'role'
    assert origins['override_set'] == 'exception'
    assert origins['override_cleared'] == 'exception'
    row = next(item for item in history.data['results'] if item['action'] == 'override_set')
    assert row['before']['codename'] == 'edit_costs'
    assert row['after']['granted'] is False
    assert row['subject_name'] == other_user.full_name

    denied = _client(other_user).get(f'/api/v1/projects/{project.id}/access-changes/')
    assert denied.status_code == status.HTTP_403_FORBIDDEN

    member.status = 'archived'
    member.save(update_fields=['status'])
    assert RoleAccessChange.objects.filter(subject_user=other_user, action='override_set').exists()


@pytest.mark.django_db
def test_global_role_is_not_attached_to_a_project_and_stays_hidden_from_a_project_manager(
    user, project,
):
    group, _created = Group.objects.get_or_create(name='admin')
    user.groups.add(group)
    created = _client(user).post(
        '/api/v1/roles/',
        {'role_name': 'hist_global', 'description': ''},
        format='json',
    )
    assert created.status_code == status.HTTP_201_CREATED
    row = RoleAccessChange.objects.get(role_id=created.data['id'], action='role_created')
    assert row.project_id is None

    user.groups.remove(group)
    project_rows = _client(user).get(f'/api/v1/projects/{project.id}/access-changes/')
    assert all(item['project_id'] == str(project.id) for item in project_rows.data['results'])
    assert _client(user).get('/api/v1/access-changes/').status_code == status.HTTP_403_FORBIDDEN
    user.groups.add(group)
    organization = _client(user).get('/api/v1/access-changes/')
    assert organization.status_code == status.HTTP_200_OK
    assert any(item['project_id'] is None for item in organization.data['results'])


@pytest.mark.django_db
def test_filters_and_pages_stay_inside_the_query(auth_client, project, user, other_user):
    record_access_change(
        actor=user, project=project, subject_user=other_user, role=None,
        action='member_status_changed', before={'status': 'active'}, after={'status': 'inactive'},
    )
    record_access_change(
        actor=other_user, project=project, subject_user=user, role=None,
        action='member_status_changed', before={'status': 'active'}, after={'status': 'suspended'},
    )
    filtered = auth_client.get(
        f'/api/v1/projects/{project.id}/access-changes/',
        {'subject': str(other_user.id), 'actor': str(user.id), 'page_size': 1, 'page': 1},
    )
    assert filtered.status_code == status.HTTP_200_OK
    assert filtered.data['count'] == 1
    assert filtered.data['page_size'] == 1
    assert filtered.data['results'][0]['subject_name'] == other_user.full_name


@pytest.mark.django_db
def test_nested_password_and_token_are_redacted_on_save_and_read(auth_client, project, user, other_user):
    record_access_change(
        actor=user,
        project=project,
        subject_user=other_user,
        role=None,
        action='account_status_changed',
        before={'nested': {'password': 'secret-value', 'permission': 'edit_costs'}},
        after={'refresh_token': 'abc', 'effect': 'inactive'},
    )
    stored = RoleAccessChange.objects.filter(action='account_status_changed').latest('created_at')
    assert stored.before['nested']['password'] == REDACTED
    assert stored.before['nested']['permission'] == 'edit_costs'
    assert stored.after['refresh_token'] == REDACTED
    assert stored.after['effect'] == 'inactive'
    shown = auth_client.get(f'/api/v1/projects/{project.id}/access-changes/')
    row = next(item for item in shown.data['results'] if item['action'] == 'account_status_changed')
    assert row['origin'] == 'account'
    assert 'secret-value' not in str(row)
    assert 'abc' not in str(row)


@pytest.mark.django_db
def test_failed_history_insert_does_not_keep_the_permission_change(member, user, monkeypatch):
    def explode(*_args, **_kwargs):
        raise RuntimeError('history store unavailable')

    monkeypatch.setattr('permissions.role_services.RoleAccessChange.objects.create', explode)
    with pytest.raises(AuditUnavailable):
        set_permission_override(member, 'view_costs', False, actor=user)
    assert not ProjectMemberPermissionOverride.objects.filter(
        member=member, permission_codename='view_costs',
    ).exists()


@pytest.mark.django_db
def test_login_recovery_events_separate_actor_and_target_and_skip_failed_login(user):
    LoginService().authenticate_and_issue_tokens(user.username, 'testpass123')
    assert RoleAccessChange.objects.filter(action='login_succeeded', subject_user=user, project=None).exists()
    with pytest.raises(Exception):
        LoginService().authenticate_and_issue_tokens(user.username, 'wrong-password')
    assert RoleAccessChange.objects.filter(action='login_succeeded', subject_user=user).count() == 1

    PasswordResetService().initiate_password_reset(user.mobile)
    recovery = RoleAccessChange.objects.get(action='recovery_requested', subject_user=user)
    assert recovery.actor_id is None
    assert 'token' not in str(recovery.before) + str(recovery.after)


@pytest.mark.django_db
def test_final_approval_and_sensitive_export_write_their_own_rows(
    auth_client, project, user, other_user, member,
):
    export = auth_client.post(
        f'/api/v1/projects/{project.id}/reports/weekly_progress/export/',
        {
            'filters': {
                'date_from': '2026-10-01',
                'date_to': '2026-10-07',
                'approved_only': True,
            },
            'format': 'json',
        },
        format='json',
    )
    assert export.status_code == status.HTTP_201_CREATED, export.data
    download = auth_client.get(
        f'/api/v1/projects/{project.id}/reports/exports/{export.data["id"]}/download/',
    )
    assert download.status_code == status.HTTP_200_OK
    assert RoleAccessChange.objects.filter(
        action='sensitive_export',
        project=project,
        actor=user,
    ).exists()

    definition = auth_client.post(
        f'/api/v1/projects/{project.id}/workflows/definitions/',
        {
            'name': 'History final approval',
            'workflow_type': 'budget_change',
            'stages': [
                {
                    'order': 1,
                    'name': 'Review',
                    'approver_user': str(other_user.id),
                    'approval_mode': 'any',
                    'on_reject': 'stop',
                },
            ],
        },
        format='json',
    )
    assert definition.status_code == status.HTTP_201_CREATED, definition.data
    activated = auth_client.post(
        f'/api/v1/projects/{project.id}/workflows/definitions/{definition.data["id"]}/activate/',
        {},
        format='json',
    )
    assert activated.status_code == status.HTTP_200_OK, activated.data
    started = auth_client.post(
        f'/api/v1/projects/{project.id}/workflows/instances/',
        {
            'definition': definition.data['id'],
            'subject_type': 'access_history_probe',
            'subject_id': '11111111-1111-1111-1111-111111111111',
            'comment': 'Submit',
        },
        format='json',
    )
    assert started.status_code == status.HTTP_201_CREATED, started.data
    approved = _client(other_user).post(
        f'/api/v1/projects/{project.id}/workflows/instances/{started.data["id"]}/approve/',
        {'comment': 'Approved'},
        format='json',
    )
    assert approved.status_code == status.HTTP_200_OK, approved.data
    assert RoleAccessChange.objects.filter(
        action='final_approval',
        project=project,
        actor=other_user,
    ).exists()
