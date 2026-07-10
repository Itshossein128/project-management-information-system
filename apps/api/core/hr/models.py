from django.conf import settings
from django.db import models

from common.models import AuditSoftDeleteModel


class OvertimeStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    SUPERVISOR_APPROVED = 'supervisor_approved', 'Supervisor approved'
    MANAGER_APPROVED = 'manager_approved', 'Manager approved'
    REJECTED = 'rejected', 'Rejected'


class OvertimeRequest(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='overtime_requests')
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='overtime_requests')
    department = models.CharField(max_length=120)
    request_date = models.DateField(auto_now_add=True)
    overtime_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    requested_hours = models.DecimalField(max_digits=5, decimal_places=2)
    reason = models.TextField()
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_overtime_requests',
    )
    supervisor_approved = models.BooleanField(null=True, blank=True)
    supervisor_notes = models.TextField(blank=True, default='')
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_overtime_requests',
    )
    manager_approved = models.BooleanField(null=True, blank=True)
    approved_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=30, choices=OvertimeStatus.choices, default=OvertimeStatus.DRAFT)

    class Meta:
        db_table = 'overtime_requests'
        ordering = ['-overtime_date']


class LeaveType(models.TextChoices):
    MISSION = 'mission', 'Mission'
    HOURLY = 'hourly', 'Hourly'
    DAILY = 'daily', 'Daily'


class LeaveStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    SUPERVISOR_APPROVED = 'supervisor_approved', 'Supervisor approved'
    MANAGER_APPROVED = 'manager_approved', 'Manager approved'
    SECURITY_APPROVED = 'security_approved', 'Security approved'
    REJECTED = 'rejected', 'Rejected'
    CANCELLED = 'cancelled', 'Cancelled'


class LeaveRequest(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='leave_requests')
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leave_requests')
    department = models.CharField(max_length=120)
    request_type = models.CharField(max_length=10, choices=LeaveType.choices)
    request_date = models.DateField(auto_now_add=True)
    leave_date = models.DateField()
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    replacement_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replacement_for_leaves',
    )
    mission_subject = models.TextField(blank=True, default='')
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_leave_requests',
    )
    supervisor_approved = models.BooleanField(null=True, blank=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_leave_requests',
    )
    manager_approved = models.BooleanField(null=True, blank=True)
    security_approved = models.BooleanField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=LeaveStatus.choices, default=LeaveStatus.DRAFT)

    class Meta:
        db_table = 'leave_requests'
        ordering = ['-leave_date']
