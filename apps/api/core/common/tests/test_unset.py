"""TDD: unset vs zero helpers (FR-CORE-010)."""
from decimal import Decimal

from common.unset import coerce_optional_decimal, is_unset


class TestUnsetHelpers:
    def test_none_is_unset(self):
        assert is_unset(None) is True
        assert coerce_optional_decimal(None) is None

    def test_zero_is_not_unset(self):
        assert is_unset(0) is False
        assert is_unset(Decimal('0')) is False
        assert coerce_optional_decimal(0) == Decimal('0')
        assert coerce_optional_decimal(Decimal('0')) == Decimal('0')

    def test_empty_string_maps_to_null(self):
        assert coerce_optional_decimal('') is None
        assert coerce_optional_decimal('   ') is None

    def test_missing_sentinel_maps_to_null(self):
        assert coerce_optional_decimal(Ellipsis) is None

    def test_numeric_string_preserved(self):
        assert coerce_optional_decimal('12.5') == Decimal('12.5')
