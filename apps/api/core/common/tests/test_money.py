"""TDD: currency mix guard helpers (FR-CORE-006)."""
from decimal import Decimal

import pytest
from rest_framework.exceptions import ValidationError

from common.money import CurrencyMixError, convert_explicit, sum_amounts


class TestSumAmounts:
    def test_same_currency_sums(self):
        total = sum_amounts(
            [
                {'amount': Decimal('100'), 'currency': 'IRR'},
                {'amount': Decimal('50.5'), 'currency': 'IRR'},
            ],
            target_currency='IRR',
        )
        assert total == Decimal('150.5')

    def test_mixed_without_rate_forbidden(self):
        with pytest.raises((ValidationError, CurrencyMixError)) as exc:
            sum_amounts(
                [
                    {'amount': Decimal('100'), 'currency': 'IRR'},
                    {'amount': Decimal('10'), 'currency': 'IRT'},
                ],
                target_currency='IRR',
            )
        message = str(exc.value)
        assert 'currency_mix_forbidden' in message or 'currency_mix' in message.lower()

    def test_mixed_with_explicit_rate_converts(self):
        total = sum_amounts(
            [
                {'amount': Decimal('100'), 'currency': 'IRR'},
                {'amount': Decimal('1'), 'currency': 'IRT'},
            ],
            target_currency='IRR',
            rate=Decimal('10'),  # 1 IRT = 10 IRR
        )
        assert total == Decimal('110')


class TestConvertExplicit:
    def test_requires_rate_when_currencies_differ(self):
        with pytest.raises((ValidationError, CurrencyMixError)):
            convert_explicit(Decimal('10'), from_currency='IRT', to_currency='IRR', rate=None)

    def test_identity_when_same_currency(self):
        assert convert_explicit(Decimal('10'), 'IRR', 'IRR', rate=None) == Decimal('10')
