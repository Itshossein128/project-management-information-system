from django.utils import timezone
from rest_framework.exceptions import ValidationError
from sub_reports.models import SubReportStatus

def submit_sub_report(sub_report, user):
    if sub_report.status != SubReportStatus.DRAFT:
        raise ValidationError('فقط گزارش‌های پیش‌نویس قابل ارسال هستند')

    sub_report.status = SubReportStatus.SUBMITTED
    sub_report.submitted_by = user
    sub_report.submitted_at = timezone.now()
    sub_report.updated_by = user
    sub_report.save(update_fields=['status', 'submitted_by', 'submitted_at', 'updated_by', 'updated_at'])
    return sub_report

def approve_sub_report(sub_report, user):
    if sub_report.status != SubReportStatus.SUBMITTED:
        raise ValidationError('فقط گزارش‌های ارسال شده قابل تأیید هستند')

    sub_report.status = SubReportStatus.APPROVED
    sub_report.approved_by = user
    sub_report.approved_at = timezone.now()
    sub_report.updated_by = user
    sub_report.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_by', 'updated_at'])
    return sub_report

def reject_sub_report(sub_report, user, rejection_reason):
    if sub_report.status != SubReportStatus.SUBMITTED:
        raise ValidationError('فقط گزارش‌های ارسال شده قابل رد هستند')

    reason = (rejection_reason or '').strip()
    if len(reason) < 10:
        raise ValidationError({'rejection_reason': 'دلیل رد باید حداقل ۱۰ کاراکتر باشد'})

    sub_report.status = SubReportStatus.REJECTED
    sub_report.rejection_reason = reason
    sub_report.updated_by = user
    sub_report.save(update_fields=['status', 'rejection_reason', 'updated_by', 'updated_at'])
    return sub_report
