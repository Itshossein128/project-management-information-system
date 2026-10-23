"""Neutral canonical SpecialtyUnit vocabulary.

One shared six-value taxonomy for reporting, department activity, template
configuration, API contracts, and aggregation (feature 032, FR-001/FR-002).

Values are language-independent stable identifiers and are never user-editable.
Display labels are localized by clients; the English labels below exist only as
Django admin/model fallbacks.
"""
from __future__ import annotations

from django.db import models


class SpecialtyUnit(models.TextChoices):
    BUILDINGS = 'buildings', 'Buildings'
    ELECTRICAL = 'electrical', 'Electrical'
    MECHANICAL = 'mechanical', 'Mechanical'
    MACHINERY = 'machinery', 'Machinery'
    WAREHOUSE = 'warehouse', 'Warehouse'
    SECURITY = 'security', 'Security/HSE'


CANONICAL_SPECIALTY_UNITS: tuple[str, ...] = tuple(SpecialtyUnit.values)

# Legacy Discipline -> canonical SpecialtyUnit mapping (FR-004).
# Machinery/warehouse/security have no truthful legacy source and must never be
# inferred from a legacy discipline value.
LEGACY_DISCIPLINE_TO_UNIT: dict[str, str] = {
    'civil': SpecialtyUnit.BUILDINGS,
    'finishing': SpecialtyUnit.BUILDINGS,
    'plumbing': SpecialtyUnit.MECHANICAL,
    'hvac': SpecialtyUnit.MECHANICAL,
    'mechanical': SpecialtyUnit.MECHANICAL,
    'electrical': SpecialtyUnit.ELECTRICAL,
}


def is_canonical_unit(value: object) -> bool:
    return isinstance(value, str) and value in SpecialtyUnit.values
