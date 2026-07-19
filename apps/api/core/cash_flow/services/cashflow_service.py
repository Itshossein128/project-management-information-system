"""Cash flow aggregation and analysis services."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from cash_flow.models import CashFlowForecast, CashTransaction, CashTransactionType


def get_cash_flow_summary(project_id, date_from: date | None, date_to: date | None):
    """Return actual monthly cash flow with cumulative balance."""
    qs = CashTransaction.objects.filter(
        project_id=project_id,
        is_deleted=False,
        is_forecast=False,
    )
    if date_from:
        qs = qs.filter(tx_date__gte=date_from)
    if date_to:
        qs = qs.filter(tx_date__lte=date_to)

    monthly: dict[date, dict] = {}
    for tx in qs.order_by('tx_date'):
        month_key = tx.tx_date.replace(day=1)
        monthly.setdefault(month_key, {'month': month_key, 'inflow': 0.0, 'outflow': 0.0})
        if tx.tx_type == CashTransactionType.IN:
            monthly[month_key]['inflow'] += float(tx.amount)
        else:
            monthly[month_key]['outflow'] += float(tx.amount)

    result = []
    cumulative_balance = 0.0
    for month in sorted(monthly.keys()):
        m = monthly[month]
        net = m['inflow'] - m['outflow']
        cumulative_balance += net
        result.append({
            'month': month.strftime('%Y-%m-%d'),
            'inflow': m['inflow'],
            'outflow': m['outflow'],
            'net': net,
            'cumulative_balance': cumulative_balance,
        })
    return result


def get_gap_analysis(project_id):
    """Identify months with projected cash deficits."""
    forecasts = CashFlowForecast.objects.filter(project_id=project_id, is_deleted=False)
    gaps = []
    cumulative = 0.0
    for f in forecasts.order_by('month'):
        net = float(f.expected_inflow or 0) - float(f.expected_outflow or 0)
        cumulative += net
        if net < 0 or cumulative < 0:
            gaps.append({
                'month': f.month.strftime('%Y-%m-%d'),
                'expected_inflow': float(f.expected_inflow or 0),
                'expected_outflow': float(f.expected_outflow or 0),
                'net': net,
                'cumulative_balance': cumulative,
                'gap_amount': abs(min(net, 0)),
                'is_cumulative_negative': cumulative < 0,
            })
    return gaps


def get_transaction_summary(qs, *, actual_only: bool = False):
    """Compute totals and category breakdown for a transaction queryset."""
    if actual_only:
        qs = qs.filter(is_forecast=False)

    total_inflow = Decimal('0')
    total_outflow = Decimal('0')
    by_category: dict[str, float] = {}

    for tx in qs:
        amt = Decimal(str(tx.amount))
        if tx.tx_type == CashTransactionType.IN:
            total_inflow += amt
        else:
            total_outflow += amt
        if tx.category:
            by_category[tx.category] = by_category.get(tx.category, 0.0) + float(amt)

    net = total_inflow - total_outflow
    return {
        'total_inflow': float(total_inflow),
        'total_outflow': float(total_outflow),
        'net_balance': float(net),
        'by_category': by_category,
    }


def get_receivables_payables(project_id):
    """Receivables/payables from approved unpaid IPCs."""
    try:
        from contracts.models import Contract, IPC, IPCStatus
    except ImportError:
        return _receivables_stub()

    today = date.today()
    approved_unpaid = IPC.objects.filter(
        project_id=project_id,
        status=IPCStatus.APPROVED,
        actual_payment_date__isnull=True,
        is_deleted=False,
    )

    receivables_total = Decimal('0')
    receivables_overdue = Decimal('0')
    for ipc in approved_unpaid.filter(contract__contract_type='main'):
        amt = ipc.net_amount or ipc.gross_amount or Decimal('0')
        receivables_total += amt
        if ipc.planned_payment_date and ipc.planned_payment_date < today:
            receivables_overdue += amt

    payables_total = Decimal('0')
    payables_overdue = Decimal('0')
    for ipc in approved_unpaid.filter(contract__contract_type='subcontract'):
        amt = ipc.net_amount or ipc.gross_amount or Decimal('0')
        payables_total += amt
        if ipc.planned_payment_date and ipc.planned_payment_date < today:
            payables_overdue += amt

    return {
        'receivables': {
            'total_approved_unpaid': float(receivables_total),
            'overdue': float(receivables_overdue),
        },
        'payables': {
            'total_approved_unpaid': float(payables_total),
            'overdue': float(payables_overdue),
        },
    }


# Fallback stub for receivables/payables calculation when the contracts/IPC module is not yet available or imported.
def _receivables_stub():
    return {
        'receivables': None,
        'payables': None,
        'note': 'IPC module not yet available.',
    }


def get_forecast_with_actuals(project_id):
    """Return forecast rows enriched with actual monthly figures."""
    forecasts = list(
        CashFlowForecast.objects.filter(project_id=project_id, is_deleted=False).order_by('month')
    )
    if not forecasts:
        return []

    date_from = forecasts[0].month
    date_to = forecasts[-1].month.replace(day=28)
    actuals = {row['month']: row for row in get_cash_flow_summary(project_id, date_from, date_to)}
    today = date.today()

    result = []
    for f in forecasts:
        month_key = f.month.strftime('%Y-%m-%d')
        actual = actuals.get(month_key, {})
        is_past = f.month.replace(day=1) < today.replace(day=1)
        result.append({
            'month': month_key,
            'expected_inflow': float(f.expected_inflow or 0),
            'expected_outflow': float(f.expected_outflow or 0),
            'confidence_pct': float(f.confidence_pct) if f.confidence_pct is not None else None,
            'notes': f.notes,
            'actual_inflow': actual.get('inflow') if is_past else None,
            'actual_outflow': actual.get('outflow') if is_past else None,
            'actual_net': actual.get('net') if is_past else None,
        })
    return result
