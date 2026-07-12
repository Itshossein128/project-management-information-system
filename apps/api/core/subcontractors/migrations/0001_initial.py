# Generated for Sprint 7

import uuid

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contracts', '0003_sprint7_audit_fields'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subcontractor',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('company_name', models.CharField(max_length=120)),
                ('discipline', models.CharField(blank=True, default='', max_length=60)),
                ('responsible_person', models.CharField(blank=True, default='', max_length=80)),
                ('phone', models.CharField(blank=True, default='', max_length=30)),
                ('status', models.CharField(default='active', max_length=20)),
                ('contract', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subcontractors', to='contracts.contract')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcontractors', to='projects.project')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'subcontractors'},
        ),
        migrations.CreateModel(
            name='SubcontractorPerformanceScore',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('score_date', models.DateField()),
                ('progress_score', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('quality_score', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('hse_score', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('payment_compliance_score', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('cooperation_score', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('overall_score', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('notes', models.TextField(blank=True, default='')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('evaluator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sub_scores', to=settings.AUTH_USER_MODEL)),
                ('subcontractor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='subcontractors.subcontractor')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'subcontractor_performance_scores'},
        ),
        migrations.CreateModel(
            name='SubcontractorWarning',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('warning_date', models.DateField()),
                ('warning_type', models.CharField(max_length=30)),
                ('reason', models.TextField()),
                ('resolved', models.BooleanField(default=False)),
                ('resolved_date', models.DateField(blank=True, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('issued_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sub_warnings', to=settings.AUTH_USER_MODEL)),
                ('subcontractor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='warnings', to='subcontractors.subcontractor')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'subcontractor_warnings'},
        ),
    ]
