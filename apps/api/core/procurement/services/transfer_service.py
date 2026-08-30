"""Inter-block material transfer — requires PM approval."""
from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from procurement.models import InternalTransfer, InventoryAllocation
from procurement.models.internal_transfer import TransferStatus


@transaction.atomic
def approve_transfer(transfer: InternalTransfer, user) -> InternalTransfer:
    if transfer.status != TransferStatus.PENDING:
        raise ValidationError({'detail': 'Transfer is not in pending state'})

    # Decrement allocation from source block
    source_alloc = InventoryAllocation.objects.filter(
        block=transfer.source_block,
        material=transfer.material,
        is_deleted=False,
    ).first()

    if source_alloc:
        source_alloc.allocated_qty = max(Decimal('0'), source_alloc.allocated_qty - transfer.quantity)
        source_alloc.received_qty = max(Decimal('0'), source_alloc.received_qty - transfer.quantity)
        source_alloc.updated_by = user
        source_alloc.save(update_fields=['allocated_qty', 'received_qty', 'updated_by', 'updated_at'])

    # Increment or create allocation for target block
    target_alloc = InventoryAllocation.objects.filter(
        block=transfer.target_block,
        material=transfer.material,
        is_deleted=False,
    ).first()

    if target_alloc:
        target_alloc.allocated_qty += transfer.quantity
        target_alloc.received_qty += transfer.quantity
        target_alloc.updated_by = user
        target_alloc.save(update_fields=['allocated_qty', 'received_qty', 'updated_by', 'updated_at'])
    else:
        req_item = source_alloc.requisition_item if source_alloc else None
        if req_item and hasattr(req_item, 'header') and req_item.header:
            mr_tag = f'{req_item.header.requisition_number}-{transfer.target_block.block_code}'
        elif source_alloc and source_alloc.mr_tag:
            mr_tag = f'{source_alloc.mr_tag}-{transfer.target_block.block_code}'
        else:
            mr_tag = f'TR-{transfer.id}-{transfer.target_block.block_code}'

        InventoryAllocation.objects.create(
            requisition_item=req_item,
            block=transfer.target_block,
            material=transfer.material,
            allocated_qty=transfer.quantity,
            received_qty=transfer.quantity,
            issued_qty=Decimal('0'),
            mr_tag=mr_tag,
            created_by=user,
            updated_by=user,
        )

    transfer.status = TransferStatus.APPROVED
    transfer.approved_by = user
    transfer.approved_at = timezone.now()
    transfer.updated_by = user
    transfer.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_by', 'updated_at'])
    return transfer


@transaction.atomic
def reject_transfer(transfer: InternalTransfer, user, reason: str = '') -> InternalTransfer:
    if transfer.status != TransferStatus.PENDING:
        raise ValidationError({'detail': 'Transfer is not in pending state'})
    transfer.status = TransferStatus.REJECTED
    transfer.cost_adjustment_notes = reason
    transfer.updated_by = user
    transfer.save(update_fields=['status', 'cost_adjustment_notes', 'updated_by', 'updated_at'])
    return transfer

