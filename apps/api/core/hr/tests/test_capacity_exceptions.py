import pytest
from django.urls import reverse
from rest_framework import status

from hr.models import CapacityExceptionStatus


@pytest.mark.django_db
def test_exception_approve_then_allocate(auth_client, project, other_user, member, user):
    alloc_url = reverse('resource-allocation-list', kwargs={'project_pk': project.id})
    auth_client.post(
        alloc_url,
        {
            'person_id': str(other_user.id),
            'start_date': '2026-04-01',
            'end_date': '2026-04-30',
            'role': 'lead',
            'capacity_percent': '80.00',
        },
        format='json',
    )

    exc_url = reverse('capacity-exception-list', kwargs={'project_pk': project.id})
    exc = auth_client.post(
        exc_url,
        {
            'person_id': str(other_user.id),
            'start_date': '2026-04-15',
            'end_date': '2026-05-15',
            'requested_capacity_percent': '50.00',
            'reason': 'Peak pour week',
            'submit': True,
        },
        format='json',
    )
    assert exc.status_code == status.HTTP_201_CREATED, exc.data
    exc_id = exc.data['id']
    assert exc.data['status'] == CapacityExceptionStatus.SUBMITTED

    approve_url = reverse(
        'capacity-exception-approve',
        kwargs={'project_pk': project.id, 'pk': exc_id},
    )
    approved = auth_client.post(approve_url, {'decision_notes': 'OK'}, format='json')
    assert approved.status_code == status.HTTP_400_BAD_REQUEST
    assert approved.data.get('code') == 'sod_self_approve'

    create = auth_client.post(
        alloc_url,
        {
            'person_id': str(other_user.id),
            'start_date': '2026-04-15',
            'end_date': '2026-05-15',
            'role': 'support',
            'capacity_percent': '50.00',
            'capacity_exception_id': exc_id,
        },
        format='json',
    )
    assert create.status_code == status.HTTP_201_CREATED, create.data
    assert create.data['has_capacity_exception'] is True
    assert create.data['capacity_exception_id'] == exc_id


@pytest.mark.django_db
def test_capacity_preview(auth_client, project, other_user, member):
    preview_url = reverse('capacity-preview', kwargs={'project_pk': project.id})
    resp = auth_client.get(
        preview_url,
        {
            'person_id': str(other_user.id),
            'from': '2026-04-01',
            'to': '2026-04-30',
            'capacity_percent': '50.00',
        },
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['available'] == '100.00'
    assert resp.data['committed'] == '0.00'
