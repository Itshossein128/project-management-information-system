# Generated manually for project delete support

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_activity_audit_soft_delete'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='wbs',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='activities',
                to='projects.wbs',
            ),
        ),
    ]
