# P6 import jobs

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0005_remove_activityprogress_actprogress_activity_date_idx'),
    ]

    operations = [
        migrations.CreateModel(
            name='P6ImportJob',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('task_id', models.CharField(blank=True, default='', max_length=64)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('done', 'Done'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('progress_pct', models.PositiveSmallIntegerField(default=0)),
                ('filename', models.CharField(blank=True, default='', max_length=255)),
                ('replace_existing', models.BooleanField(default=False)),
                ('file_data', models.BinaryField(blank=True, null=True)),
                ('result', models.JSONField(blank=True, default=dict)),
                ('error_message', models.TextField(blank=True, default='')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='p6_import_jobs', to='authentication.user')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='p6_import_jobs', to='projects.project')),
            ],
            options={
                'db_table': 'p6_import_jobs',
                'ordering': ['-created_at'],
            },
        ),
    ]
