"""Central alert evaluation and dispatch."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from django.db import models
from django.utils import timezone

from alerts.models import AlertLog, AlertRule
from notifications.models import Notification, NotificationType


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
    sent = 0
    link = (extra_context or {}).get('link', f'/projects/{project_id}/alerts')
    title = rule.name or rule.get_alert_type_display()

    for user_id in recipients:
        Notification.objects.create(
            user_id=user_id,
            project_id=project_id,
            notification_type=NotificationType.GENERIC,
            title=title,
            message=message,
            link=link,
        )
        sent += 1

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
    checkers = {
        'ipc_payment_overdue': _check_ipc_overdue,
        'guarantee_expiring': _check_guarantees,
        'budget_overrun': _check_budget_overrun,
        'cash_gap_detected': _check_cash_gap,
        'low_stock': _check_low_stock,
        'activity_behind_schedule': _check_activity_behind,
        'missing_daily_report': _check_missing_report,
        'daily_report_not_approved': _check_report_not_approved,
        'subcontractor_at_risk': _check_subcontractor_risk,
        'subcontractor_score_low': _check_subcontractor_score_low,
        'correspondence_response_due': _check_correspondence_due,
        'baseline_not_set': _check_baseline_not_set,
        'sync_conflict_unresolved': _check_sync_conflict_unresolved,
    }
    checker = checkers.get(_normalize_alert_type(rule.alert_type))
    if checker:
        checker(rule, project_id)


def _check_ipc_overdue(rule, project_id):
    from contracts.models import IPC, IPCStatus

    today = date.today()
    threshold_days = int(float(rule.threshold or 0))
    overdue = IPC.objects.filter(
        project_id=project_id,
        status=IPCStatus.APPROVED,
        planned_payment_date__lt=today - timedelta(days=threshold_days),
        actual_payment_date__isnull=True,
        is_deleted=False,
    ).select_related('contract')
    for ipc in overdue:
        delay_days = (today - ipc.planned_payment_date).days
        fire_alert(
            rule.id,
            f'ipc:{ipc.id}',
            f'صدور موقت شماره {ipc.ipc_number} قرارداد {ipc.contract.counterparty} '
            f'تاکنون {delay_days} روز از موعد پرداخت گذشته است.',
            project_id,
            extra_context={'link': f'/projects/{project_id}/ipcs/{ipc.id}/'},
        )


def _check_guarantees(rule, project_id):
    from contracts.models import Contract, ContractStatus

    threshold_days = int(float(rule.threshold or 30))
    today = date.today()
    cutoff = today + timedelta(days=threshold_days)
    contracts = Contract.objects.filter(
        project_id=project_id,
        is_deleted=False,
        status=ContractStatus.ACTIVE,
    )
    for contract in contracts:
        for field, label in (
            ('performance_guarantee_expiry', 'ضمانت‌نامه حسن انجام کار'),
            ('advance_guarantee_expiry', 'ضمانت‌نامه پیش‌پرداخت'),
        ):
            expiry = getattr(contract, field, None)
            if expiry and today <= expiry <= cutoff:
                days_left = (expiry - today).days
                fire_alert(
                    rule.id,
                    f'guarantee:{contract.id}:{field}',
                    f'{label} قرارداد {contract.contract_number or contract.counterparty} '
                    f'در {days_left} روز دیگر منقضی می‌شود.',
                    project_id,
                    extra_context={'link': f'/projects/{project_id}/contracts/{contract.id}/'},
                )


def _check_budget_overrun(rule, project_id):
    from cost_control.services.variance_service import get_budget_vs_actual

    threshold_pct = float(rule.threshold or 100)
    for item in get_budget_vs_actual(project_id, group_by='wbs'):
        budget = float(item.get('budget') or 0)
        actual = float(item.get('actual') or 0)
        if budget > 0:
            consumption = actual / budget * 100
            if consumption >= threshold_pct:
                fire_alert(
                    rule.id,
                    f'wbs:{item.get("wbs_id") or item.get("id")}',
                    f'بودجه WBS {item.get("wbs_name") or item.get("name")} '
                    f'به {consumption:.1f}٪ مصرف رسیده است',
                    project_id,
                )


def _check_cash_gap(rule, project_id):
    from cash_flow.services.cashflow_service import get_gap_analysis

    for g in get_gap_analysis(project_id):
        if g.get('is_cumulative_negative'):
            fire_alert(
                rule.id,
                f'cash_gap:{g.get("month")}',
                f'کمبود نقدینگی در {g.get("month")}: مبلغ {g.get("gap_amount", 0):,.0f} ریال',
                project_id,
            )


def _check_low_stock(rule, project_id):
    from resources.models import Material
    from resources.services.balance_service import compute_material_balance

    for material in Material.objects.filter(project_id=project_id, is_deleted=False):
        row = compute_material_balance(material)
        if row.get('is_low_stock'):
            fire_alert(
                rule.id,
                f'stock:{material.id}',
                f'موجودی {material.material_name} کمتر از حد مجاز است',
                project_id,
            )


def _check_activity_behind(rule, project_id):
    from projects.models import Activity
    from schedule.models import ActivityProgress

    threshold_pct = float(rule.threshold or 10) / 100
    for activity in Activity.objects.filter(project_id=project_id, is_deleted=False):
        prog = ActivityProgress.objects.filter(activity=activity).order_by('-report_date').first()
        if not prog:
            continue
        planned = float(prog.planned_progress or 0)
        actual = float(prog.actual_progress or 0)
        if planned - actual > threshold_pct:
            fire_alert(
                rule.id,
                f'activity:{activity.id}',
                f'فعالیت {activity.activity_name} بیش از {threshold_pct * 100:.0f}٪ از برنامه عقب است',
                project_id,
                extra_context={'link': f'/projects/{project_id}/activities'},
            )


def _check_missing_report(rule, project_id):
    from field_reports.models import DailyReport

    days = int(float(rule.threshold or 1))
    target = date.today() - timedelta(days=days)
    exists = DailyReport.objects.filter(
        project_id=project_id,
        report_date=target,
        is_deleted=False,
    ).exists()
    if not exists:
        fire_alert(
            rule.id,
            f'missing_report:{target.isoformat()}',
            f'گزارش روزانه برای تاریخ {target.isoformat()} ارسال نشده است',
            project_id,
        )


def _check_report_not_approved(rule, project_id):
    from field_reports.models import DailyReport, ReportStatus

    hours = int(float(rule.threshold or 24))
    cutoff = timezone.now() - timedelta(hours=hours)
    pending = DailyReport.objects.filter(
        project_id=project_id,
        status=ReportStatus.SUBMITTED,
        submitted_at__lte=cutoff,
        is_deleted=False,
    )
    for report in pending:
        fire_alert(
            rule.id,
            f'report:{report.id}',
            f'گزارش روزانه {report.report_date} بیش از {hours} ساعت در انتظار تأیید است',
            project_id,
        )


def _check_subcontractor_risk(rule, project_id):
    from subcontractors.models import Subcontractor
    from subcontractors.services.risk_service import compute_risk_flag

    for sub in Subcontractor.objects.filter(project_id=project_id, is_deleted=False):
        flag, reasons = compute_risk_flag(sub)
        if flag:
            fire_alert(
                rule.id,
                f'sub_risk:{sub.id}',
                f'پیمانکار {sub.company_name} در وضعیت ریسک: {"؛ ".join(reasons)}',
                project_id,
                extra_context={'link': f'/projects/{project_id}/subcontractors/{sub.id}'},
            )


def _check_subcontractor_score_low(rule, project_id):
    from subcontractors.models import Subcontractor

    threshold = float(rule.threshold or 6)
    for sub in Subcontractor.objects.filter(project_id=project_id, is_deleted=False):
        latest = sub.scores.filter(is_deleted=False).order_by('-score_date').first()
        if latest and latest.overall_score is not None and float(latest.overall_score) < threshold:
            fire_alert(
                rule.id,
                f'sub_score:{sub.id}',
                f'نمره عملکرد پیمانکار {sub.company_name} ({latest.overall_score}) کمتر از {threshold} است',
                project_id,
            )


def _check_correspondence_due(rule, project_id):
    from documents.models import Correspondence, CorrStatus

    days = int(float(rule.threshold or 3))
    cutoff = date.today() + timedelta(days=days)
    items = Correspondence.objects.filter(
        project_id=project_id,
        is_deleted=False,
        status=CorrStatus.OPEN,
        response_due_date__isnull=False,
        response_due_date__lte=cutoff,
    )
    for item in items:
        fire_alert(
            rule.id,
            f'correspondence:{item.id}',
            f'مکاتبه {item.corr_number} تا {item.response_due_date} نیاز به پاسخ دارد',
            project_id,
        )


def _check_baseline_not_set(rule, project_id):
    from schedule.models import BaselineSchedule

    if not BaselineSchedule.objects.filter(project_id=project_id, is_current=True).exists():
        fire_alert(
            rule.id,
            f'baseline:{project_id}',
            'برای این پروژه خط مبنای جاری تعریف نشده است',
            project_id,
        )


def _check_sync_conflict_unresolved(rule, project_id):
    from field_reports.models import SyncConflictLog

    for entry in SyncConflictLog.objects.filter(project_id=project_id, resolved_at__isnull=True):
        ref = entry.local_id or str(entry.daily_report_id or entry.id)
        fire_alert(
            rule.id,
            f'sync_conflict:{ref}',
            f'تعارض همگام‌سازی حل‌نشده: {entry.conflict_reason}',
            project_id,
            extra_context={'link': f'/projects/{project_id}/sync-conflicts'},
        )


def fire_alert_for_type(project_id, alert_type: str, trigger_reference: str, message: str, **extra):
    rule = _rules_for_project(project_id, alert_type).first()
    if rule:
        return fire_alert(rule.id, trigger_reference, message, project_id, extra_context=extra)
    return None
