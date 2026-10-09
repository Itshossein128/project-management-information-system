import pytest
from django.urls import reverse
from rest_framework import status

from hr.models import ResourceAllocation
from projects.models import Activity, Project, WBS


@pytest.mark.django_db
def test_resource_allocation_model_fields(project, other_user, user):
    alloc = ResourceAllocation.objects.create(
        project=project,
        person=other_user,
        start_date='2026-04-01',
        end_date='2026-04-30',
        role='site engineer',
        capacity_percent='50.00',
        created_by=user,
    )
    assert alloc.wbs_id is None
    assert alloc.activity_id is None
    assert alloc.has_capacity_exception is False
    assert alloc.capacity_exception_id is None


@pytest.mark.django_db
def test_allocation_crud_and_hours_to_percent(auth_client, project, other_user, member, wbs, activity, user):
    url = reverse('resource-allocation-list', kwargs={'project_pk': project.id})
    create = auth_client.post(
        url,
        {
            'person_id': str(other_user.id),
            'wbs_id': str(wbs.id),
            'activity_id': str(activity.id),
            'start_date': '2026-04-01',
            'end_date': '2026-04-30',
            'role': 'site engineer',
            'capacity_hours': '4.00',
            'work_location': 'Site A',
        },
        format='json',
    )
    assert create.status_code == status.HTTP_201_CREATED, create.data
    assert create.data['capacity_percent'] == '50.00'
    alloc_id = create.data['id']

    detail_url = reverse(
        'resource-allocation-detail',
        kwargs={'project_pk': project.id, 'pk': alloc_id},
    )
    assert auth_client.get(detail_url).status_code == status.HTTP_200_OK

    bad_dates = auth_client.post(
        url,
        {
            'person_id': str(other_user.id),
            'start_date': '2026-05-01',
            'end_date': '2026-04-01',
            'role': 'x',
            'capacity_percent': '10.00',
        },
        format='json',
    )
    assert bad_dates.status_code == status.HTTP_400_BAD_REQUEST

    other_project = Project.objects.create(project_code='P2', project_name='Other')
    foreign_wbs = WBS.add_root(
        project=other_project,
        wbs_code='9',
        wbs_name='Foreign',
        created_by=user,
        updated_by=user,
    )
    scope_bad = auth_client.post(
        url,
        {
            'person_id': str(other_user.id),
            'wbs_id': str(foreign_wbs.id),
            'start_date': '2026-04-01',
            'end_date': '2026-04-30',
            'role': 'x',
            'capacity_percent': '10.00',
        },
        format='json',
    )
    assert scope_bad.status_code == status.HTTP_400_BAD_REQUEST
    assert scope_bad.data['error']['code'] == 'scope_mismatch'

    assert auth_client.delete(detail_url).status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_capacity_conflict_409(auth_client, project, other_user, member, user):
    url = reverse('resource-allocation-list', kwargs={'project_pk': project.id})
    first = auth_client.post(
        url,
        {
            'person_id': str(other_user.id),
            'start_date': '2026-04-01',
            'end_date': '2026-04-30',
            'role': 'lead',
            'capacity_percent': '80.00',
        },
        format='json',
    )
    assert first.status_code == status.HTTP_201_CREATED

    conflict = auth_client.post(
        url,
        {
            'person_id': str(other_user.id),
            'start_date': '2026-04-15',
            'end_date': '2026-05-15',
            'role': 'support',
            'capacity_percent': '50.00',
        },
        format='json',
    )
    assert conflict.status_code == status.HTTP_409_CONFLICT
    assert conflict.data['error']['code'] == 'capacity_conflict'
    details = conflict.data['error']['details']
    assert details['committed'] == '80.00'
    assert details['requested'] == '50.00'
