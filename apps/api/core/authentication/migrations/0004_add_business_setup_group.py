"""
Data migration: create the 'business-setup' role group.
Users in this group can add businesses and control features per business.
Assign this group only to support users (e.g. via Django admin).
"""
from django.db import migrations


def create_business_setup_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="business-setup")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0003_add_root_group"),
    ]
    operations = [
        migrations.RunPython(create_business_setup_group, noop),
    ]
