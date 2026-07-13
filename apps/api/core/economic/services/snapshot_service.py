"""Economic P&L snapshot generation."""

from __future__ import annotations

from datetime import date

from django.db.models import Sum

from cost_control.models import ActualCost
from contracts.models import Contract, ContractType, IPC, IPCStatus
from economic.models import EconomicSnapshot
from economic.services.financing_service import compute_financing_cost
from economic.services.inflation_service import compute_total_inflation_adjusted_cost


def generate_snapshot(project_id, snapshot_date=None):
    if snapshot_date is None:
        snapshot_date = date.today()

    actual_cost = float(
        ActualCost.objects.filter(
            project_id=project_id, cost_date__lte=snapshot_date, is_deleted=False
        ).aggregate(t=Sum('amount'))['t'] or 0
    )

    revenue = float(
        IPC.objects.filter(
            project_id=project_id,
            status=IPCStatus.PAID,
            actual_payment_date__lte=snapshot_date,
            contract__contract_type=ContractType.MAIN,
            is_deleted=False,
        ).aggregate(t=Sum('net_amount'))['t'] or 0
    )

    accounting_profit = revenue - actual_cost
    inflation_adjusted_cost = compute_total_inflation_adjusted_cost(project_id, snapshot_date)
    real_profit = revenue - inflation_adjusted_cost

    financing_data = compute_financing_cost(project_id)
    financing_cost = financing_data['total_financing_cost']
    economic_profit = revenue - actual_cost - financing_cost
    working_capital = max(actual_cost - revenue, 0)

    snapshot, _ = EconomicSnapshot.objects.update_or_create(
        project_id=project_id,
        snapshot_date=snapshot_date,
        defaults={
            'actual_cost': actual_cost,
            'inflation_adj_cost': inflation_adjusted_cost,
            'financing_cost': financing_cost,
            'revenue_to_date': revenue,
            'accounting_profit': accounting_profit,
            'real_profit': real_profit,
            'economic_profit': economic_profit,
            'working_capital': working_capital,
            'avg_payment_delay_days': financing_data['avg_payment_delay_days'],
        },
    )
    return snapshot
