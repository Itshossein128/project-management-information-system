# Generated manually for Sprint 3 Section 1

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def backfill_audit_fields(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    Activity = apps.get_model('projects', 'Activity')
    ActivityRelation = apps.get_model('projects', 'ActivityRelation')
    user = User.objects.order_by('created_at').first()
    if user is None:
        return
    now = django.utils.timezone.now()
    Activity.objects.filter(created_by__isnull=True).update(
        created_by_id=user.id,
        updated_by_id=user.id,
        created_at=now,
        updated_at=now,
    )
    ActivityRelation.objects.filter(created_by__isnull=True).update(
        created_by_id=user.id,
        updated_by_id=user.id,
        created_at=now,
        updated_at=now,
    )


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0004_customer_decisions'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='activity',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activity',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='created_by',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='activity',
            name='updated_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='activity',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='activityrelation',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='activityrelation',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='activityrelation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activityrelation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='activityrelation',
            name='created_by',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='activityrelation',
            name='updated_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(backfill_audit_fields, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='activity',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='activityrelation',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='activity',
            name='wbs',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='activities',
                to='projects.wbs',
            ),
        ),
        migrations.AddConstraint(
            model_name='activityrelation',
            constraint=models.UniqueConstraint(
                condition=models.Q(('is_deleted', False)),
                fields=('predecessor', 'successor'),
                name='unique_active_activity_relation',
            ),
        ),
    ]
