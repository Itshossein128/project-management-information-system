"""Finish forecasts EAC/ETC/VAC (common method)."""

from datetime import date
from decimal import Decimal

import pytest

from schedule.models import ActivityProgress
from schedule.services.evm_service import compute_evm
from schedule.tests.evm_fixtures import (
    create_control_budget,
    lock_schedule_baseline,
    post_actual_cost,
)


@pytest.mark.django_db
class TestEvmForecast:
    def test_common_method_eac_etc_vac(self, project, user, activity, wbs):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        lock_schedule_baseline(project, user)
        create_control_budget(project, user, amount=Decimal('1000000'), wbs=wbs)
        ActivityProgress.objects.create(
            activity=activity,
            report_date=date(2024, 10, 1),
            approved_progress=0.5,
            planned_progress=0.5,
            actual_progress=0.5,
        )
        post_actual_cost(project, user, amount=Decimal('400000'))
        evm = compute_evm(project.id, date(2024, 10, 15))
        cpi = evm['cpi']['value']
        bac = evm['bac']
        assert evm['eac']['status'] == 'computable'
        assert evm['eac']['value'] == pytest.approx(bac / cpi)
        assert evm['etc']['value'] == pytest.approx(evm['eac']['value'] - 400000)
        assert evm['vac']['value'] == pytest.approx(bac - evm['eac']['value'])

    def test_meta_eac_method(self, project, user, activity, wbs):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        lock_schedule_baseline(project, user)
        create_control_budget(project, user, wbs=wbs)
        evm = compute_evm(project.id, date(2024, 10, 15))
        assert evm['meta']['eac_method'] == 'bac_over_cpi'

    def test_forecast_not_computable_without_cpi(self, project, user, activity, wbs):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        lock_schedule_baseline(project, user)
        create_control_budget(project, user, wbs=wbs)
        evm = compute_evm(project.id, date(2024, 10, 15))
        assert evm['cpi']['status'] == 'not_computable'
        assert evm['eac']['status'] == 'not_computable'
