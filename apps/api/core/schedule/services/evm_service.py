"""Earned Value Management calculations."""

from __future__ import annotations

from datetime import date

from django.db.models import Sum

from cost_control.models import ActualCost, Budget
from schedule.services.progress_service import (
    get_planned_progress_on_date,
    get_project_progress_on_date,
)


def compute_evm(project_id, as_of_date: date) -> dict:
    bac = (
        Budget.objects.filter(project_id=project_id).aggregate(total=Sum('budget_amount'))['total'] or 0
    )
    actual_progress = get_project_progress_on_date(project_id, as_of_date)
    planned_progress = get_planned_progress_on_date(project_id, as_of_date)

    ev = float(bac) * actual_progress
    pv = float(bac) * planned_progress

    ac = (
        ActualCost.objects.filter(
            project_id=project_id,
            cost_date__lte=as_of_date,
        ).aggregate(total=Sum('amount'))['total']
        or 0
    )
    ac = float(ac)

    sv = ev - pv
    cv = ev - ac
    spi = ev / pv if pv else None
    cpi = ev / ac if ac else None
    eac = float(bac) / cpi if cpi else None
    etc = eac - ac if eac is not None else None
    vac = float(bac) - eac if eac is not None else None

    return {
        'as_of_date': as_of_date.strftime('%Y-%m-%d'),
        'bac': float(bac),
        'ev': ev,
        'pv': pv,
        'ac': ac,
        'sv': sv,
        'cv': cv,
        'spi': round(spi, 3) if spi is not None else None,
        'cpi': round(cpi, 3) if cpi is not None else None,
        'eac': eac,
        'etc': etc,
        'vac': vac,
        'actual_progress_pct': round(actual_progress * 100, 2),
        'planned_progress_pct': round(planned_progress * 100, 2),
        'schedule_variance_pct': round((actual_progress - planned_progress) * 100, 2),
        'budget_consumption_pct': round(ac / float(bac) * 100, 2) if bac else None,
    }
