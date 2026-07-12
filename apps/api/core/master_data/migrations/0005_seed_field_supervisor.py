from django.db import migrations

FIELD_SUPERVISOR = 'field_supervisor'
FIELD_SUPERVISOR_PERMISSIONS = [
    'view_project',
    'view_wbs',
    'view_activities',
    'view_reports',
    'edit_reports',
]
DESCRIPTION = 'Field crew filling daily reports on mobile/tablet.'


def seed_field_supervisor(apps, schema_editor):
    Permission = apps.get_model('master_data', 'Permission')
    Role = apps.get_model('master_data', 'Role')
    RolePermission = apps.get_model('master_data', 'RolePermission')

    for codename in FIELD_SUPERVISOR_PERMISSIONS:
        Permission.objects.get_or_create(codename=codename, defaults={'label': codename})

    role, _ = Role.objects.get_or_create(
        role_name=FIELD_SUPERVISOR,
        defaults={'description': DESCRIPTION},
    )
    for codename in FIELD_SUPERVISOR_PERMISSIONS:
        RolePermission.objects.get_or_create(role=role, permission_codename=codename)


def unseed_field_supervisor(apps, schema_editor):
    Role = apps.get_model('master_data', 'Role')
    RolePermission = apps.get_model('master_data', 'RolePermission')
    RolePermission.objects.filter(role__role_name=FIELD_SUPERVISOR).delete()
    Role.objects.filter(role_name=FIELD_SUPERVISOR).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0004_seed_roles_permissions'),
    ]

    operations = [
        migrations.RunPython(seed_field_supervisor, unseed_field_supervisor),
    ]
