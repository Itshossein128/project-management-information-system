"""Periodic alert monitoring tasks."""

from celery import shared_task

from cash_flow.services.cashflow_service import get_gap_analysis


@shared_task
def monitor_cash_gaps():
    from cash_flow.models import CashFlowForecast
    from projects.models import Project

    project_ids = CashFlowForecast.objects.filter(is_deleted=False).values_list('project_id', flat=True).distinct()
    for pid in project_ids:
        gaps = get_gap_analysis(pid)
        for g in gaps:
            if g.get('is_cumulative_negative'):
                from alerts.services.evaluation import fire_cash_gap
                fire_cash_gap(pid, g['month'], g.get('gap_amount', 0))
