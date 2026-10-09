"""SC-006: remaining must not double-count commitment + linked actual."""

from decimal import Decimal

import pytest
from rest_framework import status

from cost_control.models import (
    ActualCost,
    ActualCostStatus,
    Budget,
    BudgetVersion,
    BudgetVersionKind,
    BudgetVersionStatus,
    Commitment,
    CommitmentStatus,
    CostCategory,
)


@pytest.fixture
def costs_base(project):
    return f'/api/v1/projects/{project.id}/'


@pytest.fixture
def control_labor_1000(db, project, wbs, user):
    version = BudgetVersion.objects.create(
        project=project,
        kind=BudgetVersionKind.APPROVED,
        status=BudgetVersionStatus.APPROVED,
        version_number=1,
        currency='IRR',
        is_control=True,
        created_by=user,
        updated_by=user,
    )
    Budget.objects.create(
        project=project,
        version=version,
        level='wbs',
        wbs=wbs,
        cost_category=CostCategory.LABOR,
        budget_amount=Decimal('1000'),
        created_by=user,
        updated_by=user,
    )
    return version


def _labor_heading(resp):
    headings = {h['cost_category']: h for h in resp.data['headings']}
    assert 'labor' in headings
    return headings['labor']


@pytest.mark.django_db
def test_remaining_steps_open_commitment_no_double_count(
    auth_client, costs_base, control_labor_1000, project, wbs, user
):
    """Steps A→C from remaining-and-report contract."""
    commitment = Commitment.objects.create(
        project=project,
        commitment_number='CM-OPEN-1',
        amount=Decimal('600'),
        commitment_date='2024-01-15',
        wbs=wbs,
        status=CommitmentStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )

    # Step A: commitment only → committed=600, consumed=0, remaining=400
    resp = auth_client.get(f'{costs_base}budgets/remaining/')
    assert resp.status_code == status.HTTP_200_OK
    h = _labor_heading(resp)
    assert h['approved'] == 1000.0
    assert h['committed'] == 600.0
    assert h['consumed'] == 0.0
    assert h['remaining'] == 400.0

    # Step B: linked actual 400 → committed open=200, consumed=400, remaining=400
    actual = ActualCost.objects.create(
        project=project,
        wbs=wbs,
        commitment=commitment,
        cost_date='2024-02-01',
        cost_category=CostCategory.LABOR,
        amount=Decimal('400'),
        status=ActualCostStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )
    resp = auth_client.get(f'{costs_base}budgets/remaining/')
    assert resp.status_code == status.HTTP_200_OK
    h = _labor_heading(resp)
    assert h['committed'] == 200.0
    assert h['consumed'] == 400.0
    assert h['remaining'] == 400.0

    # Step C: linked actual total 600 → committed open=0, consumed=600, remaining=400
    actual.amount = Decimal('600')
    actual.save(update_fields=['amount', 'updated_at'])
    resp = auth_client.get(f'{costs_base}budgets/remaining/')
    assert resp.status_code == status.HTTP_200_OK
    h = _labor_heading(resp)
    assert h['committed'] == 0.0
    assert h['consumed'] == 600.0
    assert h['remaining'] == 400.0


@pytest.mark.django_db
def test_unlinked_actual_still_adds_to_consumed_and_open_commitment(
    auth_client, costs_base, control_labor_1000, project, wbs, user
):
    """Unlinked actual does not reduce open commitment (legacy independent spend)."""
    Commitment.objects.create(
        project=project,
        commitment_number='CM-OPEN-2',
        amount=Decimal('300'),
        commitment_date='2024-01-15',
        wbs=wbs,
        status=CommitmentStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )
    ActualCost.objects.create(
        project=project,
        wbs=wbs,
        cost_date='2024-02-01',
        cost_category=CostCategory.LABOR,
        amount=Decimal('200'),
        status=ActualCostStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )
    resp = auth_client.get(f'{costs_base}budgets/remaining/')
    assert resp.status_code == status.HTTP_200_OK
    h = _labor_heading(resp)
    assert h['committed'] == 300.0
    assert h['consumed'] == 200.0
    assert h['remaining'] == 500.0
