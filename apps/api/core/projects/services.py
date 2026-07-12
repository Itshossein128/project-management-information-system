"""Project creation and membership business rules."""
from django.contrib.auth import get_user_model
from django.db import transaction

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role
from projects.models import Project

User = get_user_model()


@transaction.atomic
def create_project_with_creator(*, creator: User, **project_fields) -> Project:
    project = Project.objects.create(**project_fields)

    member = ProjectMember.objects.create(
        project=project,
        user=creator,
        status=MemberStatus.ACTIVE,
    )

    pm_role = Role.objects.filter(role_name='project_manager').first()
    if pm_role:
        ProjectMemberRole.objects.create(member=member, role=pm_role)

    if project.project_manager_id is None:
        project.project_manager = creator
        project.save(update_fields=['project_manager'])

    return project


def assign_roles_to_member(member: ProjectMember, role_ids: list) -> None:
    roles = Role.objects.filter(id__in=role_ids)
    member.member_roles.all().delete()
    for role in roles:
        ProjectMemberRole.objects.create(member=member, role=role)
