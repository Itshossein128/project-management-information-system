"""Inter-block material transfer — requires PM approval."""
from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from procurement.models import InternalTransfer
from procurement.models.internal_transfer import TransferStatus


@transaction.atomic
def approve_transfer(transfer: InternalTransfer, user) -> InternalTransfer:
    if transfer.status != TransferStatus.PENDING:
        raise ValidationError({'detail': 'Transfer is not in pending state'})
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
