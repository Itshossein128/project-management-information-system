"""Celery tasks for contracts module."""

from datetime import date, timedelta

from celery import shared_task
from django.contrib.auth import get_user_model

from contracts.models import Contract, IPC, IPCStatus
from notifications.models import Notification, NotificationType

User = get_user_model()


@shared_task
def populate_ipc_async(ipc_id):
    from contracts.services.ipc_service import apply_deductions, auto_populate_ipc

    auto_populate_ipc(ipc_id)
    apply_deductions(ipc_id)


@shared_task
def send_ipc_delay_notification(ipc_id, delay_days):
    from contracts.models import IPC

    ipc = IPC.objects.select_related('contract', 'project').get(pk=ipc_id)
    message = (
        f'صدور موقت شماره {ipc.ipc_number} قرارداد {ipc.contract.contract_number} '
        f'تاکنون {delay_days} روز از موعد پرداخت گذشته است'
    )
    _notify_project_roles(ipc.project_id, ['finance_manager', 'project_manager'], message)


def _notify_project_roles(project_id, role_names, message):
    from master_data.models import ProjectMember, ProjectMemberRole

    members = ProjectMember.objects.filter(project_id=project_id, status='active')
    user_ids = set()
    for m in members:
        roles = ProjectMemberRole.objects.filter(member=m).select_related('role')
        if any(r.role.role_name in role_names for r in roles):
            user_ids.add(m.user_id)
    for uid in user_ids:
        Notification.objects.create(
            user_id=uid,
            project_id=project_id,
            notification_type=NotificationType.GENERIC,
            title='هشدار قرارداد',
            message=message,
        )


@shared_task
def monitor_ipc_payment_delays():
    today = date.today()
    overdue = IPC.objects.filter(
        status=IPCStatus.APPROVED,
        planned_payment_date__lt=today,
        actual_payment_date__isnull=True,
        is_deleted=False,
    )
    for ipc in overdue:
        delay_days = (today - ipc.planned_payment_date).days
        send_ipc_delay_notification.delay(str(ipc.id), delay_days)


@shared_task
def monitor_guarantee_expiry():
    today = date.today()
    threshold = today + timedelta(days=30)
    contracts = Contract.objects.filter(is_deleted=False, status='active')
    for c in contracts:
        for label, exp in (
            ('حسن انجام کار', c.performance_guarantee_expiry),
            ('پیش‌پرداخت', c.advance_guarantee_expiry),
        ):
            if exp and today <= exp <= threshold:
                message = f'ضمانت‌نامه {label} قرارداد {c.contract_number} تا {exp} منقضی می‌شود'
                _notify_project_roles(c.project_id, ['finance_manager', 'project_manager'], message)
