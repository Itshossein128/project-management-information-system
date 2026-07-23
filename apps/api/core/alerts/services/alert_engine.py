"""Central alert evaluation and dispatch."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from django.db import models
from django.utils import timezone

from alerts.models import AlertLog, AlertRule
from notifications.services.delivery import deliver_alert_notifications


def _normalize_alert_type(value: str) -> str:
    return (value or '').lower()


def _resolve_recipients(rule: AlertRule, project_id):
    from master_data.models import ProjectMember, ProjectMemberRole

    if rule.recipient_ids:
        return list(set(rule.recipient_ids))

    role_names = [r.strip() for r in (rule.notify_roles or '').split(',') if r.strip()]
    if not role_names:
        return []

    user_ids = set()
    members = ProjectMember.objects.filter(project_id=project_id, status='active')
    for member in members:
        roles = ProjectMemberRole.objects.filter(member=member).select_related('role')
        if any(r.role.role_name in role_names for r in roles):
            user_ids.add(member.user_id)
    return list(user_ids)


def fire_alert(rule_id, trigger_reference: str, message: str, project_id, extra_context=None):
    """Fire an alert if rule is active and cooldown allows."""
    rule = AlertRule.objects.filter(id=rule_id, is_active=True, is_deleted=False).first()
    if not rule:
        return None

    now = timezone.now()
    recent = AlertLog.objects.filter(
        rule=rule,
        trigger_reference=trigger_reference,
        fired_at__gte=now - timedelta(hours=rule.cooldown_hours),
    ).exists()
    if recent:
        return None

    recipients = _resolve_recipients(rule, project_id)
    link = (extra_context or {}).get('link', f'/projects/{project_id}/alerts')
    title = rule.name or rule.get_alert_type_display()

    sent = deliver_alert_notifications(
        user_ids=recipients,
        project_id=project_id,
        title=title,
        message=message,
        link=link,
    )

    return AlertLog.objects.create(
        rule=rule,
        project_id=project_id,
        trigger_reference=trigger_reference,
        message=message,
        notifications_sent=sent,
    )


def _rules_for_project(project_id, alert_type: str | None = None):
    qs = AlertRule.objects.filter(is_active=True, is_deleted=False).filter(
        models.Q(project_id=project_id) | models.Q(project__isnull=True)
    )
    if alert_type:
        qs = qs.filter(alert_type=_normalize_alert_type(alert_type))
    return qs.order_by(models.Case(models.When(project_id=project_id, then=0), default=1))


def check_and_fire_for_project(project_id):
    rules = _rules_for_project(project_id).distinct()
    seen_types = set()
    for rule in rules:
        if rule.alert_type in seen_types and rule.project_id is None:
            continue
        if rule.project_id:
            seen_types.add(rule.alert_type)
        _evaluate_rule(rule, project_id)


def _evaluate_rule(rule: AlertRule, project_id):
    from alerts.services.registry import alert_registry

    alert_registry.evaluate(rule, project_id)


def fire_alert_for_type(project_id, alert_type: str, trigger_reference: str, message: str, **extra):
    rule = _rules_for_project(project_id, alert_type).first()
    if rule:
        return fire_alert(rule.id, trigger_reference, message, project_id, extra_context=extra)
    return None
