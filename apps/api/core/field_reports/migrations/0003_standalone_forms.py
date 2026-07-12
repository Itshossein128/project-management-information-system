# Sprint 5 standalone forms

import django.db.models.deletion
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('field_reports', '0002_seed_labor_titles'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyreportlabor',
            name='project',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='standalone_labor_entries',
                to='projects.project',
            ),
        ),
        migrations.AddField(
            model_name='dailyreportlabor',
            name='report_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dailyreportlabor',
            name='report',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='labor_entries',
                to='field_reports.dailyreport',
            ),
        ),
        migrations.CreateModel(
            name='LaborCampReport',
            fields=[
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('report_date', models.DateField()),
                ('connex_number', models.CharField(max_length=60)),
                ('subcontractor_name', models.CharField(max_length=120)),
                ('total_residents', models.PositiveIntegerField()),
                ('present_count', models.PositiveIntegerField()),
                ('on_leave_count', models.PositiveIntegerField()),
                ('capacity', models.PositiveIntegerField()),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='authentication.user')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='labor_camp_reports', to='projects.project')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='authentication.user')),
            ],
            options={'db_table': 'labor_camp_reports', 'ordering': ['-report_date', 'connex_number']},
        ),
        migrations.CreateModel(
            name='EquipmentLog',
            fields=[
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('log_date', models.DateField()),
                ('equipment_name', models.CharField(max_length=120)),
                ('equipment_ref', models.CharField(blank=True, default='', max_length=60)),
                ('shift', models.CharField(choices=[('day', 'Day'), ('night', 'Night'), ('full', 'Full')], max_length=10)),
                ('status', models.CharField(choices=[('active', 'فعال'), ('standby', 'آماده'), ('broken', 'خراب')], max_length=10)),
                ('ownership_type', models.CharField(choices=[('owned', 'تملیکی'), ('rented', 'اجاره‌ای')], max_length=10)),
                ('work_start', models.TimeField(blank=True, null=True)),
                ('work_end', models.TimeField(blank=True, null=True)),
                ('repair_hours', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('productive_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('notes', models.TextField(blank=True, default='')),
                ('activity_ref', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='equipment_logs', to='projects.activity')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='authentication.user')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='equipment_logs', to='projects.project')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='authentication.user')),
            ],
            options={'db_table': 'equipment_logs', 'ordering': ['-log_date', 'equipment_name']},
        ),
    ]
