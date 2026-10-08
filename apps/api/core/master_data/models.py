from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from common.models import TimeStampedModel, UUIDModel

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


class OrgUnitStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'


class OrganizationUnit(UUIDModel, TimeStampedModel):
    """Organization Breakdown Structure (OBS) node — org-wide, no project_id."""

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=200)
    parent = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='children',
    )
    status = models.CharField(
        max_length=20,
        choices=OrgUnitStatus.choices,
        default=OrgUnitStatus.ACTIVE,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+',
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )

    class Meta:
        db_table = 'organization_units'
        ordering = ['code']

    def __str__(self):
        return f'{self.code} — {self.name}'


class ManagedContractType(UUIDModel, TimeStampedModel):
    """Manageable contract-type catalog (org-wide reference)."""

    code = models.CharField(max_length=40, unique=True)
    name_fa = models.CharField(max_length=120)
    name_en = models.CharField(max_length=120, blank=True, default='')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'managed_contract_types'
        ordering = ['code']

    def __str__(self):
        return self.code


class Permission(UUIDModel):
    codename = models.CharField(max_length=60, unique=True)
    label = models.CharField(max_length=120)

    class Meta:
        db_table = 'permissions'
        ordering = ['codename']

    def __str__(self):
        return self.codename


class Role(UUIDModel):
    role_name = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'roles'

    def __str__(self):
        return self.role_name


class RolePermission(UUIDModel):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission_codename = models.CharField(max_length=60)

    class Meta:
        db_table = 'role_permissions'
        unique_together = [['role', 'permission_codename']]

    def __str__(self):
        return f'{self.role.role_name} — {self.permission_codename}'


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
    INACTIVE = 'inactive', 'Inactive'
    INVITED = 'invited', 'Invited'
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
        null=True,
        blank=True,
    )
    invited_email = models.EmailField(max_length=254, blank=True, default='')
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
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'user'],
                condition=models.Q(user__isnull=False),
                name='unique_project_user_member',
            ),
        ]

    def __str__(self):
        return f'{self.user} @ {self.project}'

    def has_permission(self, codename: str) -> bool:
        from permissions.services import member_has_permission

        return member_has_permission(self, codename)


class ProjectMemberRole(UUIDModel):
    member = models.ForeignKey(ProjectMember, on_delete=models.CASCADE, related_name='member_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='member_assignments')

    class Meta:
        db_table = 'project_member_roles'
        unique_together = [['member', 'role']]

    def __str__(self):
        return f'{self.member_id} — {self.role.role_name}'


class ProjectMemberPermissionOverride(UUIDModel):
    member = models.ForeignKey(
        ProjectMember,
        on_delete=models.CASCADE,
        related_name='permission_overrides',
    )
    permission_codename = models.CharField(max_length=60)
    is_granted = models.BooleanField()

    class Meta:
        db_table = 'project_member_permission_overrides'
        unique_together = [['member', 'permission_codename']]

    def __str__(self):
        state = 'grant' if self.is_granted else 'deny'
        return f'{self.member_id} — {self.permission_codename} ({state})'
