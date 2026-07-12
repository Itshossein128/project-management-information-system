
import django.db.models.deletion
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('field_reports', '0001_initial'),
        ('projects', '0001_initial'),
        migrations.swappable_dependency('authentication.User'),
    ]

    operations = [
        migrations.CreateModel(
            name='DisciplineSubReport',
            fields=[
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('report_date', models.DateField()),
                ('discipline', models.CharField(choices=[('civil', 'Civil'), ('electrical', 'Electrical'), ('mechanical', 'Mechanical'), ('plumbing', 'Plumbing'), ('hvac', 'HVAC'), ('finishing', 'Finishing')], default='civil', max_length=20)),
                ('weather_condition', models.CharField(blank=True, choices=[('sunny', 'آفتابی'), ('cloudy', 'ابری'), ('partly_cloudy', 'نیمه\u200cابری'), ('rainy', 'بارانی'), ('stormy', 'طوفانی'), ('snowy', 'برفی'), ('foggy', 'مه\u200cآلود')], default='', max_length=20)),
                ('form_code', models.CharField(blank=True, default='', max_length=60)),
                ('revision_number', models.CharField(blank=True, default='', max_length=20)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='draft', max_length=20)),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('rejection_reason', models.TextField(blank=True, default='')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_sub_reports', to='authentication.user')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='authentication.user')),
                ('linked_daily_report', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='discipline_sub_reports', to='field_reports.dailyreport')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discipline_sub_reports', to='projects.project')),
                ('submitted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='submitted_sub_reports', to='authentication.user')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='authentication.user')),
            ],
            options={'db_table': 'discipline_sub_reports'},
        ),
        migrations.CreateModel(
            name='DisciplineSubReportActivity',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('row_number', models.PositiveIntegerField()),
                ('shift', models.CharField(max_length=20)),
                ('crew_name', models.CharField(max_length=120)),
                ('foreman_count', models.PositiveIntegerField(blank=True, null=True)),
                ('worker_count', models.PositiveIntegerField(blank=True, null=True)),
                ('zone', models.CharField(blank=True, max_length=60, null=True)),
                ('block', models.CharField(blank=True, max_length=60, null=True)),
                ('floor', models.CharField(blank=True, max_length=60, null=True)),
                ('activity_description', models.TextField()),
                ('unit', models.CharField(blank=True, max_length=40, null=True)),
                ('quantity', models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True)),
                ('execution_percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('activity_ref', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sub_report_activities', to='projects.activity')),
                ('sub_report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='sub_reports.disciplinesubreport')),
            ],
            options={'db_table': 'discipline_sub_report_activities', 'ordering': ['row_number']},
        ),
        migrations.AddConstraint(
            model_name='disciplinesubreport',
            constraint=models.UniqueConstraint(condition=models.Q(('is_deleted', False)), fields=('project', 'report_date', 'discipline'), name='unique_active_sub_report_per_discipline_date'),
        ),
    ]
