from permissions.constants import ALL_PERMISSION_CODENAMES, PERMISSIONS

from master_data.models import ProjectMember, ProjectMemberPermissionOverride, RolePermission


def get_role_permission_codenames(member: ProjectMember) -> set[str]:
    codenames: set[str] = set()
    for member_role in member.member_roles.select_related('role').all():
        role_perms = RolePermission.objects.filter(role=member_role.role).values_list(
            'permission_codename', flat=True
        )
        codenames.update(role_perms)
    return codenames


def get_effective_permissions(member: ProjectMember) -> dict[str, bool | None]:
    """
    Return permission map: True/False for explicit override, or inherited bool from roles.
    Keys are all known permission codenames.
    """
    role_codenames = get_role_permission_codenames(member)
    overrides = {
        o.permission_codename: o.is_granted
        for o in member.permission_overrides.all()
    }

    result: dict[str, bool | None] = {}
    for codename in ALL_PERMISSION_CODENAMES:
        if codename in overrides:
            result[codename] = overrides[codename]
        else:
            result[codename] = codename in role_codenames
    return result


def member_has_permission(member: ProjectMember, codename: str) -> bool:
    if codename not in ALL_PERMISSION_CODENAMES:
        return False

    override = member.permission_overrides.filter(permission_codename=codename).first()
    if override is not None:
        return override.is_granted

    return codename in get_role_permission_codenames(member)


def set_permission_override(member: ProjectMember, codename: str, is_granted: bool | None) -> None:
    if codename not in ALL_PERMISSION_CODENAMES:
        raise ValueError(f'Unknown permission codename: {codename}')

    if is_granted is None:
        ProjectMemberPermissionOverride.objects.filter(
            member=member,
            permission_codename=codename,
        ).delete()
        return

    ProjectMemberPermissionOverride.objects.update_or_create(
        member=member,
        permission_codename=codename,
        defaults={'is_granted': is_granted},
    )


def permissions_summary(member: ProjectMember) -> list[dict]:
    effective = get_effective_permissions(member)
    return [
        {
            'codename': codename,
            'label': PERMISSIONS[codename],
            'granted': effective[codename],
        }
        for codename in sorted(ALL_PERMISSION_CODENAMES)
    ]
