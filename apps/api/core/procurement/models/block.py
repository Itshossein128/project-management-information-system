from django.db import models
from common.models import AuditSoftDeleteModel


class BlockKind(models.TextChoices):
    STANDARD = 'standard', 'Standard'
    WORKSHOP = 'workshop', 'Workshop'


WORKSHOP_BLOCK_CODE = 'WORKSHOP'
WORKSHOP_BLOCK_NAME = 'کارگاه'


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
    block_kind = models.CharField(
        max_length=20,
        choices=BlockKind.choices,
        default=BlockKind.STANDARD,
    )

    class Meta:
        db_table = 'procurement_blocks'
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'block_code'],
                condition=models.Q(is_deleted=False),
                name='uniq_block_project_code',
            ),
            models.UniqueConstraint(
                fields=['project'],
                condition=models.Q(is_deleted=False, block_kind='workshop'),
                name='uniq_workshop_block_per_project',
            ),
        ]

    def __str__(self):
        return f'{self.block_code} — {self.block_name}'
