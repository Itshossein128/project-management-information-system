import uuid

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0006_alter_activity_wbs_cascade'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='currency',
            field=models.CharField(
                choices=[('IRR', 'Rial'), ('IRT', 'Toman')],
                default='IRR',
                max_length=3,
            ),
        ),
        migrations.AddField(
            model_name='wbs',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='wbs',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='wbs',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wbs',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='wbs',
            name='created_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='wbs',
            name='updated_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name='ProjectCapabilitySetting',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('capability_key', models.CharField(max_length=64)),
                ('enabled', models.BooleanField(default=True)),
                (
                    'mode',
                    models.CharField(
                        choices=[
                            ('required', 'Required'),
                            ('optional', 'Optional'),
                            ('disabled', 'Disabled'),
                        ],
                        default='optional',
                        max_length=20,
                    ),
                ),
                (
                    'created_by',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='+',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'project',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='capability_settings',
                        to='projects.project',
                    ),
                ),
                (
                    'updated_by',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='+',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'db_table': 'project_capability_settings',
            },
        ),
        migrations.CreateModel(
            name='FiscalPeriodLock',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
                ('closed_at', models.DateTimeField()),
                ('reason', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                (
                    'closed_by',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='fiscal_locks_closed',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'project',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='fiscal_period_locks',
                        to='projects.project',
                    ),
                ),
            ],
            options={
                'db_table': 'fiscal_period_locks',
                'ordering': ['-period_end', '-closed_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='projectcapabilitysetting',
            constraint=models.UniqueConstraint(
                fields=('project', 'capability_key'),
                name='uniq_project_capability_key',
            ),
        ),
    ]
