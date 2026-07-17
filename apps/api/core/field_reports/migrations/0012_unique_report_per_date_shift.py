from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('field_reports', '0011_sprint10_equipment_hr'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='dailyreport',
            name='unique_active_daily_report_per_date',
        ),
        migrations.AddConstraint(
            model_name='dailyreport',
            constraint=models.UniqueConstraint(
                condition=models.Q(('is_deleted', False)),
                fields=('project', 'report_date', 'shift'),
                name='unique_active_daily_report_per_date_shift',
            ),
        ),
    ]
