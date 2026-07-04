"""
Data migration: create the 'business-setup' role group.
Users in this group can add businesses and control features per business.
Assign this group only to support users (e.g. via Django admin).
"""
from django.db import migrations


# Function to handle create business setup group
def create_business_setup_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="business-setup")


# Function to handle noop
def noop(apps, schema_editor):
    pass


# Class representing Migration
class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0003_add_root_group"),
    ]
    operations = [
        migrations.RunPython(create_business_setup_group, noop),
    ]
