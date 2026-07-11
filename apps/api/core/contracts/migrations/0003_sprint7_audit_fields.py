# Sprint 7 — contracts audit fields, ChangeOrder, IPC extensions

import django.utils.timezone
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def set_audit_user(apps, schema_editor):
    User = apps.get_model('authentication', 'User')
    user = User.objects.filter(is_superuser=True).first() or User.objects.first()
    if not user:
        return
    for model_name in ('Contract', 'ContractItem', 'IPC', 'IPCItem', 'IPCDeduction'):
        Model = apps.get_model('contracts', model_name)
        if hasattr(Model, 'objects'):
            Model.objects.filter(created_by__isnull=True).update(created_by_id=user.id)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contracts', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeOrder',
            fields=[
                ('id', models.UUIDField(default=__import__('uuid').uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('change_number', models.PositiveIntegerField()),
                ('description', models.TextField(blank=True, default='')),
                ('amount_change', models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ('approved_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(default='draft', max_length=20)),
                ('file_url', models.CharField(blank=True, default='', max_length=500)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='change_orders', to='contracts.contract')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'change_orders'},
        ),
        migrations.AlterUniqueTogether(name='changeorder', unique_together={('contract', 'change_number')}),
        migrations.AddField(model_name='contract', name='created_at', field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now), preserve_default=False),
        migrations.AddField(model_name='contract', name='updated_at', field=models.DateTimeField(auto_now=True)),
        migrations.AddField(model_name='contract', name='is_deleted', field=models.BooleanField(default=False)),
        migrations.AddField(model_name='contract', name='deleted_at', field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name='contract', name='created_by', field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name='contract', name='updated_by', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name='contract', name='performance_guarantee_amount', field=models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
        migrations.AddField(model_name='contract', name='performance_guarantee_expiry', field=models.DateField(blank=True, null=True)),
        migrations.AddField(model_name='contract', name='advance_guarantee_amount', field=models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
        migrations.AddField(model_name='contract', name='advance_guarantee_expiry', field=models.DateField(blank=True, null=True)),
        migrations.AddField(model_name='contract', name='notes', field=models.TextField(blank=True, default='')),
        migrations.AlterField(model_name='contract', name='contract_number', field=models.CharField(blank=True, default='', max_length=60)),
        migrations.AlterField(model_name='contract', name='advance_payment_pct', field=models.DecimalField(decimal_places=2, default=0, max_digits=5)),
        migrations.AlterField(model_name='contract', name='retention_pct', field=models.DecimalField(decimal_places=2, default=0, max_digits=5)),
        migrations.AlterField(model_name='contract', name='insurance_pct', field=models.DecimalField(decimal_places=2, default=0, max_digits=5)),
        migrations.AlterField(model_name='contract', name='tax_pct', field=models.DecimalField(decimal_places=2, default=0, max_digits=5)),
        migrations.AlterField(model_name='contract', name='file_url', field=models.CharField(blank=True, default='', max_length=500)),
        migrations.AddField(model_name='contractitem', name='created_at', field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now), preserve_default=False),
        migrations.AddField(model_name='contractitem', name='updated_at', field=models.DateTimeField(auto_now=True)),
        migrations.AddField(model_name='contractitem', name='is_deleted', field=models.BooleanField(default=False)),
        migrations.AddField(model_name='contractitem', name='deleted_at', field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name='contractitem', name='created_by', field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name='contractitem', name='updated_by', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name='ipc', name='created_at', field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now), preserve_default=False),
        migrations.AddField(model_name='ipc', name='updated_at', field=models.DateTimeField(auto_now=True)),
        migrations.AddField(model_name='ipc', name='is_deleted', field=models.BooleanField(default=False)),
        migrations.AddField(model_name='ipc', name='deleted_at', field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name='ipc', name='created_by', field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name='ipc', name='updated_by', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name='ipc', name='rejection_reason', field=models.TextField(blank=True, default='')),
        migrations.AddField(model_name='ipc', name='notes', field=models.TextField(blank=True, default='')),
        migrations.AlterField(model_name='ipc', name='gross_amount', field=models.DecimalField(decimal_places=2, default=0, max_digits=18)),
        migrations.AddField(model_name='ipcitem', name='created_at', field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now), preserve_default=False),
        migrations.AddField(model_name='ipcitem', name='updated_at', field=models.DateTimeField(auto_now=True)),
        migrations.AddField(model_name='ipcitem', name='is_deleted', field=models.BooleanField(default=False)),
        migrations.AddField(model_name='ipcitem', name='deleted_at', field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name='ipcitem', name='created_by', field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name='ipcitem', name='updated_by', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name='ipcitem', name='description', field=models.TextField(blank=True, default='')),
        migrations.AddField(model_name='ipcitem', name='unit', field=models.CharField(blank=True, default='', max_length=40)),
        migrations.AlterField(model_name='ipcitem', name='qty_previous', field=models.DecimalField(decimal_places=4, default=0, max_digits=18)),
        migrations.AlterField(model_name='ipcitem', name='qty_current', field=models.DecimalField(decimal_places=4, default=0, max_digits=18)),
        migrations.AlterField(model_name='ipcitem', name='qty_cumulative', field=models.DecimalField(decimal_places=4, default=0, max_digits=18)),
        migrations.AlterField(model_name='ipcitem', name='amount_current', field=models.DecimalField(decimal_places=2, default=0, max_digits=18)),
        migrations.AlterField(model_name='ipcitem', name='amount_cumulative', field=models.DecimalField(decimal_places=2, default=0, max_digits=18)),
        migrations.AddField(model_name='ipcdeduction', name='created_at', field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now), preserve_default=False),
        migrations.AddField(model_name='ipcdeduction', name='updated_at', field=models.DateTimeField(auto_now=True)),
        migrations.AddField(model_name='ipcdeduction', name='is_deleted', field=models.BooleanField(default=False)),
        migrations.AddField(model_name='ipcdeduction', name='deleted_at', field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name='ipcdeduction', name='created_by', field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name='ipcdeduction', name='updated_by', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name='ipcdeduction', name='description', field=models.CharField(blank=True, default='', max_length=200)),
        migrations.RunPython(set_audit_user, migrations.RunPython.noop),
        migrations.AlterField(model_name='contract', name='created_by', field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
        migrations.AlterField(model_name='contractitem', name='created_by', field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
        migrations.AlterField(model_name='ipc', name='created_by', field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
        migrations.AlterField(model_name='ipcitem', name='created_by', field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
        migrations.AlterField(model_name='ipcdeduction', name='created_by', field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
    ]
