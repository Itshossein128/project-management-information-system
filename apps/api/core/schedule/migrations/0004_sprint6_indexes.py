# Sprint 6 performance indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0003_activity_progress_source'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='activityprogress',
            index=models.Index(fields=['activity', 'report_date'], name='actprogress_activity_date_idx'),
        ),
    ]
