"""Suggested net cash need (FR-CASH-004)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db.models import Sum

from contracts.collection_service import remaining_receivable
from contracts.models import IPC, IPCStatus
from cost_control.cbs_services import posted_payments_total
from cost_control.models import ActualCost, ActualCostStatus, Commitment, CommitmentStatus, CostCategory
from cash_flow.services.projection_service import _month_end, _parse_month

ESSENTIAL_CATEGORIES = frozenset(
    {
        CostCategory.LABOR,
        CostCategory.SITE_OVERHEAD,
    }
)


def suggested_net_need(project_id, period_start, period_end) -> dict:
    start = period_start if isinstance(period_start, date) else _parse_month(period_start)
    end = period_end if isinstance(period_end, date) else _month_end(_parse_month(period_end))
    if end < start:
        start, end = end, start

    due_commitments = Decimal('0')
    for c in Commitment.objects.filter(
        project_id=project_id,
        is_deleted=False,
        status=CommitmentStatus.APPROVED,
        due_date__gte=start,
        due_date__lte=end,
    ):
        open_amt = Decimal(c.amount) - posted_payments_total(c)
        if open_amt > 0:
            due_commitments += open_amt

    essential_costs = (
        ActualCost.objects.filter(
            project_id=project_id,
            is_deleted=False,
            status=ActualCostStatus.APPROVED,
            cost_date__gte=start,
            cost_date__lte=end,
            cost_category__in=ESSENTIAL_CATEGORIES,
        ).aggregate(t=Sum('amount'))['t']
        or Decimal('0')
    )

    certain_planned_receipts = Decimal('0')
    for ipc in IPC.objects.filter(
        project_id=project_id,
        is_deleted=False,
        status=IPCStatus.APPROVED,
    ):
        rem = remaining_receivable(ipc)
        if rem <= 0:
            continue
        due = ipc.planned_payment_date or ipc.period_end
        if due is None:
            continue
        if start <= due <= end:
            certain_planned_receipts += rem

    suggested = due_commitments + essential_costs - certain_planned_receipts
    return {
        'period_start': start.strftime('%Y-%m-%d'),
        'period_end': end.strftime('%Y-%m-%d'),
        'due_commitments': float(due_commitments),
        'essential_costs': float(essential_costs),
        'certain_planned_receipts': float(certain_planned_receipts),
        'suggested_net_need': float(suggested),
        'meta': {
            'essential_costs_rule': 'approved_actuals_in_categories_or_zero',
            'certain_planned_receipts_rule': 'approved_ipc_remaining_due_in_period',
        },
    }
