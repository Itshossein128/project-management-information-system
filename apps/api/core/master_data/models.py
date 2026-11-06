from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.functions import Lower

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
    role_name = models.CharField(max_length=60)
    description = models.TextField(blank=True, default='')
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='local_roles',
    )

    class Meta:
        db_table = 'roles'
        constraints = [
            models.UniqueConstraint(
                fields=['role_name'],
                condition=models.Q(project__isnull=True),
                name='unique_global_role_name',
            ),
            models.UniqueConstraint(
                fields=['project', 'role_name'],
                condition=models.Q(project__isnull=False),
                name='unique_local_role_name',
            ),
        ]

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
        on_delete=models.PROTECT,
        related_name='project_memberships',
        null=True,
        blank=True,
    )
    invited_email = models.EmailField(max_length=254, blank=True, default='')
    invited_mobile = models.CharField(max_length=20, blank=True, default='')
    invite_expires_at = models.DateTimeField(null=True, blank=True)
    invite_token_hash = models.CharField(max_length=64, blank=True, default='')
    invite_cancelled_at = models.DateTimeField(null=True, blank=True)
    invite_accepted_at = models.DateTimeField(null=True, blank=True)
    delivery_status = models.CharField(
        max_length=20,
        blank=True,
        default='not_configured',
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
    positions = models.ManyToManyField(
        ProjectPosition,
        blank=True,
        related_name='assigned_members',
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
            models.UniqueConstraint(
                Lower('invited_email'),
                'project',
                condition=(
                    models.Q(user__isnull=True, status=MemberStatus.INVITED, invite_cancelled_at__isnull=True)
                    & ~models.Q(invited_email='')
                ),
                name='unique_pending_project_invite_email',
            ),
            models.UniqueConstraint(
                fields=['project', 'invited_mobile'],
                condition=(
                    models.Q(user__isnull=True, status=MemberStatus.INVITED, invite_cancelled_at__isnull=True)
                    & ~models.Q(invited_mobile='')
                ),
                name='unique_pending_project_invite_mobile',
            ),
        ]

    def __str__(self):
        return f'{self.user} @ {self.project}'

    def has_permission(self, codename: str) -> bool:
        from permissions.services import member_has_permission

        return member_has_permission(self, codename)


class ProjectMemberRole(UUIDModel):
    member = models.ForeignKey(ProjectMember, on_delete=models.CASCADE, related_name='member_roles')
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='member_assignments')

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


class PositionPermission(UUIDModel):
    position = models.ForeignKey(
        ProjectPosition,
        on_delete=models.CASCADE,
        related_name='default_permissions',
    )
    permission_codename = models.CharField(max_length=60)

    class Meta:
        db_table = 'position_permissions'
        unique_together = [['position', 'permission_codename']]


class RoleAccessChange(UUIDModel):
    """Base record for role and permission changes. Not the finished history screen."""

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='role_access_changes',
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='role_access_changes',
    )
    subject_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subject_role_access_changes',
    )
    role_id = models.UUIDField(null=True, blank=True)
    role_name = models.CharField(max_length=60, blank=True, default='')
    action = models.CharField(max_length=40)
    before = models.JSONField(default=dict, blank=True)
    after = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'role_access_changes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'created_at'], name='rac_project_created_idx'),
            models.Index(fields=['subject_user', 'created_at'], name='rac_subject_created_idx'),
            models.Index(fields=['actor', 'created_at'], name='rac_actor_created_idx'),
        ]
