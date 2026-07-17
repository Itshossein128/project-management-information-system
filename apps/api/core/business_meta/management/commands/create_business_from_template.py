from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from business_meta.services import create_business_from_template, get_available_templates

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a project with tables and fields from a template (e.g. warehouse).'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Project display name')
        parser.add_argument('slug', type=str, help='Unique project_code')
        parser.add_argument(
            '--template',
            type=str,
            default='warehouse',
            choices=[t['id'] for t in get_available_templates()],
            help='Template identifier',
        )
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='Username of the user who will own the project as project_manager',
        )

    def handle(self, *args, **options):
        name = options['name']
        slug = options['slug']
        template_id = options['template']
        try:
            creator = User.objects.get(username=options['username'])
        except User.DoesNotExist as exc:
            raise CommandError(f'User "{options["username"]}" not found.') from exc
        try:
            project = create_business_from_template(
                name=name,
                project_code=slug,
                template_id=template_id,
                creator=creator,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created project "{project.project_name}" '
                    f'(code={project.project_code}) with template "{template_id}".'
                )
            )
        except ValueError as e:
            self.stderr.write(self.style.ERROR(str(e)))
            raise SystemExit(1)
