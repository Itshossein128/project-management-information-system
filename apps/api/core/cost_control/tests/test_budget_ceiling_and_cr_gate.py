"""FR-003 / FR-006 / SC-003: CR gate and project ceiling enforcement."""

from decimal import Decimal

import pytest
from rest_framework import status

from cost_control.models import (
    Budget,
    BudgetVersion,
    BudgetVersionKind,
    BudgetVersionStatus,
    CostCategory,
    CostPool,
)
from cost_control.services.budget_change_service import assert_within_project_ceiling
from cost_control.services.cost_pool_service import allocate_cost_pool
from config.exceptions import CodedValidationError


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
        cost_category=CostCategory.LABOR,
        budget_amount=Decimal('100000'),
        created_by=user,
        updated_by=user,
    )
    return version, line


@pytest.mark.django_db
class TestBudgetChangeRequestRequired:
    def test_cannot_approve_revised_when_control_exists(
        self, auth_client, costs_base, control_budget, wbs
    ):
        create = auth_client.post(
            f'{costs_base}budget-versions/',
            {'kind': 'revised', 'name': 'Bypass attempt'},
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED
        vid = create.data['id']
        line = auth_client.post(
            f'{costs_base}budget-versions/{vid}/lines/',
            {
                'level': 'wbs',
                'wbs': str(wbs.id),
                'cost_category': 'labor',
                'budget_amount': '999999',
            },
            format='json',
        )
        assert line.status_code == status.HTTP_201_CREATED
        submit = auth_client.post(f'{costs_base}budget-versions/{vid}/submit/', {}, format='json')
        assert submit.status_code == status.HTTP_200_OK
        approve = auth_client.post(f'{costs_base}budget-versions/{vid}/approve/', {}, format='json')
        assert approve.status_code == status.HTTP_400_BAD_REQUEST
        assert approve.data.get('code') == 'budget_change_request_required' or (
            'budget_change_request_required' in str(approve.data)
        )


@pytest.mark.django_db
class TestProjectCeiling:
    def test_assert_within_ceiling_helper(self, control_budget, project):
        assert_within_project_ceiling(project.id, Decimal('100000'))
        with pytest.raises(CodedValidationError) as exc:
            assert_within_project_ceiling(project.id, Decimal('100001'))
        assert exc.value.default_code == 'project_ceiling_exceeded'

    def test_pool_allocate_blocked_over_ceiling(
        self, auth_client, costs_base, control_budget, project, user, activity
    ):
        # Ceiling is 100000; spent starts at 0. Allocating 100001 must fail.
        pool = CostPool.objects.create(
            project=project,
            pool_name='Oversize pool',
            cost_category=CostCategory.LABOR,
            total_amount=Decimal('200000'),
            created_by=user,
            updated_by=user,
        )
        with pytest.raises(CodedValidationError) as exc:
            allocate_cost_pool(
                pool,
                [{'activity_id': str(activity.id), 'amount': Decimal('100001')}],
                user,
            )
        assert exc.value.default_code == 'project_ceiling_exceeded'

        # API path
        resp = auth_client.post(
            f'{costs_base}cost-pools/{pool.id}/allocate/',
            [{'activity_id': str(activity.id), 'amount': '100001'}],
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data.get('code') == 'project_ceiling_exceeded' or (
            'project_ceiling_exceeded' in str(resp.data)
        )

    def test_cr_approve_can_raise_ceiling(self, auth_client, costs_base, control_budget):
        _version, line = control_budget
        create = auth_client.post(
            f'{costs_base}budget-change-requests/',
            {
                'reason': 'Raise labor ceiling for approved scope expansion',
                'project_impact': 'Extends foundation package budget',
                'amount_delta': '50000',
                'affected_lines': [
                    {
                        'op': 'update',
                        'line_id': str(line.id),
                        'budget_amount': '150000',
                    }
                ],
            },
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED
        cr_id = create.data['id']
        auth_client.post(f'{costs_base}budget-change-requests/{cr_id}/submit/', {}, format='json')
        approve = auth_client.post(
            f'{costs_base}budget-change-requests/{cr_id}/approve/', {}, format='json'
        )
        assert approve.status_code == status.HTTP_200_OK, approve.content
        assert approve.data['status'] == 'approved'
        # New ceiling allows 150000 spend
        assert_within_project_ceiling(line.project_id, Decimal('150000'))
