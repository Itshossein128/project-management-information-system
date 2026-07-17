"""Cost pool allocation."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import Sum

from cost_control.models import ActualCost, Budget, CostPool, CostType


class AllocationExceededError(Exception):
    pass


ALLOCATION_METHODS = frozenset({'by_budget_weight', 'by_quantity', 'by_hours'})


def _quantize_amount(value: Decimal) -> Decimal:
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def compute_auto_allocations(pool: CostPool, method: str, activity_ids: list | None = None) -> list[dict]:
    """Compute allocation rows for the remaining pool amount using the given method."""
    if method not in ALLOCATION_METHODS:
        raise ValueError(f'Unknown allocation method: {method}')

    remaining = Decimal(pool.total_amount or 0) - Decimal(pool.allocated_amount or 0)
    if remaining <= 0:
        return []

    from projects.models import Activity

    activities = Activity.objects.filter(project_id=pool.project_id, is_deleted=False)
    if activity_ids:
        activities = activities.filter(id__in=activity_ids)
    activities = list(activities.select_related('wbs'))
    if not activities:
        return []

    weights: dict = {}
    if method == 'by_budget_weight':
        budgets = (
            Budget.objects.filter(
                project_id=pool.project_id,
                is_deleted=False,
                activity_id__in=[a.id for a in activities],
            )
            .values('activity_id')
            .annotate(total=Sum('budget_amount'))
        )
        for row in budgets:
            if row['total']:
                weights[row['activity_id']] = Decimal(str(row['total']))
    elif method == 'by_quantity':
        for activity in activities:
            if activity.total_quantity:
                weights[activity.id] = Decimal(str(activity.total_quantity))
    elif method == 'by_hours':
        from field_reports.models import DailyReportEquipment

        equip_hours = (
            DailyReportEquipment.objects.filter(
                report__project_id=pool.project_id,
                report__is_deleted=False,
                is_deleted=False,
                activity_ref_id__isnull=False,
            )
            .values('activity_ref_id')
            .annotate(total=Sum('productive_hours'))
        )
        for row in equip_hours:
            aid = row['activity_ref_id']
            if aid and row['total']:
                weights[aid] = weights.get(aid, Decimal('0')) + Decimal(str(row['total']))

    if not weights:
        # Equal split fallback when no weight data exists
        per_activity = _quantize_amount(remaining / len(activities))
        return [
            {
                'activity_id': str(activity.id),
                'amount': per_activity,
                'allocation_method': method,
            }
            for activity in activities
        ]

    total_weight = sum(weights.values())
    allocations = []
    distributed = Decimal('0')
    activity_list = [a for a in activities if a.id in weights]
    for idx, activity in enumerate(activity_list):
        if idx == len(activity_list) - 1:
            amount = remaining - distributed
        else:
            share = weights[activity.id] / total_weight
            amount = _quantize_amount(remaining * share)
            distributed += amount
        if amount > 0:
            allocations.append(
                {
                    'activity_id': str(activity.id),
                    'amount': amount,
                    'allocation_method': method,
                }
            )
    return allocations


@transaction.atomic
def allocate_cost_pool(pool: CostPool, allocations: list[dict], user) -> CostPool:
    remaining = Decimal(pool.total_amount or 0) - Decimal(pool.allocated_amount or 0)
    total_requested = sum(Decimal(str(a['amount'])) for a in allocations)
    if total_requested > remaining:
        raise AllocationExceededError('Sum of allocations exceeds remaining pool amount.')

    for item in allocations:
        ActualCost.objects.create(
            project=pool.project,
            activity_id=item.get('activity_id'),
            cost_date=item.get('cost_date') or pool.created_at.date(),
            cost_category=pool.cost_category,
            amount=item['amount'],
            description=f"تخصیص از {pool.pool_name}",
            cost_type=CostType.ALLOCATED_HISTORICAL,
            confidence_level=item.get('confidence_level', pool.confidence_level),
            allocation_method=item.get('allocation_method', ''),
            cost_pool=pool,
            created_by=user,
            updated_by=user,
        )
        pool.allocated_amount = Decimal(pool.allocated_amount or 0) + Decimal(str(item['amount']))

    pool.updated_by = user
    pool.save()
    return pool


@transaction.atomic
def auto_allocate_cost_pool(
    pool: CostPool,
    method: str,
    user,
    activity_ids: list | None = None,
) -> tuple[CostPool, list[dict]]:
    allocations = compute_auto_allocations(pool, method, activity_ids=activity_ids)
    if not allocations:
        return pool, []
    pool = allocate_cost_pool(pool, allocations, user)
    return pool, allocations
