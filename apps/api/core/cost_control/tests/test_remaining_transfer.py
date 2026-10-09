"""Remaining allocatable and transfers."""

from decimal import Decimal

import pytest
from rest_framework import status

from cost_control.models import (
    ActualCost,
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
def control_with_two_lines(db, project, wbs, user):
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
    labor = Budget.objects.create(
        project=project,
        version=version,
        level='wbs',
        wbs=wbs,
        cost_category=CostCategory.LABOR,
        budget_amount=Decimal('100000'),
        created_by=user,
        updated_by=user,
    )
    material = Budget.objects.create(
        project=project,
        version=version,
        level='wbs',
        wbs=wbs,
        cost_category=CostCategory.MATERIAL,
        budget_amount=Decimal('50000'),
        created_by=user,
        updated_by=user,
    )
    return version, labor, material


@pytest.mark.django_db
class TestRemainingAndTransfer:
    def test_remaining_after_commitment_and_actual(
        self, auth_client, costs_base, control_with_two_lines, project, wbs, user
    ):
        _version, labor, _material = control_with_two_lines
        Commitment.objects.create(
            project=project,
            commitment_number='CM-1',
            amount=Decimal('30000'),
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
            amount=Decimal('20000'),
            created_by=user,
            updated_by=user,
        )
        resp = auth_client.get(f'{costs_base}budgets/remaining/')
        assert resp.status_code == status.HTTP_200_OK
        headings = {h['cost_category']: h for h in resp.data['headings']}
        assert 'labor' in headings
        # committed 30k + consumed 20k against 100k labor
        assert headings['labor']['approved'] == 100000.0
        assert headings['labor']['committed'] == 30000.0
        assert headings['labor']['consumed'] == 20000.0
        assert headings['labor']['remaining'] == 50000.0

    def test_transfer_net_zero(self, auth_client, costs_base, control_with_two_lines):
        _version, labor, material = control_with_two_lines
        resp = auth_client.post(
            f'{costs_base}budgets/transfers/',
            {
                'from_line_id': str(labor.id),
                'to_line_id': str(material.id),
                'amount': '10000',
                'note': 'Rebalance',
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.content
        labor.refresh_from_db()
        material.refresh_from_db()
        assert labor.budget_amount == Decimal('90000')
        assert material.budget_amount == Decimal('60000')

    def test_transfer_insufficient_source(self, auth_client, costs_base, control_with_two_lines):
        _version, labor, material = control_with_two_lines
        resp = auth_client.post(
            f'{costs_base}budgets/transfers/',
            {
                'from_line_id': str(labor.id),
                'to_line_id': str(material.id),
                'amount': '999999',
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data.get('code') == 'transfer_insufficient_source' or (
            'transfer_insufficient_source' in str(resp.data)
        )
