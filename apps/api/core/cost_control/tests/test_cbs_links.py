from decimal import Decimal

import pytest

from cost_control.cbs_services import create_cbs_node
from cost_control.models import ActualCost, Budget, CostCategory


@pytest.mark.django_db
def test_budget_accepts_optional_cbs(auth_client, project, wbs, user):
    node = create_cbs_node(
        project_id=project.id,
        cbs_code='C.20',
        cbs_name='Labor CBS',
        cost_type='labor',
        created_by=user,
    )
    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/budgets/',
        {
            'wbs': str(wbs.id),
            'cost_category': 'labor',
            'budget_amount': '500000',
            'cbs': str(node.id),
        },
        format='json',
    )
    assert resp.status_code == 201, resp.content
    assert Budget.objects.get(pk=resp.json()['id']).cbs_id == node.id


@pytest.mark.django_db
def test_actual_cost_accepts_optional_cbs(auth_client, project, activity, user):
    node = create_cbs_node(
        project_id=project.id,
        cbs_code='C.21',
        cbs_name='Mat CBS',
        cost_type='material',
        created_by=user,
    )
    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/costs/',
        {
            'activity': str(activity.id),
            'cost_date': '2024-06-01',
            'cost_category': 'material',
            'amount': '1000',
            'cbs': str(node.id),
        },
        format='json',
    )
    assert resp.status_code == 201, resp.content
    assert ActualCost.objects.get(pk=resp.json()['id']).cbs_id == node.id
    assert Decimal(ActualCost.objects.get(pk=resp.json()['id']).amount) == Decimal('1000')
