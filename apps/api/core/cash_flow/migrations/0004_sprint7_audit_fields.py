# Sprint 7 — audit fields, counterparty, document_ref, notes

import django.utils.timezone
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def set_audit_user(apps, schema_editor):
    User = apps.get_model('authentication', 'User')
    user = User.objects.filter(is_superuser=True).first() or User.objects.first()
    if not user:
        return
    for model_name in ('CashTransaction', 'CashFlowForecast'):
        Model = apps.get_model('cash_flow', model_name)
        Model.objects.filter(created_by__isnull=True).update(created_by_id=user.id)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cash_flow', '0003_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashtransaction',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cashtransaction',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='cashtransaction',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cashtransaction',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cashtransaction',
            name='created_by',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='cashtransaction',
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
            model_name='cashtransaction',
            name='counterparty',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='cashtransaction',
            name='document_ref',
            field=models.CharField(blank=True, default='', max_length=60),
        ),
        migrations.AddField(
            model_name='cashflowforecast',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cashflowforecast',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='cashflowforecast',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cashflowforecast',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cashflowforecast',
            name='created_by',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='cashflowforecast',
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
            model_name='cashflowforecast',
            name='notes',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='cashflowforecast',
            name='expected_inflow',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=18),
        ),
        migrations.AlterField(
            model_name='cashflowforecast',
            name='expected_outflow',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=18),
        ),
        migrations.RunPython(set_audit_user, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='cashtransaction',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='cashflowforecast',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name='cashtransaction',
            index=models.Index(fields=['project', 'tx_date'], name='cashtx_project_date_idx'),
        ),
    ]
