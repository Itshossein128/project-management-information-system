"""
Business logic for project meta. Template application and validation.
"""
from django.contrib.auth import get_user_model
from django.db import transaction

from projects.models import Project
from projects.services import attach_creator_as_member
from .models import TableDefinition, FieldDefinition, FieldType

User = get_user_model()


TEMPLATES = {
    'warehouse': {
        'name': 'Warehouse',
        'tables': [
            {
                'name': 'Locations',
                'slug': 'locations',
                'ordering': 0,
                'fields': [
                    {'name': 'Name', 'slug': 'name', 'field_type': FieldType.STRING, 'required': True},
                    {'name': 'Code', 'slug': 'code', 'field_type': FieldType.STRING, 'required': False},
                ],
            },
            {
                'name': 'Inventory',
                'slug': 'inventory',
                'ordering': 1,
                'fields': [
                    {'name': 'Name', 'slug': 'name', 'field_type': FieldType.STRING, 'required': True},
                    {'name': 'Quantity', 'slug': 'quantity', 'field_type': FieldType.NUMBER, 'required': True},
                    {'name': 'Location', 'slug': 'location', 'field_type': FieldType.REFERENCE, 'required': False, 'target_table_slug': 'locations'},
                ],
            },
        ],
    },
}


def get_available_templates():
    return [{'id': k, 'name': v['name']} for k, v in TEMPLATES.items()]


@transaction.atomic
def create_project_from_template(
    *,
    name: str,
    project_code: str,
    template_id: str,
    creator: User,
) -> Project:
    if template_id not in TEMPLATES:
        raise ValueError(f'Unknown template: {template_id}. Available: {list(TEMPLATES.keys())}')
    if Project.objects.filter(project_code=project_code).exists():
        raise ValueError(f'Project with code "{project_code}" already exists.')

    template = TEMPLATES[template_id]
    project = Project.objects.create(project_name=name, project_code=project_code)

    tables_by_slug = {}
    for tdef in template['tables']:
        table = TableDefinition.objects.create(
            project=project,
            name=tdef['name'],
            slug=tdef['slug'],
            ordering=tdef['ordering'],
        )
        tables_by_slug[table.slug] = table
        for fdef in tdef['fields']:
            target_table = None
            if fdef['field_type'] == FieldType.REFERENCE:
                ref_slug = fdef.get('target_table_slug')
                if ref_slug and ref_slug in tables_by_slug:
                    target_table = tables_by_slug[ref_slug]
            FieldDefinition.objects.create(
                table=table,
                name=fdef['name'],
                slug=fdef['slug'],
                field_type=fdef['field_type'],
                required=fdef.get('required', False),
                target_table=target_table,
            )

    attach_creator_as_member(project=project, creator=creator)
    return project


create_business_from_template = create_project_from_template


def validate_row_data(field_defs, data):
    """Validate payload against field definitions. Return (cleaned_data, errors)."""
    from datetime import datetime

    cleaned = {}
    errors = {}
    for fdef in field_defs:
        slug = fdef.slug
        value = data.get(slug)
        if value is None or value == '':
            if fdef.required:
                errors[slug] = 'This field is required.'
            continue
        if fdef.field_type == FieldType.STRING:
            if not isinstance(value, str):
                errors[slug] = 'Must be a string.'
            else:
                cleaned[slug] = value
        elif fdef.field_type == FieldType.NUMBER:
            if isinstance(value, bool):
                errors[slug] = 'Must be a number.'
            elif isinstance(value, (int, float)):
                cleaned[slug] = value
            else:
                try:
                    cleaned[slug] = float(value) if '.' in str(value) else int(value)
                except (TypeError, ValueError):
                    errors[slug] = 'Must be a number.'
        elif fdef.field_type == FieldType.DATE:
            if isinstance(value, str):
                try:
                    cleaned[slug] = datetime.fromisoformat(value.replace('Z', '+00:00')).isoformat()
                except ValueError:
                    errors[slug] = 'Invalid date format (use ISO 8601).'
            elif isinstance(value, datetime):
                cleaned[slug] = value.isoformat()
            else:
                errors[slug] = 'Must be a date (ISO 8601 string).'
        elif fdef.field_type == FieldType.BOOLEAN:
            if isinstance(value, bool):
                cleaned[slug] = value
            else:
                errors[slug] = 'Must be a boolean.'
        elif fdef.field_type == FieldType.REFERENCE:
            if isinstance(value, str):
                cleaned[slug] = value
            elif value is not None:
                errors[slug] = 'Reference must be a string (target row id).'
    allowed = {f.slug for f in field_defs}
    for key in data:
        if key not in allowed and not key.startswith('_'):
            errors[key] = 'Unknown field.'
    return cleaned, errors
