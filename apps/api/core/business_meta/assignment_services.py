"""Business rules for project member assignments."""
from django.contrib.auth import get_user_model

from master_data.models import ProjectMember, ProjectPosition, MemberStatus
from projects.models import Project

User = get_user_model()


def create_assignment_for_user(
    *,
    project_id,
    user,
    position: ProjectPosition,
    **extra,
) -> ProjectMember:
    if position.project_id and str(position.project_id) != str(project_id):
        raise ValueError('Position must belong to this project.')
    if ProjectMember.objects.filter(project_id=project_id, user=user).exists():
        raise ValueError('User is already a member of this project.')
    Project.objects.get(pk=project_id)
    return ProjectMember.objects.create(
        project_id=project_id,
        user=user,
        position=position,
        status=extra.get('status', MemberStatus.ACTIVE),
        wage=extra.get('wage', 0),
        wage_type=extra.get('wage_type', 'hourly'),
        weekly_total=extra.get('weekly_total', 0),
        monthly_total=extra.get('monthly_total', 0),
        tools=extra.get('tools') or [],
        start_date=extra.get('start_date'),
        end_date=extra.get('end_date'),
    )
