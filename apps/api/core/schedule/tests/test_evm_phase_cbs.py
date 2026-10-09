"""Phase and CBS EVM slices (FR-EVM-004/010)."""

from datetime import date
from decimal import Decimal

import pytest

from cost_control.models import Budget, BudgetLineLevel, CostCategory
from projects.models import Activity
from schedule.services.evm_slice_service import build_evm_by_cbs, build_evm_by_phase
from schedule.tests.evm_fixtures import (
    create_control_budget,
    lock_schedule_baseline,
    make_cbs,
    post_actual_cost,
    set_approved_progress,
)
from wbs.services import create_wbs_node


@pytest.mark.django_db
class TestEvmPhaseCbs:
    def test_by_phase_registered_ev(self, project, user, wbs):
        lock_schedule_baseline(project, user)
        phase_a, _ = create_wbs_node(
            project_id=project.id, wbs_code='1.1', wbs_name='Phase A', parent_id=wbs.id
        )
        phase_b, _ = create_wbs_node(
            project_id=project.id, wbs_code='1.2', wbs_name='Phase B', parent_id=wbs.id
        )
        version = create_control_budget(project, user, amount=Decimal('500000'), wbs=phase_a, level=BudgetLineLevel.PHASE)
        Budget.objects.create(
            project=project,
            version=version,
            level=BudgetLineLevel.PHASE,
            wbs=phase_b,
            cost_category=CostCategory.MATERIAL,
            budget_amount=Decimal('500000'),
            currency='IRR',
            created_by=user,
            updated_by=user,
        )
        act_a = Activity.objects.create(
            project=project,
            wbs=phase_a,
            activity_code='PA1',
            activity_name='A1',
            weight=1.0,
            created_by=user,
            updated_by=user,
        )
        act_b = Activity.objects.create(
            project=project,
            wbs=phase_b,
            activity_code='PB1',
            activity_name='B1',
            weight=1.0,
            created_by=user,
            updated_by=user,
        )
        set_approved_progress(act_a, ratio=0.5)
        set_approved_progress(act_b, ratio=0.2)

        data = build_evm_by_phase(project.id, date(2024, 10, 15))
        assert len(data['phases']) >= 2
        by_code = {p['wbs_code']: p for p in data['phases']}
        assert by_code['1.1']['ev']['status'] == 'registered'
        assert by_code['1.1']['ev']['amount'] == pytest.approx(250000.0)
        assert by_code['1.2']['ev']['status'] == 'registered'

    def test_by_cbs_cpi_computable(self, project, user, activity, wbs):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        lock_schedule_baseline(project, user)
        cbs = make_cbs(project, user)
        version = create_control_budget(
            project, user, amount=Decimal('300000'), cbs=cbs, level=BudgetLineLevel.CBS
        )
        Budget.objects.create(
            project=project,
            version=version,
            level=BudgetLineLevel.ACTIVITY,
            activity=activity,
            wbs=wbs,
            cbs=cbs,
            cost_category=CostCategory.LABOR,
            budget_amount=Decimal('0'),
            currency='IRR',
            created_by=user,
            updated_by=user,
        )
        set_approved_progress(activity, ratio=0.5)
        post_actual_cost(project, user, amount=Decimal('100000'), cbs=cbs)

        data = build_evm_by_cbs(project.id, date(2024, 10, 15))
        node = next(n for n in data['nodes'] if n['cbs_code'] == 'C-100')
        assert node['ev']['status'] == 'registered'
        assert node['ac']['status'] == 'registered'
        assert node['cpi']['status'] == 'computable'

    def test_empty_slice_not_perfect_indices(self, project, user, wbs):
        lock_schedule_baseline(project, user)
        # Use root WBS as the only phase slice (no activities → unregistered EV).
        create_control_budget(project, user, amount=Decimal('100'), wbs=wbs, level=BudgetLineLevel.PHASE)
        data = build_evm_by_phase(project.id, date(2024, 10, 15))
        assert data['phases'], data
        empty = next(p for p in data['phases'] if p['wbs_id'] == str(wbs.id))
        assert empty['spi']['status'] == 'not_computable'
        assert empty['cpi']['status'] == 'not_computable'
        assert empty['spi'].get('value') in (None, 0) or empty['spi']['status'] == 'not_computable'

    def test_mixed_currency_blocked(self, project, user, wbs):
        lock_schedule_baseline(project, user)
        version = create_control_budget(
            project, user, amount=Decimal('100'), wbs=wbs, level=BudgetLineLevel.PHASE, currency='IRR'
        )
        Budget.objects.create(
            project=project,
            version=version,
            level=BudgetLineLevel.PHASE,
            wbs=wbs,
            cost_category=CostCategory.MATERIAL,
            budget_amount=Decimal('50'),
            currency='USD',
            created_by=user,
            updated_by=user,
        )
        data = build_evm_by_phase(project.id, date(2024, 10, 15))
        assert data['phases'], data
        fx = next(p for p in data['phases'] if p['wbs_id'] == str(wbs.id))
        assert fx.get('aggregation') == 'blocked' or 'mixed_currency' in fx.get('warnings', [])
        assert fx['spi']['status'] == 'not_computable'

    def test_incomplete_phase_partition_roll_up_partial(self, project, user, wbs):
        lock_schedule_baseline(project, user)
        version = create_control_budget(
            project, user, amount=Decimal('1000000'), level=BudgetLineLevel.PROJECT
        )
        phase, _ = create_wbs_node(
            project_id=project.id, wbs_code='1.1', wbs_name='Partial Phase', parent_id=wbs.id
        )
        Budget.objects.create(
            project=project,
            version=version,
            level=BudgetLineLevel.PHASE,
            wbs=phase,
            cost_category=CostCategory.LABOR,
            budget_amount=Decimal('100000'),
            currency='IRR',
            created_by=user,
            updated_by=user,
        )
        data = build_evm_by_phase(project.id, date(2024, 10, 15))
        assert data['phases'], data
        assert all(p['roll_up'] == 'partial' for p in data['phases'])
        assert float(data['project_totals']['bac']) == pytest.approx(1100000.0)

    def test_api_endpoints(self, project, user, activity, wbs, auth_client):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        lock_schedule_baseline(project, user)
        create_control_budget(project, user, wbs=wbs)
        set_approved_progress(activity, ratio=0.3)
        r1 = auth_client.get(f'/api/v1/projects/{project.id}/progress/evm/by-phase/?force_refresh=1')
        r2 = auth_client.get(f'/api/v1/projects/{project.id}/progress/evm/by-cbs/?force_refresh=1')
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert 'phases' in r1.data
        assert 'nodes' in r2.data
