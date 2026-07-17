# Labor daily rate for auto-cost calculation

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('field_reports', '0007_remove_dailyreport_dailyreport_project_date_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyreportlabor',
            name='daily_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
    ]
