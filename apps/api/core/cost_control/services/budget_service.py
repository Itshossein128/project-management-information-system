"""Budget bulk upsert and overrun warnings."""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from cost_control.models import Budget


WBS_OVERRUN_WARNING = 'مجموع بودجه فعالیت‌های زیرمجموعه از بودجه WBS تجاوز می‌کند'


def budget_summary(project_id) -> dict:
    rows = Budget.objects.filter(project_id=project_id, is_deleted=False)
    total_bac = rows.aggregate(total=Sum('budget_amount'))['total'] or Decimal('0')
    by_category: dict[str, float] = {}
    for row in rows.values('cost_category').annotate(total=Sum('budget_amount')):
        by_category[row['cost_category']] = float(row['total'] or 0)
    return {'total_bac': float(total_bac), 'by_category': by_category}


def check_wbs_overrun(project_id) -> str | None:
    """Return warning message if activity budgets exceed WBS-level budget per category."""
    wbs_budgets = Budget.objects.filter(
        project_id=project_id,
        is_deleted=False,
        activity__isnull=True,
        wbs__isnull=False,
    )
    for wb in wbs_budgets:
        activity_sum = (
            Budget.objects.filter(
                project_id=project_id,
                is_deleted=False,
                wbs_id=wb.wbs_id,
                activity__isnull=False,
                cost_category=wb.cost_category,
            ).aggregate(total=Sum('budget_amount'))['total']
            or 0
        )
        if float(activity_sum) > float(wb.budget_amount):
            return WBS_OVERRUN_WARNING
    return None


@transaction.atomic
def bulk_upsert_budgets(project_id, entries, user) -> tuple[list[Budget], str | None]:
    saved: list[Budget] = []
    for entry in entries:
        lookup = {
            'project_id': project_id,
            'cost_category': entry['cost_category'],
            'is_deleted': False,
        }
        if entry.get('activity_id'):
            lookup['activity_id'] = entry['activity_id']
        elif entry.get('wbs_id'):
            lookup['wbs_id'] = entry['wbs_id']
            lookup['activity__isnull'] = True

        obj, created = Budget.objects.get_or_create(
            **lookup,
            defaults={
                'budget_amount': entry['budget_amount'],
                'notes': entry.get('notes', ''),
                'created_by': user,
                'updated_by': user,
            },
        )
        if not created:
            obj.budget_amount = entry['budget_amount']
            obj.notes = entry.get('notes', '')
            obj.updated_by = user
            obj.save()
        saved.append(obj)
    return saved, check_wbs_overrun(project_id)
