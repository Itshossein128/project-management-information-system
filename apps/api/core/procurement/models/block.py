from django.db import models
from common.models import AuditSoftDeleteModel


class Block(AuditSoftDeleteModel):
    """بلوک/فاز پروژه — مرکز هزینه و انبار مجازی مستقل"""
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='blocks',
    )
    block_code = models.CharField(max_length=30)
    block_name = models.CharField(max_length=200)
    wbs = models.ForeignKey(
        'projects.WBS',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blocks',
    )
    budget = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'procurement_blocks'
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'block_code'],
                condition=models.Q(is_deleted=False),
                name='uniq_block_project_code',
            )
        ]

    def __str__(self):
        return f'{self.block_code} — {self.block_name}'
