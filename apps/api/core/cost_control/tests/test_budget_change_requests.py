"""Budget change request workflow."""

from decimal import Decimal

import pytest
from rest_framework import status

from cost_control.models import (
    Budget,
    BudgetVersion,
    BudgetVersionKind,
    BudgetVersionStatus,
)


@pytest.fixture
def costs_base(project):
    return f'/api/v1/projects/{project.id}/'


@pytest.fixture
def control_budget(db, project, wbs, user):
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
    line = Budget.objects.create(
        project=project,
        version=version,
        level='wbs',
        wbs=wbs,
        cost_category='labor',
        budget_amount=Decimal('1000000'),
        created_by=user,
        updated_by=user,
    )
    return version, line


@pytest.mark.django_db
class TestBudgetChangeRequests:
    def test_direct_edit_on_control_rejected(self, auth_client, costs_base, control_budget):
        _version, line = control_budget
        resp = auth_client.patch(
            f'{costs_base}budgets/{line.id}/',
            {'budget_amount': '999'},
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data.get('code') == 'budget_version_locked' or 'budget_version_locked' in str(
            resp.data
        )

    def test_cr_approve_creates_revised_control(
        self, auth_client, costs_base, control_budget, wbs
    ):
        version, line = control_budget
        create = auth_client.post(
            f'{costs_base}budget-change-requests/',
            {
                'reason': 'Increase labor budget for foundation scope change',
                'project_impact': 'Supports extended foundation package',
                'amount_delta': '500000',
                'affected_lines': [
                    {
                        'op': 'update',
                        'line_id': str(line.id),
                        'budget_amount': '1500000',
                    }
                ],
            },
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED, create.content
        cr_id = create.data['id']

        submit = auth_client.post(
            f'{costs_base}budget-change-requests/{cr_id}/submit/', {}, format='json'
        )
        assert submit.status_code == status.HTTP_200_OK

        approve = auth_client.post(
            f'{costs_base}budget-change-requests/{cr_id}/approve/', {}, format='json'
        )
        assert approve.status_code == status.HTTP_200_OK, approve.content
        assert approve.data['status'] == 'approved'
        assert approve.data['resulting_version']

        version.refresh_from_db()
        assert version.is_control is False
        new_v = BudgetVersion.objects.get(pk=approve.data['resulting_version'])
        assert new_v.is_control is True
        assert new_v.kind == BudgetVersionKind.REVISED
        new_total = sum(
            Budget.objects.filter(version=new_v, is_deleted=False).values_list(
                'budget_amount', flat=True
            )
        )
        assert Decimal(new_total) == Decimal('1500000')

    def test_reject_leaves_baseline(self, auth_client, costs_base, control_budget):
        version, line = control_budget
        create = auth_client.post(
            f'{costs_base}budget-change-requests/',
            {
                'reason': 'Attempted increase that will be rejected now',
                'project_impact': 'Would raise labor',
                'amount_delta': '1',
                'affected_lines': [
                    {'op': 'update', 'line_id': str(line.id), 'budget_amount': '2000000'}
                ],
            },
            format='json',
        )
        cr_id = create.data['id']
        auth_client.post(f'{costs_base}budget-change-requests/{cr_id}/submit/', {}, format='json')
        reject = auth_client.post(
            f'{costs_base}budget-change-requests/{cr_id}/reject/',
            {'decision_notes': 'Not approved'},
            format='json',
        )
        assert reject.status_code == status.HTTP_200_OK
        line.refresh_from_db()
        assert line.budget_amount == Decimal('1000000')
        version.refresh_from_db()
        assert version.is_control is True
