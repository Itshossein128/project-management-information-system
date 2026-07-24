"""Alert checker functions registered with the alert_registry."""

from datetime import date, timedelta
from django.utils import timezone

from alerts.services.registry import alert_registry
from alerts.services.alert_engine import fire_alert


@alert_registry.register('ipc_payment_overdue')
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


@alert_registry.register('guarantee_expiring')
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


@alert_registry.register('budget_overrun')
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


@alert_registry.register('cash_gap_detected')
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


@alert_registry.register('low_stock')
def _check_low_stock(rule, project_id):
    from resources.models import Material
    from resources.services.balance_service import compute_material_balance

    for material in Material.objects.filter(project_id=project_id):
        row = compute_material_balance(material)
        if row.get('is_low_stock'):
            fire_alert(
                rule.id,
                f'stock:{material.id}',
                f'موجودی {material.material_name} کمتر از حد مجاز است',
                project_id,
            )


@alert_registry.register('activity_behind_schedule')
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


@alert_registry.register('missing_daily_report')
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


@alert_registry.register('daily_report_not_approved')
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


@alert_registry.register('subcontractor_at_risk')
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


@alert_registry.register('subcontractor_score_low')
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


@alert_registry.register('correspondence_response_due')
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


@alert_registry.register('baseline_not_set')
def _check_baseline_not_set(rule, project_id):
    from schedule.models import BaselineSchedule

    if not BaselineSchedule.objects.filter(project_id=project_id, is_current=True).exists():
        fire_alert(
            rule.id,
            f'baseline:{project_id}',
            'برای این پروژه خط مبنای جاری تعریف نشده است',
            project_id,
        )


@alert_registry.register('sync_conflict_unresolved')
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


@alert_registry.register('critical_path_delay')
def _check_critical_path_delay(rule, project_id):
    """Critical baseline activities behind plan by lag ≥ threshold %."""
    from schedule.models import ActivityProgress, BaselineActivity, BaselineSchedule

    threshold_pct = float(rule.threshold or 5) / 100
    current = BaselineSchedule.objects.filter(project_id=project_id, is_current=True).first()
    if not current:
        return

    critical = BaselineActivity.objects.filter(
        baseline=current,
        is_critical=True,
    ).select_related('activity')

    activity_ids = [ba.activity_id for ba in critical]
    if not activity_ids:
        return

    progresses = (
        ActivityProgress.objects.filter(activity_id__in=activity_ids)
        .order_by('activity_id', '-report_date')
        .distinct('activity_id')
    )
    progress_map = {p.activity_id: p for p in progresses}

    for ba in critical:
        act = ba.activity
        if act is None or getattr(act, 'is_deleted', False):
            continue
        prog = progress_map.get(act.id)
        if not prog:
            continue
        planned = float(prog.planned_progress or 0)
        actual = float(prog.actual_progress or 0)
        if planned - actual > threshold_pct:
            fire_alert(
                rule.id,
                f'critical_path:{act.id}',
                f'فعالیت بحرانی {act.activity_name} بیش از {threshold_pct * 100:.0f}٪ از برنامه عقب است',
                project_id,
                extra_context={'link': f'/projects/{project_id}/schedule/gantt'},
            )


@alert_registry.register('ipc_approval_delayed')
def _check_ipc_approval_delayed(rule, project_id):
    """IPC stuck in submitted/under_review beyond threshold days."""
    from contracts.models import IPC, IPCStatus

    days = int(float(rule.threshold or 7))
    cutoff = date.today() - timedelta(days=days)
    pending = IPC.objects.filter(
        project_id=project_id,
        status__in=[IPCStatus.SUBMITTED, IPCStatus.UNDER_REVIEW],
        is_deleted=False,
    ).select_related('contract')

    for ipc in pending:
        anchor = ipc.submitted_date or ipc.prepared_date
        if not anchor or anchor > cutoff:
            continue
        delay = (date.today() - anchor).days
        fire_alert(
            rule.id,
            f'ipc_approval:{ipc.id}',
            f'صدور موقت شماره {ipc.ipc_number} قرارداد {ipc.contract.counterparty} '
            f'{delay} روز در انتظار تأیید است',
            project_id,
            extra_context={'link': f'/projects/{project_id}/contracts/{ipc.contract_id}'},
        )


@alert_registry.register('procurement_overdue')
def _check_procurement_overdue(rule, project_id):
    """POs past expected delivery without actual delivery, or MRs past required_by."""
    from resources.models import MaterialRequest, MaterialRequestStatus, PurchaseOrder

    today = date.today()
    grace = int(float(rule.threshold or 0))
    cutoff = today - timedelta(days=grace)

    overdue_pos = PurchaseOrder.objects.filter(
        project_id=project_id,
        is_deleted=False,
        actual_delivery_date__isnull=True,
        expected_delivery_date__isnull=False,
        expected_delivery_date__lte=cutoff,
    ).select_related('material_request', 'material_request__material')

    for po in overdue_pos:
        mr = po.material_request
        if mr and mr.status == MaterialRequestStatus.DELIVERED:
            continue
        name = mr.material.material_name if mr and mr.material_id else f'PO-{po.po_number}'
        fire_alert(
            rule.id,
            f'po_overdue:{po.id}',
            f'سفارش خرید {po.po_number} ({name}) از موعد تحویل گذشته است',
            project_id,
            extra_context={'link': f'/projects/{project_id}/procurement'},
        )

    overdue_mrs = MaterialRequest.objects.filter(
        project_id=project_id,
        is_deleted=False,
        required_by_date__isnull=False,
        required_by_date__lte=cutoff,
    ).exclude(
        status__in=[MaterialRequestStatus.DELIVERED, MaterialRequestStatus.CANCELLED],
    ).select_related('material')

    for mr in overdue_mrs:
        # Skip if already covered by PO alert for same request
        if hasattr(mr, 'purchase_order') and mr.purchase_order and not mr.purchase_order.is_deleted:
            po = mr.purchase_order
            if po.expected_delivery_date and po.actual_delivery_date is None:
                continue
        fire_alert(
            rule.id,
            f'mr_overdue:{mr.id}',
            f'درخواست مصالح {mr.request_number} ({mr.material.material_name}) از موعد نیاز گذشته است',
            project_id,
            extra_context={'link': f'/projects/{project_id}/procurement'},
        )
