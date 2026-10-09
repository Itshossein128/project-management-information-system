# Generated manually for FR-009 baseline soft-delete + audit

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


def backfill_baseline_audit(apps, schema_editor):
    BaselineSchedule = apps.get_model('schedule', 'BaselineSchedule')
    User = apps.get_model(settings.AUTH_USER_MODEL)
    fallback = User.objects.order_by('pk').first()
    for bl in BaselineSchedule.objects.all():
        user = bl.approved_by_id or bl.locked_by_id or (fallback.id if fallback else None)
        if user is None:
            continue
        updates = {}
        if bl.created_by_id is None:
            updates['created_by_id'] = user
        if bl.updated_by_id is None:
            updates['updated_by_id'] = user
        if updates:
            BaselineSchedule.objects.filter(pk=bl.pk).update(**updates)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('schedule', '0008_schedule_baseline_gap'),
    ]

    operations = [
        migrations.AddField(
            model_name='baselineschedule',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='baselineschedule',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='baselineschedule',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='baselineschedule',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='baselineschedule',
            name='created_by',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='baselineschedule',
            name='updated_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(backfill_baseline_audit, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='baselineschedule',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
