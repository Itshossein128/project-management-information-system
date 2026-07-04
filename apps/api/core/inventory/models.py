from django.db import models

from business_meta.models import Business


# Class representing Category
class Category(models.Model):
    name = models.CharField(max_length=100)

    # Class representing Meta
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    # Function to handle   str
    def __str__(self):
        return self.name


# Class representing Item
class Item(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    # Class representing Meta
    class Meta:
        ordering = ['name']

    # Function to handle   str
    def __str__(self):
        return f"{self.name} ({self.quantity})"


# Class representing SpaceMaterialRequest
class SpaceMaterialRequest(models.Model):
    """
    Business-scoped grid/form entity for building space material requests/approvals.

    Persian fields (UI):
    - شماره بلوک: block_number
    - شماره طبقه: floor_number
    - شماره واحد: unit_number
    - نام فضا: space_name
    - کد متریال: material_code
    - شرح کالا: item_description
    - مشخصات فنی: technical_specs
    - مقدار مورد تایید (دفتر فنی): approved_quantity_technical_office
    - مقدار قابل تحویل (واحد انبار): deliverable_quantity_inventory_unit
    - واحد: unit
    """

    business = models.ForeignKey(
        Business,
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Class representing Meta
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['business', 'material_code'], name='smr_business_material_idx'),
            models.Index(fields=['business', 'block_number', 'floor_number'], name='smr_business_block_floor_idx'),
        ]

    # Function to handle   str
    def __str__(self) -> str:
        return f'{self.business.slug}: {self.material_code} ({self.space_name})'


# Class representing Department
class Department(models.TextChoices):
    """
    Department keys used as a discriminator on DepartmentActivityRecord.
    Slugs match the frontend route segments under /businesses/:id/<slug>.
    """

    BUILDINGS = 'buildings', 'ابنیه'
    MECHANICAL = 'mechanical', 'مکانیک'
    SECURITY = 'security', 'حراست'
    MACHINERY = 'machinery', 'ماشین آلات'
    WAREHOUSE = 'warehouse', 'انباردار'
    ELECTRICAL = 'electrical', 'برق'


# Class representing DepartmentActivityRecord
class DepartmentActivityRecord(models.Model):
    """
    Business-scoped per-department activity log.

    One row per activity entry. The `department` field discriminates which
    department's grid the row appears in. These records are aggregated later
    into daily reports.

    Persian field labels (UI):
    - تاریخ: date
    - موقعیت: location
    - شرح فعالیت: activity_description
    - پیمانگار: contractor
    - واحد: unit
    - توضیحات: description
    """

    business = models.ForeignKey(
        Business,
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Class representing Meta
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(
                fields=['business', 'department', 'date'],
                name='dar_biz_dept_date_idx',
            ),
            models.Index(
                fields=['business', 'department'],
                name='dar_biz_dept_idx',
            ),
        ]

    # Function to handle   str
    def __str__(self) -> str:
        return f'{self.business.slug}/{self.department}: {self.activity_description[:40]} ({self.date})'