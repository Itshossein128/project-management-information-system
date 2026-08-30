"""Add RequisitionScope, BlockKind, workshop block provisioning."""
from django.conf import settings
from django.db import migrations, models


def backfill_workshop_blocks_and_scope(apps, schema_editor):
    Project = apps.get_model('projects', 'Project')
    Block = apps.get_model('procurement', 'Block')
    RequisitionHeader = apps.get_model('procurement', 'RequisitionHeader')
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))

    fallback_user = User.objects.filter(is_superuser=True).order_by('id').first()

    for project in Project.objects.all():
        actor_id = project.project_manager_id or (fallback_user.id if fallback_user else None)
        Block.objects.get_or_create(
            project=project,
            block_kind='workshop',
            is_deleted=False,
            defaults={
                'block_code': 'WORKSHOP',
                'block_name': 'کارگاه',
                'created_by_id': actor_id,
                'updated_by_id': actor_id,
            },
        )

    RequisitionHeader.objects.filter(scope__isnull=True).update(scope='block')


class Migration(migrations.Migration):

    dependencies = [
        ('procurement', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='block',
            name='block_kind',
            field=models.CharField(
                choices=[('standard', 'Standard'), ('workshop', 'Workshop')],
                default='standard',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='requisitionheader',
            name='scope',
            field=models.CharField(
                choices=[('block', 'Block'), ('workshop', 'Workshop')],
                default='block',
                max_length=20,
            ),
        ),
        migrations.AddIndex(
            model_name='requisitionheader',
            index=models.Index(
                fields=['project', 'scope', 'status'],
                name='req_project_scope_status_idx',
            ),
        ),
        migrations.AddConstraint(
            model_name='block',
            constraint=models.UniqueConstraint(
                condition=models.Q(('block_kind', 'workshop'), ('is_deleted', False)),
                fields=('project',),
                name='uniq_workshop_block_per_project',
            ),
        ),
        migrations.RunPython(backfill_workshop_blocks_and_scope, migrations.RunPython.noop),
    ]
