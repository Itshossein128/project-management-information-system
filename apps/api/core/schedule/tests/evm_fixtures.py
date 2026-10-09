"""Shared helpers for EVM gap tests."""

from datetime import date
from decimal import Decimal

from django.utils import timezone

from cost_control.models import (
    ActualCost,
    ActualCostStatus,
    Budget,
    BudgetLineLevel,
    BudgetVersion,
    BudgetVersionKind,
    BudgetVersionStatus,
    CostBreakdownNode,
    CostCategory,
)
from schedule.models import ActivityProgress, BaselineSchedule


def lock_schedule_baseline(project, user):
    return BaselineSchedule.objects.create(
        project=project,
        version_name='BL-EVM',
        is_current=True,
        is_locked=True,
        locked_at=timezone.now(),
        locked_by=user,
        created_by=user,
        updated_by=user,
    )


def create_control_budget(project, user, *, amount=Decimal('1000000'), wbs=None, cbs=None, level=None, currency='IRR'):
    version = BudgetVersion.objects.create(
        project=project,
        kind=BudgetVersionKind.APPROVED,
        status=BudgetVersionStatus.APPROVED,
        version_number=1,
        name='Control',
        currency=currency,
        is_control=True,
        approved_at=timezone.now(),
        approved_by=user,
        created_by=user,
        updated_by=user,
    )
    if level is None:
        if cbs is not None:
            level = BudgetLineLevel.CBS
        elif wbs is not None:
            level = BudgetLineLevel.WBS
        else:
            level = BudgetLineLevel.PROJECT
    Budget.objects.create(
        project=project,
        version=version,
        level=level,
        wbs=wbs,
        cbs=cbs,
        cost_category=CostCategory.LABOR,
        budget_amount=amount,
        currency=currency,
        created_by=user,
        updated_by=user,
    )
    return version


def set_approved_progress(activity, *, ratio=0.5, report_date=None, measurement_version=None):
    report_date = report_date or date(2024, 10, 1)
    return ActivityProgress.objects.create(
        activity=activity,
        report_date=report_date,
        actual_progress=ratio,
        approved_progress=ratio,
        planned_progress=ratio,
        measurement_version=measurement_version,
    )


def post_actual_cost(project, user, *, amount=Decimal('250000'), cbs=None, wbs=None, activity=None, cost_date=None):
    return ActualCost.objects.create(
        project=project,
        amount=amount,
        cost_date=cost_date or date(2024, 10, 1),
        status=ActualCostStatus.APPROVED,
        cost_category=CostCategory.LABOR,
        cbs=cbs,
        wbs=wbs,
        activity=activity,
        created_by=user,
        updated_by=user,
    )


def make_cbs(project, user, code='C-100', name='Concrete'):
    return CostBreakdownNode.add_root(
        project=project,
        cbs_code=code,
        cbs_name=name,
        created_by=user,
    )
