from django.conf import settings
from django.db import models
from common.models import AuditSoftDeleteModel


class TransferStatus(models.TextChoices):
    PENDING  = 'pending',  'در انتظار تایید'
    APPROVED = 'approved', 'تایید شده'
    REJECTED = 'rejected', 'رد شده'


class InternalTransfer(AuditSoftDeleteModel):
    """انتقال بینبلوکی — فقط با تایید مدیر پروژه"""
    source_block = models.ForeignKey(
        'procurement.Block',
        on_delete=models.PROTECT,
        related_name='transfers_out',
    )
    target_block = models.ForeignKey(
        'procurement.Block',
        on_delete=models.PROTECT,
        related_name='transfers_in',
    )
    material = models.ForeignKey(
        'resources.Material',
        on_delete=models.PROTECT,
        related_name='internal_transfers',
    )
    quantity = models.DecimalField(max_digits=18, decimal_places=4)
    reason = models.TextField()
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_transfers',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=TransferStatus.choices,
        default=TransferStatus.PENDING,
    )
    cost_adjustment_notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'procurement_internal_transfers'
        ordering = ['-created_at']

    def __str__(self):
        return f'Transfer {self.source_block_id}→{self.target_block_id} ({self.quantity})'
