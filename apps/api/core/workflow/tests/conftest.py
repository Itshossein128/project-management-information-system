import pytest

from contracts.models import Contract, ContractType


@pytest.fixture
def finance_manager_role(db):
    from master_data.models import Role

    return Role.objects.get(role_name='finance_manager')


@pytest.fixture
def contract(db, project, user):
    return Contract.objects.create(
        project=project,
        contract_number='WF-C-001',
        contract_type=ContractType.MAIN,
        counterparty='Employer Co',
        original_amount='1000000000',
        adjusted_amount='1000000000',
        retention_pct='0',
        tax_pct='0',
        insurance_pct='0',
        advance_payment_pct='0',
        created_by=user,
        updated_by=user,
    )
