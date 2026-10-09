"""Block-level inventory locking — GRN receipt and stock issuance."""
from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import ValidationError

from procurement.models import (
    InventoryAllocation,
    RequisitionItem,
    ItemStatus,
)


class HardStopError(ValidationError):
    """Raised when block-level inventory rules are violated."""
    pass


def _require_positive_qty(qty: Decimal, field: str = 'quantity') -> None:
    if qty is None or qty <= 0:
        raise HardStopError({field: 'Quantity must be greater than zero'})


@transaction.atomic
def record_grn(
    requisition_item: RequisitionItem,
    received_qty: Decimal,
    user,
) -> InventoryAllocation:
    """GRN: record goods receipt and tag to MR + Block."""
    _require_positive_qty(received_qty, 'received_qty')

    item = RequisitionItem.objects.select_for_update().get(pk=requisition_item.pk)
    block = item.header.block
    mr_tag = f'{item.header.requisition_number}-{block.block_code}'

    allocation = (
        InventoryAllocation.objects.select_for_update()
        .filter(
            requisition_item=item,
            block=block,
            material=item.material,
        )
        .order_by('id')
        .first()
    )

    if allocation is None:
        allocation = InventoryAllocation.objects.create(
            requisition_item=item,
            block=block,
            material=item.material,
            allocated_qty=item.approved_qty or item.requested_qty,
            received_qty=received_qty,
            mr_tag=mr_tag,
            created_by=user,
            updated_by=user,
        )
    else:
        allocation.received_qty = (allocation.received_qty or Decimal('0')) + received_qty
        allocation.updated_by = user
        allocation.save(update_fields=['received_qty', 'updated_by', 'updated_at'])

    item.purchased_qty = (item.purchased_qty or Decimal('0')) + received_qty
    item.status = ItemStatus.DELIVERED
    item.updated_by = user
    item.save(update_fields=['purchased_qty', 'status', 'updated_by', 'updated_at'])

    return allocation


@transaction.atomic
def issue_stock(
    allocation: InventoryAllocation,
    issue_qty: Decimal,
    user,
) -> InventoryAllocation:
    """Hard Stop: issue stock against a specific MR allocation only."""
    _require_positive_qty(issue_qty, 'issue_qty')

    locked = InventoryAllocation.objects.select_for_update().get(pk=allocation.pk)
    available = locked.received_qty - locked.issued_qty
    if issue_qty > available:
        raise HardStopError(
            {
                'detail': (
                    f'صدور حواله ({issue_qty}) بیشتر از موجودی رسیدشده '
                    f'برای این MR ({available}) است — '
                    f'تگ: {locked.mr_tag}'
                )
            }
        )
    locked.issued_qty += issue_qty
    locked.updated_by = user
    locked.save(update_fields=['issued_qty', 'updated_by', 'updated_at'])
    return locked


def get_block_stock(block) -> list[dict]:
    """Return allocated/received/issued quantities for a block, grouped by material."""
    from django.db.models import Sum

    return list(
        InventoryAllocation.objects.filter(
            block=block,
            is_deleted=False,
        )
        .values('material', 'material__material_name', 'material__material_code')
        .annotate(
            total_allocated=Sum('allocated_qty'),
            total_received=Sum('received_qty'),
            total_issued=Sum('issued_qty'),
        )
        .order_by('material__material_code')
    )
