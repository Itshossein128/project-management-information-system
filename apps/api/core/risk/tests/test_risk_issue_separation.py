"""TDD: risk vs issue separation, impact filters, same-project links."""

import pytest
from rest_framework import status

from contracts.models import Contract, ContractType
from cost_control.models import CostBreakdownNode
from projects.models import Activity, ActivityStatus, WBS
from risk.models import EventType, RiskEvent, RiskStatus


BASE = '/api/v1/projects/{project_id}/risk-events/'


@pytest.fixture
def wbs_node(db, project, user):
    return WBS.add_root(
        project_id=project.id,
        wbs_code='1',
        wbs_name='Root',
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def activity(db, project, wbs_node, user):
    return Activity.objects.create(
        project=project,
        wbs=wbs_node,
        activity_code='A-1',
        activity_name='Pour slab',
        status=ActivityStatus.NOT_STARTED,
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def cbs_node(db, project, user):
    return CostBreakdownNode.add_root(
        project_id=project.id,
        cbs_code='C1',
        cbs_name='Civil',
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def contract(db, project, user):
    return Contract.objects.create(
        project=project,
        contract_number='C-RSK-001',
        contract_type=ContractType.MAIN,
        counterparty='Employer',
        original_amount='1000',
        adjusted_amount='1000',
        retention_pct='0',
        tax_pct='0',
        insurance_pct='0',
        advance_payment_pct='0',
        created_by=user,
        updated_by=user,
    )


@pytest.mark.django_db
class TestRiskIssueSeparation:
    def test_issue_not_in_risk_list_or_matrix(self, auth_client, project, user):
        RiskEvent.objects.create(
            project=project,
            event_type=EventType.ISSUE,
            description='Occurred delay',
            status=RiskStatus.OPEN,
            created_by=user,
            updated_by=user,
        )
        RiskEvent.objects.create(
            project=project,
            event_type=EventType.RISK,
            description='Uncertain threat',
            status=RiskStatus.OPEN,
            probability_level=2,
            impact_severity_level=2,
            composite_score=4,
            created_by=user,
            updated_by=user,
        )
        url = BASE.format(project_id=project.id)
        issues = auth_client.get(url, {'event_type': EventType.ISSUE})
        assert issues.status_code == status.HTTP_200_OK
        assert all(r['event_type'] == EventType.ISSUE for r in issues.data['results'])
        risks = auth_client.get(url, {'event_type': EventType.RISK})
        assert all(r['event_type'] == EventType.RISK for r in risks.data['results'])
        matrix = auth_client.get(f'{url}matrix/')
        assert matrix.status_code == status.HTTP_200_OK
        # Matrix is risk-only; issue must not inflate open count from issue row alone
        assert matrix.data['total_open'] >= 0

    def test_create_issue_via_api(self, auth_client, project):
        url = BASE.format(project_id=project.id)
        resp = auth_client.post(
            url,
            {'event_type': EventType.ISSUE, 'description': 'Cracked wall'},
            format='json',
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.data
        assert resp.data['event_type'] == EventType.ISSUE

    def test_impact_filters(self, auth_client, project, user):
        RiskEvent.objects.create(
            project=project,
            event_type=EventType.RISK,
            description='Quality impact',
            impact_on_quality=True,
            status=RiskStatus.OPEN,
            created_by=user,
            updated_by=user,
        )
        RiskEvent.objects.create(
            project=project,
            event_type=EventType.RISK,
            description='Safety impact',
            impact_on_safety=True,
            status=RiskStatus.OPEN,
            created_by=user,
            updated_by=user,
        )
        url = BASE.format(project_id=project.id)
        for impact, key in (
            ('quality', 'impact_on_quality'),
            ('safety', 'impact_on_safety'),
            ('schedule', 'impact_on_schedule'),
            ('cost', 'impact_on_cost'),
            ('contract', 'impact_on_contract'),
            ('liquidity', 'impact_on_liquidity'),
        ):
            resp = auth_client.get(url, {'impact': impact, 'event_type': EventType.RISK})
            assert resp.status_code == status.HTTP_200_OK
            for row in resp.data['results']:
                assert row[key] is True

    def test_same_project_links_accepted(
        self, auth_client, project, activity, cbs_node, contract,
    ):
        url = BASE.format(project_id=project.id)
        resp = auth_client.post(
            url,
            {
                'event_type': EventType.RISK,
                'description': 'Linked risk',
                'activity': str(activity.id),
                'cost_item': str(cbs_node.id),
                'contract': str(contract.id),
                'related_decision_ref': 'dec-1',
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.data
        assert str(resp.data['activity']) == str(activity.id)
        assert str(resp.data['cost_item']) == str(cbs_node.id)
        assert str(resp.data['contract']) == str(contract.id)

    def test_cross_project_links_rejected(self, auth_client, project, user):
        from projects.models import Project

        other = Project.objects.create(project_code='PRJ-X', project_name='Other')
        other_wbs = WBS.add_root(
            project_id=other.id,
            wbs_code='1',
            wbs_name='Other root',
            created_by=user,
            updated_by=user,
        )
        other_act = Activity.objects.create(
            project=other,
            wbs=other_wbs,
            activity_code='OX',
            activity_name='Other act',
            status=ActivityStatus.NOT_STARTED,
            created_by=user,
            updated_by=user,
        )
        url = BASE.format(project_id=project.id)
        resp = auth_client.post(
            url,
            {
                'event_type': EventType.RISK,
                'description': 'Bad link',
                'activity': str(other_act.id),
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
