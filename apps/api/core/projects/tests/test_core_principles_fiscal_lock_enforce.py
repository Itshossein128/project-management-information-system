"""US7: fiscal lock blocks ordinary ActualCost creates."""
from datetime import date

import pytest

from cost_control.models import ActualCost, CostCategory
from projects.fiscal_service import create_fiscal_lock


@pytest.mark.django_db
def test_locked_period_blocks_cost_create(auth_client, project, user, wbs):
    create_fiscal_lock(
        project=project,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 12, 31),
        reason='FY close',
        user=user,
    )
    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/costs/',
        {
            'wbs': str(wbs.id),
            'cost_date': '2024-06-15',
            'cost_category': CostCategory.MATERIAL,
            'amount': '1000',
            'description': 'blocked',
        },
        format='json',
    )
    assert resp.status_code == 400
    assert 'fiscal_period_locked' in str(resp.json())


@pytest.mark.django_db
def test_corrective_path_allows_create(auth_client, project, user, wbs):
    create_fiscal_lock(
        project=project,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 12, 31),
        reason='FY close',
        user=user,
    )
    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/costs/',
        {
            'wbs': str(wbs.id),
            'cost_date': '2024-06-15',
            'cost_category': CostCategory.MATERIAL,
            'amount': '1000',
            'description': 'corrective',
            'corrective': True,
            'correction_reason': 'Fix posting error',
        },
        format='json',
    )
    assert resp.status_code == 201, resp.content
    assert ActualCost.objects.filter(project=project, description='corrective').exists()
