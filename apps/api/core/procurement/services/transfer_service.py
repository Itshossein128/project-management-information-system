"""Inter-block material transfer — requires PM approval."""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from procurement.models import InternalTransfer, InventoryAllocation
from procurement.models.internal_transfer import TransferStatus


def _lock_allocations_by_ids(ids: list[UUID]) -> dict[UUID, InventoryAllocation]:
    """Lock allocation rows in a stable order to avoid deadlocks."""
    if not ids:
        return {}
    ordered = sorted(set(ids), key=str)
    return {
        row.id: row
        for row in (
            InventoryAllocation.objects.select_for_update()
            .filter(id__in=ordered)
            .order_by('id')
        )
    }


@transaction.atomic
def approve_transfer(transfer: InternalTransfer, user) -> InternalTransfer:
    locked_transfer = InternalTransfer.objects.select_for_update().get(pk=transfer.pk)
    if locked_transfer.status != TransferStatus.PENDING:
        raise ValidationError({'detail': 'Transfer is not in pending state'})

    qty = locked_transfer.quantity
    if qty is None or qty <= 0:
        raise ValidationError({'quantity': 'Transfer quantity must be greater than zero'})

    source_ids = list(
        InventoryAllocation.objects.filter(
            block=locked_transfer.source_block,
            material=locked_transfer.material,
        ).values_list('id', flat=True)
    )
    target_ids = list(
        InventoryAllocation.objects.filter(
            block=locked_transfer.target_block,
            material=locked_transfer.material,
        ).values_list('id', flat=True)
    )
    locked_rows = _lock_allocations_by_ids(source_ids + target_ids)

    source_alloc = None
    for sid in sorted(source_ids, key=str):
        if sid in locked_rows:
            source_alloc = locked_rows[sid]
            break

    if source_alloc is None:
        raise ValidationError({'detail': 'No source allocation found for transfer'})

    available = source_alloc.received_qty - source_alloc.issued_qty
    if qty > available:
        raise ValidationError(
            {
                'detail': (
                    f'Transfer quantity ({qty}) exceeds available stock ({available}) '
                    f'for material on source block'
                )
            }
        )
    if qty > source_alloc.allocated_qty:
        raise ValidationError(
            {
                'detail': (
                    f'Transfer quantity ({qty}) exceeds allocated quantity '
                    f'({source_alloc.allocated_qty}) on source block'
                )
            }
        )

    source_alloc.allocated_qty -= qty
    source_alloc.received_qty -= qty
    source_alloc.updated_by = user
    source_alloc.save(
        update_fields=['allocated_qty', 'received_qty', 'updated_by', 'updated_at']
    )

    # Re-query under the source lock so a target created by a prior serialized
    # transfer is visible (pre-lock target_ids can be stale).
    target_alloc = (
        InventoryAllocation.objects.select_for_update()
        .filter(
            block=locked_transfer.target_block,
            material=locked_transfer.material,
        )
        .order_by('id')
        .first()
    )

    if target_alloc is not None:
        target_alloc.allocated_qty += qty
        target_alloc.received_qty += qty
        target_alloc.updated_by = user
        target_alloc.save(
            update_fields=['allocated_qty', 'received_qty', 'updated_by', 'updated_at']
        )
    else:
        req_item = source_alloc.requisition_item
        if req_item and hasattr(req_item, 'header') and req_item.header:
            mr_tag = (
                f'{req_item.header.requisition_number}-'
                f'{locked_transfer.target_block.block_code}'
            )
        elif source_alloc.mr_tag:
            mr_tag = f'{source_alloc.mr_tag}-{locked_transfer.target_block.block_code}'
        else:
            mr_tag = f'TR-{locked_transfer.id}-{locked_transfer.target_block.block_code}'

        InventoryAllocation.objects.create(
            requisition_item=req_item,
            block=locked_transfer.target_block,
            material=locked_transfer.material,
            allocated_qty=qty,
            received_qty=qty,
            issued_qty=Decimal('0'),
            mr_tag=mr_tag,
            created_by=user,
            updated_by=user,
        )

    locked_transfer.status = TransferStatus.APPROVED
    locked_transfer.approved_by = user
    locked_transfer.approved_at = timezone.now()
    locked_transfer.updated_by = user
    locked_transfer.save(
        update_fields=['status', 'approved_by', 'approved_at', 'updated_by', 'updated_at']
    )
    return locked_transfer


@transaction.atomic
def reject_transfer(transfer: InternalTransfer, user, reason: str = '') -> InternalTransfer:
    locked_transfer = InternalTransfer.objects.select_for_update().get(pk=transfer.pk)
    if locked_transfer.status != TransferStatus.PENDING:
        raise ValidationError({'detail': 'Transfer is not in pending state'})
    locked_transfer.status = TransferStatus.REJECTED
    locked_transfer.cost_adjustment_notes = reason
    locked_transfer.updated_by = user
    locked_transfer.save(
        update_fields=['status', 'cost_adjustment_notes', 'updated_by', 'updated_at']
    )
    return locked_transfer
