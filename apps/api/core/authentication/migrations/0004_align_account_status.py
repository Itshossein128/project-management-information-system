from django.db import migrations

from authentication.services import align_account_rows


def align(apps, schema_editor):
    User = apps.get_model('authentication', 'User')
    align_account_rows(User)


def noop_reverse(apps, schema_editor):
    return None


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_hr_dossier'),
    ]

    operations = [
        migrations.RunPython(align, noop_reverse),
    ]
