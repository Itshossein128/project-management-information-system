"""KPI figure drill-through row builders (FR-RPT US1)."""

from __future__ import annotations

from datetime import date
from rest_framework.exceptions import NotFound

from cash_flow.models import CashTransaction
from cost_control.models import ActualCost, ActualCostStatus, Budget
from cost_control.services.budget_version_service import get_control_version
from projects.services.figure_provenance import make_drill_row
from schedule.models import ActivityProgress, BaselineActivity, BaselineSchedule
from schedule.services.progress_service import get_activity_progress_breakdown

KNOWN_FIGURE_KEYS = frozenset({
    'evm.spi',
    'evm.cpi',
    'progress.plan_vs_actual',
    'finance.budget',
    'finance.actual_cost',
    'cash.net_balance',
    'schedule.critical_activities',
})


class UnknownFigureKey(NotFound):
    default_detail = 'Unknown figure key.'
    default_code = 'unknown_figure_key'


def _progress_approved(row: dict) -> bool:
    return float(row.get('approved_progress_pct') or 0) > 0


def _drill_progress_plan_vs_actual(project_id, as_of: date, *, approved_only: bool) -> list[dict]:
    rows = get_activity_progress_breakdown(project_id, as_of)
    out = []
    for row in rows:
        approved = _progress_approved(row)
        if approved_only and not approved:
            continue
        activity_id = row.get('activity_id')
        name = row.get('activity_name') or row.get('activity_code') or 'Activity'
        planned = float(row.get('planned_progress_pct') or 0)
        actual = float(row.get('actual_progress_pct') or 0)
        out.append(
            make_drill_row(
                id=activity_id,
                display=f'{name} (plan {planned:.1f}% / act {actual:.1f}%)',
                approval_status='approved' if approved else 'draft',
                approved=approved,
                last_updated_at=None,
                amount=round(actual - planned, 4),
                source_path=f'/projects/{project_id}/progress/',
            )
        )
    return out


def _drill_evm_spi(project_id, as_of: date, *, approved_only: bool) -> list[dict]:
    return _drill_progress_plan_vs_actual(project_id, as_of, approved_only=approved_only)


def _drill_evm_cpi(project_id, as_of: date, *, approved_only: bool) -> list[dict]:
    qs = ActualCost.objects.filter(project_id=project_id, is_deleted=False)
    if approved_only:
        qs = qs.filter(status=ActualCostStatus.APPROVED)
    out = []
    for ac in qs.order_by('-cost_date')[:200]:
        approved = ac.status == ActualCostStatus.APPROVED
        out.append(
            make_drill_row(
                id=ac.id,
                display=ac.description or f'Actual {ac.cost_date}',
                approval_status=ac.status,
                approved=approved,
                last_updated_at=ac.updated_at,
                amount=float(ac.amount),
                source_path=f'/projects/{project_id}/costs/',
            )
        )
    return out


def _drill_finance_budget(project_id, as_of: date, *, approved_only: bool) -> list[dict]:
    control = get_control_version(project_id)
    if not control:
        return []
    qs = Budget.objects.filter(version=control, is_deleted=False)
    out = []
    for line in qs.order_by('cost_category')[:200]:
        approved = control.status == 'approved'
        if approved_only and not approved:
            continue
        out.append(
            make_drill_row(
                id=line.id,
                display=line.notes or line.cost_category or 'Budget line',
                approval_status=control.status,
                approved=approved,
                last_updated_at=line.updated_at,
                amount=float(line.budget_amount or 0),
                source_path=f'/projects/{project_id}/costs/',
            )
        )
    return out


def _drill_finance_actual_cost(project_id, as_of: date, *, approved_only: bool) -> list[dict]:
    return _drill_evm_cpi(project_id, as_of, approved_only=approved_only)


def _drill_cash_net_balance(project_id, as_of: date, *, approved_only: bool) -> list[dict]:
    qs = CashTransaction.objects.filter(
        project_id=project_id,
        is_deleted=False,
        is_forecast=False,
        tx_date__lte=as_of,
    )
    out = []
    for tx in qs.order_by('-tx_date')[:200]:
        signed = float(tx.amount) if tx.tx_type == 'in' else -float(tx.amount)
        out.append(
            make_drill_row(
                id=tx.id,
                display=tx.description or f'{tx.category} {tx.tx_date}',
                approval_status='posted',
                approved=True,
                last_updated_at=tx.updated_at,
                amount=signed,
                source_path=f'/projects/{project_id}/cash-flow/',
            )
        )
    return out


def _drill_critical_activities(project_id, as_of: date, *, approved_only: bool) -> list[dict]:
    current = BaselineSchedule.objects.filter(project_id=project_id, is_current=True).first()
    if not current:
        return []
    qs = BaselineActivity.objects.filter(baseline=current, is_critical=True).select_related('activity')
    out = []
    for ba in qs[:200]:
        act = ba.activity
        out.append(
            make_drill_row(
                id=act.id if act else ba.id,
                display=act.activity_name if act else str(ba.id),
                approval_status='baseline',
                approved=True,
                last_updated_at=current.updated_at,
                source_path=f'/projects/{project_id}/schedule/',
            )
        )
    return out


_HANDLERS = {
    'evm.spi': _drill_evm_spi,
    'evm.cpi': _drill_evm_cpi,
    'progress.plan_vs_actual': _drill_progress_plan_vs_actual,
    'finance.budget': _drill_finance_budget,
    'finance.actual_cost': _drill_finance_actual_cost,
    'cash.net_balance': _drill_cash_net_balance,
    'schedule.critical_activities': _drill_critical_activities,
}


def get_drill_rows(project_id, figure_key: str, as_of: date, *, approved_only: bool = True) -> dict:
    if figure_key not in KNOWN_FIGURE_KEYS:
        raise UnknownFigureKey()
    handler = _HANDLERS[figure_key]
    results = handler(project_id, as_of, approved_only=approved_only)
    return {'figure_key': figure_key, 'results': results}
