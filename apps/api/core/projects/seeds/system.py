"""Shared reference data for demo seeds (units, inflation indices)."""
from datetime import date
from decimal import Decimal

from django.db import transaction

from economic.models import InflationIndex
from master_data.models import Unit

COMMON_UNITS = (
    ('Cubic meter', 'm3'),
    ('Square meter', 'm2'),
    ('Metric ton', 'ton'),
    ('Kilogram', 'kg'),
    ('Day', 'day'),
    ('Each', 'ea'),
    ('Linear meter', 'm'),
    ('Liter', 'L'),
)

# Index names must match CostCategoryInflationMapping seeds (migration 0003).
INFLATION_INDICES = (
    ('CPI', date(2025, 1, 1), Decimal('100.0000')),
    ('CPI', date(2025, 6, 1), Decimal('108.5000')),
    ('CPI', date(2025, 12, 1), Decimal('115.2000')),
    ('Construction Materials', date(2025, 1, 1), Decimal('100.0000')),
    ('Construction Materials', date(2025, 6, 1), Decimal('112.3000')),
    ('Construction Materials', date(2025, 12, 1), Decimal('121.8000')),
    ('نیروی کار', date(2025, 1, 1), Decimal('100.0000')),
    ('نیروی کار', date(2025, 6, 1), Decimal('110.0000')),
    ('نیروی کار', date(2025, 12, 1), Decimal('118.5000')),
    ('فولاد', date(2025, 1, 1), Decimal('100.0000')),
    ('فولاد', date(2025, 6, 1), Decimal('114.0000')),
    ('فولاد', date(2025, 12, 1), Decimal('125.0000')),
    ('سیمان', date(2025, 1, 1), Decimal('100.0000')),
    ('سیمان', date(2025, 6, 1), Decimal('111.0000')),
    ('سیمان', date(2025, 12, 1), Decimal('120.5000')),
)


@transaction.atomic
def seed_system_reference() -> dict:
    units_created = 0
    for name, symbol in COMMON_UNITS:
        _, created = Unit.objects.get_or_create(
            unit_name=name,
            defaults={'unit_symbol': symbol},
        )
        if created:
            units_created += 1

    indices_created = 0
    for index_name, index_date, index_value in INFLATION_INDICES:
        _, created = InflationIndex.objects.get_or_create(
            index_name=index_name,
            index_date=index_date,
            defaults={'index_value': index_value, 'source': 'demo seed'},
        )
        if created:
            indices_created += 1

    return {'units_created': units_created, 'indices_created': indices_created}
