"""Budget bulk upsert and overrun warnings (version-aware)."""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from config.exceptions import CodedValidationError
from cost_control.models import Budget, BudgetLineLevel, BudgetVersionStatus
from cost_control.services.budget_version_service import (
    assert_version_editable,
    ensure_working_draft,
    get_control_version,
)


WBS_OVERRUN_WARNING = 'مجموع بودجه فعالیت‌های زیرمجموعه از بودجه WBS تجاوز می‌کند'


def budget_summary(project_id, version_id=None) -> dict:
    rows = Budget.objects.filter(project_id=project_id, is_deleted=False)
    if version_id:
        rows = rows.filter(version_id=version_id)
    else:
        control = get_control_version(project_id)
        if control:
            rows = rows.filter(version_id=control.id)
    total_bac = rows.aggregate(total=Sum('budget_amount'))['total'] or Decimal('0')
    by_category: dict[str, float] = {}
    for row in rows.values('cost_category').annotate(total=Sum('budget_amount')):
        by_category[row['cost_category']] = float(row['total'] or 0)
    return {'total_bac': float(total_bac), 'by_category': by_category}


def check_wbs_overrun(project_id, version_id=None) -> str | None:
    """Return warning message if activity budgets exceed WBS-level budget per category."""
    qs = Budget.objects.filter(
        project_id=project_id,
        is_deleted=False,
        activity__isnull=True,
        wbs__isnull=False,
    )
    if version_id:
        qs = qs.filter(version_id=version_id)
    else:
        control = get_control_version(project_id)
        if control:
            qs = qs.filter(version_id=control.id)
    for wb in qs:
        activity_sum = (
            Budget.objects.filter(
                project_id=project_id,
                is_deleted=False,
                version_id=wb.version_id,
                wbs_id=wb.wbs_id,
                activity__isnull=False,
                cost_category=wb.cost_category,
            ).aggregate(total=Sum('budget_amount'))['total']
            or 0
        )
        if float(activity_sum) > float(wb.budget_amount):
            return WBS_OVERRUN_WARNING
    return None


def _infer_level(entry: dict) -> str:
    if entry.get('level'):
        return entry['level']
    if entry.get('activity_id'):
        return BudgetLineLevel.ACTIVITY
    if entry.get('contract_id') and not entry.get('wbs_id'):
        return BudgetLineLevel.CONTRACT
    if entry.get('cbs_id') and not entry.get('wbs_id') and not entry.get('activity_id'):
        return BudgetLineLevel.CBS
    if entry.get('wbs_id'):
        return BudgetLineLevel.WBS
    return BudgetLineLevel.PROJECT


def _validate_level(entry: dict, level: str) -> None:
    if level == BudgetLineLevel.PROJECT:
        return
    if level == BudgetLineLevel.CONTRACT and not entry.get('contract_id'):
        raise CodedValidationError(
            {'contract': 'contract is required for contract-level lines.'},
            code='invalid_budget_level',
        )
    if level in (BudgetLineLevel.PHASE, BudgetLineLevel.WBS) and not entry.get('wbs_id'):
        raise CodedValidationError(
            {'wbs': 'wbs is required for this budget level.'},
            code='invalid_budget_level',
        )
    if level == BudgetLineLevel.CBS and not entry.get('cbs_id'):
        raise CodedValidationError(
            {'cbs': 'cbs is required for cbs-level lines.'},
            code='invalid_budget_level',
        )
    if level == BudgetLineLevel.ACTIVITY and not entry.get('activity_id'):
        raise CodedValidationError(
            {'activity': 'activity is required for activity-level lines.'},
            code='invalid_budget_level',
        )
    if level == BudgetLineLevel.WBS and not entry.get('wbs_id') and not entry.get('activity_id'):
        raise CodedValidationError(
            {'wbs': 'At least one of wbs or activity is required.'},
            code='invalid_budget_level',
        )


@transaction.atomic
def bulk_upsert_budgets(project_id, entries, user, version_id=None) -> tuple[list[Budget], str | None]:
    if version_id:
        from cost_control.models import BudgetVersion

        version = BudgetVersion.objects.get(pk=version_id, project_id=project_id, is_deleted=False)
    else:
        version = ensure_working_draft(project_id, user)
    assert_version_editable(version)

    saved: list[Budget] = []
    for entry in entries:
        level = _infer_level(entry)
        _validate_level(entry, level)
        lookup = {
            'project_id': project_id,
            'version_id': version.id,
            'cost_category': entry['cost_category'],
            'is_deleted': False,
            'level': level,
        }
        if entry.get('activity_id'):
            lookup['activity_id'] = entry['activity_id']
        elif entry.get('wbs_id'):
            lookup['wbs_id'] = entry['wbs_id']
            lookup['activity__isnull'] = True
        elif entry.get('contract_id'):
            lookup['contract_id'] = entry['contract_id']
            lookup['wbs__isnull'] = True
            lookup['activity__isnull'] = True
        elif entry.get('cbs_id'):
            lookup['cbs_id'] = entry['cbs_id']
            lookup['wbs__isnull'] = True
            lookup['activity__isnull'] = True
        else:
            lookup['wbs__isnull'] = True
            lookup['activity__isnull'] = True
            lookup['contract__isnull'] = True
            lookup['cbs__isnull'] = True

        defaults = {
            'budget_amount': entry['budget_amount'],
            'notes': entry.get('notes', ''),
            'cbs_id': entry.get('cbs_id'),
            'contract_id': entry.get('contract_id'),
            'period_start': entry.get('period_start'),
            'period_end': entry.get('period_end'),
            'created_by': user,
            'updated_by': user,
        }
        if entry.get('wbs_id'):
            defaults['wbs_id'] = entry['wbs_id']

        obj, created = Budget.objects.get_or_create(**lookup, defaults=defaults)
        if not created:
            obj.budget_amount = entry['budget_amount']
            obj.notes = entry.get('notes', '')
            if entry.get('cbs_id') is not None:
                obj.cbs_id = entry.get('cbs_id')
            if entry.get('contract_id') is not None:
                obj.contract_id = entry.get('contract_id')
            if 'period_start' in entry:
                obj.period_start = entry.get('period_start')
            if 'period_end' in entry:
                obj.period_end = entry.get('period_end')
            obj.updated_by = user
            obj.save()
        saved.append(obj)
    return saved, check_wbs_overrun(project_id, version_id=version.id)


def assert_line_mutable(line: Budget) -> None:
    if line.version_id and line.version.status != BudgetVersionStatus.DRAFT:
        raise CodedValidationError(
            {'version': 'Only draft budget versions can be edited.'},
            code='budget_version_locked',
        )
