from django.conf import settings
from django.db import models
from treebeard.mp_tree import MP_Node

import uuid

from common.models import UUIDModel


class ProjectStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    SUSPENDED = 'suspended', 'Suspended'
    COMPLETED = 'completed', 'Completed'
    HANDED_OVER = 'handed_over', 'Handed over'


class Project(UUIDModel):
    project_code = models.CharField(max_length=30, unique=True)
    project_name = models.CharField(max_length=200)
    employer = models.CharField(max_length=120, blank=True, default='')
    contractor = models.CharField(max_length=120, blank=True, default='')
    consultant = models.CharField(max_length=120, blank=True, default='')
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_projects',
    )
    location = models.TextField(blank=True, default='')
    start_date = models.DateField(null=True, blank=True)
    planned_finish_date = models.DateField(null=True, blank=True)
    contract_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    contract_type = models.CharField(max_length=60, blank=True, default='')
    status = models.CharField(
        max_length=30,
        choices=ProjectStatus.choices,
        default=ProjectStatus.ACTIVE,
    )
    cut_off_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        ordering = ['project_name']

    def __str__(self):
        return self.project_name

    @property
    def name(self):
        return self.project_name

    @property
    def slug(self):
        return self.project_code


class WBS(MP_Node):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='wbs_nodes')
    wbs_code = models.CharField(max_length=30)
    wbs_name = models.CharField(max_length=200)
    weight_physical = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    weight_financial = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    description = models.TextField(blank=True, default='')

    node_order_by = ['wbs_code']

    class Meta:
        db_table = 'wbs'
        unique_together = [['project', 'wbs_code']]
        verbose_name = 'WBS'
        verbose_name_plural = 'WBS'

    def __str__(self):
        return f'{self.wbs_code} — {self.wbs_name}'


class ActivityStatus(models.TextChoices):
    NOT_STARTED = 'not_started', 'Not started'
    IN_PROGRESS = 'in_progress', 'In progress'
    SUSPENDED = 'suspended', 'Suspended'
    COMPLETED = 'completed', 'Completed'


class Activity(UUIDModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='activities')
    wbs = models.ForeignKey(WBS, on_delete=models.CASCADE, related_name='activities')
    activity_code = models.CharField(max_length=30)
    activity_name = models.CharField(max_length=200)
    unit = models.ForeignKey(
        'master_data.Unit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities',
    )
    total_quantity = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    planned_start = models.DateField(null=True, blank=True)
    planned_finish = models.DateField(null=True, blank=True)
    actual_start = models.DateField(null=True, blank=True)
    actual_finish = models.DateField(null=True, blank=True)
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='responsible_activities',
    )
    status = models.CharField(
        max_length=20,
        choices=ActivityStatus.choices,
        default=ActivityStatus.NOT_STARTED,
    )

    class Meta:
        db_table = 'activities'
        unique_together = [['project', 'activity_code']]

    def __str__(self):
        return f'{self.activity_code} — {self.activity_name}'


class RelationType(models.TextChoices):
    FS = 'FS', 'Finish-to-Start'
    SS = 'SS', 'Start-to-Start'
    FF = 'FF', 'Finish-to-Finish'
    SF = 'SF', 'Start-to-Finish'


class ActivityRelation(UUIDModel):
    predecessor = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='successor_relations',
    )
    successor = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='predecessor_relations',
    )
    relation_type = models.CharField(max_length=4, choices=RelationType.choices, default=RelationType.FS)
    lag_days = models.IntegerField(default=0)

    class Meta:
        db_table = 'activity_relations'

    def __str__(self):
        return f'{self.predecessor_id} -> {self.successor_id} ({self.relation_type})'
