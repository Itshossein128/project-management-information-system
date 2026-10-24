from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sub_reports', '0010_disciplinesubreportactivity_headcount'),
    ]

    operations = [
        migrations.AddField(
            model_name='disciplinesubreportgeneralactivity',
            name='row_number',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
