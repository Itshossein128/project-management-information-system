"""Overdue and near-due receivables report for approved IPCs (FR-CON-005)."""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from contracts.collection_service import collections_total, remaining_receivable
from contracts.models import IPC, IPCStatus


def build_receivables_report(
    *,
    project_id,
    near_due_days: int = 7,
    contract_id=None,
    as_of: date | None = None,
) -> dict:
    as_of = as_of or date.today()
    if near_due_days < 0:
        near_due_days = 0
    near_end = as_of + timedelta(days=near_due_days)

    qs = (
        IPC.objects.filter(
            project_id=project_id,
            is_deleted=False,
            status=IPCStatus.APPROVED,
            planned_payment_date__isnull=False,
        )
        .select_related('contract')
        .order_by('planned_payment_date', 'ipc_number')
    )
    if contract_id:
        qs = qs.filter(contract_id=contract_id)

    items = []
    overdue_remaining = Decimal('0')
    near_due_remaining = Decimal('0')
    overdue_count = 0
    near_due_count = 0

    for ipc in qs:
        remaining = remaining_receivable(ipc)
        if remaining <= 0:
            continue
        due = ipc.planned_payment_date
        if due < as_of:
            band = 'overdue'
            days_overdue = (as_of - due).days
            days_until_due = None
            overdue_count += 1
            overdue_remaining += remaining
        elif due <= near_end:
            band = 'near_due'
            days_overdue = None
            days_until_due = (due - as_of).days
            near_due_count += 1
            near_due_remaining += remaining
        else:
            continue

        items.append(
            {
                'ipc_id': str(ipc.id),
                'contract_id': str(ipc.contract_id),
                'contract_number': ipc.contract.contract_number,
                'ipc_number': ipc.ipc_number,
                'status': ipc.status,
                'submitted_amount': str(ipc.submitted_amount) if ipc.submitted_amount is not None else None,
                'approved_amount': str(ipc.approved_amount) if ipc.approved_amount is not None else None,
                'net_amount': str(ipc.net_amount) if ipc.net_amount is not None else None,
                'collected_total': str(collections_total(ipc)),
                'remaining_receivable': str(remaining),
                'planned_payment_date': due.isoformat(),
                'band': band,
                'days_overdue': days_overdue,
                'days_until_due': days_until_due,
            }
        )

    return {
        'as_of': as_of.isoformat(),
        'near_due_days': near_due_days,
        'summary': {
            'overdue_count': overdue_count,
            'overdue_remaining': str(overdue_remaining),
            'near_due_count': near_due_count,
            'near_due_remaining': str(near_due_remaining),
        },
        'items': items,
    }
