"""Celery tasks and notification helpers for daily reports."""
import logging

from celery import shared_task
from django.db.models import Sum

logger = logging.getLogger(__name__)


@shared_task
def recalculate_activity_progress(report_id):
    """Recompute cumulative progress for activities linked to an approved report.

    Enqueued on approve (direct Celery path for reliability without a consumer)
    and by the ``daily-report.approved`` event handler when the worker is running.
    Idempotent via ``ActivityProgress.update_or_create``.
    """
    from field_reports.models import DailyReport, DailyReportActivity, ReportStatus
    from schedule.models import ActivityProgress, MeasurementMethod
    from schedule.services.measurement_service import (
        ProgressValidationError,
        compute_quantity_progress,
        get_current_approved_version,
        record_progress,
    )

    report = DailyReport.objects.get(id=report_id)

    linked_rows = report.activities.filter(is_deleted=False, activity_ref__isnull=False)
    applied = 0
    skipped: list[dict] = []
    seen_activity_ids = set()
    for row in linked_rows:
        activity = row.activity_ref
        if activity.id in seen_activity_ids:
            continue
        seen_activity_ids.add(activity.id)

        version = get_current_approved_version(activity)
        if version is None or version.method != MeasurementMethod.QUANTITY:
            reason = 'measurement_not_approved' if version is None else 'method_not_quantity'
            logger.info(
                'Skipping progress recalculation for activity %s (report %s): %s',
                activity.id, report_id, reason,
            )
            skipped.append({'activity_id': str(activity.id), 'code': reason})
            continue

        cumulative = (
            DailyReportActivity.objects.filter(
                report__project=report.project,
                report__status=ReportStatus.APPROVED,
                report__is_deleted=False,
                activity_ref=activity,
                is_deleted=False,
                quantity_measured=True,
            ).aggregate(total=Sum('quantity'))['total']
            or 0
        )

        try:
            progress_pct = compute_quantity_progress(activity, cumulative, version)
        except ProgressValidationError as exc:
            # Do not clamp: >100% (or an incomplete basis) is never written as success.
            logger.warning(
                'Progress recalculation rejected for activity %s (report %s): %s',
                activity.id, report_id, exc.code,
            )
            skipped.append({'activity_id': str(activity.id), 'code': exc.code})
            continue

        record_progress(
            activity,
            report.report_date,
            progress_pct,
            report.approved_by,
            source=ActivityProgress.ProgressSource.DAILY_REPORT,
            cumulative_quantity=cumulative,
            version=version,
            approve=True,
        )
        applied += 1

    from schedule.services.progress_service import invalidate_s_curve_cache

    _auto_create_costs_from_report(report)
    _auto_create_inventory_from_report(report)
    invalidate_s_curve_cache(report.project_id)
    try:
        from common.cache_utils import invalidate_project_caches

        invalidate_project_caches(report.project_id)
    except Exception:
        pass
    return {
        'report_id': str(report_id),
        'activities': linked_rows.count(),
        'applied': applied,
        'skipped': skipped,
    }


def _auto_create_costs_from_report(report):
    """Create ActualCost rows from approved daily report equipment and material entries."""
    from cost_control.models import ActualCost, CostType
    from decimal import Decimal

    for eq_entry in report.equipment_entries.filter(is_deleted=False):
        if not eq_entry.productive_hours or not eq_entry.hourly_rate:
            continue
        amount = Decimal(str(eq_entry.productive_hours)) * Decimal(str(eq_entry.hourly_rate))
        ActualCost.objects.get_or_create(
            project=report.project,
            daily_report=report,
            activity=eq_entry.activity_ref,
            cost_category='equipment',
            defaults={
                'cost_date': report.report_date,
                'amount': amount,
                'description': f'ماشین\u200cآلات: {eq_entry.equipment_name}',
                'cost_type': CostType.DIRECT,
                'approved_by': report.approved_by,
                'created_by': report.approved_by or report.updated_by,
                'updated_by': report.approved_by or report.updated_by,
            },
        )

    for mat_entry in report.material_entries.filter(is_deleted=False):
        if not mat_entry.unit_cost or not mat_entry.material_ref_id:
            continue
        amount = Decimal(str(mat_entry.quantity)) * Decimal(str(mat_entry.unit_cost))
        ActualCost.objects.get_or_create(
            project=report.project,
            daily_report=report,
            activity=mat_entry.activity_ref,
            cost_category='material',
            defaults={
                'cost_date': report.report_date,
                'amount': amount,
                'description': f'مصالح: {mat_entry.material_description}',
                'cost_type': CostType.DIRECT,
                'approved_by': report.approved_by,
                'created_by': report.approved_by or report.updated_by,
                'updated_by': report.approved_by or report.updated_by,
            },
        )

    for labor_entry in report.labor_entries.filter(is_deleted=False):
        if not labor_entry.daily_rate or not labor_entry.total_count:
            continue
        amount = Decimal(str(labor_entry.total_count)) * Decimal(str(labor_entry.daily_rate))
        ActualCost.objects.get_or_create(
            project=report.project,
            daily_report=report,
            cost_category='labor',
            description=f'نیروی انسانی: {labor_entry.job_title}',
            defaults={
                'cost_date': report.report_date,
                'amount': amount,
                'cost_type': CostType.DIRECT,
                'approved_by': report.approved_by,
                'created_by': report.approved_by or report.updated_by,
                'updated_by': report.approved_by or report.updated_by,
            },
        )


def _auto_create_inventory_from_report(report):
    """Create inventory transactions from approved daily report material entries."""
    from field_reports.models import MaterialTransactionType
    from resources.models import InventoryTransaction, TransactionType

    type_map = {
        MaterialTransactionType.RECEIPT: TransactionType.IN,
        MaterialTransactionType.ISSUE: TransactionType.OUT,
        MaterialTransactionType.WASTE: TransactionType.WASTE,
    }

    for mat_entry in report.material_entries.filter(is_deleted=False):
        if not mat_entry.material_ref_id:
            continue
        tx_type = type_map.get(mat_entry.transaction_type, TransactionType.OUT)
        InventoryTransaction.objects.get_or_create(
            project=report.project,
            material=mat_entry.material_ref,
            daily_report=report,
            tx_type=tx_type,
            defaults={
                'tx_date': report.report_date,
                'quantity': mat_entry.quantity,
                'unit_cost': mat_entry.unit_cost,
                'activity': mat_entry.activity_ref,
                'notes': mat_entry.notes or '',
                'created_by': report.approved_by or report.updated_by,
                'updated_by': report.approved_by or report.updated_by,
            },
        )


def notify_report_event(event: str, report_id: str, project_id: str) -> None:
    """Create in-app notifications for a daily-report workflow event.

    Best-effort: if the notifications app is unavailable it logs and returns.
    """
    try:
        from field_reports.models import DailyReport
        from master_data.models import ProjectMember
        from notifications.models import Notification
    except Exception:  # noqa: BLE001 - notifications app optional until Section 5
        logger.info('Notifications not available; skipping event=%s report=%s', event, report_id)
        return

    try:
        report = DailyReport.objects.select_related('prepared_by').get(id=report_id)
    except DailyReport.DoesNotExist:
        return

    link = f'/projects/{project_id}/daily-reports/{report_id}/view'
    date = report.report_date

    if event == 'submitted':
        title = 'گزارش روزانه در انتظار تأیید'
        message = f'گزارش روزانه {date} ارسال شد و منتظر تأیید است'
        members = ProjectMember.objects.filter(
            project_id=project_id, status='active', user__isnull=False,
        ).select_related('user')
        recipients = [m.user for m in members if m.has_permission('approve_reports')]
        for user in recipients:
            Notification.objects.create(
                user=user,
                project_id=project_id,
                notification_type='report_submitted',
                title=title,
                message=message,
                link=link,
            )
        return

    if event == 'approved':
        if report.prepared_by:
            Notification.objects.create(
                user=report.prepared_by,
                project_id=project_id,
                notification_type='report_approved',
                title='گزارش روزانه تأیید شد',
                message=f'گزارش روزانه {date} تأیید شد.',
                link=link,
            )
        return

    if event == 'rejected':
        if report.prepared_by:
            edit_link = f'/projects/{project_id}/daily-reports/{report_id}/edit'
            Notification.objects.create(
                user=report.prepared_by,
                project_id=project_id,
                notification_type='report_rejected',
                title='گزارش روزانه رد شد',
                message=f'گزارش روزانه {date} رد شد. دلیل: {report.rejection_reason}',
                link=edit_link,
            )
        return
