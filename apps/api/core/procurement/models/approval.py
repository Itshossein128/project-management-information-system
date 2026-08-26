from django.conf import settings
from django.db import models
from common.models import UUIDModel


class ApprovalAction(models.TextChoices):
    APPROVE = 'approve', 'تایید'
    REJECT  = 'reject',  'رد'
    RETURN  = 'return',  'بازگشت'


class ApprovalLog(UUIDModel):
    """ردپای تاییدها — immutable audit record"""
    requisition = models.ForeignKey(
        'procurement.RequisitionHeader',
        on_delete=models.CASCADE,
        related_name='approval_logs',
    )
    step_from = models.CharField(max_length=30)
    step_to = models.CharField(max_length=30)
    action = models.CharField(max_length=10, choices=ApprovalAction.choices)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+',
    )
    performed_at = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'procurement_approval_logs'
        ordering = ['performed_at']

    def __str__(self):
        return f'{self.requisition_id} | {self.step_from}→{self.step_to} ({self.action})'
