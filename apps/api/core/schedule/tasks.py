from celery import shared_task
from datetime import timedelta

from django.conf import settings

from schedule.models import ActivityProgress, BaselineSchedule, MspImportJob, P6ImportJob
from schedule.services.import_operations import run_claimed_import, run_maintenance
from schedule.services.import_process import reconcile_abandoned_scratch
from schedule.services.msp_import import execute_msp_import
from schedule.services.p6_import import execute_p6_import


@shared_task
def compute_baseline_progress(baseline_id):
    baseline = BaselineSchedule.objects.get(pk=baseline_id)
    if not baseline.is_current:
        return {'baseline_id': str(baseline_id), 'skipped': True}

    count = 0
    for ba in baseline.baseline_activities.filter(activity__is_deleted=False).select_related('activity'):
        activity = ba.activity
        if not ba.planned_start or not ba.planned_finish:
            continue
        total_days = (ba.planned_finish - ba.planned_start).days
        if total_days <= 0:
            continue
        current = ba.planned_start
        while current <= ba.planned_finish:
            elapsed = (current - ba.planned_start).days
            planned_pct = min(elapsed / total_days, 1.0)
            ActivityProgress.objects.update_or_create(
                activity=activity,
                report_date=current,
                defaults={'planned_progress': planned_pct},
            )
            count += 1
            current += timedelta(days=1)

    from schedule.services.progress_service import invalidate_s_curve_cache

    invalidate_s_curve_cache(baseline.project_id)
    return {'baseline_id': str(baseline_id), 'rows': count}


@shared_task(
    bind=True,
    acks_late=True,
    soft_time_limit=settings.IMPORT_EXECUTION_SOFT_SECONDS,
    time_limit=settings.IMPORT_EXECUTION_HARD_SECONDS,
)
def run_msp_import_task(self, job_id: str):
    return run_claimed_import(MspImportJob, job_id, execute_msp_import, 'msp')


@shared_task(
    bind=True,
    acks_late=True,
    soft_time_limit=settings.IMPORT_EXECUTION_SOFT_SECONDS,
    time_limit=settings.IMPORT_EXECUTION_HARD_SECONDS,
)
def run_p6_import_task(self, job_id: str):
    return run_claimed_import(P6ImportJob, job_id, execute_p6_import, 'p6')


@shared_task
def reconcile_import_jobs():
    return run_maintenance('recovery')


@shared_task
def purge_import_originals():
    return run_maintenance('purge')


@shared_task
def reconcile_import_scratch():
    return reconcile_abandoned_scratch()
