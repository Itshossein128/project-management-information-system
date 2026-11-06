"""Role management helpers for system vs custom project roles."""
from django.db import transaction
from django.db.models import Count, ProtectedError

from master_data.models import ProjectMember, ProjectMemberRole, Role, RoleAccessChange, RolePermission
from permissions.constants import ALL_PERMISSION_CODENAMES, DEFAULT_ROLE_PERMISSIONS

SYSTEM_ROLE_NAMES = frozenset(DEFAULT_ROLE_PERMISSIONS.keys())


def is_system_role(role: Role) -> bool:
    return role.project_id is None and role.role_name in SYSTEM_ROLE_NAMES


def validate_permission_codenames(codenames: list[str]) -> list[str]:
    invalid = set(codenames) - ALL_PERMISSION_CODENAMES
    if invalid:
        raise ValueError(f'Unknown permission codenames: {", ".join(sorted(invalid))}')
    return list(dict.fromkeys(codenames))


@transaction.atomic
def set_role_permissions(role: Role, codenames: list[str], actor=None) -> Role:
    validate_permission_codenames(codenames)
    from permissions.services import get_inherited_codenames

    previous_codes = sorted(
        RolePermission.objects.filter(role=role).values_list('permission_codename', flat=True)
    )
    member_ids = list(
        ProjectMemberRole.objects.filter(role=role).values_list('member_id', flat=True)
    )
    before = {
        member_id: sorted(get_inherited_codenames(ProjectMember.objects.get(pk=member_id)))
        for member_id in member_ids
    }
    RolePermission.objects.filter(role=role).delete()
    RolePermission.objects.bulk_create(
        [RolePermission(role=role, permission_codename=c) for c in codenames],
    )
    for member_id, previous in before.items():
        member = ProjectMember.objects.select_related('user', 'project').get(pk=member_id)
        current = sorted(get_inherited_codenames(member))
        if previous == current:
            continue
        record_access_change(
            actor=actor,
            project=member.project,
            subject_user=member.user,
            role=role,
            action='role_permissions_changed',
            before={'permissions': previous},
            after={'permissions': current},
        )
    if previous_codes != sorted(codenames):
        record_access_change(
            actor=actor,
            project=role.project,
            subject_user=None,
            role=role,
            action='role_permissions_changed',
            before={'permissions': previous_codes},
            after={'permissions': sorted(codenames)},
        )
    return role


class RoleInUse(Exception):
    def __init__(self, impact: dict):
        self.impact = impact
        super().__init__(impact)


def assignment_impact(role: Role, project_id=None) -> dict:
    queryset = ProjectMemberRole.objects.filter(role=role)
    if project_id is not None and role.project_id is not None:
        queryset = queryset.filter(member__project_id=project_id)
    grouped = (
        queryset.values('member__project_id')
        .annotate(assignment_count=Count('id'))
        .order_by('member__project_id')
    )
    projects = [
        {
            'project_id': str(row['member__project_id']),
            'assignment_count': row['assignment_count'],
        }
        for row in grouped
        if row['member__project_id'] is not None
    ]
    return {
        'assignment_count': sum(item['assignment_count'] for item in projects),
        'projects': projects,
    }


def delete_custom_role(role: Role, actor=None) -> None:
    with transaction.atomic():
        locked = Role.objects.select_for_update().get(pk=role.pk)
        if is_system_role(locked):
            raise PermissionError('system')
        impact = assignment_impact(locked)
        if impact['assignment_count']:
            raise RoleInUse(impact)
        record_access_change(
            actor=actor,
            project=locked.project,
            subject_user=None,
            role=locked,
            action='role_deleted',
            before={'role_name': locked.role_name, 'project_id': str(locked.project_id) if locked.project_id else None},
            after={},
        )
        try:
            locked.delete()
        except ProtectedError as exc:
            raise RoleInUse(assignment_impact(locked)) from exc


def record_access_change(*, actor, project, subject_user, role, action, before, after) -> None:
    """Persist a base access-history row.

    Break-glass final approve (A6-P4) uses ``action='sod_break_glass'`` with
    ``after`` containing at least ``reason``, ``exception``: true, and
    ``record_id``. Full history UI remains A6-P5.
    """
    RoleAccessChange.objects.create(
        actor=actor if getattr(actor, 'is_authenticated', False) else None,
        project=project,
        subject_user=subject_user,
        role_id=getattr(role, 'id', None),
        role_name=getattr(role, 'role_name', '') or '',
        action=action,
        before=before,
        after=after,
    )
