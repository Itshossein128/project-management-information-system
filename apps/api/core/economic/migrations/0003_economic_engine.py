from django.db import migrations, models
import uuid


DEFAULT_MAPPINGS = [
    ('labor', 'نیروی کار', 1.0),
    ('material', 'فولاد', 0.4),
    ('material', 'سیمان', 0.3),
    ('material', 'CPI', 0.3),
    ('equipment', 'CPI', 1.0),
    ('subcontract', 'CPI', 1.0),
    ('site_overhead', 'CPI', 1.0),
    ('hq_overhead', 'CPI', 1.0),
    ('transport', 'CPI', 1.0),
    ('other', 'CPI', 1.0),
]


def seed_mappings(apps, schema_editor):
    Mapping = apps.get_model('economic', 'CostCategoryInflationMapping')
    for cat, index_name, weight in DEFAULT_MAPPINGS:
        Mapping.objects.get_or_create(
            project_id=None,
            cost_category=cat,
            index_name=index_name,
            defaults={'weight': weight},
        )


class Migration(migrations.Migration):

    dependencies = [
        ('economic', '0002_initial'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inflationindex',
            name='source',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='simulationresult',
            name='scenario_params_json',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='economicsnapshot',
            name='avg_payment_delay_days',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='economicsnapshot',
            unique_together={('project', 'snapshot_date')},
        ),
        migrations.CreateModel(
            name='CostCategoryInflationMapping',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('cost_category', models.CharField(max_length=40)),
                ('index_name', models.CharField(max_length=80)),
                ('weight', models.DecimalField(decimal_places=4, default=1, max_digits=5)),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='inflation_mappings', to='projects.project')),
            ],
            options={'db_table': 'cost_category_inflation_mappings'},
        ),
        migrations.RunPython(seed_mappings, migrations.RunPython.noop),
    ]
