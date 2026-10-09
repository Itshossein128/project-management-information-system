"""Helpers to distinguish unset/not-recorded from zero (FR-CORE-010)."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any


def is_unset(value: Any) -> bool:
    return value is None


def coerce_optional_decimal(value: Any) -> Decimal | None:
    """Map blank/missing inputs to None; preserve explicit zero."""
    if value is None or value is Ellipsis:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == '':
            return None
        try:
            return Decimal(stripped)
        except InvalidOperation as exc:
            raise ValueError(f'Invalid decimal: {value!r}') from exc
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    raise ValueError(f'Unsupported optional decimal input: {type(value)!r}')
