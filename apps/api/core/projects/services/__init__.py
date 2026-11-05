"""Project creation and membership business rules."""
from uuid import UUID

from django.contrib.auth import get_user_model
from django.db import transaction

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role
from projects.models import Project

User = get_user_model()


def attach_creator_as_member(*, project: Project, creator: User) -> ProjectMember:
    """Make creator an active project_manager member (idempotent if already member)."""
    member, _created = ProjectMember.objects.get_or_create(
        project=project,
        user=creator,
        defaults={'status': MemberStatus.ACTIVE},
    )
    if member.status != MemberStatus.ACTIVE:
        member.status = MemberStatus.ACTIVE
        member.save(update_fields=['status'])

    pm_role = Role.objects.filter(role_name='project_manager').first()
    if pm_role and not member.member_roles.filter(role=pm_role).exists():
        ProjectMemberRole.objects.create(member=member, role=pm_role)

    if project.project_manager_id is None:
        project.project_manager = creator
        project.save(update_fields=['project_manager'])

    return member


@transaction.atomic
def create_project_with_creator(*, creator: User, **project_fields) -> Project:
    project = Project.objects.create(**project_fields)
    attach_creator_as_member(project=project, creator=creator)
    from procurement.services.workshop_block_service import ensure_workshop_block

    ensure_workshop_block(project, created_by=creator)
    return project


class PositionSelectionError(Exception):
    def __init__(self, position_ids: list):
        self.position_ids = list(position_ids)
        super().__init__(self.position_ids)


class RoleProjectMismatch(Exception):
    def __init__(self, role_ids: list):
        self.role_ids = list(role_ids)
        super().__init__(self.role_ids)


class UnknownRoles(Exception):
    """One or more submitted role ids are not assignable."""

    def __init__(self, missing_ids: list):
        self.missing_ids = list(missing_ids)
        super().__init__(self.missing_ids)


def missing_role_ids(role_ids) -> list:
    """Return submitted ids that do not refer to an existing role, in order."""
    if not role_ids:
        return []
    requested = []
    invalid = []
    for raw in role_ids:
        try:
            requested.append(raw if isinstance(raw, UUID) else UUID(str(raw)))
        except (TypeError, ValueError):
            invalid.append(raw)
    found = set(Role.objects.filter(id__in=requested).values_list('id', flat=True))
    missing = [item for item in requested if item not in found]
    return invalid + missing


def replace_member_positions(member: ProjectMember, position_ids: list, actor=None) -> None:
    """Select several job titles without changing access roles."""
    from master_data.models import ProjectPosition
    from permissions.role_services import record_access_change
    from permissions.services import get_inherited_codenames

    requested = list(dict.fromkeys(position_ids))
    positions = list(ProjectPosition.objects.filter(id__in=requested))
    found = {position.id for position in positions}
    if len(found) != len(requested):
        raise PositionSelectionError([item for item in requested if item not in found])
    rejected = [
        position.id
        for position in positions
        if (not position.is_active)
        or (position.project_id is not None and position.project_id != member.project_id)
    ]
    if rejected:
        raise PositionSelectionError(rejected)
    before_ids = sorted(str(position_id) for position_id in member.positions.values_list('id', flat=True))
    before_permissions = sorted(get_inherited_codenames(member))
    member.positions.set(positions)
    member.position = positions[0] if positions else None
    member.save(update_fields=['position'])
    member = ProjectMember.objects.get(pk=member.pk)
    after_ids = sorted(str(position.id) for position in positions)
    after_permissions = sorted(get_inherited_codenames(member))
    if before_ids != after_ids or before_permissions != after_permissions:
        record_access_change(
            actor=actor,
            project=member.project,
            subject_user=member.user,
            role=None,
            action='positions_replaced',
            before={'position_ids': before_ids, 'permissions': before_permissions},
            after={'position_ids': after_ids, 'permissions': after_permissions},
        )


def assign_roles_to_member(member: ProjectMember, role_ids: list, actor=None) -> None:
    """Replace member roles only when every submitted id exists and belongs here."""
    from permissions.role_services import record_access_change
    from permissions.services import get_inherited_codenames

    missing = missing_role_ids(role_ids)
    if missing:
        raise UnknownRoles(missing)
    roles = list(Role.objects.filter(id__in=role_ids))
    seen = set()
    unique_roles = []
    for role in roles:
        if role.id in seen:
            continue
        seen.add(role.id)
        unique_roles.append(role)
    mismatched = [
        role.id for role in unique_roles
        if role.project_id is not None and role.project_id != member.project_id
    ]
    if mismatched:
        raise RoleProjectMismatch(mismatched)
    before_roles = sorted(str(role_id) for role_id in member.member_roles.values_list('role_id', flat=True))
    before_permissions = sorted(get_inherited_codenames(member))
    member.member_roles.all().delete()
    ProjectMemberRole.objects.bulk_create(
        [ProjectMemberRole(member=member, role=role) for role in unique_roles]
    )
    member = ProjectMember.objects.get(pk=member.pk)
    after_roles = sorted(str(role.id) for role in unique_roles)
    after_permissions = sorted(get_inherited_codenames(member))
    if before_roles != after_roles or before_permissions != after_permissions:
        record_access_change(
            actor=actor,
            project=member.project,
            subject_user=member.user,
            role=unique_roles[0] if len(unique_roles) == 1 else None,
            action='roles_replaced',
            before={'role_ids': before_roles, 'permissions': before_permissions},
            after={'role_ids': after_roles, 'permissions': after_permissions},
        )
