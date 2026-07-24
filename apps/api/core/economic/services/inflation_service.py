"""Inflation adjustment calculations."""

from __future__ import annotations

from django.db import models

from economic.models import CostCategoryInflationMapping, InflationIndex

# Alternate names accepted when looking up an index (mapping name → aliases).
INDEX_ALIASES: dict[str, tuple[str, ...]] = {
    'نیروی کار': ('Labor', 'labor'),
    'فولاد': ('Construction Materials', 'Steel'),
    'سیمان': ('Construction Materials', 'Cement'),
    'CPI': ('Consumer Price Index',),
    'Construction Materials': ('فولاد', 'سیمان'),
}


def get_index_value(index_name: str, on_date) -> float:
    """Latest index value on or before ``on_date``; tries aliases; defaults to 100."""
    names = (index_name, *INDEX_ALIASES.get(index_name, ()))
    record = (
        InflationIndex.objects.filter(index_name__in=names, index_date__lte=on_date)
        .order_by('-index_date')
        .first()
    )
    return float(record.index_value) if record else 100.0


def adjust_cost_for_inflation(amount, cost_category, cost_date, target_date, project_id=None) -> float:
    mappings = CostCategoryInflationMapping.objects.filter(cost_category=cost_category).filter(
        models.Q(project_id=project_id) | models.Q(project__isnull=True)
    ).order_by(models.Case(models.When(project_id=project_id, then=0), default=1))

    if not mappings.exists():
        return float(amount)

    adjusted = 0.0
    for mapping in mappings:
        index_at_cost = get_index_value(mapping.index_name, cost_date)
        index_at_target = get_index_value(mapping.index_name, target_date)
        ratio = index_at_target / index_at_cost if index_at_cost > 0 else 1.0
        adjusted += float(amount) * float(mapping.weight) * ratio
    return adjusted


def compute_total_inflation_adjusted_cost(project_id, as_of_date) -> float:
    from cost_control.models import ActualCost

    costs = ActualCost.objects.filter(
        project_id=project_id, is_deleted=False, cost_date__lte=as_of_date
    )
    total = 0.0
    for cost in costs:
        total += adjust_cost_for_inflation(
            cost.amount,
            cost.cost_category or 'other',
            cost.cost_date,
            as_of_date,
            project_id=project_id,
        )
    return total


def inflation_detail_by_category(project_id, as_of_date) -> list[dict]:
    from cost_control.models import ActualCost
    from django.db.models import Sum

    rows = []
    categories = (
        ActualCost.objects.filter(project_id=project_id, is_deleted=False, cost_date__lte=as_of_date)
        .values('cost_category')
        .annotate(nominal=Sum('amount'))
    )
    for row in categories:
        cat = row['cost_category'] or 'other'
        nominal = float(row['nominal'] or 0)
        adjusted = 0.0
        costs = ActualCost.objects.filter(
            project_id=project_id, is_deleted=False, cost_category=cat, cost_date__lte=as_of_date
        )
        for cost in costs:
            adjusted += adjust_cost_for_inflation(
                cost.amount, cat, cost.cost_date, as_of_date, project_id=project_id
            )
        factor = adjusted / nominal if nominal else 1.0
        rows.append({
            'cost_category': cat,
            'nominal_cost': nominal,
            'adjusted_cost': adjusted,
            'inflation_factor': factor,
            'difference': adjusted - nominal,
        })
    return rows
