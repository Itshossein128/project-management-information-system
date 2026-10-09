"""Best-effort notifications for overdue workflow stages (FR-COL edge case)."""

from __future__ import annotations

from django.utils import timezone

from alerts.models import AlertLog
from workflow.models import WorkflowInstance, WorkflowInstanceStatus

NON_TERMINAL = (
    WorkflowInstanceStatus.PENDING,
    WorkflowInstanceStatus.IN_PROGRESS,
    WorkflowInstanceStatus.RETURNED,
)


def notify_overdue_instances(project_id) -> int:
    """Create AlertLog rows for overdue in-flight instances. Returns count created.

    Idempotent within a day via trigger_reference uniqueness check.
    Does not require a dedicated AlertRule / Celery worker.
    """
    now = timezone.now()
    qs = WorkflowInstance.objects.filter(
        project_id=project_id,
        status__in=NON_TERMINAL,
        current_due_at__lt=now,
        is_deleted=False,
    )
    created = 0
    day = now.date().isoformat()
    for instance in qs.iterator():
        ref = f'workflow-overdue:{instance.id}:{day}'
        if AlertLog.objects.filter(trigger_reference=ref).exists():
            continue
        AlertLog.objects.create(
            project_id=project_id,
            trigger_reference=ref,
            message=(
                f'Workflow instance {instance.id} stage {instance.current_stage_order} '
                f'is overdue (due {instance.current_due_at}).'
            ),
        )
        created += 1
    return created
