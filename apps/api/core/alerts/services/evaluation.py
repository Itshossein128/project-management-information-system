"""Alert evaluation and notification dispatch."""

from __future__ import annotations

from alerts.models import AlertLog, AlertRule
from notifications.models import Notification, NotificationType

DEFAULT_RULE_TYPES = [
    'IPC_PAYMENT_OVERDUE',
    'GUARANTEE_EXPIRING',
    'CORRESPONDENCE_RESPONSE_DUE',
    'SUBCONTRACTOR_AT_RISK',
    'CASH_GAP_DETECTED',
]


def ensure_project_rules(project_id):
    for alert_type in DEFAULT_RULE_TYPES:
        AlertRule.objects.get_or_create(
            project_id=project_id,
            alert_type=alert_type,
            defaults={
                'threshold': 30 if alert_type == 'GUARANTEE_EXPIRING' else 3,
                'condition': 'lte',
                'is_active': True,
                'recipient_ids': [],
            },
        )


def _notify_roles(project_id, role_names: list[str], title: str, message: str, rule: AlertRule | None = None):
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
            title=title,
            message=message,
        )
    if rule:
        AlertLog.objects.create(rule=rule, message=message)


def fire_subcontractor_at_risk(sub, reasons: list[str]):
    ensure_project_rules(sub.project_id)
    rule = AlertRule.objects.filter(project_id=sub.project_id, alert_type='SUBCONTRACTOR_AT_RISK').first()
    msg = f'پیمانکار {sub.company_name} در وضعیت ریسک قرار گرفت: {"؛ ".join(reasons)}'
    _notify_roles(sub.project_id, ['project_manager'], 'ریسک پیمانکار', msg, rule)


def fire_cash_gap(project_id, month: str, amount: float):
    ensure_project_rules(project_id)
    rule = AlertRule.objects.filter(project_id=project_id, alert_type='CASH_GAP_DETECTED').first()
    msg = f'کمبود نقدینگی در {month}: مبلغ {amount:,.0f} ریال'
    _notify_roles(project_id, ['finance_manager', 'project_manager'], 'کمبود نقدینگی', msg, rule)
