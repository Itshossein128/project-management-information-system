# Generated manually for 028-auto-daily-report-summary T070

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sub_reports', '0002_auto_daily_report_summary'),
    ]

    operations = [
        migrations.AddField(
            model_name='disciplinesubreport',
            name='site_status',
            field=models.CharField(
                choices=[('active', 'فعال'), ('inactive', 'غیرفعال')],
                default='active',
                max_length=10,
            ),
        ),
    ]
