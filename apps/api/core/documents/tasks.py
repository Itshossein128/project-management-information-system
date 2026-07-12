"""Document monitoring Celery tasks."""

from datetime import date, timedelta

from celery import shared_task

from documents.models import Correspondence, CorrStatus
from notifications.models import Notification, NotificationType


@shared_task
def monitor_correspondence_due():
    threshold = date.today() + timedelta(days=3)
    today = date.today()
    overdue = Correspondence.objects.filter(
        is_deleted=False,
        status=CorrStatus.OPEN,
        response_due_date__isnull=False,
        response_due_date__lte=threshold,
        response_due_date__gte=today - timedelta(days=1),
    )
    for corr in overdue:
        message = f'مکاتبه {corr.corr_number} تا {corr.response_due_date} نیاز به پاسخ دارد'
        _notify_roles(corr.project_id, ['document_controller', 'project_manager'], message)


def _notify_roles(project_id, role_names, message):
    from master_data.models import ProjectMember, ProjectMemberRole

    members = ProjectMember.objects.filter(project_id=project_id, status='active')
    for m in members:
        roles = ProjectMemberRole.objects.filter(member=m).select_related('role')
        if any(r.role.role_name in role_names for r in roles):
            Notification.objects.create(
                user_id=m.user_id,
                project_id=project_id,
                notification_type=NotificationType.GENERIC,
                title='مهلت مکاتبه',
                message=message,
            )
