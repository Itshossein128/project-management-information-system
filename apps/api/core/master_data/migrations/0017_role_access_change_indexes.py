from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0016_team_invitation_fields'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='roleaccesschange',
            index=models.Index(fields=['project', 'created_at'], name='rac_project_created_idx'),
        ),
        migrations.AddIndex(
            model_name='roleaccesschange',
            index=models.Index(fields=['subject_user', 'created_at'], name='rac_subject_created_idx'),
        ),
        migrations.AddIndex(
            model_name='roleaccesschange',
            index=models.Index(fields=['actor', 'created_at'], name='rac_actor_created_idx'),
        ),
    ]
