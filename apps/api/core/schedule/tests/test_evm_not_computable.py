"""Not-computable / unregistered EVM semantics (FR-EVM-005/006/008)."""

from datetime import date
from decimal import Decimal

import pytest

from schedule.services.evm_service import compute_evm
from schedule.tests.evm_fixtures import (
    create_control_budget,
    lock_schedule_baseline,
    post_actual_cost,
)


@pytest.mark.django_db
class TestEvmNotComputable:
    def test_no_approved_progress_ev_unregistered(self, project, user, activity, wbs):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        lock_schedule_baseline(project, user)
        create_control_budget(project, user, wbs=wbs)
        evm = compute_evm(project.id, date(2024, 10, 15))
        assert evm['ev']['status'] == 'unregistered'
        assert evm['ev']['amount'] is None

    def test_ac_without_ev_cpi_and_cv_not_computable(self, project, user, activity, wbs):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        lock_schedule_baseline(project, user)
        create_control_budget(project, user, wbs=wbs)
        post_actual_cost(project, user, amount=Decimal('100000'))
        evm = compute_evm(project.id, date(2024, 10, 15))
        assert evm['ac']['status'] == 'registered'
        assert evm['cpi']['status'] == 'not_computable'
        assert evm['cv']['status'] == 'not_computable'

    def test_pv_zero_spi_not_computable(self, project, user, activity, wbs):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        lock_schedule_baseline(project, user)
        create_control_budget(project, user, wbs=wbs)
        from schedule.models import ActivityProgress

        ActivityProgress.objects.create(
            activity=activity,
            report_date=date(2024, 10, 1),
            approved_progress=0.5,
            planned_progress=0.0,
            actual_progress=0.5,
        )
        evm = compute_evm(project.id, date(2024, 10, 15))
        assert evm['pv']['amount'] == pytest.approx(0.0)
        assert evm['spi']['status'] == 'not_computable'
        assert evm['spi']['reason'] == 'pv_zero'

    def test_cpi_not_computable_blocks_forecasts(self, project, user, activity, wbs):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        lock_schedule_baseline(project, user)
        create_control_budget(project, user, wbs=wbs)
        post_actual_cost(project, user, amount=Decimal('50000'))
        evm = compute_evm(project.id, date(2024, 10, 15))
        assert evm['cpi']['status'] == 'not_computable'
        assert evm['eac']['status'] == 'not_computable'
        assert evm['etc']['status'] == 'not_computable'
        assert evm['vac']['status'] == 'not_computable'
        assert evm['eac']['value'] is None
