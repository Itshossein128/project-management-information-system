from celery import shared_task


@shared_task
def run_monte_carlo_task(project_id, iterations=5000, scenario_params=None):
    from economic.services.monte_carlo_service import run_monte_carlo
    return run_monte_carlo(project_id, iterations=iterations, scenario_params=scenario_params or {})


@shared_task
def generate_daily_snapshots():
    from datetime import date

    from projects.models import Project

    from economic.services.snapshot_service import generate_snapshot

    for pid in Project.objects.filter(status='active', is_deleted=False).values_list('id', flat=True):
        generate_snapshot(pid, date.today())
