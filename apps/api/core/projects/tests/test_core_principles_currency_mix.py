"""US3: currency mix forbidden without rate."""
from decimal import Decimal

import pytest
from rest_framework.exceptions import ValidationError

from common.money import CurrencyMixError, sum_amounts


def test_mix_forbidden():
    with pytest.raises((ValidationError, CurrencyMixError)):
        sum_amounts(
            [
                {'amount': Decimal('1'), 'currency': 'IRR'},
                {'amount': Decimal('1'), 'currency': 'IRT'},
            ],
            target_currency='IRR',
        )


def test_mix_with_rate_ok():
    total = sum_amounts(
        [
            {'amount': Decimal('1'), 'currency': 'IRR'},
            {'amount': Decimal('1'), 'currency': 'IRT'},
        ],
        target_currency='IRR',
        rate=Decimal('10'),
    )
    assert total == Decimal('11')
