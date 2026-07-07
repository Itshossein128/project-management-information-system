"""Role management helpers for system vs custom project roles."""
from django.db import transaction

from master_data.models import Role, RolePermission
from permissions.constants import ALL_PERMISSION_CODENAMES, DEFAULT_ROLE_PERMISSIONS

SYSTEM_ROLE_NAMES = frozenset(DEFAULT_ROLE_PERMISSIONS.keys())


def is_system_role(role: Role) -> bool:
    return role.role_name in SYSTEM_ROLE_NAMES


def validate_permission_codenames(codenames: list[str]) -> list[str]:
    invalid = set(codenames) - ALL_PERMISSION_CODENAMES
    if invalid:
        raise ValueError(f'Unknown permission codenames: {", ".join(sorted(invalid))}')
    return list(dict.fromkeys(codenames))


@transaction.atomic
def set_role_permissions(role: Role, codenames: list[str]) -> Role:
    validate_permission_codenames(codenames)
    RolePermission.objects.filter(role=role).delete()
    RolePermission.objects.bulk_create(
        [RolePermission(role=role, permission_codename=c) for c in codenames],
    )
    return role
