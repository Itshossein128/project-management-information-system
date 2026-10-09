"""Barrier API regression after FR-RSK status migration."""

from datetime import date

import pytest
from rest_framework import status

from risk.models import EventType, RiskEvent, RiskStatus


BARRIERS = '/api/v1/projects/{project_id}/barriers/'


@pytest.mark.django_db
class TestBarrierStatusMigration:
    def test_create_and_list_barrier(self, auth_client, project):
        url = BARRIERS.format(project_id=project.id)
        create = auth_client.post(
            url,
            {
                'log_date': '2026-10-01',
                'description': 'Equipment down',
                'category': 'equipment_failure',
                'status': 'open',
            },
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED, create.data
        assert create.data['status'] in (RiskStatus.OPEN, 'open')
        listing = auth_client.get(url)
        assert listing.status_code == status.HTTP_200_OK
        assert listing.data['count'] >= 1

    def test_legacy_resolved_normalizes_to_closed(self, auth_client, project, user):
        event = RiskEvent.objects.create(
            project=project,
            event_type=EventType.BARRIER,
            description='Legacy barrier',
            status=RiskStatus.OPEN,
            event_date=date.today(),
            created_by=user,
            updated_by=user,
        )
        url = f"{BARRIERS.format(project_id=project.id)}{event.id}/"
        # Client may still send legacy 'resolved'; serializer normalizes to closed
        patch = auth_client.patch(
            url,
            {'status': 'resolved', 'resolved_date': '2026-10-09'},
            format='json',
        )
        assert patch.status_code == status.HTTP_200_OK, patch.data
        assert patch.data['status'] == RiskStatus.CLOSED
        event.refresh_from_db()
        assert event.status == RiskStatus.CLOSED

    def test_close_requires_resolved_date(self, auth_client, project, user):
        event = RiskEvent.objects.create(
            project=project,
            event_type=EventType.BARRIER,
            description='Needs date',
            status=RiskStatus.OPEN,
            event_date=date.today(),
            created_by=user,
            updated_by=user,
        )
        url = f"{BARRIERS.format(project_id=project.id)}{event.id}/"
        bad = auth_client.patch(url, {'status': RiskStatus.CLOSED}, format='json')
        assert bad.status_code == status.HTTP_400_BAD_REQUEST
