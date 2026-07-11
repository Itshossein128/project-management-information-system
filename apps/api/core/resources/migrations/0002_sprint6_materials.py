# Sprint 6 — materials, suppliers, inventory extensions

import django.utils.timezone
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


def set_supplier_audit(apps, schema_editor):
    User = apps.get_model('authentication', 'User')
    user = User.objects.filter(is_superuser=True).first() or User.objects.first()
    if not user:
        return
    Supplier = apps.get_model('resources', 'Supplier')
    Supplier.objects.filter(created_by__isnull=True).update(created_by_id=user.id)
    InventoryTransaction = apps.get_model('resources', 'InventoryTransaction')
    InventoryTransaction.objects.filter(created_by__isnull=True).update(created_by_id=user.id)


class Migration(migrations.Migration):

    dependencies = [
        ('field_reports', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='project',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='suppliers',
                to='projects.project',
            ),
        ),
        migrations.AddField(
            model_name='supplier',
            name='supplier_code',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AddField(
            model_name='supplier',
            name='contact_person',
            field=models.CharField(blank=True, default='', max_length=80),
        ),
        migrations.AddField(
            model_name='supplier',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AddField(
            model_name='supplier',
            name='email',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='supplier',
            name='address',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='supplier',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='supplier',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='supplier',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='created_by',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='supplier',
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
            model_name='material',
            name='project',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='materials',
                to='projects.project',
            ),
        ),
        migrations.AlterField(
            model_name='material',
            name='material_code',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='material',
            name='material_name',
            field=models.CharField(max_length=200),
        ),
        migrations.AddField(
            model_name='material',
            name='discipline',
            field=models.CharField(blank=True, default='general', max_length=20),
        ),
        migrations.AddField(
            model_name='material',
            name='location',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='material',
            name='block_type',
            field=models.CharField(blank=True, default='', max_length=80),
        ),
        migrations.AddField(
            model_name='material',
            name='estimated_total_qty',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True),
        ),
        migrations.AddField(
            model_name='material',
            name='qty_per_block',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True),
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='block_ref',
            field=models.CharField(blank=True, default='', max_length=60),
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='daily_report',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='inventory_transactions',
                to='field_reports.dailyreport',
            ),
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='created_by',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='updated_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='inventorytransaction',
            name='material',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='transactions',
                to='resources.material',
            ),
        ),
        migrations.CreateModel(
            name='MaterialRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('request_number', models.PositiveIntegerField()),
                ('requested_qty', models.DecimalField(decimal_places=4, max_digits=18)),
                ('unit', models.CharField(max_length=40)),
                ('request_date', models.DateField(blank=True, null=True)),
                ('required_by_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending'),
                        ('ordered', 'Ordered'),
                        ('delivered', 'Delivered'),
                        ('cancelled', 'Cancelled'),
                    ],
                    default='pending',
                    max_length=20,
                )),
                ('notes', models.TextField(blank=True, default='')),
                ('created_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('updated_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('material', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='requests',
                    to='resources.material',
                )),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='material_requests',
                    to='projects.project',
                )),
            ],
            options={'db_table': 'material_requests'},
        ),
        migrations.RunPython(set_supplier_audit, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='supplier',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='inventorytransaction',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name='material',
            constraint=models.UniqueConstraint(
                fields=('project', 'material_code'),
                name='uniq_material_project_code',
            ),
        ),
        migrations.AddConstraint(
            model_name='materialrequest',
            constraint=models.UniqueConstraint(
                fields=('project', 'material', 'request_number'),
                name='uniq_material_request_number',
            ),
        ),
        migrations.AddIndex(
            model_name='inventorytransaction',
            index=models.Index(fields=['material', 'tx_date'], name='invtx_material_date_idx'),
        ),
    ]
