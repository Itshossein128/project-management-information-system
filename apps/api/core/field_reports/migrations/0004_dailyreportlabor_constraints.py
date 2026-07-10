# Sprint 5 — standalone manpower unique constraints

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('field_reports', '0003_standalone_forms'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='dailyreportlabor',
            name='unique_active_labor_row',
        ),
        migrations.AddConstraint(
            model_name='dailyreportlabor',
            constraint=models.UniqueConstraint(
                condition=models.Q(('is_deleted', False), ('report__isnull', False)),
                fields=('report', 'labor_category', 'job_title'),
                name='unique_active_labor_row',
            ),
        ),
        migrations.AddConstraint(
            model_name='dailyreportlabor',
            constraint=models.UniqueConstraint(
                condition=models.Q(('is_deleted', False), ('report__isnull', True)),
                fields=('project', 'report_date', 'labor_category', 'job_title'),
                name='unique_standalone_labor_row',
            ),
        ),
    ]
