"""Cost pool allocation."""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from cost_control.models import ActualCost, CostPool, CostType


class AllocationExceededError(Exception):
    pass


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
