"""Shared fixtures for cash-flow projection / allocation tests."""

from datetime import date
from decimal import Decimal

import pytest

from contracts.models import Contract, ContractType, IPC, IPCStatus
from cost_control.models import Commitment, CommitmentStatus
from projects.models import ProjectStatus
from projects.services import create_project_with_creator


@pytest.fixture
def contract(db, project, user, activity):
    return Contract.objects.create(
        project=project,
        contract_number='CF-C-001',
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


@pytest.fixture
def approved_ipc(db, project, contract, user):
    return IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=1,
        period_start=date(2026, 10, 1),
        period_end=date(2026, 10, 31),
        planned_payment_date=date(2026, 10, 15),
        status=IPCStatus.APPROVED,
        gross_amount=Decimal('1200000'),
        net_amount=Decimal('1200000'),
        approved_amount=Decimal('1200000'),
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def approved_commitment(db, project, user, wbs):
    return Commitment.objects.create(
        project=project,
        commitment_number='CF-CM-1',
        amount=Decimal('800000'),
        commitment_date=date(2026, 10, 1),
        due_date=date(2026, 10, 20),
        wbs=wbs,
        status=CommitmentStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def second_project(db, user, project_manager_role):
    from django.utils import timezone

    p = create_project_with_creator(
        creator=user,
        project_code='PRJ-002',
        project_name='Second Project',
        employer='Employer Co',
        start_date='2024-01-01',
    )
    p.status = ProjectStatus.ACTIVE
    p.scope_description = 'Second'
    if p.contract_amount is None:
        p.contract_amount = 1
    p.budget_approved_at = timezone.now()
    p.save(
        update_fields=[
            'status',
            'scope_description',
            'contract_amount',
            'budget_approved_at',
            'updated_at',
        ],
    )
    return p


@pytest.fixture
def outsider_user(db):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.create_user(
        username='outsider',
        mobile='+989121234569',
        full_name='Outsider',
        password='testpass123',
    )
