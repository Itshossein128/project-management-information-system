# Generated manually for 006-hr-capacity

import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0011_schedule_baseline_gap'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hr', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResourceAllocation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('role', models.CharField(max_length=120)),
                ('capacity_percent', models.DecimalField(decimal_places=2, max_digits=8)),
                ('capacity_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('work_location', models.CharField(blank=True, default='', max_length=200)),
                ('status', models.CharField(
                    choices=[
                        ('planned', 'Planned'),
                        ('active', 'Active'),
                        ('completed', 'Completed'),
                        ('cancelled', 'Cancelled'),
                    ],
                    default='planned',
                    max_length=20,
                )),
                ('has_capacity_exception', models.BooleanField(default=False)),
                ('activity', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='resource_allocations',
                    to='projects.activity',
                )),
                ('created_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('person', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='resource_allocations',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='resource_allocations',
                    to='projects.project',
                )),
                ('supervisor', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='supervised_resource_allocations',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('updated_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('wbs', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='resource_allocations',
                    to='projects.wbs',
                )),
            ],
            options={
                'db_table': 'resource_allocations',
                'ordering': ['-start_date'],
            },
        ),
        migrations.CreateModel(
            name='CapacityException',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('reason', models.TextField(blank=True, default='')),
                ('status', models.CharField(
                    choices=[
                        ('draft', 'Draft'),
                        ('submitted', 'Submitted'),
                        ('approved', 'Approved'),
                        ('rejected', 'Rejected'),
                    ],
                    default='draft',
                    max_length=20,
                )),
                ('requested_capacity_percent', models.DecimalField(decimal_places=2, max_digits=8)),
                ('overlapping_snapshot', models.JSONField(blank=True, default=dict)),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('decided_at', models.DateTimeField(blank=True, null=True)),
                ('decision_notes', models.TextField(blank=True, default='')),
                ('allocation', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='linked_exceptions',
                    to='hr.resourceallocation',
                )),
                ('created_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('decided_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='decided_capacity_exceptions',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('person', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='capacity_exceptions',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='capacity_exceptions',
                    to='projects.project',
                )),
                ('updated_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'capacity_exceptions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='resourceallocation',
            name='capacity_exception',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='allocations',
                to='hr.capacityexception',
            ),
        ),
        migrations.CreateModel(
            name='ApprovedLaborRate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=14)),
                ('currency', models.CharField(default='IRR', max_length=3)),
                ('effective_from', models.DateField()),
                ('effective_to', models.DateField(blank=True, null=True)),
                ('created_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('person', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='approved_labor_rates',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='approved_labor_rates',
                    to='projects.project',
                )),
                ('updated_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'approved_labor_rates',
                'ordering': ['-effective_from'],
            },
        ),
    ]
