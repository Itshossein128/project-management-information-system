"""
Meta models for multi-project dynamic schema.
TableDefinition, FieldDefinition, RelationDefinition, DynamicTableRow.
"""
import re

from django.db import models
from django.core.validators import RegexValidator

from common.models import TimeStampedModel
from projects.models import Project

SLUG_REGEX = re.compile(r'^[a-z][a-z0-9_]*$')

slug_validator = RegexValidator(
    regex=SLUG_REGEX,
    message='Slug must start with a letter, then only lowercase letters, numbers, and underscores.',
)


class TableDefinition(TimeStampedModel):
    """A logical table (collection) within a project."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tables')
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=100, validators=[slug_validator])
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['project', 'ordering', 'name']
        unique_together = [['project', 'slug']]

    def __str__(self):
        return f'{self.project.project_code}.{self.slug}'


class FieldType(models.TextChoices):
    STRING = 'string', 'String'
    NUMBER = 'number', 'Number'
    DATE = 'date', 'Date'
    BOOLEAN = 'boolean', 'Boolean'
    REFERENCE = 'reference', 'Reference (FK to another table)'


class FieldDefinition(TimeStampedModel):
    table = models.ForeignKey(TableDefinition, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=100, validators=[slug_validator])
    field_type = models.CharField(max_length=20, choices=FieldType.choices, default=FieldType.STRING)
    required = models.BooleanField(default=False)
    target_table = models.ForeignKey(
        TableDefinition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referencing_fields',
    )
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['table', 'ordering', 'name']
        unique_together = [['table', 'slug']]

    def __str__(self):
        return f'{self.table}.{self.slug}'


class RelationKind(models.TextChoices):
    ONE_TO_MANY = 'one_to_many', 'One to many'
    MANY_TO_ONE = 'many_to_one', 'Many to one'


class RelationDefinition(models.Model):
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


class DynamicTableRow(TimeStampedModel):
    table = models.ForeignKey(
        TableDefinition,
        on_delete=models.CASCADE,
        related_name='rows',
    )
    data = models.JSONField(default=dict)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['table']),
        ]

    def __str__(self):
        return f'{self.table}.row_{self.pk}'


# Backward-compatible aliases (deprecated)
Business = Project
