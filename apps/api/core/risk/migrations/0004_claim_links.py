# Generated manually for Sprint 11 claim documentation linker

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_alter_correspondence_corr_type_and_more'),
        ('field_reports', '0012_unique_report_per_date_shift'),
        ('risk', '0003_riskevent_audit_non_nullable'),
    ]

    operations = [
        migrations.AddField(
            model_name='riskevent',
            name='related_correspondence',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='linked_risk_events',
                to='documents.correspondence',
            ),
        ),
        migrations.AddField(
            model_name='riskevent',
            name='related_daily_report',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='linked_risk_events',
                to='field_reports.dailyreport',
            ),
        ),
    ]
