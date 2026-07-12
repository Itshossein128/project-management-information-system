from django.db import models

from common.models import TimeStampedModel
from projects.models import Project


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Item(models.Model):
    """Deprecated global inventory item — use resources.Material instead."""

    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.quantity})'


class SpaceMaterialRequest(TimeStampedModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='space_material_requests',
    )
    block_number = models.PositiveIntegerField()
    floor_number = models.IntegerField()
    unit_number = models.CharField(max_length=50)
    space_name = models.CharField(max_length=255)
    material_code = models.CharField(max_length=100, db_index=True)
    item_description = models.CharField(max_length=500)
    technical_specs = models.TextField(blank=True, default='')
    approved_quantity_technical_office = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    deliverable_quantity_inventory_unit = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    unit = models.CharField(max_length=50)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'material_code'], name='smr_project_material_idx'),
            models.Index(fields=['project', 'block_number', 'floor_number'], name='smr_project_block_floor_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.project.project_code}: {self.material_code} ({self.space_name})'


class Department(models.TextChoices):
    BUILDINGS = 'buildings', 'ابنیه'
    MECHANICAL = 'mechanical', 'مکانیک'
    SECURITY = 'security', 'حراست'
    MACHINERY = 'machinery', 'ماشین آلات'
    WAREHOUSE = 'warehouse', 'انباردار'
    ELECTRICAL = 'electrical', 'برق'


class DepartmentActivityRecord(TimeStampedModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='department_activity_records',
    )
    department = models.CharField(max_length=32, choices=Department.choices, db_index=True)
    date = models.DateField()
    location = models.CharField(max_length=255)
    activity_description = models.CharField(max_length=500)
    contractor = models.CharField(max_length=255)
    unit = models.CharField(max_length=64)
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(
                fields=['project', 'department', 'date'],
                name='dar_proj_dept_date_idx',
            ),
            models.Index(
                fields=['project', 'department'],
                name='dar_proj_dept_idx',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.project.project_code}/{self.department}: {self.activity_description[:40]} ({self.date})'
