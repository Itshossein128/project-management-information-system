# Generated manually — Sprint 5 barriers

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='riskevent',
            name='category',
            field=models.CharField(
                blank=True,
                choices=[
                    ('equipment_failure', 'خرابی تجهیزات'),
                    ('payment_delay', 'تأخیر پرداخت'),
                    ('design_change', 'تغییر طراحی'),
                    ('weather', 'شرایط جوی'),
                    ('subcontractor', 'پیمانکار'),
                    ('safety', 'ایمنی'),
                    ('other', 'سایر'),
                ],
                default='',
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name='riskevent',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='riskevent',
            name='created_by',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='riskevent',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='riskevent',
            name='impact_on_cost',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='riskevent',
            name='impact_on_schedule',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='riskevent',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='riskevent',
            name='resolved_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='riskevent',
            name='responsible_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='barrier_assignments',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='riskevent',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='riskevent',
            name='updated_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='riskevent',
            name='status',
            field=models.CharField(
                choices=[
                    ('open', 'باز'),
                    ('in_progress', 'در حال پیگیری'),
                    ('resolved', 'رفع شده'),
                ],
                default='open',
                max_length=20,
            ),
        ),
    ]
