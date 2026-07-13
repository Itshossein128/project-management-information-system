"""Celery tasks for contracts module."""

from datetime import date, timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

from common.jalali import gregorian_to_jalali
from contracts.models import Contract, ContractStatus, IPC, IPCStatus
from notifications.models import Notification, NotificationType

User = get_user_model()

GUARANTEE_THRESHOLD_DAYS = 30


@shared_task
def populate_ipc_async(ipc_id):
    from contracts.services.ipc_service import apply_deductions, auto_populate_ipc

    auto_populate_ipc(ipc_id)
    apply_deductions(ipc_id)


def _project_role_user_ids(project_id, role_names):
    from master_data.models import ProjectMember, ProjectMemberRole

    members = ProjectMember.objects.filter(project_id=project_id, status='active')
    user_ids = set()
    for member in members:
        roles = ProjectMemberRole.objects.filter(member=member).select_related('role')
        if any(r.role.role_name in role_names for r in roles):
            user_ids.add(member.user_id)
    return user_ids


def _notify_ipc_payment_delay(ipc, delay_days):
    title = f'تأخیر پرداخت صدور موقت شماره {ipc.ipc_number}'
    message = (
        f'صدور موقت شماره {ipc.ipc_number} '
        f'قرارداد {ipc.contract.counterparty or ipc.contract.contract_number} '
        f'تاکنون {delay_days} روز از موعد پرداخت گذشته است.'
    )
    link = f'/projects/{ipc.project_id}/ipcs/{ipc.id}/'
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    for user_id in _project_role_user_ids(ipc.project_id, ['finance_manager', 'project_manager']):
        if Notification.objects.filter(
            user_id=user_id,
            project_id=ipc.project_id,
            title=title,
            created_at__gte=today_start,
        ).exists():
            continue
        Notification.objects.create(
            user_id=user_id,
            project_id=ipc.project_id,
            notification_type=NotificationType.GENERIC,
            title=title,
            message=message,
            link=link,
        )


@shared_task
def send_ipc_delay_notification(ipc_id, delay_days):
    ipc = IPC.objects.select_related('contract', 'project').get(pk=ipc_id)
    _notify_ipc_payment_delay(ipc, delay_days)


@shared_task
def monitor_ipc_payment_delays():
    from alerts.services.alert_engine import fire_alert_for_type

    today = date.today()
    overdue = IPC.objects.filter(
        status=IPCStatus.APPROVED,
        planned_payment_date__lt=today,
        actual_payment_date__isnull=True,
        is_deleted=False,
    ).select_related('contract', 'project')
    for ipc in overdue:
        delay_days = (today - ipc.planned_payment_date).days
        fire_alert_for_type(
            ipc.project_id,
            'ipc_payment_overdue',
            f'ipc:{ipc.id}',
            (
                f'صدور موقت شماره {ipc.ipc_number} '
                f'قرارداد {ipc.contract.counterparty or ipc.contract.contract_number} '
                f'تاکنون {delay_days} روز از موعد پرداخت گذشته است.'
            ),
            link=f'/projects/{ipc.project_id}/ipcs/{ipc.id}/',
        )


@shared_task
def monitor_guarantee_expiry():
    from alerts.services.alert_engine import fire_alert_for_type

    today = date.today()
    threshold = today + timedelta(days=GUARANTEE_THRESHOLD_DAYS)

    expiring_performance = Contract.objects.filter(
        is_deleted=False,
        status=ContractStatus.ACTIVE,
        performance_guarantee_expiry__isnull=False,
        performance_guarantee_expiry__lte=threshold,
        performance_guarantee_expiry__gte=today,
    ).select_related('project')
    for contract in expiring_performance:
        days_left = (contract.performance_guarantee_expiry - today).days
        jalali_expiry = gregorian_to_jalali(contract.performance_guarantee_expiry)
        fire_alert_for_type(
            contract.project_id,
            'guarantee_expiring',
            f'guarantee:{contract.id}:performance',
            (
                f'ضمانت‌نامه حسن انجام کار قرارداد '
                f'{contract.contract_number or contract.counterparty} '
                f'در {days_left} روز دیگر ({jalali_expiry}) منقضی می‌شود.'
            ),
            link=f'/projects/{contract.project_id}/contracts/{contract.id}/',
        )

    expiring_advance = Contract.objects.filter(
        is_deleted=False,
        status=ContractStatus.ACTIVE,
        advance_guarantee_expiry__isnull=False,
        advance_guarantee_expiry__lte=threshold,
        advance_guarantee_expiry__gte=today,
    ).select_related('project')
    for contract in expiring_advance:
        days_left = (contract.advance_guarantee_expiry - today).days
        jalali_expiry = gregorian_to_jalali(contract.advance_guarantee_expiry)
        fire_alert_for_type(
            contract.project_id,
            'guarantee_expiring',
            f'guarantee:{contract.id}:advance',
            (
                f'ضمانت‌نامه پیش‌پرداخت قرارداد '
                f'{contract.contract_number or contract.counterparty} '
                f'در {days_left} روز دیگر ({jalali_expiry}) منقضی می‌شود.'
            ),
            link=f'/projects/{contract.project_id}/contracts/{contract.id}/',
        )
