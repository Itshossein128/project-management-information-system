import pytest
from django.urls import reverse
from rest_framework import status

from authentication.models import User, UserStatus
from master_data.models import OrganizationUnit, ProjectMember


@pytest.mark.django_db
def test_user_dossier_schema_fields(user):
    assert user.skills == []
    assert user.qualifications == []
    assert user.org_unit_id is None
    assert user.supervisor_id is None
    assert user.default_capacity_percent == 100


@pytest.mark.django_db
def test_dossier_get_patch(auth_client, project, other_user, member, user):
    org = OrganizationUnit.objects.create(code='ENG', name='Engineering', created_by=user)
    url = reverse(
        'person-dossier',
        kwargs={'project_pk': project.id, 'user_id': other_user.id},
    )
    resp = auth_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['skills'] == []

    patch = auth_client.patch(
        url,
        {
            'skills': ['welding'],
            'qualifications': ['ISO 9606'],
            'org_unit_id': str(org.id),
            'supervisor_id': str(user.id),
            'default_capacity_percent': '90.00',
        },
        format='json',
    )
    assert patch.status_code == status.HTTP_200_OK, patch.data
    other_user.refresh_from_db()
    assert other_user.skills == ['welding']
    assert other_user.org_unit_id == org.id
    assert other_user.supervisor_id == user.id
    assert str(other_user.default_capacity_percent) == '90.00'


@pytest.mark.django_db
def test_inactive_person_rejected_for_allocation(auth_client, project, other_user, member):
    other_user.status = UserStatus.INACTIVE
    other_user.is_active = False
    other_user.save()
    url = reverse('resource-allocation-list', kwargs={'project_pk': project.id})
    resp = auth_client.post(
        url,
        {
            'person_id': str(other_user.id),
            'start_date': '2026-04-01',
            'end_date': '2026-04-30',
            'role': 'engineer',
            'capacity_percent': '50.00',
        },
        format='json',
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data['error']['code'] == 'person_inactive'
