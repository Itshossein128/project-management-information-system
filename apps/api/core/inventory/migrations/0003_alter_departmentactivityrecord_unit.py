# Generated manually for security department optional unit

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='departmentactivityrecord',
            name='unit',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
    ]
