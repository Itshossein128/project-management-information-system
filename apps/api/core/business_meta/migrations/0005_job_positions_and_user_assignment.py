import django.core.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


# Function to handle migrate memberships to job positions
def migrate_memberships_to_job_positions(apps, schema_editor):
    Business = apps.get_model('business_meta', 'Business')
    BusinessJobPosition = apps.get_model('business_meta', 'BusinessJobPosition')
    BusinessRoleDefinition = apps.get_model('business_meta', 'BusinessRoleDefinition')
    BusinessMembership = apps.get_model('business_meta', 'BusinessMembership')

    for business in Business.objects.all():
        slugs = (
            BusinessMembership.objects.filter(business_id=business.id)
            .values_list('business_role', flat=True)
            .distinct()
        )
        for slug in slugs:
            brd = BusinessRoleDefinition.objects.filter(key=slug).first()
            label = brd.label if brd else slug.replace('_', ' ').title()
            ordering = brd.ordering if brd else 0
            BusinessJobPosition.objects.get_or_create(
                business_id=business.id,
                slug=slug,
                defaults={'label': label, 'ordering': ordering},
            )

    for m in BusinessMembership.objects.all():
        jp = BusinessJobPosition.objects.get(business_id=m.business_id, slug=m.business_role)
        m.job_position_id = jp.id
        m.save(update_fields=['job_position_id'])


# Function to handle noop reverse
def noop_reverse(apps, schema_editor):
    pass


# Class representing Migration
class Migration(migrations.Migration):

    dependencies = [
        ('business_meta', '0004_business_role_definition'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessJobPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'slug',
                    models.CharField(
                        help_text='Stable identifier per business: lowercase, starts with a letter, then letters/digits/underscores.',
                        max_length=64,
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
                (
                    'business',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='job_positions',
                        to='business_meta.business',
                    ),
                ),
            ],
            options={
                'verbose_name': 'business job position',
                'verbose_name_plural': 'business job positions',
                'ordering': ['business', 'ordering', 'slug'],
            },
        ),
        migrations.AddField(
            model_name='businessmembership',
            name='wage',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='businessmembership',
            name='wage_type',
            field=models.CharField(
                choices=[('hourly', 'Hourly'), ('daily', 'Daily'), ('monthly', 'Monthly')],
                default='hourly',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='businessmembership',
            name='weekly_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='businessmembership',
            name='monthly_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='businessmembership',
            name='tools',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='businessmembership',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='businessmembership',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='businessmembership',
            name='status',
            field=models.CharField(
                choices=[('active', 'Active'), ('suspended', 'Suspended'), ('archived', 'Archived')],
                default='active',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='businessmembership',
            name='job_position',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='assignments',
                to='business_meta.businessjobposition',
            ),
        ),
        migrations.AddConstraint(
            model_name='businessjobposition',
            constraint=models.UniqueConstraint(
                fields=('business', 'slug'),
                name='uniq_business_job_position_slug',
            ),
        ),
        migrations.RunPython(migrate_memberships_to_job_positions, noop_reverse),
        migrations.RemoveField(
            model_name='businessmembership',
            name='business_role',
        ),
        migrations.AlterField(
            model_name='businessmembership',
            name='job_position',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='assignments',
                to='business_meta.businessjobposition',
            ),
        ),
        migrations.RenameModel(
            old_name='BusinessMembership',
            new_name='UserBusinessAssignment',
        ),
        migrations.AlterModelOptions(
            name='userbusinessassignment',
            options={
                'ordering': ['business', 'user__phone_number'],
                'verbose_name': 'user business assignment',
                'verbose_name_plural': 'user business assignments',
            },
        ),
        migrations.AlterField(
            model_name='userbusinessassignment',
            name='business',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='user_assignments',
                to='business_meta.business',
            ),
        ),
        migrations.AlterField(
            model_name='userbusinessassignment',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='business_assignments',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name='userbusinessassignment',
            index=models.Index(fields=['user', 'business'], name='uba_user_business_idx'),
        ),
        migrations.RemoveConstraint(
            model_name='userbusinessassignment',
            name='uniq_business_membership_per_user',
        ),
        migrations.AddConstraint(
            model_name='userbusinessassignment',
            constraint=models.UniqueConstraint(
                fields=('business', 'user'),
                name='uniq_user_business_assignment',
            ),
        ),
        migrations.DeleteModel(
            name='BusinessRoleDefinition',
        ),
    ]
