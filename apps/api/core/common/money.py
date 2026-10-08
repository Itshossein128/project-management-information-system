"""Currency helpers: refuse silent rial/toman mixing (FR-CORE-006)."""
from __future__ import annotations

from decimal import Decimal
from typing import Iterable, Mapping

from rest_framework.exceptions import ValidationError

ALLOWED_CURRENCIES = frozenset({'IRR', 'IRT'})


class CurrencyMixError(ValidationError):
    default_code = 'currency_mix_forbidden'

    def __init__(self, detail=None, code=None):
        super().__init__(
            detail=detail
            or {
                'code': 'currency_mix_forbidden',
                'message': 'Cannot mix currencies without an explicit conversion rate.',
            },
            code=code or self.default_code,
        )


def assert_same_currency(currencies: Iterable[str], *, target_currency: str) -> None:
    target = (target_currency or '').upper()
    if target not in ALLOWED_CURRENCIES:
        raise ValidationError(
            {'code': 'invalid_currency', 'message': f'Invalid currency: {target_currency}'}
        )
    seen = {(c or '').upper() for c in currencies}
    seen.discard('')
    if not seen:
        return
    if seen == {target}:
        return
    if len(seen) == 1 and target not in seen:
        # homogeneous but not target — still needs rate
        raise CurrencyMixError()
    if len(seen) > 1 or target not in seen:
        raise CurrencyMixError()


def convert_explicit(
    amount: Decimal,
    from_currency: str,
    to_currency: str,
    rate: Decimal | None,
) -> Decimal:
    src = (from_currency or '').upper()
    dst = (to_currency or '').upper()
    if src not in ALLOWED_CURRENCIES or dst not in ALLOWED_CURRENCIES:
        raise ValidationError(
            {'code': 'invalid_currency', 'message': f'Invalid currency pair {src}->{dst}'}
        )
    value = Decimal(amount)
    if src == dst:
        return value
    if rate is None:
        raise CurrencyMixError()
    return value * Decimal(rate)


def sum_amounts(
    items: Iterable[Mapping],
    *,
    target_currency: str,
    rate: Decimal | None = None,
) -> Decimal:
    """Sum amounts into target_currency.

    ``rate`` is the multiplier from *other* currency into ``target_currency``
    when exactly one foreign currency appears (e.g. IRT→IRR with rate=10).
    """
    target = (target_currency or '').upper()
    if target not in ALLOWED_CURRENCIES:
        raise ValidationError(
            {'code': 'invalid_currency', 'message': f'Invalid currency: {target_currency}'}
        )

    rows = list(items)
    currencies = {(row.get('currency') or '').upper() for row in rows}
    currencies.discard('')

    if not currencies or currencies == {target}:
        return sum((Decimal(row['amount']) for row in rows), Decimal('0'))

    foreign = currencies - {target}
    if len(foreign) > 1:
        raise CurrencyMixError()
    if rate is None:
        raise CurrencyMixError()

    total = Decimal('0')
    for row in rows:
        cur = (row.get('currency') or target).upper()
        amt = Decimal(row['amount'])
        if cur == target:
            total += amt
        else:
            total += convert_explicit(amt, cur, target, rate)
    return total
