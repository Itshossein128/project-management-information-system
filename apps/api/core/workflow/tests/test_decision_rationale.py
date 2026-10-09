"""TDD: management decisions — rationale, execution owner, same-project links."""

import uuid

import pytest
from rest_framework import status

from contracts.models import Contract, ContractType
from risk.models import EventType, RiskEvent

DECISIONS = '/api/v1/projects/{project_id}/decisions/'


def _decision_payload(user, execution_owner=None, **overrides):
    data = {
        'subject': 'Approve temporary diversion',
        'options': 'A) North\nB) South',
        'criteria': 'Cost + safety',
        'proposer': str(user.id),
        'approver_ids': [str(user.id)],
        'execution_owner': str(execution_owner or user.id),
        'rationale': 'North route avoids live traffic',
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
class TestDecisionRationale:
    def test_blank_rationale_rejected(self, auth_client, project, user):
        url = DECISIONS.format(project_id=project.id)
        payload = _decision_payload(user, rationale='   ')
        resp = auth_client.post(url, payload, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data['error']['code'] == 'rationale_required'

    def test_missing_rationale_rejected(self, auth_client, project, user):
        url = DECISIONS.format(project_id=project.id)
        payload = _decision_payload(user)
        del payload['rationale']
        resp = auth_client.post(url, payload, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data['error']['code'] == 'rationale_required'

    def test_valid_rationale_and_execution_owner_created(
        self, auth_client, project, user,
    ):
        url = DECISIONS.format(project_id=project.id)
        resp = auth_client.post(url, _decision_payload(user), format='json')
        assert resp.status_code == status.HTTP_201_CREATED, resp.data
        assert resp.data['rationale'] == 'North route avoids live traffic'
        assert str(resp.data['execution_owner']) == str(user.id)

    def test_missing_execution_owner_rejected(self, auth_client, project, user):
        url = DECISIONS.format(project_id=project.id)
        payload = _decision_payload(user)
        payload['execution_owner'] = None
        resp = auth_client.post(url, payload, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestDecisionProjectLinks:
    def test_same_project_optional_links_accepted(
        self, auth_client, project, user, activity, contract,
    ):
        risk = RiskEvent.objects.create(
            project=project,
            event_type=EventType.RISK,
            description='Linked',
            created_by=user,
            updated_by=user,
        )
        url = DECISIONS.format(project_id=project.id)
        payload = _decision_payload(
            user,
            related_risk=str(risk.id),
            related_activity=str(activity.id),
            related_contract=str(contract.id),
        )
        resp = auth_client.post(url, payload, format='json')
        assert resp.status_code == status.HTTP_201_CREATED, resp.data
        assert str(resp.data['related_risk']) == str(risk.id)
        assert str(resp.data['related_activity']) == str(activity.id)
        assert str(resp.data['related_contract']) == str(contract.id)

    def test_cross_project_activity_rejected(self, auth_client, project, user):
        from projects.models import Activity
        from wbs.services import create_wbs_node

        from projects.models import Project

        other = Project.objects.create(project_code='PRJ-OTH', project_name='Other')
        other_wbs, _ = create_wbs_node(project_id=other.id, wbs_code='1', wbs_name='Root')
        other_act = Activity.objects.create(
            project=other,
            wbs=other_wbs,
            activity_code='OX',
            activity_name='Other',
            total_quantity=1,
            created_by=user,
            updated_by=user,
        )
        url = DECISIONS.format(project_id=project.id)
        payload = _decision_payload(user, related_activity=str(other_act.id))
        resp = auth_client.post(url, payload, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_cross_project_contract_rejected(self, auth_client, project, user):
        from projects.models import Project

        other = Project.objects.create(project_code='PRJ-OTH2', project_name='Other2')
        other_contract = Contract.objects.create(
            project=other,
            contract_number='X-1',
            contract_type=ContractType.MAIN,
            counterparty='X',
            original_amount='1',
            adjusted_amount='1',
            retention_pct='0',
            tax_pct='0',
            insurance_pct='0',
            advance_payment_pct='0',
            created_by=user,
            updated_by=user,
        )
        url = DECISIONS.format(project_id=project.id)
        payload = _decision_payload(user, related_contract=str(other_contract.id))
        resp = auth_client.post(url, payload, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_cross_project_risk_rejected(self, auth_client, project, user):
        from projects.models import Project

        other = Project.objects.create(project_code='PRJ-OTH3', project_name='Other3')
        risk = RiskEvent.objects.create(
            project=other,
            event_type=EventType.RISK,
            description='Other risk',
            created_by=user,
            updated_by=user,
        )
        url = DECISIONS.format(project_id=project.id)
        payload = _decision_payload(user, related_risk=str(risk.id))
        resp = auth_client.post(url, payload, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
