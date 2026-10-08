import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0008_central_data_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='wbs',
            name='acceptance_criteria',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='wbs',
            name='responsible',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='responsible_wbs_nodes',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='wbs',
            name='status',
            field=models.CharField(
                choices=[
                    ('draft', 'Draft'),
                    ('active', 'Active'),
                    ('completed', 'Completed'),
                    ('on_hold', 'On hold'),
                ],
                default='active',
                max_length=20,
            ),
        ),
    ]
