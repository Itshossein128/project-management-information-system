"""Development seed: auth groups, sample projects, positions, users, members."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

from master_data.models import MemberStatus, ProjectMember, ProjectPosition, WageType
from projects.models import Project
from projects.seeds import DEMO_PROJECT_SPECS, seed_full_project, seed_system_reference
from projects.services import attach_creator_as_member

User = get_user_model()

GROUPS = [
    'admin', 'hr', 'manager', 'visitor', 'business-setup', 'engineer', 'accountant',
]
DEV_PASSWORD = 'devpass123'


@transaction.atomic
def run_seed():
    for name in GROUPS:
        Group.objects.get_or_create(name=name)

    def upsert_user(mobile, username, full_name, group_name=None):
        user, _ = User.objects.get_or_create(
            mobile=mobile,
            defaults={'username': username, 'full_name': full_name},
        )
        user.set_password(DEV_PASSWORD)
        user.save()
        if group_name:
            user.groups.set([Group.objects.get(name=group_name)])
        else:
            user.groups.clear()
        return user

    u_admin = upsert_user('+10000000001', '10000000001', 'Admin User', 'admin')
    u_admin.is_staff = True
    u_admin.is_superuser = True
    u_admin.save(update_fields=['is_staff', 'is_superuser'])
    u_hr = upsert_user('+10000000002', '10000000002', 'HR User', 'hr')
    u_visitor = upsert_user('+10000000003', '10000000003', 'Visitor User', 'visitor')
    u_worker = upsert_user('+10000000004', '10000000004', 'Worker User', None)

    system_stats = seed_system_reference()

    project_users = {
        'acme': (u_admin, u_hr, u_worker),
        'buildco': (u_admin, u_hr, u_worker),
    }
    project_results = []

    for spec in DEMO_PROJECT_SPECS:
        project, _ = Project.objects.get_or_create(
            project_code=spec.project_code,
            defaults={'project_name': spec.project_name},
        )
        admin_user, hr_user, worker_user = project_users[spec.project_code]

        for slug, name, ordering in (
            ('electrician', 'Electrician', 0),
            ('worker', 'Worker', 1),
            ('supervisor', 'Supervisor', 2),
            ('plumber', 'Plumber', 3),
        ):
            ProjectPosition.objects.get_or_create(
                project=project,
                slug=slug,
                defaults={'position_name': name, 'ordering': ordering},
            )

        pos_e = ProjectPosition.objects.get(project=project, slug='electrician')
        pos_w = ProjectPosition.objects.get(project=project, slug='worker')
        pos_s = ProjectPosition.objects.get(project=project, slug='supervisor')

        if spec.project_code == 'acme':
            member_specs = (
                (worker_user, pos_e, Decimal('45.00'), WageType.HOURLY, MemberStatus.ACTIVE, ['drill']),
                (hr_user, pos_w, Decimal('30.00'), WageType.HOURLY, MemberStatus.ACTIVE, []),
            )
        else:
            member_specs = (
                (worker_user, pos_s, Decimal('5000.00'), WageType.MONTHLY, MemberStatus.SUSPENDED, []),
                (hr_user, pos_w, Decimal('35.00'), WageType.HOURLY, MemberStatus.ACTIVE, []),
            )

        members: list[ProjectMember] = []
        for user, position, wage, wage_type, status, tools in member_specs:
            member, _ = ProjectMember.objects.get_or_create(
                user=user,
                project=project,
                defaults={
                    'position': position,
                    'wage': wage,
                    'wage_type': wage_type,
                    'status': status,
                    'tools': tools,
                },
            )
            members.append(member)

        attach_creator_as_member(project=project, creator=admin_user)
        admin_member = ProjectMember.objects.get(project=project, user=admin_user)
        if admin_member not in members:
            members.insert(0, admin_member)

        project_results.append(
            seed_full_project(
                project=project,
                spec=spec,
                creator=admin_user,
                members=members,
            )
        )

    return system_stats, project_results


class Command(BaseCommand):
    help = 'Seed development RBAC and two full demo projects (Acme, BuildCo). Password: devpass123'

    def handle(self, *args, **options):
        system_stats, project_results = run_seed()
        self.stdout.write(
            self.style.SUCCESS(
                'Seeded groups, users, units, inflation indices, and full demo projects. '
                f'System: {system_stats}. Projects: {project_results}. '
                'Password: devpass123. Django admin: username 10000000001 (or +10000000001).'
            )
        )
