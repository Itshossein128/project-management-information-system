"""Unknown role ids must not leave a partial membership."""

import uuid

import pytest
from django.utils import translation
from rest_framework import status

from master_data.models import (
    ProjectMember,
    ProjectMemberPermissionOverride,
    ProjectMemberRole,
)


def _error(response):
    return response.data['error']


@pytest.fixture
def members_base(project):
    return f'/api/v1/projects/{project.id}/members/'


@pytest.mark.django_db
def test_unknown_role_does_not_create_member(auth_client, members_base, other_user):
    before = ProjectMember.objects.count()
    response = auth_client.post(
        members_base,
        {'user_id': str(other_user.id), 'role_ids': [str(uuid.uuid4())]},
        format='json',
        HTTP_ACCEPT_LANGUAGE='en',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert _error(response)['code'] == 'unknown_role'
    assert 'do not exist' in _error(response)['message']
    assert ProjectMember.objects.count() == before


@pytest.mark.django_db
def test_unknown_role_message_is_persian(auth_client, members_base, other_user):
    with translation.override('fa'):
        response = auth_client.post(
            members_base,
            {'user_id': str(other_user.id), 'role_ids': [str(uuid.uuid4())]},
            format='json',
            HTTP_ACCEPT_LANGUAGE='fa',
        )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'وجود ندارد' in _error(response)['message']


@pytest.mark.django_db
def test_mixed_roles_do_not_create_member(auth_client, members_base, other_user, viewer_role):
    before = ProjectMember.objects.count()
    response = auth_client.post(
        members_base,
        {
            'user_id': str(other_user.id),
            'role_ids': [str(viewer_role.id), str(uuid.uuid4())],
        },
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert _error(response)['code'] == 'unknown_role'
    assert ProjectMember.objects.filter(user=other_user).count() == 0
    assert ProjectMember.objects.count() == before


@pytest.mark.django_db
def test_failed_role_update_keeps_previous_roles_and_overrides(
    auth_client, members_base, member, viewer_role,
):
    ProjectMemberPermissionOverride.objects.create(
        member=member,
        permission_codename='edit_wbs',
        is_granted=False,
    )
    previous = set(member.member_roles.values_list('role_id', flat=True))
    response = auth_client.patch(
        f'{members_base}{member.user_id}/',
        {'role_ids': [str(viewer_role.id), str(uuid.uuid4())], 'status': 'inactive'},
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert _error(response)['code'] == 'unknown_role'
    member.refresh_from_db()
    assert member.status == 'active'
    assert set(member.member_roles.values_list('role_id', flat=True)) == previous
    assert ProjectMemberRole.objects.filter(member=member, role=viewer_role).exists()
    assert ProjectMemberPermissionOverride.objects.filter(
        member=member,
        permission_codename='edit_wbs',
        is_granted=False,
    ).exists()
