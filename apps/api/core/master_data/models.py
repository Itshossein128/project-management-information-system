from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from common.models import UUIDModel

slug_validator = RegexValidator(
    regex=r'^[a-z][a-z0-9_]*$',
    message='Slug must start with a letter, then only lowercase letters, numbers, and underscores.',
)


class Unit(UUIDModel):
    unit_name = models.CharField(max_length=40)
    unit_symbol = models.CharField(max_length=10, blank=True, default='')

    class Meta:
        db_table = 'units'

    def __str__(self):
        return self.unit_name


class Role(UUIDModel):
    role_name = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'roles'

    def __str__(self):
        return self.role_name


class ProjectPosition(UUIDModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='positions',
    )
    position_name = models.CharField(max_length=120)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    slug = models.CharField(max_length=64, validators=[slug_validator], blank=True, default='')
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'project_positions'
        ordering = ['ordering', 'position_name']

    def __str__(self):
        return self.position_name

    @property
    def label(self):
        return self.position_name


class MemberStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    SUSPENDED = 'suspended', 'Suspended'
    ARCHIVED = 'archived', 'Archived'


class WageType(models.TextChoices):
    HOURLY = 'hourly', 'Hourly'
    DAILY = 'daily', 'Daily'
    MONTHLY = 'monthly', 'Monthly'


class ProjectMember(UUIDModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='members',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_memberships',
    )
    status = models.CharField(max_length=20, choices=MemberStatus.choices, default=MemberStatus.ACTIVE)
    joined_at = models.DateTimeField(auto_now_add=True)
    position = models.ForeignKey(
        ProjectPosition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
    )
    wage = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    wage_type = models.CharField(max_length=20, choices=WageType.choices, default=WageType.HOURLY)
    weekly_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tools = models.JSONField(default=list, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'project_members'
        unique_together = [['project', 'user']]

    def __str__(self):
        return f'{self.user} @ {self.project}'


class ProjectMemberRole(UUIDModel):
    member = models.ForeignKey(ProjectMember, on_delete=models.CASCADE, related_name='member_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='member_assignments')

    class Meta:
        db_table = 'project_member_roles'
        unique_together = [['member', 'role']]

    def __str__(self):
        return f'{self.member_id} — {self.role.role_name}'
