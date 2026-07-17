"""Project creation and membership business rules."""
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
    return project


def assign_roles_to_member(member: ProjectMember, role_ids: list) -> None:
    roles = Role.objects.filter(id__in=role_ids)
    member.member_roles.all().delete()
    for role in roles:
        ProjectMemberRole.objects.create(member=member, role=role)
