"""EV from approved progress; EV ≠ AC (FR-EVM-002/007)."""

from datetime import date
from decimal import Decimal

import pytest

from schedule.models import ActivityProgress
from schedule.services.evm_service import compute_evm
from schedule.tests.evm_fixtures import (
    create_control_budget,
    lock_schedule_baseline,
    post_actual_cost,
    set_approved_progress,
)


@pytest.mark.django_db
class TestEvmApprovedProgress:
    def test_registered_measures_with_approved_progress(self, project, user, activity, wbs):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        lock_schedule_baseline(project, user)
        create_control_budget(project, user, amount=Decimal('1000000'), wbs=wbs)
        set_approved_progress(activity, ratio=0.5)
        post_actual_cost(project, user, amount=Decimal('250000'))

        evm = compute_evm(project.id, date(2024, 10, 15))
        assert evm['ev']['status'] == 'registered'
        assert evm['pv']['status'] == 'registered'
        assert evm['ac']['status'] == 'registered'
        assert evm['ev']['amount'] == pytest.approx(500000.0)
        assert evm['ac']['amount'] == pytest.approx(250000.0)
        assert evm['meta']['ev_basis'] == 'approved_progress'

    def test_ev_uses_approved_not_unapproved_actual(self, project, user, activity, wbs):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        lock_schedule_baseline(project, user)
        create_control_budget(project, user, amount=Decimal('1000000'), wbs=wbs)
        ActivityProgress.objects.create(
            activity=activity,
            report_date=date(2024, 10, 1),
            actual_progress=0.9,
            approved_progress=None,
            planned_progress=0.5,
        )
        evm = compute_evm(project.id, date(2024, 10, 15))
        assert evm['ev']['status'] == 'unregistered'
        assert evm['ev']['amount'] is None

    def test_ev_unchanged_when_only_ac_changes(self, project, user, activity, wbs):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        lock_schedule_baseline(project, user)
        create_control_budget(project, user, amount=Decimal('1000000'), wbs=wbs)
        set_approved_progress(activity, ratio=0.4)
        post_actual_cost(project, user, amount=Decimal('100000'))
        first = compute_evm(project.id, date(2024, 10, 15))
        post_actual_cost(project, user, amount=Decimal('500000'), cost_date=date(2024, 10, 2))
        second = compute_evm(project.id, date(2024, 10, 15))
        assert first['ev']['amount'] == second['ev']['amount']
        assert second['ac']['amount'] != first['ac']['amount']
        assert second['ev']['amount'] != second['ac']['amount']

    def test_spi_cpi_sv_cv_formulas(self, project, user, activity, wbs):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        lock_schedule_baseline(project, user)
        create_control_budget(project, user, amount=Decimal('1000000'), wbs=wbs)
        ActivityProgress.objects.create(
            activity=activity,
            report_date=date(2024, 10, 1),
            actual_progress=0.5,
            approved_progress=0.5,
            planned_progress=0.4,
        )
        post_actual_cost(project, user, amount=Decimal('400000'))
        evm = compute_evm(project.id, date(2024, 10, 15))
        assert evm['spi']['status'] == 'computable'
        assert evm['cpi']['status'] == 'computable'
        assert evm['spi']['value'] == pytest.approx(0.5 / 0.4, rel=1e-3)
        assert evm['cpi']['value'] == pytest.approx(500000 / 400000, rel=1e-3)
        assert evm['sv']['value'] == pytest.approx(100000.0)
        assert evm['cv']['value'] == pytest.approx(100000.0)

    def test_unapproved_measurement_edit_does_not_change_ev(
        self, project, user, activity, wbs, approved_measurement
    ):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        lock_schedule_baseline(project, user)
        create_control_budget(project, user, amount=Decimal('1000000'), wbs=wbs)
        version = approved_measurement.versions.order_by('-version_number').first()
        set_approved_progress(activity, ratio=0.5, measurement_version=version)
        before = compute_evm(project.id, date(2024, 10, 15))
        # Unapproved draft edit on definition must not rewrite stamped approved_progress rows.
        approved_measurement.total_quantity = 200
        approved_measurement.save(update_fields=['total_quantity', 'updated_at'])
        after = compute_evm(project.id, date(2024, 10, 15))
        assert before['ev']['amount'] == after['ev']['amount']
        row = ActivityProgress.objects.filter(activity=activity).first()
        assert float(row.approved_progress) == pytest.approx(0.5)
