from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procurement', '0002_workshop_scope'),
    ]

    operations = [
        migrations.AddField(
            model_name='approvallog',
            name='details',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='approvallog',
            name='action',
            field=models.CharField(
                choices=[
                    ('create', 'ثبت پیش‌نویس'),
                    ('approve', 'تایید'),
                    ('reject', 'رد'),
                    ('return', 'بازگشت'),
                    ('partial_approve', 'تایید جزئی آیتم'),
                ],
                max_length=20,
            ),
        ),
    ]
