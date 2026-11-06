# Generated manually for A6-P4 stored file source binding.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('storage', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='storedfile',
            name='source',
            field=models.CharField(blank=True, choices=[
                ('documents', 'documents'),
                ('reports', 'reports'),
            ], default='', max_length=20),
        ),
        migrations.AddField(
            model_name='storedfile',
            name='restricted_allowlist',
            field=models.ManyToManyField(
                blank=True,
                related_name='allowed_stored_files',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
