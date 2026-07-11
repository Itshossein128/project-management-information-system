# Sprint 6 — equipment/material cost fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('field_reports', '0004_dailyreportlabor_constraints'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyreportequipment',
            name='hourly_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='dailyreportequipment',
            name='fuel_cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='equipmentlog',
            name='hourly_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='equipmentlog',
            name='fuel_cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='dailyreportmaterial',
            name='unit_cost',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True),
        ),
    ]
