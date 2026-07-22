# Generated manually for Sprint 13 hardening

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0004_sprint13_alert_types'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='alertlog',
            index=models.Index(fields=['project', 'acknowledged_at'], name='alertlog_proj_ack_idx'),
        ),
        migrations.AddIndex(
            model_name='alertlog',
            index=models.Index(fields=['project', '-fired_at'], name='alertlog_proj_fired_idx'),
        ),
    ]
