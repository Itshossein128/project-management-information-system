from django.utils import timezone
from rest_framework.exceptions import ValidationError

from sub_reports.models import SubReportStatus

def submit_sub_report(obj, user):
    if obj.status != SubReportStatus.DRAFT:
        raise ValidationError('فقط گزارش‌های پیش‌نویس قابل ارسال هستند')

    obj.status = SubReportStatus.SUBMITTED
    obj.submitted_by = user
    obj.submitted_at = timezone.now()
    obj.updated_by = user
    obj.save(update_fields=['status', 'submitted_by', 'submitted_at', 'updated_by', 'updated_at'])
    return obj


def approve_sub_report(obj, user):
    if obj.status != SubReportStatus.SUBMITTED:
        raise ValidationError('فقط گزارش‌های ارسال شده قابل تأیید هستند')

    obj.status = SubReportStatus.APPROVED
    obj.approved_by = user
    obj.approved_at = timezone.now()
    obj.updated_by = user
    obj.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_by', 'updated_at'])
    return obj


def reject_sub_report(obj, user, rejection_reason):
    if obj.status != SubReportStatus.SUBMITTED:
        raise ValidationError('فقط گزارش‌های ارسال شده قابل رد هستند')

    reason = (rejection_reason or '').strip()
    if len(reason) < 10:
        raise ValidationError({'rejection_reason': 'دلیل رد باید حداقل ۱۰ کاراکتر باشد'})

    obj.status = SubReportStatus.REJECTED
    obj.rejection_reason = reason
    obj.updated_by = user
    obj.save(update_fields=['status', 'rejection_reason', 'updated_by', 'updated_at'])
    return obj
