from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0019_project_approval_submitted_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='planned_percent',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=6, null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='is_critical',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='total_slack_days',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='free_slack_days',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
