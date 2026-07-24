from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role
from projects.models import Project
from projects.services import attach_creator_as_member, create_project_with_creator

User = get_user_model()

E2E_PROJECT_CODE = 'E2E-ROLES'
E2E_ROLES = (
    'project_manager',
    'planning_engineer',
    'site_supervisor',
    'field_supervisor',
    'finance_manager',
    'procurement_officer',
    'document_controller',
    'viewer',
)


class Command(BaseCommand):
    help = 'Seeds E2E role users and a shared project for role-redirect tests.'

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(
            mobile='+10000000001',
            defaults={'username': 'admin', 'full_name': 'Admin'},
        )
        admin.set_password('devpass123')
        admin.save()

        project = Project.objects.filter(project_code=E2E_PROJECT_CODE).first()
        if project is None:
            project = create_project_with_creator(
                creator=admin,
                project_code=E2E_PROJECT_CODE,
                project_name='E2E Roles Test',
                employer='Test',
                start_date='2026-01-01',
            )
        else:
            attach_creator_as_member(project=project, creator=admin)

        for i, role_name in enumerate(E2E_ROLES, start=10):
            mobile = f'+100000000{i}'
            user, _ = User.objects.get_or_create(
                mobile=mobile,
                defaults={'username': f'user_{role_name}', 'full_name': f'User {role_name}'},
            )
            user.set_password('devpass123')
            user.save()

            role = Role.objects.get(role_name=role_name)
            member, _ = ProjectMember.objects.get_or_create(
                project=project,
                user=user,
                defaults={'status': MemberStatus.ACTIVE},
            )
            if member.status != MemberStatus.ACTIVE:
                member.status = MemberStatus.ACTIVE
                member.save(update_fields=['status'])
            ProjectMemberRole.objects.get_or_create(member=member, role=role)

        self.stdout.write(self.style.SUCCESS('Seeded E2E role users and project.'))
