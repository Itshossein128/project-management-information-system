"""Development seed: auth groups, sample projects, positions, users, members."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

from master_data.models import ProjectMember, ProjectPosition, MemberStatus, WageType
from projects.models import Project

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
    u_hr = upsert_user('+10000000002', '10000000002', 'HR User', 'hr')
    u_visitor = upsert_user('+10000000003', '10000000003', 'Visitor User', 'visitor')
    u_worker = upsert_user('+10000000004', '10000000004', 'Worker User', None)

    p1, _ = Project.objects.get_or_create(
        project_code='acme',
        defaults={'project_name': 'Acme Construction'},
    )
    p2, _ = Project.objects.get_or_create(
        project_code='buildco',
        defaults={'project_name': 'BuildCo'},
    )

    for project in (p1, p2):
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

    pos_e = ProjectPosition.objects.get(project=p1, slug='electrician')
    pos_w = ProjectPosition.objects.get(project=p1, slug='worker')
    pos_s = ProjectPosition.objects.get(project=p2, slug='supervisor')

    for user, project, position, wage, wage_type, status in (
        (u_worker, p1, pos_e, Decimal('45.00'), WageType.HOURLY, MemberStatus.ACTIVE),
        (u_hr, p1, pos_w, Decimal('30.00'), WageType.HOURLY, MemberStatus.ACTIVE),
        (u_worker, p2, pos_s, Decimal('5000.00'), WageType.MONTHLY, MemberStatus.SUSPENDED),
    ):
        ProjectMember.objects.get_or_create(
            user=user,
            project=project,
            defaults={
                'position': position,
                'wage': wage,
                'wage_type': wage_type,
                'status': status,
                'tools': ['drill'] if user == u_worker and project == p1 else [],
            },
        )


class Command(BaseCommand):
    help = 'Seed development RBAC and sample projects. Password: devpass123'

    def handle(self, *args, **options):
        run_seed()
        self.stdout.write(self.style.SUCCESS('Seeded groups, users, projects, members. Password: devpass123'))
