"""Team selection, invitation, conflicts, and membership status."""

from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from authentication.services import _hash_token
from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, RoleAccessChange
from permissions.services import set_permission_override
from projects.services import create_project_with_creator

User = get_user_model()


def _client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def _person(username, mobile):
    return User.objects.create_user(
        username=username,
        mobile=mobile,
        full_name=username,
        password='testpass123',
        email=f'{username}@example.com',
    )


@pytest.mark.django_db
def test_same_person_joins_two_projects_without_a_second_account(user, other_user, project, viewer_role):
    project_b = create_project_with_creator(
        creator=other_user,
        project_code='PRJ-TEAM-B',
        project_name='Project B',
        employer='Employer Co',
        start_date='2024-03-01',
    )
    before = User.objects.count()
    response = _client(other_user).post(
        f'/api/v1/projects/{project_b.id}/members/',
        {'user_id': str(user.id), 'role_ids': [str(viewer_role.id)]},
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['user_id'] == str(user.id)
    assert User.objects.count() == before
    assert ProjectMember.objects.filter(project=project, user=user).count() == 1
    assert ProjectMember.objects.filter(project=project_b, user=user).count() == 1


@pytest.mark.django_db
def test_viewer_non_member_inactive_and_deny_cannot_add(user, other_user, project, member, viewer_role):
    outsider = _person('outsider', '+989120000201')
    target = _person('target', '+989120000202')
    payload = {'user_id': str(target.id), 'role_ids': [str(viewer_role.id)]}
    url = f'/api/v1/projects/{project.id}/members/'
    assert _client(other_user).post(url, payload, format='json').status_code == status.HTTP_403_FORBIDDEN
    assert _client(outsider).post(url, payload, format='json').status_code == status.HTTP_403_FORBIDDEN
    creator = ProjectMember.objects.get(project=project, user=user)
    creator.status = MemberStatus.INACTIVE
    creator.save(update_fields=['status'])
    assert _client(user).post(url, payload, format='json').status_code == status.HTTP_403_FORBIDDEN
    creator.status = MemberStatus.ACTIVE
    creator.save(update_fields=['status'])
    set_permission_override(creator, 'manage_members', False, actor=user)
    assert _client(user).post(url, payload, format='json').status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_invitation_connect_cancel_and_accept(user, project, viewer_role):
    created = _client(user).post(
        f'/api/v1/projects/{project.id}/members/',
        {'email': 'invitee@example.com', 'mobile': '+989120000301', 'role_ids': [str(viewer_role.id)]},
        format='json',
    )
    assert created.status_code == status.HTTP_201_CREATED
    assert created.data['user_id'] is None
    assert created.data['delivery_status'] in {'not_configured', 'not_sent'}
    assert 'token' not in created.data
    member_id = created.data['id']
    assert RoleAccessChange.objects.filter(action='invitation_created', project=project).exists()
    listed = _client(user).get(f'/api/v1/projects/{project.id}/members/')
    row = next(item for item in listed.data if item['id'] == member_id)
    assert row['last_login'] is None

    invitee = _person('invitee', '+989120000301')
    invitee.email = 'invitee@example.com'
    invitee.save(update_fields=['email'])
    raw = 'accepted-token-value-with-enough-length'
    membership = ProjectMember.objects.get(pk=member_id)
    membership.invite_token_hash = _hash_token(raw)
    membership.invite_expires_at = timezone.now() + timedelta(days=7)
    membership.save(update_fields=['invite_token_hash', 'invite_expires_at'])

    stranger = _person('stranger', '+989120000399')
    mismatched = _client(stranger).post('/api/auth/invitations/accept/', {'token': raw}, format='json')
    assert mismatched.status_code == status.HTTP_400_BAD_REQUEST
    assert mismatched.data['error']['code'] == 'invitation_invalid'

    accepted = _client(invitee).post('/api/auth/invitations/accept/', {'token': raw}, format='json')
    assert accepted.status_code == status.HTTP_200_OK
    assert accepted.data['user_id'] == str(invitee.id)
    assert accepted.data['status'] == MemberStatus.ACTIVE
    again = _client(invitee).post('/api/auth/invitations/accept/', {'token': raw}, format='json')
    assert again.status_code == status.HTTP_400_BAD_REQUEST

    cancelled = _client(user).post(
        f'/api/v1/projects/{project.id}/members/',
        {'email': 'other-invite@example.com', 'role_ids': [str(viewer_role.id)]},
        format='json',
    )
    cancel = _client(user).post(
        f'/api/v1/projects/{project.id}/members/invitations/{cancelled.data["id"]}/cancel/',
        format='json',
    )
    assert cancel.status_code == status.HTTP_200_OK
    stale = ProjectMember.objects.get(pk=cancelled.data['id'])
    stale.invite_token_hash = _hash_token('cancelled-token-value-with-length')
    stale.invite_cancelled_at = None
    stale.save(update_fields=['invite_token_hash', 'invite_cancelled_at'])
    stale.invite_cancelled_at = timezone.now()
    stale.save(update_fields=['invite_cancelled_at'])
    refused = _client(invitee).post(
        '/api/auth/invitations/accept/',
        {'token': 'cancelled-token-value-with-length'},
        format='json',
    )
    assert refused.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_repeated_and_conflicting_add_leaves_one_membership(user, other_user, project, viewer_role):
    url = f'/api/v1/projects/{project.id}/members/'
    payload = {'user_id': str(other_user.id), 'role_ids': [str(viewer_role.id)]}
    first = _client(user).post(url, payload, format='json')
    assert first.status_code == status.HTTP_201_CREATED
    second = _client(user).post(url, payload, format='json')
    assert second.status_code == status.HTTP_409_CONFLICT
    assert second.data['error']['code'] == 'already_member'
    assert ProjectMember.objects.filter(project=project, user=other_user).count() == 1
    role_count = ProjectMemberRole.objects.filter(member__project=project, member__user=other_user).count()
    fresh = _person('race-user', '+989120000250')
    with patch('projects.services.ProjectMember.objects.create', side_effect=IntegrityError):
        conflict = _client(user).post(
            url,
            {'user_id': str(fresh.id), 'role_ids': [str(viewer_role.id)]},
            format='json',
        )
    assert conflict.status_code == status.HTTP_409_CONFLICT
    assert ProjectMember.objects.filter(project=project, user=fresh).count() == 0
    assert ProjectMemberRole.objects.filter(member__user=fresh).count() == 0
    assert ProjectMemberRole.objects.filter(member__project=project, member__user=other_user).count() == role_count


@pytest.mark.django_db
def test_connect_refuses_a_person_who_already_belongs(user, other_user, project, member, viewer_role):
    created = _client(user).post(
        f'/api/v1/projects/{project.id}/members/',
        {'email': 'dup@example.com', 'role_ids': [str(viewer_role.id)]},
        format='json',
    )
    response = _client(user).post(
        f'/api/v1/projects/{project.id}/members/invitations/{created.data["id"]}/connect/',
        {'user_id': str(other_user.id)},
        format='json',
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    invite = ProjectMember.objects.get(pk=created.data['id'])
    assert invite.user_id is None
    assert ProjectMember.objects.filter(project=project, user=other_user).count() == 1


@pytest.mark.django_db
def test_project_status_does_not_change_the_other_project_or_account(user, other_user, project, activity):
    project_b = create_project_with_creator(
        creator=other_user,
        project_code='PRJ-TEAM-C',
        project_name='Project C',
        employer='Employer Co',
        start_date='2024-04-01',
    )
    added = _client(other_user).post(
        f'/api/v1/projects/{project_b.id}/members/',
        {'user_id': str(user.id), 'role_ids': [str(ProjectMemberRole.objects.filter(member__project=project, member__user=user).first().role_id)]},
        format='json',
    )
    assert added.status_code == status.HTTP_201_CREATED
    membership = ProjectMember.objects.get(project=project, user=user)
    joined = membership.joined_at
    response = _client(user).patch(
        f'/api/v1/projects/{project.id}/members/{user.id}/',
        {'status': MemberStatus.ARCHIVED},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    membership.refresh_from_db()
    assert membership.status == MemberStatus.ARCHIVED
    assert membership.joined_at == joined
    assert user.project_memberships.get(project=project_b).status == MemberStatus.ACTIVE
    user.refresh_from_db()
    assert user.status == 'active'
    activity.refresh_from_db()
    assert activity.created_by_id == user.id
    restored = _client(other_user).patch(
        f'/api/v1/projects/{project_b.id}/members/{other_user.id}/',
        {'status': MemberStatus.SUSPENDED},
        format='json',
    )
    assert restored.status_code == status.HTTP_200_OK
    assert RoleAccessChange.objects.filter(action='member_status_changed', project=project).exists()


@pytest.mark.django_db
def test_inactive_member_role_change_does_not_grant_access_and_delegation_revokes(
    user, other_user, project, member, viewer_role,
):
    member.status = MemberStatus.INACTIVE
    member.save(update_fields=['status'])
    _client(user).patch(
        f'/api/v1/projects/{project.id}/members/{other_user.id}/',
        {'role_ids': [str(viewer_role.id)]},
        format='json',
    )
    denied = _client(other_user).post(
        f'/api/v1/projects/{project.id}/members/',
        {'email': 'still-out@example.com', 'role_ids': [str(viewer_role.id)]},
        format='json',
    )
    assert denied.status_code == status.HTTP_403_FORBIDDEN
    member.status = MemberStatus.ACTIVE
    member.save(update_fields=['status'])
    set_permission_override(member, 'manage_members', True, actor=user)
    target = _person('delegated-target', '+989120000401')
    allowed = _client(other_user).post(
        f'/api/v1/projects/{project.id}/members/',
        {'user_id': str(target.id), 'role_ids': [str(viewer_role.id)]},
        format='json',
    )
    assert allowed.status_code == status.HTTP_201_CREATED
    project_b = create_project_with_creator(
        creator=user,
        project_code='PRJ-TEAM-D',
        project_name='Project D',
        employer='Employer Co',
        start_date='2024-05-01',
    )
    cross = _client(other_user).post(
        f'/api/v1/projects/{project_b.id}/members/',
        {'user_id': str(target.id), 'role_ids': [str(viewer_role.id)]},
        format='json',
    )
    assert cross.status_code == status.HTTP_403_FORBIDDEN
    set_permission_override(member, 'manage_members', None, actor=user)
    revoked = _client(other_user).post(
        f'/api/v1/projects/{project.id}/members/',
        {'email': 'after-revoke@example.com', 'role_ids': [str(viewer_role.id)]},
        format='json',
    )
    assert revoked.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_member_list_last_login_stays_empty_until_sign_in(user, project, api_client):
    listed = _client(user).get(f'/api/v1/projects/{project.id}/members/')
    row = next(item for item in listed.data if item['user_id'] == str(user.id))
    assert row['last_login'] is None
    assert row['joined_at']
    signed = api_client.post(
        '/api/auth/login/',
        {'username': user.username, 'password': 'testpass123'},
        format='json',
    )
    assert signed.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.last_login is not None
    listed_again = _client(user).get(f'/api/v1/projects/{project.id}/members/')
    row = next(item for item in listed_again.data if item['user_id'] == str(user.id))
    assert row['last_login'] is not None
    stamp = user.last_login
    _client(user).patch(
        f'/api/v1/projects/{project.id}/members/{user.id}/',
        {'status': MemberStatus.SUSPENDED},
        format='json',
    )
    user.refresh_from_db()
    assert user.last_login == stamp


@pytest.mark.django_db
def test_connect_open_invitation_and_refuse_closed_ones(user, project, viewer_role):
    created = _client(user).post(
        f'/api/v1/projects/{project.id}/members/',
        {'email': 'open@example.com', 'role_ids': [str(viewer_role.id)]},
        format='json',
    )
    person = _person('open-person', '+989120000701')
    person.email = 'open@example.com'
    person.save(update_fields=['email'])
    connected = _client(user).post(
        f'/api/v1/projects/{project.id}/members/invitations/{created.data["id"]}/connect/',
        {'user_id': str(person.id), 'role_ids': [str(viewer_role.id)]},
        format='json',
    )
    assert connected.status_code == status.HTTP_200_OK
    assert connected.data['user_id'] == str(person.id)
    assert connected.data['status'] == MemberStatus.ACTIVE
    again = _client(user).post(
        f'/api/v1/projects/{project.id}/members/invitations/{created.data["id"]}/connect/',
        {'user_id': str(person.id)},
        format='json',
    )
    assert again.status_code == status.HTTP_400_BAD_REQUEST
    assert again.data['error']['code'] == 'invitation_invalid'

    expired = _client(user).post(
        f'/api/v1/projects/{project.id}/members/',
        {'mobile': '+989120000702', 'role_ids': [str(viewer_role.id)]},
        format='json',
    )
    row = ProjectMember.objects.get(pk=expired.data['id'])
    row.invite_expires_at = timezone.now() - timedelta(minutes=1)
    row.save(update_fields=['invite_expires_at'])
    other = _person('late-person', '+989120000702')
    refused = _client(user).post(
        f'/api/v1/projects/{project.id}/members/invitations/{row.id}/connect/',
        {'user_id': str(other.id)},
        format='json',
    )
    assert refused.status_code == status.HTTP_400_BAD_REQUEST
    assert refused.data['error']['code'] == 'invitation_invalid'
    for change in RoleAccessChange.objects.filter(project=project):
        blob = str(change.before) + str(change.after)
        assert 'token' not in blob.lower() or 'invite_token' not in blob


@pytest.mark.django_db
def test_operational_delivery_only_for_the_agreed_recipient(user, project, viewer_role, settings):
    settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    settings.TEAM_DELIVERY_TEST_RECIPIENT = 'agreed@example.com'
    with patch('notifications.services.delivery.send_mail', return_value=1) as send:
        sent = _client(user).post(
            f'/api/v1/projects/{project.id}/members/',
            {'email': 'agreed@example.com', 'role_ids': [str(viewer_role.id)]},
            format='json',
        )
    assert sent.status_code == status.HTTP_201_CREATED
    assert sent.data['delivery_status'] == 'sent'
    assert send.called
    skipped = _client(user).post(
        f'/api/v1/projects/{project.id}/members/',
        {'email': 'other@example.com', 'role_ids': [str(viewer_role.id)]},
        format='json',
    )
    assert skipped.data['delivery_status'] == 'not_sent'


@pytest.mark.django_db
def test_archived_membership_restores_on_the_same_row(user, other_user, project, member):
    archived = _client(user).patch(
        f'/api/v1/projects/{project.id}/members/{other_user.id}/',
        {'status': MemberStatus.ARCHIVED},
        format='json',
    )
    assert archived.status_code == status.HTTP_200_OK
    restored = _client(user).patch(
        f'/api/v1/projects/{project.id}/members/{other_user.id}/',
        {'status': MemberStatus.ACTIVE},
        format='json',
    )
    assert restored.status_code == status.HTTP_200_OK
    member.refresh_from_db()
    assert member.status == MemberStatus.ACTIVE
    assert member.id == ProjectMember.objects.get(project=project, user=other_user).id
