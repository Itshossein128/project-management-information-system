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


def _validate_string(value, slug):
    if not isinstance(value, str):
        return None, 'Must be a string.'
    return value, None

def _validate_number(value, slug):
    if isinstance(value, bool):
        return None, 'Must be a number.'
    if isinstance(value, (int, float)):
        return value, None
    try:
        cleaned_val = float(value) if '.' in str(value) else int(value)
        return cleaned_val, None
    except (TypeError, ValueError):
        return None, 'Must be a number.'

def _validate_date(value, slug):
    from datetime import datetime
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00')).isoformat(), None
        except ValueError:
            return None, 'Invalid date format (use ISO 8601).'
    if isinstance(value, datetime):
        return value.isoformat(), None
    return None, 'Must be a date (ISO 8601 string).'

def _validate_boolean(value, slug):
    if isinstance(value, bool):
        return value, None
    return None, 'Must be a boolean.'

def _validate_reference(value, slug):
    if isinstance(value, str):
        return value, None
    if value is not None:
        return None, 'Reference must be a string (target row id).'
    return None, None

FIELD_VALIDATORS = {
    FieldType.STRING: _validate_string,
    FieldType.NUMBER: _validate_number,
    FieldType.DATE: _validate_date,
    FieldType.BOOLEAN: _validate_boolean,
    FieldType.REFERENCE: _validate_reference,
}

def validate_row_data(field_defs, data):
    """Validate payload against field definitions. Return (cleaned_data, errors)."""
    cleaned = {}
    errors = {}

    for fdef in field_defs:
        slug = fdef.slug
        value = data.get(slug)

        if value is None or value == '':
            if fdef.required:
                errors[slug] = 'This field is required.'
            continue

        validator = FIELD_VALIDATORS.get(fdef.field_type)
        if validator:
            cleaned_val, err = validator(value, slug)
            if err:
                errors[slug] = err
            elif cleaned_val is not None:
                cleaned[slug] = cleaned_val
        else:
            errors[slug] = f'Unknown field type {fdef.field_type}.'

    allowed = {f.slug for f in field_defs}
    for key in data:
        if key not in allowed and not key.startswith('_'):
            errors[key] = 'Unknown field.'

    return cleaned, errors
