from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0018_contractor_stakeholder_ref'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='approval_submitted_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='projects_submitted_for_approval',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
