# Sprint 6 — audit fields, notes, daily_report FK, indexes

import django.utils.timezone
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def set_audit_user(apps, schema_editor):
    User = apps.get_model('authentication', 'User')
    user = User.objects.filter(is_superuser=True).first() or User.objects.first()
    if not user:
        return
    for model_name in ('CostPool', 'Budget', 'ActualCost'):
        Model = apps.get_model('cost_control', model_name)
        Model.objects.filter(created_by__isnull=True).update(created_by_id=user.id)


class Migration(migrations.Migration):

    dependencies = [
        ('field_reports', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cost_control', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='budget',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='budget',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='budget',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='budget',
            name='created_by',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='budget',
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
            model_name='budget',
            name='notes',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='actualcost',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='actualcost',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='actualcost',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='actualcost',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='actualcost',
            name='created_by',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='actualcost',
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
            model_name='actualcost',
            name='daily_report',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='actual_costs',
                to='field_reports.dailyreport',
            ),
        ),
        migrations.AddField(
            model_name='costpool',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='costpool',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='costpool',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='costpool',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='costpool',
            name='created_by',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='costpool',
            name='updated_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(set_audit_user, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='budget',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='actualcost',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='costpool',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name='budget',
            index=models.Index(fields=['project', 'cost_category'], name='budget_project_cat_idx'),
        ),
        migrations.AddIndex(
            model_name='actualcost',
            index=models.Index(fields=['project', 'cost_date'], name='actualcost_project_date_idx'),
        ),
    ]
