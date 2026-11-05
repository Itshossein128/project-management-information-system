"""Grant delete_activities to roles that can already edit activities."""

from django.db import migrations

DELETE_CODENAME = 'delete_activities'
EDIT_CODENAME = 'edit_activities'


def grant_delete_activities(apps, schema_editor):
    Permission = apps.get_model('master_data', 'Permission')
    RolePermission = apps.get_model('master_data', 'RolePermission')
    Permission.objects.get_or_create(
        codename=DELETE_CODENAME,
        defaults={'label': 'Delete activities'},
    )
    role_ids = RolePermission.objects.filter(
        permission_codename=EDIT_CODENAME,
    ).values_list('role_id', flat=True)
    for role_id in role_ids:
        RolePermission.objects.get_or_create(
            role_id=role_id,
            permission_codename=DELETE_CODENAME,
        )


def revoke_inserted_delete_activities(apps, schema_editor):
    """Remove delete grants from roles that also edit activities.

    Before this migration the delete codename was not assigned. Roles that
    hold delete without edit are left untouched.
    """
    RolePermission = apps.get_model('master_data', 'RolePermission')
    editor_ids = RolePermission.objects.filter(
        permission_codename=EDIT_CODENAME,
    ).values_list('role_id', flat=True)
    RolePermission.objects.filter(
        role_id__in=editor_ids,
        permission_codename=DELETE_CODENAME,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0013_decision_support_permissions'),
    ]

    operations = [
        migrations.RunPython(grant_delete_activities, revoke_inserted_delete_activities),
    ]
