from django.db import migrations

from permissions.constants import (
    DEFAULT_ROLE_DESCRIPTIONS,
    DEFAULT_ROLE_PERMISSIONS,
    PERMISSIONS,
)


def seed_sprint7_permissions(apps, schema_editor):
    Permission = apps.get_model('master_data', 'Permission')
    Role = apps.get_model('master_data', 'Role')
    RolePermission = apps.get_model('master_data', 'RolePermission')

    for codename, label in PERMISSIONS.items():
        Permission.objects.get_or_create(codename=codename, defaults={'label': label})

    for role_name, codenames in DEFAULT_ROLE_PERMISSIONS.items():
        role, _ = Role.objects.get_or_create(
            role_name=role_name,
            defaults={'description': DEFAULT_ROLE_DESCRIPTIONS.get(role_name, '')},
        )
        for codename in codenames:
            RolePermission.objects.get_or_create(role=role, permission_codename=codename)


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0006_sprint6_cost_supplier_permissions'),
    ]

    operations = [
        migrations.RunPython(seed_sprint7_permissions, migrations.RunPython.noop),
    ]
