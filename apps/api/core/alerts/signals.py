"""Real-time alert triggers via Django signals."""

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver


def _delay_project_check(project_id):
    """Queue alert evaluation after the surrounding DB transaction commits.

    When CELERY_TASK_ALWAYS_EAGER is true, running the task inside post_save
    shares the open transaction; any engine error aborts allocate/create flows.
    """
    from alerts.tasks import check_and_fire_for_project_task

    pid = str(project_id)

    def _enqueue():
        check_and_fire_for_project_task.delay(pid)

    transaction.on_commit(_enqueue)


@receiver(post_save, sender='field_reports.DailyReport')
def on_daily_report_saved(sender, instance, **kwargs):
    if instance.status == 'approved':
        _delay_project_check(instance.project_id)


@receiver(post_save, sender='cost_control.ActualCost')
def on_actual_cost_saved(sender, instance, **kwargs):
    _delay_project_check(instance.project_id)


@receiver(post_save, sender='resources.InventoryTransaction')
def on_inventory_tx_saved(sender, instance, **kwargs):
    _delay_project_check(instance.material.project_id)


@receiver(post_save, sender='subcontractors.SubcontractorPerformanceScore')
def on_score_saved(sender, instance, **kwargs):
    _delay_project_check(instance.subcontractor.project_id)


@receiver(post_save, sender='documents.Correspondence')
def on_correspondence_saved(sender, instance, **kwargs):
    _delay_project_check(instance.project_id)
