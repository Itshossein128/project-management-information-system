"""EVM measure/index status DTO helpers (FR-EVM incomplete-data semantics)."""

from __future__ import annotations

from typing import Any

MEASURE_REGISTERED = 'registered'
MEASURE_UNREGISTERED = 'unregistered'
MEASURE_INCOMPLETE = 'incomplete'

INDEX_COMPUTABLE = 'computable'
INDEX_NOT_COMPUTABLE = 'not_computable'


def measure(amount: float | None, status: str, *, currency: str | None = None) -> dict[str, Any]:
    """Build a PV/EV/AC measure. Unregistered measures MUST have amount=None."""
    if status == MEASURE_UNREGISTERED:
        amount = None
    payload: dict[str, Any] = {'amount': amount, 'status': status}
    if currency is not None:
        payload['currency'] = currency
    return payload


def index(
    value: float | None,
    status: str,
    *,
    reason: str | None = None,
    round_digits: int | None = 3,
) -> dict[str, Any]:
    """Build SV/CV/SPI/CPI/EAC/ETC/VAC. Not-computable MUST have value=None."""
    if status == INDEX_NOT_COMPUTABLE:
        value = None
    elif value is not None and round_digits is not None and status == INDEX_COMPUTABLE:
        value = round(float(value), round_digits)
    payload: dict[str, Any] = {'value': value, 'status': status}
    if reason:
        payload['reason'] = reason
    return payload


def not_computable(reason: str) -> dict[str, Any]:
    return index(None, INDEX_NOT_COMPUTABLE, reason=reason, round_digits=None)
