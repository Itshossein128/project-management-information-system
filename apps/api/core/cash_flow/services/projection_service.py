"""Domain-fed projected cash series (IPC dues + commitment dues)."""

from __future__ import annotations

from calendar import monthrange
from datetime import date
from decimal import Decimal

from contracts.collection_service import remaining_receivable
from contracts.models import IPC, IPCStatus
from cost_control.cbs_services import posted_payments_total
from cost_control.models import Commitment, CommitmentStatus
from cash_flow.models import CashFlowForecast, CashTransaction, CashTransactionType


def _month_start(d: date) -> date:
    return d.replace(day=1)


def _parse_month(value) -> date:
    if isinstance(value, date):
        return _month_start(value)
    text = str(value)
    if len(text) >= 7:
        y, m = int(text[:4]), int(text[5:7])
        return date(y, m, 1)
    raise ValueError(f'Invalid month: {value}')


def _month_end(month: date) -> date:
    last = monthrange(month.year, month.month)[1]
    return month.replace(day=last)


def _iter_months(start: date, end: date):
    cur = _month_start(start)
    end = _month_start(end)
    while cur <= end:
        yield cur
        if cur.month == 12:
            cur = date(cur.year + 1, 1, 1)
        else:
            cur = date(cur.year, cur.month + 1, 1)


def build_projected_series(project_id, from_month, to_month) -> dict:
    start = _parse_month(from_month)
    end = _parse_month(to_month)
    if end < start:
        start, end = end, start

    # Inflows: approved unpaid IPCs with remaining > 0
    ipc_by_month: dict[date, Decimal] = {}
    ipcs = IPC.objects.filter(
        project_id=project_id,
        is_deleted=False,
        status=IPCStatus.APPROVED,
    )
    for ipc in ipcs:
        rem = remaining_receivable(ipc)
        if rem <= 0:
            continue
        due = ipc.planned_payment_date or ipc.period_end
        if due is None:
            continue
        key = _month_start(due)
        if start <= key <= end:
            ipc_by_month[key] = ipc_by_month.get(key, Decimal('0')) + rem
    has_any_ipc_due = bool(ipc_by_month)

    # Outflows: approved commitments open amount by due_date
    out_by_month: dict[date, Decimal] = {}
    commitments = Commitment.objects.filter(
        project_id=project_id,
        is_deleted=False,
        status=CommitmentStatus.APPROVED,
        due_date__isnull=False,
    )
    for c in commitments:
        open_amt = Decimal(c.amount) - posted_payments_total(c)
        if open_amt <= 0:
            continue
        key = _month_start(c.due_date)
        if start <= key <= end:
            out_by_month[key] = out_by_month.get(key, Decimal('0')) + open_amt

    months = []
    for m in _iter_months(start, end):
        inflow = ipc_by_month.get(m, Decimal('0'))
        outflow = out_by_month.get(m, Decimal('0'))
        # Unregistered inflow for the whole range if no IPC dues anywhere in range
        # Per-month: if no IPC dues exist at all for project in range, mark unregistered
        inflow_status = 'registered' if has_any_ipc_due else 'unregistered'
        months.append(
            {
                'month': m.strftime('%Y-%m-%d'),
                'projected_inflow': float(inflow),
                'projected_outflow': float(outflow),
                'net_need': float(inflow - outflow),
                'inflow_status': inflow_status,
                'outflow_status': 'registered',
            }
        )

    actual_months = _actual_months(project_id, start, end)
    manual_forecast_months = _manual_forecast_months(project_id, start, end)

    return {
        'series': 'projected',
        'months': months,
        'actual_months': actual_months,
        'manual_forecast_months': manual_forecast_months,
        'meta': {
            'inflow_sources': 'approved_ipc_remaining_by_planned_payment_date',
            'outflow_sources': 'approved_commitment_open_by_due_date',
        },
    }


def _actual_months(project_id, start: date, end: date) -> list[dict]:
    qs = CashTransaction.objects.filter(
        project_id=project_id,
        is_deleted=False,
        is_forecast=False,
        tx_date__gte=start,
        tx_date__lte=_month_end(end),
    )
    monthly: dict[date, dict] = {}
    for tx in qs:
        key = _month_start(tx.tx_date)
        monthly.setdefault(key, {'inflow': Decimal('0'), 'outflow': Decimal('0')})
        if tx.tx_type == CashTransactionType.IN:
            monthly[key]['inflow'] += Decimal(tx.amount)
        else:
            monthly[key]['outflow'] += Decimal(tx.amount)
    result = []
    for m in sorted(monthly.keys()):
        row = monthly[m]
        result.append(
            {
                'month': m.strftime('%Y-%m-%d'),
                'actual_inflow': float(row['inflow']),
                'actual_outflow': float(row['outflow']),
                'net': float(row['inflow'] - row['outflow']),
            }
        )
    return result


def _manual_forecast_months(project_id, start: date, end: date) -> list[dict]:
    rows = CashFlowForecast.objects.filter(
        project_id=project_id,
        is_deleted=False,
        month__gte=start,
        month__lte=end,
    ).order_by('month')
    return [
        {
            'month': f.month.strftime('%Y-%m-%d'),
            'expected_inflow': float(f.expected_inflow or 0),
            'expected_outflow': float(f.expected_outflow or 0),
            'net': float((f.expected_inflow or 0) - (f.expected_outflow or 0)),
        }
        for f in rows
    ]
