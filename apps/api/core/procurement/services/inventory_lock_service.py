"""Block-level inventory locking — GRN receipt and stock issuance."""
from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import ValidationError

from procurement.models import (
    Block,
    InventoryAllocation,
    RequisitionItem,
    ItemStatus,
)


class HardStopError(ValidationError):
    """Raised when block-level inventory rules are violated."""
    pass


@transaction.atomic
def record_grn(
    requisition_item: RequisitionItem,
    received_qty: Decimal,
    user,
) -> InventoryAllocation:
    """GRN: record goods receipt and tag to MR + Block."""
    block = requisition_item.header.block
    mr_tag = f'{requisition_item.header.requisition_number}-{block.block_code}'

    allocation, created = InventoryAllocation.objects.get_or_create(
        requisition_item=requisition_item,
        block=block,
        material=requisition_item.material,
        defaults={
            'allocated_qty': requisition_item.approved_qty or requisition_item.requested_qty,
            'mr_tag': mr_tag,
            'created_by': user,
            'updated_by': user,
        },
    )

    if not created:
        allocation.updated_by = user

    allocation.received_qty = (allocation.received_qty or Decimal('0')) + received_qty
    allocation.save(update_fields=['received_qty', 'updated_by', 'updated_at'])

    # Update item purchased_qty
    requisition_item.purchased_qty = (
        requisition_item.purchased_qty or Decimal('0')
    ) + received_qty
    requisition_item.status = ItemStatus.DELIVERED
    requisition_item.updated_by = user
    requisition_item.save(update_fields=['purchased_qty', 'status', 'updated_by', 'updated_at'])

    return allocation


@transaction.atomic
def issue_stock(
    allocation: InventoryAllocation,
    issue_qty: Decimal,
    user,
) -> InventoryAllocation:
    """Hard Stop: issue stock against a specific MR allocation only."""
    available = allocation.received_qty - allocation.issued_qty
    if issue_qty > available:
        raise HardStopError(
            {
                'detail': (
                    f'صدور حواله ({issue_qty}) بیشتر از موجودی رسیدشده '
                    f'برای این MR ({available}) است — '
                    f'تگ: {allocation.mr_tag}'
                )
            }
        )
    allocation.issued_qty += issue_qty
    allocation.updated_by = user
    allocation.save(update_fields=['issued_qty', 'updated_by', 'updated_at'])
    return allocation


def get_block_stock(block: Block) -> list[dict]:
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
