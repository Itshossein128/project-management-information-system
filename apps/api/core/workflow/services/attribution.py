"""Capture project position evidence at the time of a workflow action."""
from master_data.models import MemberStatus, ProjectMember


def actor_position_at_action(project_id, actor):
    if actor is None:
        return None
    member = ProjectMember.objects.filter(
        project_id=project_id, user_id=actor.pk, status=MemberStatus.ACTIVE,
    ).select_related('position').first()
    if member is None:
        return None
    position = member.position
    if position is not None and position.is_active and position.project_id in (None, project_id):
        return position.position_name
    positions = list(member.positions.filter(is_active=True, project_id=project_id).values_list('position_name', flat=True)[:2])
    return positions[0] if len(positions) == 1 else None
