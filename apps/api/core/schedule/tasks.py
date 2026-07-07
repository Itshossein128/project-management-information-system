from celery import shared_task

from schedule.models import MspImportJob, MspImportStatus
from schedule.services.msp_import import execute_msp_import


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
