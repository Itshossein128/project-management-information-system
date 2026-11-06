"""FR-COL US1: stakeholder relationship_owner and contact redaction."""

import pytest
from rest_framework.test import APIClient

from master_data.models import MemberStatus, ProjectMemberRole, Role, RolePermission


@pytest.mark.django_db
def test_stakeholder_relationship_owner_in_list(auth_client, project, user):
    create = auth_client.post(
        f'/api/v1/projects/{project.id}/stakeholders/',
        {
            'name': 'Owner Rep',
            'email': 'owner@example.com',
            'phone': '+10000000001',
            'relationship_owner': str(user.id),
        },
        format='json',
    )
    assert create.status_code == 201, create.content
    sid = create.json()['id']
    assert create.json().get('relationship_owner') == str(user.id)

    listing = auth_client.get(f'/api/v1/projects/{project.id}/stakeholders/')
    assert listing.status_code == 200
    rows = listing.json()
    if isinstance(rows, dict):
        rows = rows.get('results', rows)
    row = next(r for r in rows if r['id'] == sid)
    assert row.get('relationship_owner') == str(user.id)


@pytest.mark.django_db
def test_stakeholder_contacts_redacted_for_viewer(
    auth_client, api_client, project, user, other_user, member
):
    """Viewer has view_project but not edit_project or view_sensitive_contacts."""
    create = auth_client.post(
        f'/api/v1/projects/{project.id}/stakeholders/',
        {
            'name': 'Secret Contact',
            'email': 'secret@example.com',
            'phone': '+10000000002',
        },
        format='json',
    )
    assert create.status_code == 201
    sid = create.json()['id']

    api_client.force_authenticate(user=other_user)
    detail = api_client.get(f'/api/v1/projects/{project.id}/stakeholders/{sid}/')
    assert detail.status_code == 200
    data = detail.json()
    assert data.get('email') in (None, '')
    assert data.get('phone') in (None, '')
    assert data.get('contacts_redacted') is True


@pytest.mark.django_db
def test_observation_admin_without_sensitive_permission_sees_no_contacts(
    api_client, project, user
):
    """Organizational observation does not open stakeholder contacts."""
    from django.contrib.auth.models import Group
    from django.contrib.auth import get_user_model

    User = get_user_model()
    create = APIClient()
    create.force_authenticate(user=user)
    created = create.post(
        f'/api/v1/projects/{project.id}/stakeholders/',
        {
            'name': 'Obs Hidden',
            'email': 'obs-hidden@example.com',
            'phone': '+10000000009',
        },
        format='json',
    )
    assert created.status_code == 201
    sid = created.json()['id']

    admin = User.objects.create_user(
        username='obs_stake',
        mobile='+989120000701',
        password='x',
    )
    group, _ = Group.objects.get_or_create(name='admin')
    admin.groups.add(group)
    api_client.force_authenticate(user=admin)
    detail = api_client.get(f'/api/v1/projects/{project.id}/stakeholders/{sid}/')
    # Observation may read project-scoped stakeholder list/detail as view_project,
    # but contacts must stay redacted without view_sensitive_contacts.
    assert detail.status_code in (200, 403)
    if detail.status_code == 200:
        data = detail.json()
        assert data.get('email') in (None, '')
        assert data.get('phone') in (None, '')
        assert data.get('contacts_redacted') is True


@pytest.mark.django_db
def test_edit_project_does_not_reveal_stakeholder_contacts(
    auth_client, api_client, project, user, other_user, project_manager_role
):
    """Contact visibility follows ``view_sensitive_contacts`` only (A6-P4 T073)."""
    RolePermission.objects.filter(
        role=project_manager_role,
        permission_codename='view_sensitive_contacts',
    ).delete()
    from master_data.models import ProjectMember, ProjectMemberRole

    m, _ = ProjectMember.objects.get_or_create(
        project=project,
        user=other_user,
        defaults={'status': MemberStatus.ACTIVE},
    )
    ProjectMemberRole.objects.get_or_create(member=m, role=project_manager_role)

    create = auth_client.post(
        f'/api/v1/projects/{project.id}/stakeholders/',
        {
            'name': 'PM edit only',
            'email': 'pm-edit@example.com',
            'phone': '+10000000011',
        },
        format='json',
    )
    assert create.status_code == 201
    sid = create.json()['id']

    api_client.force_authenticate(user=other_user)
    detail = api_client.get(f'/api/v1/projects/{project.id}/stakeholders/{sid}/')
    assert detail.status_code == 200
    data = detail.json()
    assert data.get('email') in (None, '')
    assert data.get('phone') in (None, '')
    assert data.get('contacts_redacted') is True


@pytest.mark.django_db
def test_stakeholder_contacts_visible_with_sensitive_permission(
    api_client, project, user, other_user
):
    role = Role.objects.get(role_name='document_controller')
    from master_data.models import ProjectMember

    m, _ = ProjectMember.objects.get_or_create(
        project=project,
        user=other_user,
        defaults={'status': MemberStatus.ACTIVE},
    )
    ProjectMemberRole.objects.get_or_create(member=m, role=role)

    create_resp = APIClient()
    create_resp.force_authenticate(user=user)
    create = create_resp.post(
        f'/api/v1/projects/{project.id}/stakeholders/',
        {
            'name': 'Visible Contact',
            'email': 'visible@example.com',
            'phone': '+10000000003',
        },
        format='json',
    )
    assert create.status_code == 201
    sid = create.json()['id']

    api_client.force_authenticate(user=other_user)
    detail = api_client.get(f'/api/v1/projects/{project.id}/stakeholders/{sid}/')
    assert detail.status_code == 200
    data = detail.json()
    assert data.get('email') == 'visible@example.com'
    assert data.get('phone') == '+10000000003'
    assert data.get('contacts_redacted') is not True
