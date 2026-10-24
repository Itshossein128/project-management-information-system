import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sub_reports', '0011_general_activity_row_number'),
        ('field_reports', '0021_section_projection'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyreportincident',
            name='row_number',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='dailyreportincident',
            name='source_row_id',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
        migrations.AddField(
            model_name='dailyreportincident',
            name='source_report',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='derived_daily_incidents',
                to='sub_reports.disciplinesubreport',
            ),
        ),
        migrations.AlterModelOptions(
            name='dailyreportincident',
            options={'ordering': ['row_number']},
        ),
    ]
