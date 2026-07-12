# Sprint 6 performance indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('field_reports', '0005_sprint6_cost_fields'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='dailyreport',
            index=models.Index(fields=['project', 'report_date'], name='dailyreport_project_date_idx'),
        ),
        migrations.AddIndex(
            model_name='weatherlog',
            index=models.Index(fields=['project', 'log_date'], name='weatherlog_project_date_idx'),
        ),
    ]
