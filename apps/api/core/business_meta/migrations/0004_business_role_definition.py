import django.core.validators
from django.db import migrations, models


def seed_business_roles(apps, schema_editor):
    BusinessRoleDefinition = apps.get_model('business_meta', 'BusinessRoleDefinition')
    seed = [
        ('worker', 'Worker', 0),
        ('engineer', 'Engineer', 1),
        ('manager', 'Manager', 2),
        ('accountant', 'Accountant', 3),
        ('site_engineer', 'Site engineer', 4),
    ]
    for key, label, ordering in seed:
        BusinessRoleDefinition.objects.get_or_create(
            key=key,
            defaults={'label': label, 'ordering': ordering},
        )


class Migration(migrations.Migration):

    dependencies = [
        ('business_meta', '0003_business_membership'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessRoleDefinition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'key',
                    models.CharField(
                        help_text='Stable identifier: lowercase, starts with a letter, then letters/digits/underscores.',
                        max_length=64,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message='Slug must start with a letter, then only lowercase letters, numbers, and underscores.',
                                regex='^[a-z][a-z0-9_]*$',
                            )
                        ],
                    ),
                ),
                ('label', models.CharField(max_length=255)),
                ('ordering', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'business role definition',
                'verbose_name_plural': 'business role definitions',
                'ordering': ['ordering', 'key'],
            },
        ),
        migrations.RunPython(seed_business_roles, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='businessmembership',
            name='business_role',
            field=models.CharField(default='worker', max_length=64),
        ),
    ]
