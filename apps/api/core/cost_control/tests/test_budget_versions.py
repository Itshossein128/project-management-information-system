"""Budget version lifecycle and multi-level lines."""

from decimal import Decimal

import pytest
from rest_framework import status

from cost_control.models import Budget, BudgetVersion, BudgetVersionKind, BudgetVersionStatus


@pytest.fixture
def costs_base(project):
    return f'/api/v1/projects/{project.id}/'


@pytest.mark.django_db
class TestBudgetVersions:
    def test_create_submit_approve_locks(self, auth_client, costs_base, wbs, project):
        create = auth_client.post(
            f'{costs_base}budget-versions/',
            {'kind': 'initial', 'name': 'Initial', 'currency': 'IRR'},
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED, create.content
        vid = create.data['id']
        assert create.data['status'] == 'draft'

        line = auth_client.post(
            f'{costs_base}budget-versions/{vid}/lines/',
            {
                'level': 'wbs',
                'wbs': str(wbs.id),
                'cost_category': 'labor',
                'budget_amount': '1000000',
            },
            format='json',
        )
        assert line.status_code == status.HTTP_201_CREATED, line.content

        submit = auth_client.post(f'{costs_base}budget-versions/{vid}/submit/', {}, format='json')
        assert submit.status_code == status.HTTP_200_OK
        assert submit.data['status'] == 'submitted'

        approve = auth_client.post(f'{costs_base}budget-versions/{vid}/approve/', {}, format='json')
        assert approve.status_code == status.HTTP_200_OK, approve.content
        assert approve.data['status'] == 'approved'
        assert approve.data['is_control'] is True
        assert approve.data['kind'] == 'approved'

        locked = auth_client.post(
            f'{costs_base}budget-versions/{vid}/lines/',
            {
                'level': 'wbs',
                'wbs': str(wbs.id),
                'cost_category': 'material',
                'budget_amount': '1',
            },
            format='json',
        )
        assert locked.status_code == status.HTTP_400_BAD_REQUEST
        assert locked.data.get('code') == 'budget_version_locked' or 'budget_version_locked' in str(
            locked.data
        )

    def test_project_and_cbs_levels(self, auth_client, costs_base, project, user):
        from cost_control.models import CostBreakdownNode

        cbs = CostBreakdownNode.add_root(
            project=project,
            cbs_code='C1',
            cbs_name='CBS1',
            created_by=user,
        )
        create = auth_client.post(
            f'{costs_base}budget-versions/',
            {'kind': 'initial'},
            format='json',
        )
        vid = create.data['id']
        project_line = auth_client.post(
            f'{costs_base}budget-versions/{vid}/lines/',
            {
                'level': 'project',
                'cost_category': 'other',
                'budget_amount': '5000',
            },
            format='json',
        )
        assert project_line.status_code == status.HTTP_201_CREATED, project_line.content

        cbs_line = auth_client.post(
            f'{costs_base}budget-versions/{vid}/lines/',
            {
                'level': 'cbs',
                'cbs': str(cbs.id),
                'cost_category': 'material',
                'budget_amount': '2000',
            },
            format='json',
        )
        assert cbs_line.status_code == status.HTTP_201_CREATED, cbs_line.content

    def test_compare_requires_fx_when_currency_differs(self, auth_client, costs_base, wbs, project, user):
        v1 = BudgetVersion.objects.create(
            project=project,
            kind=BudgetVersionKind.APPROVED,
            status=BudgetVersionStatus.APPROVED,
            version_number=1,
            currency='IRR',
            is_control=True,
            created_by=user,
            updated_by=user,
        )
        v2 = BudgetVersion.objects.create(
            project=project,
            kind=BudgetVersionKind.FINAL_FORECAST,
            status=BudgetVersionStatus.DRAFT,
            version_number=2,
            currency='USD',
            created_by=user,
            updated_by=user,
        )
        Budget.objects.create(
            project=project,
            version=v1,
            level='wbs',
            wbs=wbs,
            cost_category='labor',
            budget_amount=Decimal('100'),
            created_by=user,
            updated_by=user,
        )
        Budget.objects.create(
            project=project,
            version=v2,
            level='wbs',
            wbs=wbs,
            cost_category='labor',
            budget_amount=Decimal('1'),
            created_by=user,
            updated_by=user,
        )
        bad = auth_client.get(
            f'{costs_base}budget-versions/compare/?left={v1.id}&right={v2.id}'
        )
        assert bad.status_code == status.HTTP_400_BAD_REQUEST
        ok = auth_client.get(
            f'{costs_base}budget-versions/compare/?left={v1.id}&right={v2.id}&fx_rate=50000'
        )
        assert ok.status_code == status.HTTP_200_OK
        assert 'diffs' in ok.data

    def test_legacy_bulk_still_works(self, auth_client, costs_base, wbs):
        response = auth_client.post(
            f'{costs_base}budgets/bulk/',
            [
                {
                    'wbs': str(wbs.id),
                    'cost_category': 'material',
                    'budget_amount': '200000',
                }
            ],
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['saved'] == 1
        assert response.data.get('version_id')
