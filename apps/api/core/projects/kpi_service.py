"""Unified project KPI aggregation (blueprint K-02)."""

from __future__ import annotations

import logging
from datetime import date

from django.db.models import Sum

from alerts.models import AlertLog
from cash_flow.models import CashTransaction, CashTransactionType
from cash_flow.services.cashflow_service import get_gap_analysis, get_receivables_payables
from common.cache_helpers import cache_key, get_cached_or_compute
from schedule.models import BaselineActivity, BaselineSchedule
from schedule.services.evm_service import compute_evm
from schedule.services.progress_service import (
    get_activity_progress_breakdown,
    get_progress_snapshot,
)

logger = logging.getLogger(__name__)

KPI_CACHE_TTL = 300  # 5 minutes


def project_kpis_cache_key(project_id, as_of: date) -> str:
    return cache_key('project_kpis', project_id, as_of.isoformat())


def invalidate_project_kpis_cache(project_id) -> None:
    """Best-effort clear of unified KPI cache keys for a project."""
    try:
        from django.core.cache import cache
        import redis
        from django.conf import settings

        # LocMem / simple backends: delete known recent keys is hard; pattern via Redis.
        client = redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)
        for key in client.scan_iter(match=f'project_kpis:{project_id}:*'):
            client.delete(key)
        # Also try Django cache delete for exact keys if locmem — no-op pattern.
        cache.delete_many([])  # noop keep import used
    except Exception:  # noqa: BLE001
        logger.debug('Failed to invalidate project_kpis for %s', project_id, exc_info=True)


def _cash_totals(project_id) -> dict:
    qs = CashTransaction.objects.filter(
        project_id=project_id,
        is_deleted=False,
        is_forecast=False,
    )
    agg = qs.values('tx_type').annotate(total=Sum('amount'))
    received = 0.0
    paid = 0.0
    for row in agg:
        if row['tx_type'] == CashTransactionType.IN:
            received = float(row['total'] or 0)
        else:
            paid = float(row['total'] or 0)
    return {
        'total_received': received,
        'total_paid_out': paid,
        'net_balance': received - paid,
    }


def _schedule_counts(project_id, as_of: date) -> dict:
    snapshot = get_progress_snapshot(project_id, as_of)
    behind = snapshot.get('activities_behind_schedule') or 0

    current = BaselineSchedule.objects.filter(
        project_id=project_id,
        is_current=True,
    ).first()
    critical = 0
    if current:
        critical = BaselineActivity.objects.filter(
            baseline=current,
            is_critical=True,
        ).count()

    ahead = 0
    try:
        rows = get_activity_progress_breakdown(project_id, as_of)
        for row in rows:
            planned = float(row.get('planned_progress_pct') or 0) / 100.0
            actual = float(row.get('actual_progress_pct') or 0) / 100.0
            if actual - planned > 0.05:
                ahead += 1
    except Exception:  # noqa: BLE001
        logger.debug('ahead count failed', exc_info=True)

    return {
        'critical_activities': critical,
        'behind_schedule': behind,
        'ahead_of_schedule': ahead,
    }


def _open_alerts_total(project_id) -> int:
    return AlertLog.objects.filter(
        project_id=project_id,
        acknowledged_at__isnull=True,
    ).count()


def _money_str(value) -> str:
    v = float(value or 0)
    if v == int(v):
        return str(int(v))
    return str(v)


def build_project_kpis(project_id, as_of: date) -> dict:
    """Compose blueprint-shaped KPI payload from existing domain services."""
    evm = compute_evm(project_id, as_of)
    planned = (evm.get('planned_progress_pct') or 0) / 100.0
    actual = (evm.get('actual_progress_pct') or 0) / 100.0
    variance = actual - planned

    bac = float(evm.get('bac') or 0)
    ac = float(evm.get('ac') or 0)
    budget_consumption = (ac / bac) if bac else 0.0

    cash = _cash_totals(project_id)
    rp = get_receivables_payables(project_id)
    receivables = 0.0
    payables = 0.0
    if rp.get('receivables'):
        receivables = float(rp['receivables'].get('total_approved_unpaid') or 0)
    if rp.get('payables'):
        payables = float(rp['payables'].get('total_approved_unpaid') or 0)

    gaps = get_gap_analysis(project_id)
    has_cash_gap = bool(gaps)

    schedule = _schedule_counts(project_id, as_of)
    open_alerts = _open_alerts_total(project_id)

    return {
        'as_of': as_of.strftime('%Y-%m-%d'),
        'physical_progress': {
            'planned': round(planned, 4),
            'actual': round(actual, 4),
            'variance': round(variance, 4),
            'spi': evm.get('spi'),
        },
        'cost': {
            'budget': _money_str(bac),
            'actual_cost': _money_str(ac),
            'earned_value': _money_str(evm.get('ev')),
            'cost_variance': _money_str(evm.get('cv')),
            'cpi': evm.get('cpi'),
            'budget_consumption': round(budget_consumption, 4),
            'eac': evm.get('eac'),
        },
        'cash': {
            'total_received': _money_str(cash['total_received']),
            'total_paid_out': _money_str(cash['total_paid_out']),
            'net_balance': _money_str(cash['net_balance']),
            'receivables': _money_str(receivables),
            'payables_to_subs': _money_str(payables),
            'has_cash_gap': has_cash_gap,
        },
        'schedule': schedule,
        'alerts': {
            'unacknowledged_total': open_alerts,
        },
        'panel': {
            'spi': evm.get('spi'),
            'cpi': evm.get('cpi'),
            'physical_actual_pct': evm.get('actual_progress_pct'),
            'schedule_variance_pct': evm.get('schedule_variance_pct'),
            'budget_consumption_pct': evm.get('budget_consumption_pct'),
            'net_cash': cash['net_balance'],
            'has_cash_gap': has_cash_gap,
            'open_alerts': open_alerts,
            'critical_activities': schedule['critical_activities'],
            'behind_schedule': schedule['behind_schedule'],
            'eac': evm.get('eac'),
        },
    }


def get_project_kpis(project_id, as_of: date, *, force_refresh: bool = False) -> dict:
    key = project_kpis_cache_key(project_id, as_of)
    if force_refresh:
        from django.core.cache import cache

        cache.delete(key)
    return get_cached_or_compute(key, KPI_CACHE_TTL, lambda: build_project_kpis(project_id, as_of))
