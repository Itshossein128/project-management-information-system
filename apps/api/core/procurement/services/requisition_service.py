"""Requisition CRUD + business logic."""
from __future__ import annotations

from django.db import transaction
from rest_framework.exceptions import ValidationError

from procurement.models import (
    ItemStatus,
    RequisitionHeader,
    RequisitionItem,
    RequisitionStatus,
)


@transaction.atomic
def assign_items(
    requisition: RequisitionHeader,
    assignments: list[dict],  # [{item_id, assigned_to_id}]
    user,
) -> list[RequisitionItem]:
    """Line-item splitting — assign items to different procurement officers."""
    updated = []
    for assignment in assignments:
        item_id = assignment.get('item_id')
        assigned_to_id = assignment.get('assigned_to_id')
        try:
            item = requisition.items.get(id=item_id, is_deleted=False)
        except RequisitionItem.DoesNotExist:
            raise ValidationError({'detail': f'Item {item_id} not found in this requisition'})
        item.assigned_to_id = assigned_to_id
        item.updated_by = user
        item.save(update_fields=['assigned_to', 'updated_by', 'updated_at'])
        updated.append(item)
    return updated


@transaction.atomic
def partial_approve_items(
    requisition: RequisitionHeader,
    approvals: list[dict],  # [{item_id, approved_qty}]
    user,
) -> list[RequisitionItem]:
    """Approve/hold individual line items — partial fulfillment support."""
    if requisition.status != RequisitionStatus.FINAL_APPROVAL:
        raise ValidationError(
            {'detail': 'Partial approval only allowed at final_approval stage'}
        )
    updated = []
    for approval in approvals:
        item_id = approval.get('item_id')
        approved_qty = approval.get('approved_qty')
        try:
            item = requisition.items.get(id=item_id, is_deleted=False)
        except RequisitionItem.DoesNotExist:
            raise ValidationError({'detail': f'Item {item_id} not found'})
        if approved_qty is None or approved_qty <= 0:
            item.status = ItemStatus.ON_HOLD
            item.approved_qty = None
        else:
            item.approved_qty = approved_qty
            item.status = ItemStatus.APPROVED
        item.updated_by = user
        item.save(update_fields=['approved_qty', 'status', 'updated_by', 'updated_at'])
        updated.append(item)
    return updated


@transaction.atomic
def put_item_on_hold(item: RequisitionItem, user) -> RequisitionItem:
    """Put a requisition item On-Hold (awaiting budget)."""
    item.status = ItemStatus.ON_HOLD
    item.updated_by = user
    item.save(update_fields=['status', 'updated_by', 'updated_at'])
    return item
