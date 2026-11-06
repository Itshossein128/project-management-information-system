from permissions.constants import ALL_PERMISSION_CODENAMES, PERMISSIONS

from master_data.models import MemberStatus, ProjectMember, ProjectMemberPermissionOverride, RolePermission


def get_role_permission_codenames(member: ProjectMember) -> set[str]:
    codenames: set[str] = set()
    # ⚡ Bolt: Removed .select_related() and used .all() to utilize prefetch cache
    for member_role in member.member_roles.all():
        # ⚡ Bolt: Iterate over .all() to utilize prefetch cache instead of querying DB
        role_perms = [rp.permission_codename for rp in member_role.role.role_permissions.all()]
        codenames.update(role_perms)
    return codenames


def get_position_permission_codenames(member: ProjectMember) -> set[str]:
    """Default permissions from every selected job title, including the legacy single title."""
    positions = list(member.positions.all())
    if member.position_id and all(position.id != member.position_id for position in positions):
        if member.position is not None:
            positions.append(member.position)
    codenames: set[str] = set()
    for position in positions:
        codenames.update(
            item.permission_codename for item in position.default_permissions.all()
        )
    return codenames


def get_inherited_codenames(member: ProjectMember) -> set[str]:
    return get_role_permission_codenames(member) | get_position_permission_codenames(member)


def get_effective_permissions(member: ProjectMember) -> dict[str, bool | None]:
    """
    Return permission map: True/False for explicit override, or inherited bool from roles.
    Keys are all known permission codenames.
    """
    if member.status != MemberStatus.ACTIVE:
        return {codename: False for codename in ALL_PERMISSION_CODENAMES}

    inherited = get_inherited_codenames(member)
    overrides = {
        o.permission_codename: o.is_granted
        for o in member.permission_overrides.all()
    }

    result: dict[str, bool | None] = {}
    for codename in ALL_PERMISSION_CODENAMES:
        if codename in overrides:
            result[codename] = overrides[codename]
        else:
            result[codename] = codename in inherited
    return result


def permission_origin(member: ProjectMember, codename: str) -> str:
    override = next(
        (item for item in member.permission_overrides.all() if item.permission_codename == codename),
        None,
    )
    if override is None:
        return 'inherit'
    return 'grant' if override.is_granted else 'deny'


def member_has_permission(member: ProjectMember, codename: str) -> bool:
    if codename not in ALL_PERMISSION_CODENAMES:
        return False
    if member.status != MemberStatus.ACTIVE:
        return False

    # ⚡ Bolt: Iterate over prefetched .all() to avoid hitting the DB with .filter()
    override = next((o for o in member.permission_overrides.all() if o.permission_codename == codename), None)
    if override is not None:
        return override.is_granted

    return codename in get_inherited_codenames(member)


def set_permission_override(
    member: ProjectMember,
    codename: str,
    is_granted: bool | None,
    actor=None,
) -> None:
    if codename not in ALL_PERMISSION_CODENAMES:
        raise ValueError(f'Unknown permission codename: {codename}')

    from permissions.role_services import record_access_change

    before_origin = permission_origin(member, codename)
    before_granted = member_has_permission(member, codename)
    if is_granted is None:
        ProjectMemberPermissionOverride.objects.filter(
            member=member,
            permission_codename=codename,
        ).delete()
    else:
        ProjectMemberPermissionOverride.objects.update_or_create(
            member=member,
            permission_codename=codename,
            defaults={'is_granted': is_granted},
        )
    member = ProjectMember.objects.get(pk=member.pk)
    record_access_change(
        actor=actor,
        project=member.project,
        subject_user=member.user,
        role=None,
        action='override_cleared' if is_granted is None else 'override_set',
        before={'codename': codename, 'origin': before_origin, 'granted': before_granted},
        after={
            'codename': codename,
            'origin': permission_origin(member, codename),
            'granted': member_has_permission(member, codename),
        },
    )


def permissions_summary(member: ProjectMember) -> list[dict]:
    effective = get_effective_permissions(member)
    return [
        {
            'codename': codename,
            'label': PERMISSIONS[codename],
            'granted': effective[codename],
            'origin': permission_origin(member, codename),
        }
        for codename in sorted(ALL_PERMISSION_CODENAMES)
    ]
