"""Cost summary for dashboards and EVM."""

from __future__ import annotations

from datetime import date

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models.functions import TruncMonth

import jdatetime

from contracts.models import Contract, ContractStatus
from cost_control.models import ActualCost, Budget, CostCategory
from cost_control.services.variance_service import get_budget_vs_actual


def cost_summary(project_id, as_of_date: date | None = None) -> dict:
    if as_of_date is None:
        as_of_date = date.today()

    total_budget = (
        Budget.objects.filter(project_id=project_id, is_deleted=False).aggregate(
            total=Sum('budget_amount')
        )['total']
        or 0
    )
    total_actual = (
        ActualCost.objects.filter(
            project_id=project_id,
            is_deleted=False,
            cost_date__lte=as_of_date,
        ).aggregate(total=Sum('amount'))['total']
        or 0
    )

    by_category: dict = {}
    for cat, _label in CostCategory.choices:
        b = (
            Budget.objects.filter(
                project_id=project_id, is_deleted=False, cost_category=cat
            ).aggregate(total=Sum('budget_amount'))['total']
            or 0
        )
        a = (
            ActualCost.objects.filter(
                project_id=project_id,
                is_deleted=False,
                cost_category=cat,
                cost_date__lte=as_of_date,
            ).aggregate(total=Sum('amount'))['total']
            or 0
        )
        by_category[cat] = {'budget': float(b), 'actual': float(a)}

    cost_trend = []
    cumulative = 0.0
    monthly = (
        ActualCost.objects.filter(project_id=project_id, is_deleted=False, cost_date__lte=as_of_date)
        .annotate(month=TruncMonth('cost_date'))
        .values('month')
        .annotate(actual=Sum('amount'))
        .order_by('month')
    )
    for row in monthly:
        actual = float(row['actual'] or 0)
        cumulative += actual
        jmonth = jdatetime.date.fromgregorian(date=row['month']).strftime('%Y/%m')
        cost_trend.append({'month': jmonth, 'actual': actual, 'cumulative': cumulative})

    consumption = float(total_actual) / float(total_budget) * 100 if total_budget else None

    total_committed = (
        Contract.objects.filter(
            project_id=project_id,
            is_deleted=False,
            status__in=[ContractStatus.ACTIVE, ContractStatus.SUSPENDED],
        ).aggregate(total=Sum(Coalesce('adjusted_amount', 'original_amount')))['total']
        or 0
    )

    return {
        'total_budget': float(total_budget),
        'total_actual': float(total_actual),
        'total_committed': float(total_committed),
        'budget_consumption_pct': round(consumption, 2) if consumption is not None else None,
        'by_category': by_category,
        'by_wbs': get_budget_vs_actual(project_id, group_by='wbs', as_of_date=as_of_date),
        'cost_trend': cost_trend,
    }
