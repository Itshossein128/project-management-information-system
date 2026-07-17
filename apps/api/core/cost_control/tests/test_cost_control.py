"""Cost control API tests."""

import pytest
from decimal import Decimal
from rest_framework import status

from cost_control.models import ActualCost, Budget, CostCategory, CostPool, CostType
from cost_control.services.cost_pool_service import AllocationExceededError, auto_allocate_cost_pool
from contracts.models import Contract, ContractStatus, ContractType
from field_reports.models import DailyReport, DailyReportEquipment, DailyReportLabor, ReportStatus
from field_reports.tasks import _auto_create_costs_from_report


@pytest.fixture
def costs_base(project):
    return f'/api/v1/projects/{project.id}/'


@pytest.fixture
def budget(db, project, wbs, user):
    return Budget.objects.create(
        project=project,
        wbs=wbs,
        cost_category=CostCategory.LABOR,
        budget_amount=Decimal('1000000'),
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def cost_pool(db, project, user):
    return CostPool.objects.create(
        project=project,
        pool_name='Historical overhead',
        cost_category=CostCategory.SITE_OVERHEAD,
        total_amount=Decimal('100000'),
        created_by=user,
        updated_by=user,
    )


@pytest.mark.django_db
class TestBudgetAPI:
    def test_create_budget(self, auth_client, costs_base, wbs):
        response = auth_client.post(
            f'{costs_base}budgets/',
            {
                'wbs': str(wbs.id),
                'cost_category': 'labor',
                'budget_amount': '500000',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['budget_amount'] == '500000.00'

    def test_bulk_upsert(self, auth_client, costs_base, wbs):
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


@pytest.mark.django_db
class TestActualCostAPI:
    def test_create_and_list(self, auth_client, costs_base, activity):
        create = auth_client.post(
            f'{costs_base}costs/',
            {
                'activity': str(activity.id),
                'cost_date': '1403/05/01',
                'cost_category': 'material',
                'amount': '150000',
                'description': 'Test cost',
            },
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED

        listing = auth_client.get(f'{costs_base}costs/')
        assert listing.status_code == status.HTTP_200_OK
        assert listing.data['meta']['total_actual'] == 150000.0

    def test_auto_cost_not_editable(self, auth_client, costs_base, project, user, activity):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-08-01',
            status=ReportStatus.APPROVED,
            created_by=user,
            updated_by=user,
        )
        cost = ActualCost.objects.create(
            project=project,
            daily_report=report,
            activity=activity,
            cost_date='2024-08-01',
            cost_category='equipment',
            amount=Decimal('50000'),
            cost_type=CostType.DIRECT,
            created_by=user,
            updated_by=user,
        )
        response = auth_client.patch(
            f'{costs_base}costs/{cost.id}/',
            {'amount': '60000'},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestVarianceAndSummary:
    def test_variance_by_wbs(self, auth_client, costs_base, budget):
        response = auth_client.get(f'{costs_base}costs/variance/?group_by=wbs')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['group_by'] == 'wbs'

    def test_cost_summary_includes_committed(self, auth_client, costs_base, project, user):
        Contract.objects.create(
            project=project,
            contract_number='C-100',
            contract_type=ContractType.MAIN,
            counterparty='Employer',
            original_amount=Decimal('5000000'),
            adjusted_amount=Decimal('5500000'),
            status=ContractStatus.ACTIVE,
            created_by=user,
            updated_by=user,
        )
        response = auth_client.get(f'{costs_base}costs/summary/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_committed'] == 5500000.0


@pytest.mark.django_db
class TestCostPoolAllocation:
    def test_manual_allocate(self, auth_client, costs_base, cost_pool, activity):
        response = auth_client.post(
            f'{costs_base}cost-pools/{cost_pool.id}/allocate/',
            [{'activity_id': str(activity.id), 'amount': '40000'}],
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert float(response.data['allocated_amount']) == 40000.0

    def test_auto_allocate_by_budget_weight(self, auth_client, costs_base, cost_pool, budget, activity):
        budget.activity = activity
        budget.save(update_fields=['activity'])

        response = auth_client.post(
            f'{costs_base}cost-pools/{cost_pool.id}/auto-allocate/',
            {'method': 'by_budget_weight'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['allocations']
        assert float(response.data['pool']['allocated_amount']) > 0

    def test_allocation_exceeded(self, cost_pool, activity, user):
        from cost_control.services.cost_pool_service import allocate_cost_pool

        with pytest.raises(AllocationExceededError):
            allocate_cost_pool(
                cost_pool,
                [{'activity_id': str(activity.id), 'amount': '150000'}],
                user,
            )


@pytest.mark.django_db
class TestLaborAutoCost:
    def test_labor_auto_cost_from_report(self, project, user, activity):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-08-01',
            status=ReportStatus.APPROVED,
            approved_by=user,
            created_by=user,
            updated_by=user,
        )
        DailyReportLabor.objects.create(
            report=report,
            labor_category='direct',
            job_title='کارگر ماهر',
            shift_1_count=5,
            daily_rate=Decimal('500000'),
        )
        _auto_create_costs_from_report(report)
        labor_cost = ActualCost.objects.filter(
            project=project,
            daily_report=report,
            cost_category='labor',
        ).first()
        assert labor_cost is not None
        assert labor_cost.amount == Decimal('2500000')

    def test_equipment_auto_cost(self, project, user, activity):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-08-02',
            status=ReportStatus.APPROVED,
            approved_by=user,
            created_by=user,
            updated_by=user,
        )
        DailyReportEquipment.objects.create(
            report=report,
            equipment_name='جرثقیل',
            shift='day',
            status='active',
            ownership_type='owned',
            productive_hours=Decimal('8'),
            hourly_rate=Decimal('100000'),
            activity_ref=activity,
        )
        _auto_create_costs_from_report(report)
        cost = ActualCost.objects.get(project=project, daily_report=report, cost_category='equipment')
        assert cost.amount == Decimal('800000')


@pytest.mark.django_db
class TestCostControlPermissions:
    def test_unauthenticated_budget_list_returns_401(self, api_client, costs_base):
        response = api_client.get(f'{costs_base}budgets/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_viewer_cannot_create_budget(self, api_client, member, costs_base, wbs):
        api_client.force_authenticate(user=member.user)
        response = api_client.post(
            f'{costs_base}budgets/',
            {
                'wbs': str(wbs.id),
                'cost_category': 'labor',
                'budget_amount': '1000',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_auto_allocate_by_hours(self, auth_client, costs_base, cost_pool, project, user, activity):
        from decimal import Decimal
        from field_reports.models import DailyReport, DailyReportEquipment, ReportStatus

        report = DailyReport.objects.create(
            project=project,
            report_date='2024-09-01',
            status=ReportStatus.APPROVED,
            created_by=user,
            updated_by=user,
        )
        DailyReportEquipment.objects.create(
            report=report,
            equipment_name='لودر',
            shift='day',
            status='active',
            ownership_type='owned',
            productive_hours=Decimal('10'),
            activity_ref=activity,
        )
        response = auth_client.post(
            f'{costs_base}cost-pools/{cost_pool.id}/auto-allocate/',
            {'method': 'by_hours'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['allocations']
