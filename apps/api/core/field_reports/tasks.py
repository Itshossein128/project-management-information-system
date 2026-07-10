"""Celery tasks and notification helpers for daily reports."""
import logging

from celery import shared_task
from django.db.models import Sum

logger = logging.getLogger(__name__)


@shared_task
def recalculate_activity_progress(report_id):
    """Recompute cumulative progress for activities linked to an approved report.

    Triggered on the ``daily-report.approved`` event.
    """
    from field_reports.models import DailyReport, DailyReportActivity, ReportStatus
    from schedule.models import ActivityProgress

    report = DailyReport.objects.get(id=report_id)

    linked_rows = report.activities.filter(is_deleted=False, activity_ref__isnull=False)
    for row in linked_rows:
        activity = row.activity_ref
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

        progress_pct = 0
        if activity.total_quantity and activity.total_quantity > 0:
            progress_pct = min(float(cumulative) / float(activity.total_quantity), 1.0)

        ActivityProgress.objects.update_or_create(
            activity=activity,
            report_date=report.report_date,
            defaults={
                'actual_progress': progress_pct,
                'cumulative_quantity': cumulative,
                'updated_by': report.approved_by,
                'source': ActivityProgress.ProgressSource.DAILY_REPORT,
            },
        )

    from schedule.services.progress_service import invalidate_s_curve_cache

    invalidate_s_curve_cache(report.project_id)
    return {'report_id': str(report_id), 'activities': linked_rows.count()}


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
