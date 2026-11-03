"""Seed isolated test-env role accounts and reference project memberships (R.0.03).

Preserves ``seed_rbac_dev`` / ``projects.seeds`` behaviour: optionally reuses
``run_seed`` for Acme/BuildCo demo data, then provisions all 11 reference
accounts with ``DEFAULT_ROLE_PERMISSIONS``-aligned project roles on
``acme``, ``buildco``, and the Shiraz housing reference project.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

from business_meta.management.commands.seed_rbac_dev import GROUPS, run_seed
from master_data.models import (
    MemberStatus,
    Permission,
    ProjectMember,
    ProjectMemberRole,
    Role,
    RolePermission,
)
from permissions.constants import (
    DEFAULT_ROLE_DESCRIPTIONS,
    DEFAULT_ROLE_PERMISSIONS,
    PERMISSIONS,
)
from permissions.test_accounts import (
    DEV_PASSWORD,
    REFERENCE_PROJECT_CODES,
    SHIRAZ_PROJECT_NAME,
    TEST_ROLE_ACCOUNTS,
)
from projects.models import Project

User = get_user_model()


def ensure_system_roles() -> dict[str, Role]:
    """Ensure Permission rows and system Roles match DEFAULT_ROLE_PERMISSIONS."""
    for codename, label in PERMISSIONS.items():
        Permission.objects.get_or_create(codename=codename, defaults={'label': label})

    roles: dict[str, Role] = {}
    for role_name, codenames in DEFAULT_ROLE_PERMISSIONS.items():
        role, _ = Role.objects.get_or_create(
            role_name=role_name,
            defaults={'description': DEFAULT_ROLE_DESCRIPTIONS.get(role_name, '')},
        )
        existing = set(
            RolePermission.objects.filter(role=role).values_list('permission_codename', flat=True)
        )
        expected = set(codenames)
        if existing != expected:
            RolePermission.objects.filter(role=role).delete()
            RolePermission.objects.bulk_create(
                [RolePermission(role=role, permission_codename=c) for c in codenames]
            )
        roles[role_name] = role
    return roles


def ensure_reference_projects() -> dict[str, Project]:
    """Return acme/buildco/shiraz projects, creating a light Shiraz shell if needed."""
    projects: dict[str, Project] = {}
    for code in REFERENCE_PROJECT_CODES:
        if code == 'shiraz':
            project, _ = Project.objects.get_or_create(
                project_code=code,
                defaults={'project_name': SHIRAZ_PROJECT_NAME},
            )
            if project.project_name != SHIRAZ_PROJECT_NAME:
                project.project_name = SHIRAZ_PROJECT_NAME
                project.save(update_fields=['project_name'])
        else:
            project = Project.objects.filter(project_code=code).first()
            if project is None:
                names = {
                    'acme': 'Acme Construction',
                    'buildco': 'BuildCo',
                }
                project, _ = Project.objects.get_or_create(
                    project_code=code,
                    defaults={'project_name': names.get(code, code)},
                )
        projects[code] = project
    return projects


def upsert_test_user(account) -> User:
    user, _ = User.objects.get_or_create(
        mobile=account.mobile,
        defaults={
            'username': account.username,
            'full_name': account.full_name,
        },
    )
    user.username = account.username
    user.full_name = account.full_name
    user.set_password(DEV_PASSWORD)
    user.is_staff = account.is_staff
    user.is_superuser = account.is_superuser
    user.is_active = True
    user.save()

    if account.auth_group:
        group, _ = Group.objects.get_or_create(name=account.auth_group)
        user.groups.set([group])
    else:
        user.groups.clear()
    return user


def assign_project_role(
    *,
    user: User,
    project: Project,
    role: Role | None,
    replace_roles: bool = True,
) -> ProjectMember:
    """Attach user to project; optionally replace roles so test accounts are exact."""
    member, created = ProjectMember.objects.get_or_create(
        user=user,
        project=project,
        defaults={'status': MemberStatus.ACTIVE},
    )
    if not created and member.status != MemberStatus.ACTIVE:
        member.status = MemberStatus.ACTIVE
        member.save(update_fields=['status'])

    if role is None:
        return member

    if replace_roles:
        # Demo seed may have attached different roles to the shared admin/hr/worker
        # mobiles; reference accounts must match DEFAULT_ROLE_PERMISSIONS exactly.
        ProjectMemberRole.objects.filter(member=member).exclude(role=role).delete()
    ProjectMemberRole.objects.get_or_create(member=member, role=role)
    return member


@transaction.atomic
def run_seed_test_roles(*, with_demo: bool = True) -> dict:
    """Provision auth groups, system roles, reference projects, and 11 accounts."""
    for name in GROUPS:
        Group.objects.get_or_create(name=name)

    demo_stats = None
    if with_demo:
        demo_stats = run_seed()

    roles = ensure_system_roles()
    projects = ensure_reference_projects()

    seeded_users: list[dict] = []
    for account in TEST_ROLE_ACCOUNTS:
        user = upsert_test_user(account)
        project_role = roles.get(account.project_role) if account.project_role else None
        memberships = []
        for code, project in projects.items():
            member = assign_project_role(user=user, project=project, role=project_role)
            memberships.append(
                {
                    'project_code': code,
                    'member_id': str(member.id),
                    'role': account.project_role,
                }
            )
        seeded_users.append(
            {
                'key': account.key,
                'mobile': account.mobile,
                'project_role': account.project_role,
                'auth_group': account.auth_group,
                'memberships': memberships,
            }
        )

    return {
        'demo': demo_stats,
        'projects': list(projects.keys()),
        'users': seeded_users,
        'password': DEV_PASSWORD,
    }


class Command(BaseCommand):
    help = (
        'Seed 11 reference role accounts (password: devpass123) on acme, buildco, '
        'and shiraz. Optionally runs seed_rbac_dev first for demo project data.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-demo',
            action='store_true',
            help='Do not call seed_rbac_dev; only ensure projects/roles/accounts.',
        )

    def handle(self, *args, **options):
        result = run_seed_test_roles(with_demo=not options['skip_demo'])
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(result['users'])} role accounts on projects "
                f"{result['projects']}. Password: {result['password']}."
            )
        )
        for user in result['users']:
            self.stdout.write(
                f"  - {user['key']}: {user['mobile']} "
                f"(group={user['auth_group']}, role={user['project_role']})"
            )
