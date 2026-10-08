"""IPC partial collection helpers — never mutate IPC gross/net amounts."""
from __future__ import annotations

from decimal import Decimal

from django.db.models import Sum
from rest_framework.exceptions import ValidationError

from contracts.models import IPC, IPCCollection


def collections_total(ipc: IPC) -> Decimal:
    total = (
        IPCCollection.objects.filter(ipc=ipc, is_deleted=False).aggregate(t=Sum('amount'))['t']
        or 0
    )
    return Decimal(total)


def payable_net(ipc: IPC) -> Decimal:
    if ipc.net_amount is not None:
        return Decimal(ipc.net_amount)
    return Decimal(ipc.gross_amount or 0)


def remaining_receivable(ipc: IPC) -> Decimal:
    return payable_net(ipc) - collections_total(ipc)


def add_collection(*, ipc: IPC, amount, collected_at, user, currency='IRR', fx_rate=None, reference='', notes='') -> IPCCollection:
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
    # Snapshot original amounts for invariant checks by callers/tests.
    return IPCCollection.objects.create(
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
