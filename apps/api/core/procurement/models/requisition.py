from django.conf import settings
from django.db import models
from common.models import AuditSoftDeleteModel


class RequisitionType(models.TextChoices):
    PLANNED    = 'planned',    'عادی (Planned)'
    FAST_TRACK = 'fast_track', 'فورسماژور (Fast-Track)'
    POST_FACTO = 'post_facto', 'پسنگر (Post-Facto)'


class RequisitionPriority(models.TextChoices):
    NORMAL    = 'normal',    'Normal'
    HIGH      = 'high',      'High'
    EMERGENCY = 'emergency', 'Emergency'


class RequisitionStatus(models.TextChoices):
    DRAFT                = 'draft',                'پیشنویس'
    TECHNICAL_REVIEW     = 'technical_review',     'بررسی فنی'
    WORKSHOP_APPROVAL    = 'workshop_approval',    'تایید کارگاه'
    CONTROL_CHECK        = 'control_check',        'کنترل پروژه'
    PM_APPROVAL          = 'pm_approval',          'تایید مدیر پروژه'
    PROCUREMENT_QUEUE    = 'procurement_queue',    'صف تدارکات'
    HQ_CONTROL_APPROVAL  = 'hq_control_approval',  'تایید دفتر مرکزی'
    FINAL_APPROVAL       = 'final_approval',       'تایید نهایی'
    APPROVED             = 'approved',             'تایید شده'
    REJECTED             = 'rejected',             'رد شده'


class ItemStatus(models.TextChoices):
    PENDING   = 'pending',   'در انتظار'
    APPROVED  = 'approved',  'تایید شده'
    ON_HOLD   = 'on_hold',   'در انتظار بودجه'
    ORDERED   = 'ordered',   'سفارش داده شده'
    DELIVERED = 'delivered', 'تحویل شده'
    CANCELLED = 'cancelled', 'لغو شده'


class RequisitionHeader(AuditSoftDeleteModel):
    """سرتیتر درخواست خرید — چند آیتمی"""
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='requisitions',
    )
    block = models.ForeignKey(
        'procurement.Block',
        on_delete=models.PROTECT,
        related_name='requisitions',
    )
    requisition_number = models.CharField(max_length=30, unique=True, editable=False)
    requisition_type = models.CharField(
        max_length=20,
        choices=RequisitionType.choices,
        default=RequisitionType.PLANNED,
    )
    priority = models.CharField(
        max_length=20,
        choices=RequisitionPriority.choices,
        default=RequisitionPriority.NORMAL,
    )
    urgency = models.CharField(max_length=50, blank=True, default='')
    status = models.CharField(
        max_length=30,
        choices=RequisitionStatus.choices,
        default=RequisitionStatus.DRAFT,
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='requisitions_requested',
    )
    request_date = models.DateField()
    required_by_date = models.DateField(null=True, blank=True)
    is_grn_provisional = models.BooleanField(
        default=False,
        help_text='برای پسنگر: رسید انبار «موقت» تا تکمیل امضا',
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'procurement_requisitions'
        ordering = ['-request_date', '-created_at']
        indexes = [
            models.Index(fields=['project', 'status'], name='req_project_status_idx'),
            models.Index(fields=['block', 'status'], name='req_block_status_idx'),
        ]

    def __str__(self):
        return f'{self.requisition_number} ({self.get_status_display()})'

    def save(self, *args, **kwargs):
        if not self.requisition_number:
            self.requisition_number = self._generate_number()
        super().save(*args, **kwargs)

    @classmethod
    def _generate_number(cls):
        import uuid as _uuid
        from django.utils import timezone
        today = timezone.localdate()
        suffix = _uuid.uuid4().hex[:4].upper()
        return f'REQ-{today.strftime("%Y%m%d")}-{suffix}'


class RequisitionItem(AuditSoftDeleteModel):
    """ردیفهای درخواست خرید"""
    header = models.ForeignKey(
        RequisitionHeader,
        on_delete=models.CASCADE,
        related_name='items',
    )
    line_number = models.PositiveIntegerField()
    material = models.ForeignKey(
        'resources.Material',
        on_delete=models.PROTECT,
        related_name='requisition_items',
    )
    wbs_node = models.ForeignKey(
        'projects.WBS',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requisition_items',
    )
    requested_qty = models.DecimalField(max_digits=18, decimal_places=4)
    approved_qty = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    purchased_qty = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    status = models.CharField(
        max_length=20,
        choices=ItemStatus.choices,
        default=ItemStatus.PENDING,
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requisition_items',
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'procurement_requisition_items'
        unique_together = [['header', 'line_number']]
        ordering = ['line_number']

    def __str__(self):
        return f'{self.header.requisition_number} / Line {self.line_number}'
