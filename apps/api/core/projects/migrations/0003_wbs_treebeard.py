# Generated manually for Sprint 2 — migrate WBS to django-treebeard MP_Node

from django.db import migrations, models
import uuid


def clear_wbs_nodes(apps, schema_editor):
    WBS = apps.get_model('projects', 'WBS')
    WBS.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_sprint2_permissions'),
    ]

    operations = [
        migrations.RunPython(clear_wbs_nodes, migrations.RunPython.noop),
        migrations.RemoveField(model_name='wbs', name='parent'),
        migrations.RemoveField(model_name='wbs', name='level'),
        migrations.AddField(
            model_name='wbs',
            name='depth',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='wbs',
            name='numchild',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='wbs',
            name='path',
            field=models.CharField(default='0001', max_length=255, unique=True),
            preserve_default=False,
        ),
    ]
