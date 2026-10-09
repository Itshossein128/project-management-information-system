# Generated manually for 006-hr-capacity

from decimal import Decimal

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0009_central_data_model'),
        ('authentication', '0002_alter_user_mobile'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='default_capacity_percent',
            field=models.DecimalField(decimal_places=2, default=Decimal('100'), max_digits=6),
        ),
        migrations.AddField(
            model_name='user',
            name='org_unit',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='users',
                to='master_data.organizationunit',
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='qualifications',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='user',
            name='skills',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='user',
            name='supervisor',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='supervised_persons',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
