from django.conf import settings
from django.db import models

from common.models import UUIDModel


class ProjectType(models.TextChoices):
    RESIDENTIAL = 'residential', 'Residential'
    ROAD = 'road', 'Road'
    COMMERCIAL = 'commercial', 'Commercial'
    INDUSTRIAL = 'industrial', 'Industrial'
    EPC = 'epc', 'EPC'
    OTHER = 'other', 'Other'


class ProjectTemplate(UUIDModel):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
