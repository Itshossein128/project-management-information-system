"""Budget vs actual variance calculations."""

from __future__ import annotations

from datetime import date

from django.db.models import Sum

from cost_control.models import ActualCost, Budget, CostCategory


def get_budget_vs_actual(project_id, group_by='wbs', as_of_date: date | None = None):
    if as_of_date is None:
        as_of_date = date.today()

    budgets = Budget.objects.filter(project_id=project_id, is_deleted=False)
    actuals = ActualCost.objects.filter(
        project_id=project_id,
        cost_date__lte=as_of_date,
        is_deleted=False,
    )

    if group_by == 'category':
        return _group_by_category(budgets, actuals)
    if group_by == 'activity':
        return _group_by_activity(budgets, actuals)
    return _group_by_wbs(budgets, actuals)


def _empty_row(key, **extra):
    row = {'budget': 0.0, 'actual': 0.0}
    row.update(extra)
    return row


def _finalize(rows: dict) -> list[dict]:
    for item in rows.values():
        item['variance'] = item['budget'] - item['actual']
        item['consumption_pct'] = (
            item['actual'] / item['budget'] * 100 if item['budget'] else None
        )
    return list(rows.values())


def _group_by_wbs(budgets, actuals):
    result: dict[str, dict] = {}
    for b in budgets.select_related('wbs'):
        key = str(b.wbs_id) if b.wbs_id else 'unassigned'
        result.setdefault(
            key,
            _empty_row(
                key,
                wbs_id=b.wbs_id,
                wbs_code=b.wbs.wbs_code if b.wbs else None,
                wbs_name=b.wbs.wbs_name if b.wbs else 'تخصیص‌نیافته',
            ),
        )
        result[key]['budget'] += float(b.budget_amount)
    for a in actuals.select_related('wbs'):
        key = str(a.wbs_id) if a.wbs_id else 'unassigned'
        result.setdefault(
            key,
            _empty_row(
                key,
                wbs_id=a.wbs_id,
                wbs_code=a.wbs.wbs_code if a.wbs else None,
                wbs_name=a.wbs.wbs_name if a.wbs else 'تخصیص‌نیافته',
            ),
        )
        result[key]['actual'] += float(a.amount)
    return _finalize(result)


def _group_by_activity(budgets, actuals):
    result: dict[str, dict] = {}
    for b in budgets.select_related('activity'):
        key = str(b.activity_id) if b.activity_id else 'unassigned'
        result.setdefault(
            key,
            _empty_row(
                key,
                activity_id=b.activity_id,
                activity_code=b.activity.activity_code if b.activity else None,
                activity_name=b.activity.activity_name if b.activity else 'تخصیص‌نیافته',
            ),
        )
        result[key]['budget'] += float(b.budget_amount)
    for a in actuals.select_related('activity'):
        key = str(a.activity_id) if a.activity_id else 'unassigned'
        result.setdefault(
            key,
            _empty_row(
                key,
                activity_id=a.activity_id,
                activity_code=a.activity.activity_code if a.activity else None,
                activity_name=a.activity.activity_name if a.activity else 'تخصیص‌نیافته',
            ),
        )
        result[key]['actual'] += float(a.amount)
    return _finalize(result)


def _group_by_category(budgets, actuals):
    result: dict[str, dict] = {}
    for cat, _label in CostCategory.choices:
        result[cat] = _empty_row(cat, cost_category=cat)
    for b in budgets:
        result.setdefault(b.cost_category, _empty_row(b.cost_category, cost_category=b.cost_category))
        result[b.cost_category]['budget'] += float(b.budget_amount)
    for a in actuals:
        cat = a.cost_category or 'other'
        result.setdefault(cat, _empty_row(cat, cost_category=cat))
        result[cat]['actual'] += float(a.amount)
    return _finalize(result)
