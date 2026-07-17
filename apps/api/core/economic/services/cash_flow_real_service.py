"""Economic (inflation-adjusted) cash flow curve."""

from __future__ import annotations

from collections import defaultdict
from datetime import date

from cash_flow.models import CashTransaction, CashTransactionType
from contracts.models import IPC, IPCStatus
from cost_control.models import ActualCost
from economic.services.inflation_service import adjust_cost_for_inflation


def _month_key(d: date) -> str:
    return d.strftime('%Y-%m')


def compute_cash_flow_real(project_id, as_of_date=None) -> dict:
    as_of = as_of_date or date.today()
    nominal_out: dict[str, float] = defaultdict(float)
    real_out: dict[str, float] = defaultdict(float)
    inflows: dict[str, float] = defaultdict(float)

    costs = ActualCost.objects.filter(
        project_id=project_id,
        is_deleted=False,
        cost_date__lte=as_of,
    )
    for cost in costs:
        key = _month_key(cost.cost_date)
        amount = float(cost.amount)
        nominal_out[key] += amount
        real_out[key] += adjust_cost_for_inflation(
            cost.amount,
            cost.cost_category or 'other',
            cost.cost_date,
            as_of,
            project_id=project_id,
        )

    for ipc in IPC.objects.filter(
        project_id=project_id,
        status=IPCStatus.PAID,
        is_deleted=False,
        actual_payment_date__isnull=False,
        actual_payment_date__lte=as_of,
    ):
        inflows[_month_key(ipc.actual_payment_date)] += float(ipc.net_amount or 0)

    for tx in CashTransaction.objects.filter(
        project_id=project_id,
        is_deleted=False,
        is_forecast=False,
    ):
        tx_date = tx.actual_date or tx.tx_date
        if tx_date > as_of:
            continue
        key = _month_key(tx_date)
        amount = float(tx.amount)
        if tx.tx_type == CashTransactionType.IN:
            inflows[key] += amount
        else:
            nominal_out[key] += amount
            real_out[key] += amount

    months = sorted(set(nominal_out.keys()) | set(real_out.keys()) | set(inflows.keys()))
    points = []
    for month in months:
        nom = nominal_out.get(month, 0)
        real = real_out.get(month, 0)
        inf = inflows.get(month, 0)
        points.append({
            'month': month,
            'nominal_outflow': round(nom, 2),
            'real_outflow': round(real, 2),
            'inflow': round(inf, 2),
            'net_nominal': round(inf - nom, 2),
            'net_real': round(inf - real, 2),
        })

    return {'as_of_date': as_of.isoformat(), 'points': points}
