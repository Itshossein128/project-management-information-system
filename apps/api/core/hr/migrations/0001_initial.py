
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0001_initial'),
        migrations.swappable_dependency('authentication.User'),
    ]

    operations = [
        migrations.CreateModel(
            name='OvertimeRequest',
            fields=[
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('department', models.CharField(max_length=120)),
                ('request_date', models.DateField(auto_now_add=True)),
                ('overtime_date', models.DateField()),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('requested_hours', models.DecimalField(decimal_places=2, max_digits=5)),
                ('reason', models.TextField()),
                ('supervisor_approved', models.BooleanField(blank=True, null=True)),
                ('supervisor_notes', models.TextField(blank=True, default='')),
                ('manager_approved', models.BooleanField(blank=True, null=True)),
                ('approved_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('supervisor_approved', 'Supervisor approved'), ('manager_approved', 'Manager approved'), ('rejected', 'Rejected')], default='draft', max_length=30)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='authentication.user')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_overtime_requests', to='authentication.user')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='overtime_requests', to='projects.project')),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='overtime_requests', to='authentication.user')),
                ('supervisor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='supervised_overtime_requests', to='authentication.user')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='authentication.user')),
            ],
            options={'db_table': 'overtime_requests', 'ordering': ['-overtime_date']},
        ),
        migrations.CreateModel(
            name='LeaveRequest',
            fields=[
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('department', models.CharField(max_length=120)),
                ('request_type', models.CharField(choices=[('mission', 'Mission'), ('hourly', 'Hourly'), ('daily', 'Daily')], max_length=10)),
                ('request_date', models.DateField(auto_now_add=True)),
                ('leave_date', models.DateField()),
                ('start_datetime', models.DateTimeField(blank=True, null=True)),
                ('end_datetime', models.DateTimeField(blank=True, null=True)),
                ('mission_subject', models.TextField(blank=True, default='')),
                ('supervisor_approved', models.BooleanField(blank=True, null=True)),
                ('manager_approved', models.BooleanField(blank=True, null=True)),
                ('security_approved', models.BooleanField(blank=True, null=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('supervisor_approved', 'Supervisor approved'), ('manager_approved', 'Manager approved'), ('security_approved', 'Security approved'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], default='draft', max_length=30)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='authentication.user')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_leave_requests', to='authentication.user')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_requests', to='projects.project')),
                ('replacement_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replacement_for_leaves', to='authentication.user')),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_requests', to='authentication.user')),
                ('supervisor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='supervised_leave_requests', to='authentication.user')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='authentication.user')),
            ],
            options={'db_table': 'leave_requests', 'ordering': ['-leave_date']},
        ),
    ]
