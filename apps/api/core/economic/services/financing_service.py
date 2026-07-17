"""Financing cost from delayed IPC payments."""

from __future__ import annotations

from contracts.models import IPC, IPCStatus

ANNUAL_FINANCING_RATE = 0.28


def compute_financing_cost(project_id) -> dict:
    paid_ipcs = IPC.objects.filter(
        project_id=project_id,
        status=IPCStatus.PAID,
        planned_payment_date__isnull=False,
        actual_payment_date__isnull=False,
        contract__contract_type='main',
        is_deleted=False,
    ).select_related('contract')

    total_financing_cost = 0.0
    details = []
    for ipc in paid_ipcs:
        delay = (ipc.actual_payment_date - ipc.planned_payment_date).days
        if delay > 0:
            cost = float(ipc.net_amount or ipc.gross_amount or 0) * ANNUAL_FINANCING_RATE * delay / 365
            total_financing_cost += cost
            details.append({
                'ipc_id': str(ipc.id),
                'ipc_number': ipc.ipc_number,
                'net_amount': float(ipc.net_amount or 0),
                'delay_days': delay,
                'financing_cost': cost,
            })

    avg_delay = sum(d['delay_days'] for d in details) / len(details) if details else 0
    return {
        'total_financing_cost': total_financing_cost,
        'avg_payment_delay_days': avg_delay,
        'details': details,
    }
