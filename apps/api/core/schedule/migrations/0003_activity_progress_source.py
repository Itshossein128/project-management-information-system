# Generated manually for Sprint 5

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0002_customer_decisions'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityprogress',
            name='notes',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='activityprogress',
            name='source',
            field=models.CharField(
                choices=[('daily_report', 'Daily report'), ('manual', 'Manual')],
                default='daily_report',
                max_length=20,
            ),
        ),
    ]
