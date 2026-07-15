from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subcontractors', '0002_alter_subcontractor_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcontractorwarning',
            name='resolution_notes',
            field=models.TextField(blank=True, default=''),
        ),
    ]
