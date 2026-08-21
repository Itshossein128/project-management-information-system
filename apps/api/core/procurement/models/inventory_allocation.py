from django.db import models
from common.models import AuditSoftDeleteModel


class InventoryAllocation(AuditSoftDeleteModel):
    """قفلگذاری موجودی به کد MR و بلوک"""
    requisition_item = models.ForeignKey(
        'procurement.RequisitionItem',
        on_delete=models.CASCADE,
        related_name='allocations',
    )
    block = models.ForeignKey(
        'procurement.Block',
        on_delete=models.PROTECT,
        related_name='allocations',
    )
    material = models.ForeignKey(
        'resources.Material',
        on_delete=models.PROTECT,
        related_name='allocations',
    )
    allocated_qty = models.DecimalField(max_digits=18, decimal_places=4)
    received_qty = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    issued_qty = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    mr_tag = models.CharField(
        max_length=120,
        help_text='[MR-ID]-[Block-ID] tag for block-level inventory tracing',
    )

    class Meta:
        db_table = 'procurement_inventory_allocations'
        indexes = [
            models.Index(fields=['block', 'material'], name='alloc_block_material_idx'),
            models.Index(fields=['mr_tag'], name='alloc_mr_tag_idx'),
        ]

    def __str__(self):
        return f'{self.mr_tag} — {self.allocated_qty}'
