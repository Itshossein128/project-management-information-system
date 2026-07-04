"""
Data migration: create the 'root' role group.
Users in this group can add businesses and control features per business.
Assign this group only to support/root users (e.g. via Django admin).
"""
from django.db import migrations


# Function to handle create root group
def create_root_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="root")


# Function to handle noop
def noop(apps, schema_editor):
    pass


# Class representing Migration
class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0002_add_role_groups"),
    ]
    operations = [
        migrations.RunPython(create_root_group, noop),
    ]
