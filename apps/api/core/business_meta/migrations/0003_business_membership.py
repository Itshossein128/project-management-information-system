# Generated manually for BusinessMembership

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


# Class representing Migration
class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('business_meta', '0002_add_dynamic_table_row'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_role', models.CharField(
                    choices=[
                        ('worker', 'Worker'),
                        ('engineer', 'Engineer'),
                        ('manager', 'Manager'),
                        ('accountant', 'Accountant'),
                        ('site_engineer', 'Site engineer'),
                    ],
                    default='worker',
                    max_length=32,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='memberships',
                    to='business_meta.business',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='business_memberships',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'business membership',
                'verbose_name_plural': 'business memberships',
                'ordering': ['business', 'user__phone_number'],
            },
        ),
        migrations.AddConstraint(
            model_name='businessmembership',
            constraint=models.UniqueConstraint(
                fields=('business', 'user'),
                name='uniq_business_membership_per_user',
            ),
        ),
    ]
