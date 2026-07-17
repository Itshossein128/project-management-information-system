"""Working capital forecast curve."""

from __future__ import annotations

from collections import defaultdict
from datetime import date

from django.db.models import Sum

from cash_flow.models import CashTransaction, CashTransactionType
from contracts.models import IPC, IPCStatus
from cost_control.models import ActualCost


def _month_key(d: date) -> str:
    return d.strftime('%Y-%m')


def compute_working_capital_curve(project_id) -> dict:
    cost_by_month: dict[str, float] = defaultdict(float)
    payment_by_month: dict[str, float] = defaultdict(float)

    for row in (
        ActualCost.objects.filter(project_id=project_id, is_deleted=False)
        .values('cost_date')
        .annotate(total=Sum('amount'))
    ):
        if row['cost_date']:
            cost_by_month[_month_key(row['cost_date'])] += float(row['total'] or 0)

    for ipc in IPC.objects.filter(
        project_id=project_id,
        status=IPCStatus.PAID,
        is_deleted=False,
        actual_payment_date__isnull=False,
    ):
        payment_by_month[_month_key(ipc.actual_payment_date)] += float(ipc.net_amount or 0)

    for tx in CashTransaction.objects.filter(project_id=project_id, is_deleted=False, is_forecast=False):
        tx_date = tx.actual_date or tx.tx_date
        key = _month_key(tx_date)
        if tx.tx_type == CashTransactionType.IN:
            payment_by_month[key] += float(tx.amount)
        else:
            cost_by_month[key] += float(tx.amount)

    months = sorted(set(cost_by_month.keys()) | set(payment_by_month.keys()))
    cumulative_cost = 0.0
    cumulative_payment = 0.0
    points = []
    peak = 0.0

    for month in months:
        cumulative_cost += cost_by_month.get(month, 0)
        cumulative_payment += payment_by_month.get(month, 0)
        wc = max(cumulative_cost - cumulative_payment, 0)
        peak = max(peak, wc)
        points.append({
            'month': month,
            'cumulative_cost': round(cumulative_cost, 2),
            'cumulative_payment': round(cumulative_payment, 2),
            'working_capital': round(wc, 2),
        })

    return {
        'points': points,
        'peak_working_capital': round(peak, 2),
    }
