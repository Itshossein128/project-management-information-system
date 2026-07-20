from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projects.services import create_project_with_creator
from master_data.models import ProjectMember, ProjectMemberRole, Role, MemberStatus

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds E2E roles and users for testing role redirects.'

    def handle(self, *args, **options):
        # Create a single project
        u_admin, _ = User.objects.get_or_create(mobile='+10000000001', defaults={'username': 'admin', 'full_name': 'Admin'})
        u_admin.set_password('devpass123')
        u_admin.save()

        project = create_project_with_creator(
            creator=u_admin,
            project_code='E2E-ROLES',
            project_name='E2E Roles Test',
            employer='Test',
            start_date='2026-01-01'
        )

        roles = [
            'project_manager',
            'planning_engineer',
            'site_supervisor',
            'field_supervisor',
            'finance_manager',
            'procurement_officer',
            'document_controller',
            'viewer'
        ]

        for i, role_name in enumerate(roles, start=10):
            mobile = f'+100000000{i}'
            u, _ = User.objects.get_or_create(mobile=mobile, defaults={'username': f'user_{role_name}', 'full_name': f'User {role_name}'})
            u.set_password('devpass123')
            u.save()

            role = Role.objects.get(role_name=role_name)
            member, _ = ProjectMember.objects.get_or_create(
                project=project,
                user=u,
                defaults={'status': MemberStatus.ACTIVE}
            )
            ProjectMemberRole.objects.get_or_create(member=member, role=role)

        self.stdout.write(self.style.SUCCESS('Seeded E2E specific users and roles.'))
