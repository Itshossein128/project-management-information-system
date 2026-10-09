"""Unit tests for EVM status DTO helpers."""

import pytest

from schedule.services.evm_status import (
    INDEX_NOT_COMPUTABLE,
    MEASURE_UNREGISTERED,
    index,
    measure,
    not_computable,
)


@pytest.mark.django_db
class TestEvmStatusHelpers:
    def test_unregistered_measure_has_null_amount(self):
        m = measure(123.0, MEASURE_UNREGISTERED)
        assert m['status'] == MEASURE_UNREGISTERED
        assert m['amount'] is None

    def test_not_computable_index_has_null_value(self):
        i = index(1.5, INDEX_NOT_COMPUTABLE, reason='ac_zero')
        assert i['status'] == INDEX_NOT_COMPUTABLE
        assert i['value'] is None
        assert i['reason'] == 'ac_zero'

    def test_not_computable_helper(self):
        i = not_computable('ev_unregistered')
        assert i['value'] is None
        assert i['status'] == INDEX_NOT_COMPUTABLE
