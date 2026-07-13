"""Periodic and batch alert tasks."""

from celery import shared_task

from cash_flow.services.cashflow_service import get_gap_analysis


@shared_task
def monitor_cash_gaps():
    from cash_flow.models import CashFlowForecast

    project_ids = CashFlowForecast.objects.filter(is_deleted=False).values_list(
        'project_id', flat=True
    ).distinct()
    for pid in project_ids:
        gaps = get_gap_analysis(pid)
        for g in gaps:
            if g.get('is_cumulative_negative'):
                from alerts.services.evaluation import fire_cash_gap
                fire_cash_gap(pid, g['month'], g.get('gap_amount', 0))


@shared_task
def run_daily_alert_checks():
    from projects.models import Project

    active_projects = Project.objects.filter(status='active', is_deleted=False).values_list(
        'id', flat=True
    )
    for project_id in active_projects:
        check_and_fire_for_project_task.delay(str(project_id))


@shared_task
def check_and_fire_for_project_task(project_id):
    from alerts.services.alert_engine import check_and_fire_for_project
    check_and_fire_for_project(project_id)
