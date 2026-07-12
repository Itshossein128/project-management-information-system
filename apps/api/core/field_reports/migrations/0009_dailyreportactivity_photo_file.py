# Activity photo attachment

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0001_initial'),
        ('field_reports', '0008_dailyreportlabor_daily_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyreportactivity',
            name='photo_file',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='daily_report_activities',
                to='storage.storedfile',
            ),
        ),
    ]
