from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0009_central_data_model'),
        ('projects', '0020_activity_import_fidelity_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='measurement_unit',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='projects',
                to='master_data.unit',
            ),
        ),
    ]
