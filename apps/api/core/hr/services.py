from rest_framework.exceptions import ValidationError
from hr.models import LeaveType, LeaveStatus, OvertimeStatus


def check_overtime_draft_status(overtime_request):
    if overtime_request.status != OvertimeStatus.DRAFT:
        raise ValidationError({'message': 'فقط درخواست‌های پیش‌نویس قابل ویرایش یا حذف هستند.'})


def submit_overtime(overtime_request, user):
    if overtime_request.status != OvertimeStatus.DRAFT:
        raise ValidationError({'message': 'وضعیت نامعتبر'})

    overtime_request.status = OvertimeStatus.SUBMITTED
    overtime_request.updated_by = user
    overtime_request.save(update_fields=['status', 'updated_by', 'updated_at'])
    return overtime_request


def supervisor_approve_overtime(overtime_request, user, approved: bool, notes: str = ''):
    overtime_request.supervisor_approved = approved
    overtime_request.supervisor_notes = notes
    overtime_request.status = OvertimeStatus.SUPERVISOR_APPROVED if approved else OvertimeStatus.REJECTED
    overtime_request.updated_by = user
    overtime_request.save()
    return overtime_request


def manager_approve_overtime(overtime_request, user, approved: bool, approved_hours: float = None):
    if approved:
        approved_hours_val = approved_hours if approved_hours is not None else overtime_request.requested_hours
        if float(approved_hours_val) > float(overtime_request.requested_hours):
            raise ValidationError({'message': 'ساعات تأییدشده نمی‌تواند بیشتر از درخواست باشد.'})
        overtime_request.approved_hours = approved_hours_val
        overtime_request.status = OvertimeStatus.MANAGER_APPROVED
    else:
        overtime_request.status = OvertimeStatus.REJECTED

    overtime_request.manager_approved = approved
    overtime_request.updated_by = user
    overtime_request.save()
    return overtime_request


def check_leave_draft_status(leave_request):
    if leave_request.status != LeaveStatus.DRAFT:
        raise ValidationError({'message': 'فقط درخواست‌های پیش‌نویس قابل ویرایش یا حذف هستند.'})


def submit_leave(leave_request, user):
    if leave_request.status != LeaveStatus.DRAFT:
        raise ValidationError({'message': 'وضعیت نامعتبر'})

    leave_request.status = LeaveStatus.SUBMITTED
    leave_request.updated_by = user
    leave_request.save(update_fields=['status', 'updated_by', 'updated_at'])
    return leave_request


def supervisor_approve_leave(leave_request, user, approved: bool):
    leave_request.supervisor_approved = approved
    leave_request.status = LeaveStatus.SUPERVISOR_APPROVED if approved else LeaveStatus.REJECTED
    leave_request.updated_by = user
    leave_request.save()
    return leave_request


def manager_approve_leave(leave_request, user, approved: bool):
    leave_request.manager_approved = approved
    leave_request.status = LeaveStatus.MANAGER_APPROVED if approved else LeaveStatus.REJECTED
    leave_request.updated_by = user
    leave_request.save()
    return leave_request


def security_approve_leave(leave_request, user, approved: bool):
    if leave_request.request_type != LeaveType.MISSION or leave_request.status != LeaveStatus.MANAGER_APPROVED:
        raise ValidationError({'message': 'فقط مأموریت‌های تأییدشده توسط مدیر قابل تأیید حراست هستند.'})

    leave_request.security_approved = approved
    leave_request.status = LeaveStatus.SECURITY_APPROVED if approved else LeaveStatus.REJECTED
    leave_request.updated_by = user
    leave_request.save()
    return leave_request
