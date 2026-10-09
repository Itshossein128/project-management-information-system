"""IPC partial collection helpers — never mutate IPC amounts or approval status."""
from __future__ import annotations

from decimal import Decimal

from django.db.models import Sum
from rest_framework.exceptions import ValidationError

from config.exceptions import CodedValidationError
from contracts.models import IPC, IPCCollection, IPCStatus


def collections_total(ipc: IPC) -> Decimal:
    total = (
        IPCCollection.objects.filter(ipc=ipc, is_deleted=False).aggregate(t=Sum('amount'))['t']
        or 0
    )
    return Decimal(total)


def payable_net(ipc: IPC) -> Decimal:
    if ipc.net_amount is not None:
        return Decimal(ipc.net_amount)
    if ipc.approved_amount is not None:
        return Decimal(ipc.approved_amount)
    return Decimal(ipc.gross_amount or 0)


def remaining_receivable(ipc: IPC) -> Decimal:
    return payable_net(ipc) - collections_total(ipc)


def add_collection(*, ipc: IPC, amount, collected_at, user, currency='IRR', fx_rate=None, reference='', notes='') -> IPCCollection:
    """
    Record a partial cash receipt. NEVER changes IPC status, submitted_amount,
    approved_amount, gross_amount, or net_amount. Full collection does NOT auto-mark paid.
    """
    if ipc.status != IPCStatus.APPROVED:
        raise CodedValidationError(
            detail='Collections are only allowed on approved IPCs.',
            code='collection_requires_approved',
        )
    amount = Decimal(amount)
    if amount <= 0:
        raise ValidationError({'amount': 'Must be greater than zero'})
    if collections_total(ipc) + amount > payable_net(ipc):
        raise ValidationError(
            {
                'code': 'collection_exceeds_payable',
                'message': 'Collection would exceed IPC payable amount.',
            }
        )

    before_status = ipc.status
    before_gross = ipc.gross_amount
    before_net = ipc.net_amount
    before_submitted = ipc.submitted_amount
    before_approved = ipc.approved_amount

    row = IPCCollection.objects.create(
        ipc=ipc,
        amount=amount,
        currency=currency or 'IRR',
        fx_rate=fx_rate,
        collected_at=collected_at,
        reference=reference or '',
        notes=notes or '',
        created_by=user,
        updated_by=user,
    )

    ipc.refresh_from_db()
    if (
        ipc.status != before_status
        or ipc.gross_amount != before_gross
        or ipc.net_amount != before_net
        or ipc.submitted_amount != before_submitted
        or ipc.approved_amount != before_approved
    ):
        raise CodedValidationError(
            detail='Collection must not mutate IPC status or amounts.',
            code='collection_mutated_ipc',
        )
    return row
