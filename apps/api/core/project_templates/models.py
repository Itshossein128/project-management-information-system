from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from common.models import TimeStampedModel, UUIDModel
from common.reporting_units import SpecialtyUnit


class ProjectType(models.TextChoices):
    RESIDENTIAL = 'residential', 'Residential'
    ROAD = 'road', 'Road'
    COMMERCIAL = 'commercial', 'Commercial'
    INDUSTRIAL = 'industrial', 'Industrial'
    EPC = 'epc', 'EPC'
    OTHER = 'other', 'Other'


class ProjectTemplate(UUIDModel, TimeStampedModel):
    template_name = models.CharField(max_length=120)
    description = models.TextField(blank=True, default='')
    project_type = models.CharField(max_length=30, choices=ProjectType.choices, default=ProjectType.OTHER)
    is_system = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_project_templates',
    )

    class Meta(UUIDModel.Meta):
        db_table = 'project_templates'
        ordering = ['template_name']

    def __str__(self):
        return self.template_name


class ProjectTemplateWBS(UUIDModel):
    template = models.ForeignKey(ProjectTemplate, on_delete=models.CASCADE, related_name='wbs_nodes')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
    )
    wbs_code = models.CharField(max_length=30)
    wbs_name = models.CharField(max_length=200)
    weight_physical = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    level = models.PositiveIntegerField()
    order = models.PositiveIntegerField(default=0)

    class Meta(UUIDModel.Meta):
        db_table = 'project_template_wbs'
        ordering = ['level', 'order', 'wbs_code']
        unique_together = [['template', 'wbs_code']]


class ProjectTemplateActivity(UUIDModel):
    template_wbs = models.ForeignKey(
        ProjectTemplateWBS,
        on_delete=models.CASCADE,
        related_name='activities',
    )
    activity_code = models.CharField(max_length=30)
    activity_name = models.CharField(max_length=200)
    unit = models.CharField(max_length=40, blank=True, default='')
    duration_days = models.PositiveIntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)

    class Meta(UUIDModel.Meta):
        db_table = 'project_template_activities'


class ProjectTemplateRole(UUIDModel):
    template = models.ForeignKey(ProjectTemplate, on_delete=models.CASCADE, related_name='template_roles')
    role = models.ForeignKey('master_data.Role', on_delete=models.CASCADE, related_name='template_assignments')

    class Meta(UUIDModel.Meta):
        db_table = 'project_template_roles'
        unique_together = [['template', 'role']]


class LaborTitleCategory(models.TextChoices):
    INDIRECT = 'indirect', 'Indirect'
    DIRECT = 'direct', 'Direct'


class ManHoursRuleCode(models.TextChoices):
    """Fixed, code-reviewed registry of man-hours rules (feature 033, data-model §1.2).

    Rule implementations live in ``field_reports.services.man_hours``; only codes
    listed here are selectable, never hard-coded project counts.
    """

    STANDARD_SHIFT_PLUS_OVERTIME = 'standard_shift_plus_overtime', 'Standard shift + overtime'


class LaborTitleCatalog(UUIDModel, TimeStampedModel):
    """Versioned draft labor-title catalog owned by a project template
    (feature 033, data-model §1.1). Editable only while the owning template is
    still a draft; ``activate`` snapshots titles immutably into the reporting
    configuration.
    """

    template = models.ForeignKey(
        ProjectTemplate, on_delete=models.CASCADE, related_name='labor_catalogs',
    )
    version_name = models.CharField(max_length=120)
    notes = models.TextField(blank=True, default='')

    class Meta(UUIDModel.Meta):
        db_table = 'labor_title_catalogs'
        ordering = ['template', 'version_name']

    def __str__(self):
        return f'{self.template_id}:{self.version_name}'


class LaborTitleCatalogTitle(UUIDModel):
    """One stable, language-independent title row inside a catalog version."""

    catalog = models.ForeignKey(
        LaborTitleCatalog, on_delete=models.CASCADE, related_name='titles',
    )
    title_code = models.CharField(max_length=60)
    title_label = models.CharField(max_length=120, blank=True, default='')
    title_label_fa = models.CharField(max_length=120, blank=True, default='')
    category = models.CharField(max_length=10, choices=LaborTitleCategory.choices)
    display_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    legacy_alias = models.CharField(max_length=120, blank=True, default='')
    project_specific = models.BooleanField(default=False)

    class Meta(UUIDModel.Meta):
        db_table = 'labor_title_catalog_titles'
        ordering = ['category', 'display_order', 'title_code']
        constraints = [
            models.UniqueConstraint(
                fields=['catalog', 'title_code'], name='unique_catalog_title_code',
            ),
            models.UniqueConstraint(
                fields=['catalog', 'category', 'display_order'],
                name='unique_catalog_category_display_order',
            ),
        ]


class ProjectTemplateRequiredUnit(UUIDModel):
    """Canonical reporting units declared by a reusable project template
    (feature 032, data-model §2). Editing this configuration never changes an
    already activated project configuration.
    """
    template = models.ForeignKey(ProjectTemplate, on_delete=models.CASCADE, related_name='required_units')
    unit = models.CharField(max_length=20, choices=SpecialtyUnit.choices)
    display_order = models.PositiveIntegerField(default=0)

    class Meta(UUIDModel.Meta):
        db_table = 'project_template_required_units'
        ordering = ['display_order', 'unit']
        constraints = [
            models.UniqueConstraint(fields=['template', 'unit'], name='unique_template_required_unit'),
        ]


class ProjectReportingConfiguration(UUIDModel, TimeStampedModel):
    """Immutable, effective-dated snapshot of a project's reporting template
    (feature 032, data-model §3). Rows and required-unit children are immutable
    after activation.
    """
    project = models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE, related_name='reporting_configurations',
    )
    source_template = models.ForeignKey(
        ProjectTemplate, on_delete=models.PROTECT, related_name='reporting_configurations',
    )
    effective_from = models.DateField()
    activated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
    )
    activated_at = models.DateTimeField(auto_now_add=True)
    supersedes = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='superseded_configurations',
    )
    source_template_name_snapshot = models.CharField(max_length=120, blank=True, default='')
    # Feature 033 (data-model §1.2): man-hours rule + shift parameter are part of
    # the immutable snapshot; the rule implementation itself is the fixed registry
    # in field_reports.services.man_hours.
    man_hours_rule_code = models.CharField(
        max_length=40,
        choices=ManHoursRuleCode.choices,
        default=ManHoursRuleCode.STANDARD_SHIFT_PLUS_OVERTIME,
    )
    standard_shift_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=8,
        validators=[MinValueValidator(1)],
    )

    class Meta(UUIDModel.Meta):
        db_table = 'project_reporting_configurations'
        ordering = ['-effective_from']
        constraints = [
            models.UniqueConstraint(fields=['project', 'effective_from'], name='unique_project_configuration_effective_from'),
        ]


class ProjectReportingConfigurationUnit(UUIDModel):
    """Snapshot of the required canonical units at activation time; immutable."""
    configuration = models.ForeignKey(
        ProjectReportingConfiguration, on_delete=models.CASCADE, related_name='required_units',
    )
    unit = models.CharField(max_length=20, choices=SpecialtyUnit.choices)
    display_order = models.PositiveIntegerField(default=0)

    class Meta(UUIDModel.Meta):
        db_table = 'project_reporting_configuration_units'
        ordering = ['display_order', 'unit']
        constraints = [
            models.UniqueConstraint(fields=['configuration', 'unit'], name='unique_configuration_required_unit'),
        ]


class ProjectReportingConfigurationLaborTitle(UUIDModel):
    """Immutable activation-time snapshot of one effective labor title
    (feature 033, data-model §1.1), mirroring the 032 required-unit pattern.
    """

    configuration = models.ForeignKey(
        ProjectReportingConfiguration, on_delete=models.CASCADE, related_name='labor_titles',
    )
    title_code = models.CharField(max_length=60)
    title_label = models.CharField(max_length=120, blank=True, default='')
    title_label_fa = models.CharField(max_length=120, blank=True, default='')
    category = models.CharField(max_length=10, choices=LaborTitleCategory.choices)
    display_order = models.PositiveIntegerField(default=0)
    legacy_alias = models.CharField(max_length=120, blank=True, default='')
    source_catalog_version = models.CharField(max_length=120, blank=True, default='')

    class Meta(UUIDModel.Meta):
        db_table = 'project_reporting_configuration_labor_titles'
        ordering = ['category', 'display_order', 'title_code']
        constraints = [
            models.UniqueConstraint(
                fields=['configuration', 'title_code'],
                name='unique_configuration_labor_title_code',
            ),
        ]


class ProjectReportingConfigurationStoppageReason(UUIDModel):
    """Immutable controlled stoppage-reason vocabulary at activation time
    (feature 033, data-model §1.2). Codes are stable and language-independent;
    labels are translatable.
    """

    configuration = models.ForeignKey(
        ProjectReportingConfiguration, on_delete=models.CASCADE, related_name='stoppage_reasons',
    )
    reason_code = models.CharField(max_length=60)
    reason_label = models.CharField(max_length=120, blank=True, default='')
    reason_label_fa = models.CharField(max_length=120, blank=True, default='')
    display_order = models.PositiveIntegerField(default=0)

    class Meta(UUIDModel.Meta):
        db_table = 'project_reporting_configuration_stoppage_reasons'
        ordering = ['display_order', 'reason_code']
        constraints = [
            models.UniqueConstraint(
                fields=['configuration', 'reason_code'],
                name='unique_configuration_stoppage_reason',
            ),
        ]
