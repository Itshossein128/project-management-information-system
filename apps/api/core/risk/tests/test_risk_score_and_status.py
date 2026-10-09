"""TDD: composite score, FR statuses, close-with-open-actions."""

from datetime import date

import pytest
from rest_framework import status

from risk.models import EventType, RiskAction, RiskActionStatus, RiskEvent, RiskStatus
from risk.services.score_service import (
    compute_composite_score,
    default_status_for_incomplete_score,
)


BASE = '/api/v1/projects/{project_id}/risk-events/'


class TestScoreHelpers:
    def test_both_levels_yield_product(self):
        assert compute_composite_score(3, 4) == 12

    def test_missing_level_yields_none_not_zero(self):
        assert compute_composite_score(3, None) is None
        assert compute_composite_score(None, 4) is None
        assert compute_composite_score(None, None) is None

    def test_incomplete_score_defaults_under_review(self):
        assert (
            default_status_for_incomplete_score(None, 3, explicit_status=None)
            == RiskStatus.UNDER_REVIEW
        )
        assert default_status_for_incomplete_score(3, 4, explicit_status=None) is None
        assert (
            default_status_for_incomplete_score(None, 3, explicit_status=RiskStatus.OPEN) is None
        )


@pytest.mark.django_db
class TestRiskScoreAndStatusAPI:
    def test_create_risk_computes_composite_score(self, auth_client, project):
        url = BASE.format(project_id=project.id)
        resp = auth_client.post(
            url,
            {
                'event_type': EventType.RISK,
                'description': 'Steel delay',
                'probability_level': 3,
                'impact_severity_level': 4,
                'status': RiskStatus.OPEN,
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.data
        assert resp.data['composite_score'] == 12
        listing = auth_client.get(url, {'event_type': EventType.RISK})
        assert any(r['id'] == resp.data['id'] for r in listing.data['results'])

    def test_partial_levels_leave_score_null(self, auth_client, project):
        url = BASE.format(project_id=project.id)
        resp = auth_client.post(
            url,
            {
                'event_type': EventType.RISK,
                'description': 'Incomplete score',
                'probability_level': 2,
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.data
        assert resp.data['composite_score'] is None
        assert resp.data['status'] == RiskStatus.UNDER_REVIEW

    def test_fr_statuses_accepted(self, auth_client, project, user):
        event = RiskEvent.objects.create(
            project=project,
            event_type=EventType.RISK,
            description='Status walk',
            status=RiskStatus.OPEN,
            created_by=user,
            updated_by=user,
        )
        url = f"{BASE.format(project_id=project.id)}{event.id}/"
        for st in (
            RiskStatus.UNDER_REVIEW,
            RiskStatus.MITIGATED,
            RiskStatus.RESIDUAL,
            RiskStatus.CLOSED,
        ):
            patch = auth_client.patch(url, {'status': st}, format='json')
            assert patch.status_code == status.HTTP_200_OK, patch.data
            assert patch.data['status'] == st

    def test_close_with_open_action_requires_acknowledge(self, auth_client, project, user):
        event = RiskEvent.objects.create(
            project=project,
            event_type=EventType.RISK,
            description='Has open action',
            status=RiskStatus.OPEN,
            created_by=user,
            updated_by=user,
        )
        RiskAction.objects.create(
            risk_event=event,
            description='Follow up supplier',
            status=RiskActionStatus.OPEN,
            due_date=date.today(),
            created_by=user,
            updated_by=user,
        )
        url = f"{BASE.format(project_id=project.id)}{event.id}/"
        blocked = auth_client.patch(url, {'status': RiskStatus.CLOSED}, format='json')
        assert blocked.status_code == status.HTTP_400_BAD_REQUEST
        assert blocked.data.get('code') == 'open_actions_warning' or (
            isinstance(blocked.data.get('error'), dict)
            and blocked.data['error'].get('code') == 'open_actions_warning'
        )
        ok = auth_client.patch(
            url,
            {'status': RiskStatus.CLOSED, 'acknowledge_open_actions': True},
            format='json',
        )
        assert ok.status_code == status.HTTP_200_OK, ok.data
        assert ok.data['status'] == RiskStatus.CLOSED
