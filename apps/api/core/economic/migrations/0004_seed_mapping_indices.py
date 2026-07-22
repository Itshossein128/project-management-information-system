"""Seed InflationIndex rows that match default CostCategoryInflationMapping names."""

from datetime import date
from decimal import Decimal

from django.db import migrations

INDEX_ROWS = (
    ('نیروی کار', date(2025, 1, 1), Decimal('100.0000')),
    ('نیروی کار', date(2025, 6, 1), Decimal('110.0000')),
    ('نیروی کار', date(2025, 12, 1), Decimal('118.5000')),
    ('فولاد', date(2025, 1, 1), Decimal('100.0000')),
    ('فولاد', date(2025, 6, 1), Decimal('114.0000')),
    ('فولاد', date(2025, 12, 1), Decimal('125.0000')),
    ('سیمان', date(2025, 1, 1), Decimal('100.0000')),
    ('سیمان', date(2025, 6, 1), Decimal('111.0000')),
    ('سیمان', date(2025, 12, 1), Decimal('120.5000')),
    ('CPI', date(2025, 1, 1), Decimal('100.0000')),
    ('CPI', date(2025, 6, 1), Decimal('108.5000')),
    ('CPI', date(2025, 12, 1), Decimal('115.2000')),
)


def seed_indices(apps, schema_editor):
    InflationIndex = apps.get_model('economic', 'InflationIndex')
    for index_name, index_date, index_value in INDEX_ROWS:
        InflationIndex.objects.get_or_create(
            index_name=index_name,
            index_date=index_date,
            defaults={'index_value': index_value, 'source': 'sprint12 seed'},
        )


class Migration(migrations.Migration):
    dependencies = [
        ('economic', '0003_economic_engine'),
    ]

    operations = [
        migrations.RunPython(seed_indices, migrations.RunPython.noop),
    ]
