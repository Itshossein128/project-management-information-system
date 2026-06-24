from django.core.management.base import BaseCommand
from business_meta.services import create_business_from_template, get_available_templates


class Command(BaseCommand):
    help = 'Create a business with tables and fields from a template (e.g. warehouse).'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Business display name')
        parser.add_argument('slug', type=str, help='Unique slug (lowercase, letters, numbers, underscores)')
        parser.add_argument(
            '--template',
            type=str,
            default='warehouse',
            choices=[t['id'] for t in get_available_templates()],
            help='Template identifier',
        )

    def handle(self, *args, **options):
        name = options['name']
        slug = options['slug']
        template_id = options['template']
        try:
            business = create_business_from_template(name=name, slug=slug, template_id=template_id)
            self.stdout.write(self.style.SUCCESS(f'Created business "{business.name}" (slug={business.slug}) with template "{template_id}".'))
        except ValueError as e:
            self.stderr.write(self.style.ERROR(str(e)))
            raise SystemExit(1)
