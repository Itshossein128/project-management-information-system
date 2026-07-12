from celery import shared_task
from datetime import timedelta

from schedule.models import ActivityProgress, BaselineSchedule, MspImportJob, MspImportStatus
from schedule.services.msp_import import execute_msp_import


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


@shared_task(bind=True)
def run_msp_import_task(self, job_id: str):
    job = MspImportJob.objects.select_related('project').get(pk=job_id)
    job.status = MspImportStatus.RUNNING
    job.task_id = self.request.id or ''
    job.save(update_fields=['status', 'task_id', 'updated_at'])

    file_bytes = bytes(job.file_data or b'')

    def on_progress(pct: int):
        job.progress_pct = min(pct, 99)
        job.save(update_fields=['progress_pct', 'updated_at'])

    try:
        result = execute_msp_import(
            job.project,
            file_bytes,
            filename=job.filename,
            replace=job.replace_existing,
            progress_callback=on_progress,
            user=job.created_by,
        )
        job.status = MspImportStatus.DONE
        job.progress_pct = 100
        job.result = result
        job.save(update_fields=['status', 'progress_pct', 'result', 'updated_at'])
        return result
    except Exception as exc:
        job.status = MspImportStatus.FAILED
        job.error_message = str(exc)
        job.save(update_fields=['status', 'error_message', 'updated_at'])
        raise
