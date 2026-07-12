import pytest
from decimal import Decimal

from contracts.models import Contract, ContractItem, ContractType, IPC, IPCItem, IPCStatus
from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role


@pytest.fixture
def finance_manager_role(db):
    return Role.objects.get(role_name='finance_manager')


@pytest.fixture
def finance_client(api_client, user, project, finance_manager_role):
    member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.create(member=member, role=finance_manager_role)
    api_client.force_authenticate(user=user)
    return api_client


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


@pytest.fixture
def contract_item(db, contract, activity, user):
    return ContractItem.objects.create(
        contract=contract,
        activity=activity,
        boq_code='BOQ-1',
        description='Earthworks',
        unit_price='10000',
        quantity='100',
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def ipc(db, project, contract, user):
    from datetime import date

    from contracts.models import IPC, IPCStatus

    return IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=1,
        period_start=date(2024, 3, 1),
        period_end=date(2024, 3, 31),
        prepared_date=date(2024, 4, 1),
        status=IPCStatus.DRAFT,
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def viewer_client(api_client, other_user, project, viewer_role):
    member = ProjectMember.objects.create(
        project=project,
        user=other_user,
        status=MemberStatus.ACTIVE,
    )
    ProjectMemberRole.objects.create(member=member, role=viewer_role)
    api_client.force_authenticate(user=other_user)
    return api_client


@pytest.fixture
def ipc_with_item(db, project, contract, contract_item, user):
    ipc = IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=1,
        gross_amount=Decimal('100000'),
        status=IPCStatus.DRAFT,
        created_by=user,
        updated_by=user,
    )
    IPCItem.objects.create(
        ipc=ipc,
        contract_item=contract_item,
        description='Line',
        qty_current=Decimal('10'),
        unit_price=Decimal('10000'),
        amount_current=Decimal('100000'),
        created_by=user,
        updated_by=user,
    )
    return ipc
