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


def assign_roles_to_member(member: ProjectMember, role_ids: list) -> None:
    """Replace member roles only when every submitted id exists."""
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
    member.member_roles.all().delete()
    ProjectMemberRole.objects.bulk_create(
        [ProjectMemberRole(member=member, role=role) for role in unique_roles]
    )
