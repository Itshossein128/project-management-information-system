import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectDocument',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('doc_code', models.CharField(blank=True, default='', max_length=60)),
                ('title', models.CharField(max_length=200)),
                ('doc_type', models.CharField(default='other', max_length=40)),
                ('discipline', models.CharField(blank=True, default='', max_length=60)),
                ('revision', models.CharField(blank=True, default='', max_length=20)),
                ('revision_date', models.DateField(blank=True, null=True)),
                ('file_url', models.CharField(blank=True, default='', max_length=500)),
                ('file_name', models.CharField(blank=True, default='', max_length=200)),
                ('file_size_kb', models.PositiveIntegerField(blank=True, null=True)),
                ('access_level', models.CharField(default='project', max_length=20)),
                ('tags', models.CharField(blank=True, default='', max_length=200)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='projects.project')),
                ('related_activity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='documents', to='projects.activity')),
                ('related_wbs', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='documents', to='projects.wbs')),
                ('restricted_to', models.ManyToManyField(blank=True, related_name='restricted_documents', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='uploaded_documents', to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'project_documents'},
        ),
        migrations.CreateModel(
            name='MeetingMinutes',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('meeting_date', models.DateField()),
                ('meeting_type', models.CharField(max_length=40)),
                ('location', models.CharField(blank=True, default='', max_length=120)),
                ('external_attendees', models.TextField(blank=True, default='')),
                ('agenda', models.TextField(blank=True, default='')),
                ('decisions', models.TextField()),
                ('action_items', models.TextField(blank=True, default='')),
                ('file_url', models.CharField(blank=True, default='', max_length=500)),
                ('attendees', models.ManyToManyField(blank=True, related_name='meetings_attended', to=settings.AUTH_USER_MODEL)),
                ('chairperson', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chaired_meetings', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meetings', to='projects.project')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'meeting_minutes'},
        ),
        migrations.CreateModel(
            name='DocumentRevision',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('revision_label', models.CharField(max_length=20)),
                ('revision_date', models.DateField()),
                ('file_url', models.CharField(max_length=500)),
                ('change_description', models.TextField(blank=True, default='')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revisions', to='documents.projectdocument')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'document_revisions'},
        ),
        migrations.CreateModel(
            name='Correspondence',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('corr_number', models.CharField(max_length=60)),
                ('corr_type', models.CharField(max_length=20)),
                ('subject', models.CharField(max_length=200)),
                ('from_party', models.CharField(max_length=120)),
                ('to_party', models.CharField(max_length=120)),
                ('corr_date', models.DateField()),
                ('received_date', models.DateField(blank=True, null=True)),
                ('response_due_date', models.DateField(blank=True, null=True)),
                ('response_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(default='open', max_length=30)),
                ('summary', models.TextField(blank=True, default='')),
                ('file_url', models.CharField(blank=True, default='', max_length=500)),
                ('tags', models.CharField(blank=True, default='', max_length=200)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='correspondence', to='projects.project')),
                ('related_activity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='correspondence', to='projects.activity')),
                ('related_document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='correspondence', to='documents.projectdocument')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'correspondence'},
        ),
    ]
