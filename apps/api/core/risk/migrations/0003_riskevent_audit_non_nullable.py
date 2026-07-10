# Sprint 5 — align RiskEvent audit fields with AuditSoftDeleteModel

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


def backfill_audit_timestamps(apps, schema_editor):
    RiskEvent = apps.get_model('risk', 'RiskEvent')
    now = django.utils.timezone.now()
    RiskEvent.objects.filter(created_at__isnull=True).update(
        created_at=now,
        updated_at=now,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0002_barrier_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(backfill_audit_timestamps, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='riskevent',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='riskevent',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='riskevent',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
