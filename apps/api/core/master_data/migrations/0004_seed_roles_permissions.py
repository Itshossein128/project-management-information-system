from django.db import migrations

from permissions.constants import (
    DEFAULT_ROLE_DESCRIPTIONS,
    DEFAULT_ROLE_PERMISSIONS,
    PERMISSIONS,
)


def seed_permissions_and_roles(apps, schema_editor):
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
        if not role.description:
            role.description = DEFAULT_ROLE_DESCRIPTIONS.get(role_name, '')
            role.save(update_fields=['description'])

        for codename in codenames:
            RolePermission.objects.get_or_create(
                role=role,
                permission_codename=codename,
            )


def unseed_permissions_and_roles(apps, schema_editor):
    RolePermission = apps.get_model('master_data', 'RolePermission')
    Role = apps.get_model('master_data', 'Role')
    Permission = apps.get_model('master_data', 'Permission')

    RolePermission.objects.filter(
        role__role_name__in=list(DEFAULT_ROLE_PERMISSIONS.keys())
    ).delete()
    Role.objects.filter(role_name__in=list(DEFAULT_ROLE_PERMISSIONS.keys())).delete()
    Permission.objects.filter(codename__in=list(PERMISSIONS.keys())).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0003_sprint2_permissions'),
    ]

    operations = [
        migrations.RunPython(seed_permissions_and_roles, unseed_permissions_and_roles),
    ]
