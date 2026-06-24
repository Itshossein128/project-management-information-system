"""
Data migration: create default role groups (visitor, manager, commentor).
Assign users to these groups for role-based permissions.
"""
from django.db import migrations


def create_role_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for name in ("visitor", "manager", "commentor"):
        Group.objects.get_or_create(name=name)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(create_role_groups, noop),
    ]
