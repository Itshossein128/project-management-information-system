"""
Meta models for multi-business dynamic schema.
Business, TableDefinition, FieldDefinition, RelationDefinition, DynamicTableRow.
BusinessJobPosition: per-business job titles; UserBusinessAssignment: user–business link with work details.
"""
import re
from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator

# Allowlist for slugs and programmatic names: lowercase, start with letter, then alphanumeric/underscore
SLUG_REGEX = re.compile(r'^[a-z][a-z0-9_]*$')

slug_validator = RegexValidator(
    regex=SLUG_REGEX,
    message='Slug must start with a letter, then only lowercase letters, numbers, and underscores.',
)


class Business(models.Model):
    """A tenant (e.g. warehouse or inventory system)."""
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=100, unique=True, validators=[slug_validator])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Businesses'
        ordering = ['name']

    def __str__(self):
        return self.name


class BusinessJobPosition(models.Model):
    """
    A job title within a specific business (e.g. electrician, worker).
    Not to be confused with Django auth Groups (system roles).
    """
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='job_positions',
    )
    slug = models.CharField(
        max_length=64,
        validators=[slug_validator],
        help_text='Stable identifier per business: lowercase, starts with a letter, then letters/digits/underscores.',
    )
    label = models.CharField(max_length=255)
    ordering = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['business', 'ordering', 'slug']
        constraints = [
            models.UniqueConstraint(
                fields=['business', 'slug'],
                name='uniq_business_job_position_slug',
            ),
        ]
        verbose_name = 'business job position'
        verbose_name_plural = 'business job positions'

    def __str__(self) -> str:
        return f'{self.business.name}: {self.label}'


class WageType(models.TextChoices):
    HOURLY = 'hourly', 'Hourly'
    DAILY = 'daily', 'Daily'
    MONTHLY = 'monthly', 'Monthly'


class AssignmentStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    SUSPENDED = 'suspended', 'Suspended'
    ARCHIVED = 'archived', 'Archived'


class UserBusinessAssignment(models.Model):
    """
    Links a user to a business with a job position and work details.
    At most one row per (user, business).
    """
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='user_assignments',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='business_assignments',
    )
    job_position = models.ForeignKey(
        BusinessJobPosition,
        on_delete=models.PROTECT,
        related_name='assignments',
    )
    wage = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    wage_type = models.CharField(
        max_length=20,
        choices=WageType.choices,
        default=WageType.HOURLY,
    )
    weekly_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tools = models.JSONField(default=list, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=AssignmentStatus.choices,
        default=AssignmentStatus.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'user business assignment'
        verbose_name_plural = 'user business assignments'
        ordering = ['business', 'user__phone_number']
        constraints = [
            models.UniqueConstraint(
                fields=['business', 'user'],
                name='uniq_user_business_assignment',
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'business'], name='uba_user_business_idx'),
        ]

    def __str__(self):
        return f'{self.user} @ {self.business} ({self.job_position.slug})'


class TableDefinition(models.Model):
    """A logical table (collection) within a business."""
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='tables')
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=100, validators=[slug_validator])
    ordering = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['business', 'ordering', 'name']
        unique_together = [['business', 'slug']]

    def __str__(self):
        return f'{self.business.slug}.{self.slug}'


class FieldType(models.TextChoices):
    STRING = 'string', 'String'
    NUMBER = 'number', 'Number'
    DATE = 'date', 'Date'
    BOOLEAN = 'boolean', 'Boolean'
    REFERENCE = 'reference', 'Reference (FK to another table)'


class FieldDefinition(models.Model):
    """A field (column) of a table."""
    table = models.ForeignKey(TableDefinition, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=100, validators=[slug_validator])
    field_type = models.CharField(max_length=20, choices=FieldType.choices, default=FieldType.STRING)
    required = models.BooleanField(default=False)
    # For REFERENCE: target table (optional, set when field_type is reference)
    target_table = models.ForeignKey(
        TableDefinition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referencing_fields',
    )
    ordering = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['table', 'ordering', 'name']
        unique_together = [['table', 'slug']]

    def __str__(self):
        return f'{self.table}.{self.slug}'


class RelationKind(models.TextChoices):
    ONE_TO_MANY = 'one_to_many', 'One to many'
    MANY_TO_ONE = 'many_to_one', 'Many to one'


class RelationDefinition(models.Model):
    """Relation between two tables (from_field -> to_table/to_field)."""
    from_table = models.ForeignKey(
        TableDefinition,
        on_delete=models.CASCADE,
        related_name='outgoing_relations',
    )
    to_table = models.ForeignKey(
        TableDefinition,
        on_delete=models.CASCADE,
        related_name='incoming_relations',
    )
    from_field = models.ForeignKey(
        FieldDefinition,
        on_delete=models.CASCADE,
        related_name='relation_as_from',
    )
    to_field = models.ForeignKey(
        FieldDefinition,
        on_delete=models.CASCADE,
        related_name='relation_as_to',
        null=True,
        blank=True,
    )
    kind = models.CharField(max_length=20, choices=RelationKind.choices, default=RelationKind.ONE_TO_MANY)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['from_table', 'to_table']

    def __str__(self):
        return f'{self.from_table}.{self.from_field} -> {self.to_table}'


class DynamicTableRow(models.Model):
    """A single row of data for a dynamic table. Payload stored in JSONField."""
    table = models.ForeignKey(
        TableDefinition,
        on_delete=models.CASCADE,
        related_name='rows',
    )
    data = models.JSONField(default=dict)  # field slug -> value (validated by table schema)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['table']),
        ]

    def __str__(self):
        return f'{self.table}.row_{self.pk}'
