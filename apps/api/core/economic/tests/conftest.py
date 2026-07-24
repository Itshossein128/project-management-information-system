"""Shared fixtures for economic tests."""

import pytest

from contracts.models import Contract, ContractType


@pytest.fixture
def contract(db, project, user, activity):
    return Contract.objects.create(
        project=project,
        contract_number='C-001',
        contract_type=ContractType.MAIN,
        counterparty='Employer Co',
        original_amount='1000000000',
        adjusted_amount='1000000000',
        retention_pct='10',
        tax_pct='9',
        insurance_pct='1',
        advance_payment_pct='20',
        created_by=user,
        updated_by=user,
    )
